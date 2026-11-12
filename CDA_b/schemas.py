"""Core data structures for CDA (design v4).

Design rules
- Step IDs ("r2_s3") are created by code only, never by an LLM, and never renumbered.
- Every edge means the same thing: `src` must finish before `dst` can finish.
- Stage 2 writes LOCAL / ASK_HELP / RECEIVE / PASS. HELP is created only in Stage 3, when a robot
  answers YES to an ASK_HELP.
- A collaboration edge exists only if the providing side said YES (I1 consent). Its consent label:
    mutual         the other side named me (or offered to me) and I said YES
    provider-only  I volunteered for someone else's request, or my PASS offer was not taken
  A request with no candidate edge is a node state ("no candidate"), not an edge.
- Stage 4: the Graph LLM edits (SELECT / MERGE / DROP / ORDER, existing ids only), rules check
  structure, confirm edges (default policy), run dependency closure, schedule and finalize the report.
- Two kinds of collaboration only:
    ASK_HELP <-> HELP     capability: work the requester's body cannot do
    RECEIVE  <-> PASS     object: an object from another room
  An object is moved by whichever end of the handoff is mobile. Two fixed robots cannot exchange objects.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- step / edge vocab
LOCAL, ASK_HELP, HELP, RECEIVE, PASS = "LOCAL", "ASK_HELP", "HELP", "RECEIVE", "PASS"
STEP_TYPES = {LOCAL, ASK_HELP, HELP, RECEIVE, PASS}
PLAN_TYPES = {LOCAL, ASK_HELP, RECEIVE, PASS}      # what Stage 2 may write
REQUEST_TYPES = {ASK_HELP, RECEIVE}
PROVIDER_TYPES = {HELP, PASS}
PROVIDER_FOR = {ASK_HELP: HELP, RECEIVE: PASS}

SEQ, TRANSFER, HELP_EDGE, ORDER = "SEQ", "TRANSFER", "HELP", "ORDER"   # ORDER: added by Stage 4
CONFIRMED, PROPOSED = "CONFIRMED", "PROPOSED"      # collaboration edges: PROPOSED until 4.3 confirms
MUTUAL, PROVIDER_ONLY, MERGED = "mutual", "provider-only", "merged"   # consent label κ (merged: 4.2 MERGE)

PHASE_MIN = 5              # the Joint Plan is scheduled in 5-minute slots (assigned in Stage 4)
SIZE_MIN = {"short": 1, "medium": 2}   # default step length by type (minutes, coarse)


def agent_num(agent: str) -> int:
    return int(agent.lstrip("Rr"))


def norm(s: str | None) -> str:
    return " ".join((s or "").lower().split())


def action_str(action) -> str:
    """A step action as text. Stage 2 may write {"verb","object","from","to","state"}."""
    if isinstance(action, dict):
        parts = [action.get("verb", "")]
        if action.get("object"):
            parts += ["the", action["object"]]
        if action.get("from") and action.get("to"):
            parts += ["from", action["from"], "to", action["to"]]
        elif action.get("from"):
            parts += ["from", action["from"]]
        elif action.get("to"):
            parts += ["to", action["to"]]
        if action.get("state"):
            parts.append(f"({action['state']})")
        return " ".join(p for p in parts if p).strip()
    return str(action or "").strip()


def match_item(item: str | None, items: list[str]) -> str | None:
    """Look an item name up in a has_items list (list check, not a meaning check).
    has_items entries look like "white mug (cabinet, image 1)"; "white mug" matches it."""
    x = norm(item)
    if not x:
        return None
    for h in items:
        base = norm(h.split("(")[0])
        if x == norm(h) or x == base or (base and (x in norm(h) or base in x)):
            return h
    return None


# ---------------------------------------------------------------- task config
@dataclass
class Profile:
    room: str
    mobile: bool
    payload_kg: float | None
    embodiment: str            # e.g. "wheeled base, one 6-DoF arm, low reach"


@dataclass
class AgentInput:
    id: str                    # "R1"
    profile: Profile
    images: list[str] = field(default_factory=list)
    instruction: str = ""      # text about areas the robot cannot see (no exploration)


@dataclass
class TaskConfig:
    task_id: str
    task: str
    deadline_min: int
    agents: list[AgentInput]

    @classmethod
    def load(cls, path: str | Path) -> "TaskConfig":
        path = Path(path)
        d = json.loads(path.read_text(encoding="utf-8"))
        agents = []
        for a in d["agents"]:
            imgs = [str((path.parent / p).resolve()) if not Path(p).is_absolute() else p
                    for p in a.get("images", [])]
            agents.append(AgentInput(a["id"], Profile(**a["profile"]), imgs, a.get("instruction", "")))
        return cls(d["task_id"], d["task"], d["deadline_min"], agents)

    @classmethod
    def from_notebook(cls, task: str, agents: list[dict], deadline_min: int = 20,
                      task_id: str = "task") -> "TaskConfig":
        """agents: [{"room", "mobile", "capability", "images", "hidden_info", "payload_kg"?}, ...]
        Robots are named R1..Rn in the given order."""
        out = []
        for i, a in enumerate(agents, start=1):
            hid = a.get("hidden_info", "")
            hid = "\n".join(hid) if isinstance(hid, list) else (hid or "")
            out.append(AgentInput(f"R{i}", Profile(room=a["room"], mobile=bool(a["mobile"]),
                                                   payload_kg=(float(a["payload_kg"]) if a.get("payload_kg") else None),
                                                   embodiment=a["capability"]),
                                  list(a.get("images", [])), hid))
        return cls(task_id, task, deadline_min, out)

    def agent(self, aid: str) -> AgentInput:
        return next(a for a in self.agents if a.id == aid)

    @property
    def ids(self) -> list[str]:
        return [a.id for a in self.agents]

    def mover(self, giver: str, receiver: str) -> str | None:
        """Who physically moves an object from giver's room to receiver's room.
        A mobile giver brings it; otherwise a mobile receiver collects it; two fixed robots: None."""
        if giver in self.ids and self.agent(giver).profile.mobile:
            return giver
        if receiver in self.ids and self.agent(receiver).profile.mobile:
            return receiver
        return None


# ---------------------------------------------------------------- stage 1
@dataclass
class Offer:
    """O_i = <C_i, A_i+, A_i-, H_i, N_i, G_i>. Everything is public except obs_scope / reasoning."""
    agent: str
    capability: str
    can_do: list[str]
    cannot_do: list[str]
    has_items: list[str]
    need_from_others: list[str]
    intends: list[str] = field(default_factory=list)   # G_i: sub-goals (numbered), not steps
    # private (never broadcast)
    obs_scope: str = ""
    reasoning: str = ""

    def public(self) -> dict:
        return {"agent": self.agent, "capability": self.capability, "can_do": self.can_do,
                "cannot_do": self.cannot_do, "has_items": self.has_items,
                "need_from_others": self.need_from_others, "intends": self.intends}

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- graph elements
@dataclass
class Node:
    id: str
    agent: str
    type: str
    action: str | dict = ""
    item: str | None = None
    target: str | None = None          # request / PASS: the robot named (non-binding hint); HELP/PASS answer: requester
    uses: int | None = None            # index into the agent's own can_do
    location: str = ""
    origin: str = "local"              # local | offer (PASS offered in Stage 2) | accept | volunteer | receive
    answers: str | None = None         # provider created in Stage 3 -> id of the request it answers
    enables: str | None = None         # request -> id of the own later LOCAL step that needs it
    serves: int | None = None          # index into the agent's own intends (G_i)
    serves_text: str = ""
    replies: list[dict] = field(default_factory=list)   # request / offer: NO answers and reasons (Stage 3)
    status: str = "active"             # active | dropped (4.2 DROP) | removed (4.4 closure)
    status_reason: str = ""
    size: str | None = None            # short | medium (4.5 default by type)
    phase: int | None = None           # 5-minute slot (1 = 0-5 min)
    t_start: float | None = None       # minutes
    t_end: float | None = None

    def brief(self) -> dict:
        d = {"id": self.id, "agent": self.agent, "type": self.type, "text": self.text()}
        if self.item:
            d["item"] = self.item
        if self.target:
            d["target"] = self.target
        return d

    def text(self) -> str:
        a = action_str(self.action)
        if self.type in (RECEIVE, PASS):
            return f"{a} ({self.item})" if a and self.item and norm(self.item) not in norm(a) else (a or self.item or "")
        return a


@dataclass
class Edge:
    src: str
    dst: str
    kind: str                          # SEQ | TRANSFER | HELP | ORDER
    kappa: str | None = None           # mutual | provider-only | merged  (collaboration edges only)
    status: str = PROPOSED             # PROPOSED | CONFIRMED  (SEQ / ORDER are always CONFIRMED)
    source: str = "stage3"             # stage3 | graph
    existing: bool = False             # provider is a step the robot already had (YES + existing_step)
    decided_by: str = ""               # 4.3: SELECT | MERGE | default (mutual, single candidate)

    @property
    def key(self) -> tuple[str, str]:
        return (self.src, self.dst)


def describe_config(cfg: TaskConfig) -> str:
    lines = [f"TASK ({cfg.task_id}, deadline {cfg.deadline_min} min): {cfg.task}", ""]
    for a in cfg.agents:
        p = a.profile
        lines.append(f"{a.id} | room={p.room} | mobile={p.mobile} | {p.embodiment}")
        lines.append(f"     images={a.images}")
        if a.instruction:
            lines.append(f"     hidden_info={a.instruction}")
    return "\n".join(lines)

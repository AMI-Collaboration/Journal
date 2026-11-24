"""Core data structures for CDA.

CDA is a HIGH-LEVEL planner. It does not track paths, hands, or travel time. A step is a short
natural-language sentence plus a few fields (type, room, item, partner robot, enables).

Step types
    LOCAL     work in my own room
    PASS      give object o to robot j. Includes picking it up and carrying it; whichever side is
              mobile moves. When it ends, j has o.
    RECEIVE   I want object o that robot i has.
    ASK_HELP  I need help. Names no robot, only a condition ("someone who can lift a sofa").
    HELP      I go to robot j's room and do the work for j.

Order rules (the only timing rules)
    - a RECEIVE starts only after its PASS ends     (PASS -> RECEIVE edge)
    - an ASK_HELP starts only after its HELP ends   (HELP -> ASK_HELP edge)
    - one robot's steps run in the order it wrote them (SEQ edges)
    - Stage 4 may add ORDER edges between robots

Design rules
    - Step ids ("r2_s3") are made by code only and never renumbered. A robot's order is kept
      separately (Plan.order), so a step added in Stage 3 can be inserted without renaming others.
    - Every edge means: src must finish before dst can start.
    - LLM decides, rules verify. Rules never rewrite a decision; they accept it or reject and record it.
    - Nothing disappears silently: every removal is written to the report with a reason.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- step / edge vocabulary
LOCAL, PASS, RECEIVE, ASK_HELP, HELP = "LOCAL", "PASS", "RECEIVE", "ASK_HELP", "HELP"
STEP_TYPES = (LOCAL, PASS, RECEIVE, ASK_HELP, HELP)
REQUEST_TYPES = (RECEIVE, ASK_HELP)
PROVIDER_TYPES = (PASS, HELP)
PROVIDER_FOR = {RECEIVE: PASS, ASK_HELP: HELP}      # request type -> provider type
REQUEST_FOR = {PASS: RECEIVE, HELP: ASK_HELP}

SEQ, TRANSFER, HELP_EDGE, ORDER = "SEQ", "TRANSFER", "HELP", "ORDER"
EDGE_KIND = {PASS: TRANSFER, HELP: HELP_EDGE}       # provider type -> collaboration edge kind

# who proposed a collaboration edge
BY_PROVIDER, BY_REQUESTER, BY_BOTH, BY_CENTER = "provider", "requester", "both", "center"

# step origin
FROM_PLAN, FROM_STAGE3 = "plan", "stage3"

# step length in minutes (coarse; used only for the schedule)
DURATION_MIN = {LOCAL: 1, PASS: 1, RECEIVE: 1, HELP: 1, ASK_HELP: 0}   # ASK_HELP only marks "help me now"
PHASE_MIN = 5              # output is grouped in 5-minute blocks; the schedule itself is in minutes


def agent_num(agent: str) -> int:
    return int(agent.lstrip("Rr"))


def norm(s: str | None) -> str:
    return " ".join((s or "").lower().split())


# ---------------------------------------------------------------- task config
@dataclass
class Profile:
    room: str
    mobile: bool
    payload_kg: float | None
    embodiment: str            # capability text (from robot.json)


@dataclass
class AgentInput:
    id: str                    # "R1"
    profile: Profile
    images: list[str] = field(default_factory=list)
    instruction: str = ""      # hidden info: ONLY objects the robot cannot see (e.g. inside a closed cabinet)


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
        """agents: [{"room", "mobile", "capability", "images", "hidden_info", "payload_kg"?}, ...].
        Robots are named R1..Rn in the given order. A robot learns about objects only from its images
        and from "hidden_info" (objects it cannot see); there is no full object list of the room."""
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

    @property
    def rooms(self) -> list[str]:
        return list(dict.fromkeys(a.profile.room for a in self.agents))

    def room_of(self, aid: str) -> str:
        return self.agent(aid).profile.room

    def mover(self, giver: str, receiver: str) -> str | None:
        """Who carries an object from giver to receiver. A mobile giver brings it; otherwise a mobile
        receiver collects it. Two fixed robots cannot exchange objects (even in the same room)."""
        if giver in self.ids and self.agent(giver).profile.mobile:
            return giver
        if receiver in self.ids and self.agent(receiver).profile.mobile:
            return receiver
        return None

    def can_help(self, helper: str) -> bool:
        """HELP means going to another robot's room: only a mobile robot can do it."""
        return helper in self.ids and self.agent(helper).profile.mobile


# ---------------------------------------------------------------- stage 1
@dataclass
class Offer:
    """What a robot tells the team for THIS task. room / mobile / capability come from code, the rest
    from the LLM. Everything except `reasoning` is broadcast, so that in Stage 2 a robot can plan
    "I will get the apple from R2" (RECEIVE, from R2's has_items) or "someone who can carry it" (ASK_HELP).
        can_do     : actions my body and room allow, broad menu of "verb object" strings (filtered later)
        can_help   : work I can do for other robots (e.g. "bring food"; usually empty for a fixed robot)
        need_from_others : what the task needs that I cannot do or get myself, "verb object" strings by object or
                     action only (never a robot), verbs from the whole team's capability lists
        has_items  : movable objects in my room that matter for the task (no furniture / appliances)"""
    agent: str
    room: str
    mobile: bool
    capability: str                    # from robot.json (code), not written by the LLM
    can_do: list[str]
    can_help: list[str]
    need_from_others: list[str]
    has_items: list[str]
    reasoning: str = ""                # private

    def public(self) -> dict:
        d = asdict(self)
        d.pop("reasoning")
        return d

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- graph elements
@dataclass
class Node:
    id: str
    agent: str
    type: str
    text: str                          # short natural-language sentence
    room: str = ""                     # where the step happens (one of the task's rooms)
    item: str | None = None            # PASS / RECEIVE
    target: str | None = None          # PASS: receiver, RECEIVE: giver, HELP: robot helped
    condition: str | None = None       # ASK_HELP: who could help, in words (no robot named)
    enables: str | None = None         # RECEIVE / ASK_HELP: id of my own later step that needs it
    after: str | None = None           # PASS: my own step that must be done before I can give (e.g. make it)
    serves: int | None = None          # index into the robot's own goals
    origin: str = FROM_PLAN            # plan | stage3
    status: str = "active"             # active | dropped (Graph LLM) | removed (cleanup)
    status_reason: str = ""
    t_start: float | None = None       # minutes
    t_end: float | None = None

    @property
    def phase(self) -> int | None:
        return None if self.t_start is None else int(self.t_start // PHASE_MIN) + 1

    def brief(self) -> dict:
        d = {"id": self.id, "robot": self.agent, "type": self.type, "text": self.text}
        for k in ("item", "target", "condition", "enables", "after"):
            if getattr(self, k):
                d[k] = getattr(self, k)
        if self.origin != FROM_PLAN:
            d["origin"] = "added in Stage 3"
        return d


@dataclass
class Edge:
    src: str                           # must finish before dst starts
    dst: str
    kind: str                          # SEQ | TRANSFER | HELP | ORDER
    proposed_by: str | None = None     # provider | requester | both | center (collaboration edges)
    reasons: list[str] = field(default_factory=list)
    decided_by: str = ""               # Stage 4: graph_llm | both_proposed (rule)

    @property
    def key(self) -> tuple[str, str]:
        return (self.src, self.dst)

    @property
    def id(self) -> str:
        return f"{self.src}->{self.dst}"


@dataclass
class Plan:
    """One robot's Local Plan: its goals, its steps (by id) and their order."""
    agent: str
    goals: list[str]
    nodes: dict[str, Node]
    order: list[str]                   # step ids in execution order
    next_k: int = 1                    # next step number for a new id

    def new_id(self) -> str:
        nid = f"r{agent_num(self.agent)}_s{self.next_k}"
        self.next_k += 1
        return nid

    def steps(self) -> list[Node]:
        return [self.nodes[i] for i in self.order]

    def insert(self, node: Node, before: str | None = None) -> None:
        self.nodes[node.id] = node
        if before in self.order:
            self.order.insert(self.order.index(before), node.id)
        else:
            self.order.append(node.id)


# ================================================================================================
# event log
# ================================================================================================
class EventLog:
    """Ordered log of what each robot / stage did. Saved as events.json."""

    def __init__(self, verbose: bool = True):
        self.events: list[dict] = []
        self.verbose = verbose
        self.t0 = time.time()

    def log(self, stage: str, who: str, what: str, **data) -> None:
        e = {"t": round(time.time() - self.t0, 2), "stage": stage, "who": who, "what": what, **data}
        self.events.append(e)
        if self.verbose:
            extra = " ".join(f"{k}={v}" for k, v in data.items() if k not in ("detail",))
            print(f"[{e['t']:6.2f}s] {stage:<8} {who:<4} {what} {extra}".rstrip())


def _j(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=1)


def as_list(x) -> list[str]:
    """LLM list field -> list of non-empty strings."""
    if isinstance(x, str):
        return [x.strip()] if x.strip() else []
    out = []
    for v in x or []:
        if isinstance(v, dict):
            v = next((v[k] for k in ("text", "name", "goal", "item") if v.get(k)), "")
        if str(v).strip():
            out.append(str(v).strip())
    return out


def as_int(x) -> int | None:
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, str) and x.strip().lstrip("-").isdigit():
        return int(x.strip())
    return None

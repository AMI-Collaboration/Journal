"""Stage 3 - Edge Proposal. Robots answer each other's requests; nobody chooses yet.

Every Local Plan is broadcast. Each robot, in parallel, reads the other robots' requests and
answers the ones it can serve by adding ONE step of its own per answer:
    RECEIVE  (object o from me)  <-  my new PASS   ("I give you o")
    ASK_HELP (exact work)        <-  my new HELP   ("I come to your room and do it")
Each answer becomes a candidate edge  new step -> request.  Several robots may answer the same
request; choosing between them is Stage 4's job. Steps added here are marked "added in Stage 3" and
are removed again in Stage 4 if their edge is not chosen.

Code checks only the shape of each answer (the request exists, belongs to another robot, the step
type fits) and records it. Rejected answers and requests nobody answered are recorded.
"""
from __future__ import annotations

import asyncio

from .core import (ASK_HELP, BY_CENTER, BY_PROVIDER, EDGE_KIND, FROM_STAGE3, HELP, PASS, PROVIDER_FOR, RECEIVE,
                   REQUEST_TYPES, Edge, EventLog, Node, Offer, Plan, TaskConfig, _j)
from .llm import BaseLLM

FROM_CENTER = "center"

# ================================================================================================
# PROMPTS
# ================================================================================================
PROPOSE_SYSTEM = """You are robot {agent} ({mobility}, in the {room}).
All robots have shared their plans. Now you ANSWER the other robots' requests that you can serve.
You do not decide who finally does it: several robots may answer the same request, and another
stage chooses later. You only offer.

How to answer:
- a RECEIVE (the robot wants an object):  add a PASS step: you give that object to that robot.
  Picking it up and carrying it is included; whichever of you can move does the moving.
- an ASK_HELP (the robot needs exact work done): add a HELP step: you go to its room and do that work.

Answer a request ONLY if ALL of these are true:
1. YOUR BODY CAN DO IT: it fits your capability. A FIXED robot cannot HELP (it cannot go to another
   room), and two FIXED robots cannot give objects to each other.
2. YOU HAVE WHAT IT NEEDS: for a PASS, the object is in YOUR has_items or one of YOUR steps makes it
   (e.g. you give the sandwich that your step "make a sandwich" makes; then set "after" to that step).
3. THE TASK NEEDS IT: it really serves the task, not only because someone asked.
4. IT IS NOT ALREADY DONE: no other step (yours or another robot's) already does this work.
If any of these is false or unclear, do not answer. An unanswered request is fine: it is reported.

Write one entry per request you answer. "after" is the id of YOUR step that must be finished before
you can do the new step (e.g. the step that makes or gets the object you give or carry); null if
nothing has to happen first.
You will do the new step as soon as it is possible, in between your own steps.

Return JSON:
{{"answers":[{{"request":"<request step id>","step":{{"type":"PASS"|"HELP","text":"<one short sentence>","item":"<object, PASS only>"}},
             "after":"<your step id or null>","reason":"<why you can do it, one sentence>"}}]}}
Return {{"answers":[]}} if you cannot serve any request."""

PROPOSE_USER = """TASK: {task}

ROBOTS: {robots}

YOUR STEPS:
{own_steps}

REQUESTS OF OTHER ROBOTS:
{requests}

OTHER ROBOTS' STEPS (for context):
{other_steps}"""


def steps_view(plan: Plan) -> list[dict]:
    return [n.brief() for n in plan.steps()]


def robots_view(cfg: TaskConfig, offers: dict[str, Offer]) -> dict:
    return {a.id: {"room": a.profile.room, "mobile": a.profile.mobile, "capability": a.profile.embodiment,
                   "has_items": offers[a.id].has_items if a.id in offers else []} for a in cfg.agents}


# ================================================================================================
# CODE
# ================================================================================================
_NOT_OBJECTS = {"carry", "bring", "place", "put", "take", "give", "get", "move", "make", "pack", "prepare",
                "from", "into", "onto", "with", "the", "and", "for", "living", "room", "kitchen", "bedroom",
                "bathroom", "table", "coffee table", "counter", "shelf", "help", "quick", "some", "them", "it"}


def object_words(text: str | None) -> set[str]:
    """Rough object words of a sentence (for the default "after")."""
    t = (text or "").lower().replace("coffee table", " ").replace("coffee machine", " ")
    return {w.strip(".,;:!?") for w in t.split() if len(w.strip(".,;:!?")) >= 3} - _NOT_OBJECTS


def add_provider_step(plan: Plan, req: Node, spec: dict, cfg: TaskConfig, origin: str,
                      after: str | None = None) -> tuple[Node | None, str]:
    """Add the PASS / HELP step that answers `req` to `plan`. Returns (node, error)."""
    spec = spec if isinstance(spec, dict) else {}
    want = PROVIDER_FOR[req.type]
    t = str(spec.get("type") or want).upper().strip()
    if t != want:
        return None, f"a {req.type} is answered with {want}, got '{t}'"
    item = (str(spec["item"]).strip() if spec.get("item") else req.item) if t == PASS else None
    text = str(spec.get("text") or "").strip() or (
        f"give the {item} to {req.agent}" if t == PASS else req.text)
    n = Node(id=plan.new_id(), agent=plan.agent, type=t, text=text, origin=origin, item=item, target=req.agent,
             room=cfg.room_of(req.agent) if t == HELP else cfg.room_of(plan.agent))
    # "after": my own step that must be finished first (the step that makes / gets the object).
    own = [i for i in plan.order if plan.nodes[i].origin == "plan" and plan.nodes[i].type in ("LOCAL", RECEIVE)]
    if after in own:
        n.after = after
    else:
        # not given: wait for my last own LOCAL / RECEIVE step that mentions the object, so nothing is
        # given or carried before it exists. None found = I already have it / nothing to wait for.
        words = object_words(item if t == PASS else req.text)
        hits = [i for i in own if words & object_words(f"{plan.nodes[i].text} {plan.nodes[i].item or ''}")]
        n.after = hits[-1] if hits else None
    plan.insert(n)                       # order is only a priority; timing comes from dependencies
    return n, ""


async def edge_proposal(cfg: TaskConfig, plans: dict[str, Plan], offers: dict[str, Offer], llm: BaseLLM,
                        log: EventLog) -> tuple[dict[tuple[str, str], Edge], dict]:
    """Returns (candidate edges keyed by (provider step, request), record)."""
    robots = _j(robots_view(cfg, offers))
    req_of = {n.id: n for p in plans.values() for n in p.steps() if n.type in REQUEST_TYPES}

    async def ask(agent: str) -> dict:
        a = cfg.agent(agent)
        others = {b: p for b, p in plans.items() if b != agent}
        reqs = [n.brief() for n in req_of.values() if n.agent != agent]
        if not reqs:
            return {"answers": []}
        system = PROPOSE_SYSTEM.format(agent=agent, room=a.profile.room,
                                       mobility="mobile" if a.profile.mobile else "FIXED")
        user = PROPOSE_USER.format(task=cfg.task, robots=robots, own_steps=_j(steps_view(plans[agent])),
                                   requests=_j(reqs), other_steps=_j({b: steps_view(p) for b, p in others.items()}))
        return await llm.complete(system, user, key=f"propose:{agent}")

    answers = dict(zip(cfg.ids, await asyncio.gather(*[ask(a) for a in cfg.ids])))

    cand: dict[tuple[str, str], Edge] = {}
    rejected: list[dict] = []
    added: list[dict] = []
    for agent in cfg.ids:                                  # deterministic merge, robot order
        raw = answers[agent].get("answers") if isinstance(answers[agent], dict) else None
        seen: set[str] = set()
        for x in raw if isinstance(raw, list) else []:
            x = x if isinstance(x, dict) else {}
            rid, reason = str(x.get("request") or "").strip(), str(x.get("reason") or "").strip()

            def reject(why: str):
                rejected.append({"by": agent, "request": rid, "why": why, "answer": x})
                log.log("propose", agent, "rejected", request=rid, why=why)

            if rid not in req_of:
                reject(f"{rid} is not a request (RECEIVE / ASK_HELP)")
                continue
            req = req_of[rid]
            if req.agent == agent:
                reject("a robot cannot answer its own request")
                continue
            if rid in seen:
                reject("answered the same request twice")
                continue
            node, err = add_provider_step(plans[agent], req, x.get("step"), cfg, FROM_STAGE3, x.get("after"))
            if node is None:
                reject(err)
                continue
            seen.add(rid)
            cand[(node.id, rid)] = Edge(node.id, rid, EDGE_KIND[node.type], proposed_by=BY_PROVIDER,
                                        reasons=[f"{agent}: {reason}"] if reason else [])
            added.append({"by": agent, "step": node.id, "type": node.type, "text": node.text, "for": rid})
            log.log("propose", agent, "answer", step=node.id, type=node.type, request=rid)

    no_answer = [{"request": n.id, "robot": n.agent, "type": n.type, "text": n.text}
                 for n in req_of.values() if not any(k[1] == n.id for k in cand)]
    for x in no_answer:
        log.log("propose", x["robot"], "no_answer", request=x["request"])
    record = {"answers": answers, "rejected": rejected, "added_steps": added, "no_proposal": no_answer}
    return cand, record


def center_candidates(cfg: TaskConfig, plans: dict[str, Plan]) -> tuple[dict[tuple[str, str], Edge], dict]:
    """Ablation "no edge proposal": robots do not answer each other. Code makes a draft answer for
    every (request, other robot) pair that is physically possible, and the Graph LLM chooses centrally.
    Unchosen drafts are removed in Stage 4 like unchosen Stage-3 steps."""
    cand: dict[tuple[str, str], Edge] = {}
    reqs = [n for p in plans.values() for n in p.steps() if n.type in REQUEST_TYPES]
    for req in reqs:
        for b in cfg.ids:
            if b == req.agent:
                continue
            if req.type == RECEIVE and cfg.mover(b, req.agent) is None:
                continue
            if req.type == ASK_HELP and not cfg.can_help(b):
                continue
            node, _ = add_provider_step(plans[b], req, {}, cfg, FROM_CENTER)
            cand[(node.id, req.id)] = Edge(node.id, req.id, EDGE_KIND[node.type], proposed_by=BY_CENTER)
    return cand, {"mode": "center", "n_drafts": len(cand)}

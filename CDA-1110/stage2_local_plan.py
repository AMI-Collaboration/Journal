"""Stage 2 - Local Plan. Each robot, in parallel, writes LOCAL / ASK_HELP / RECEIVE / PASS steps.

Code checks FORMAT only (numbers and lists, never meaning):
- the step type is allowed; target is another existing robot
- uses / enables / serves are existing indices (enables: an own LATER LOCAL step; required for ASK_HELP)
- a PASS item is in the robot's own has_items; a RECEIVE item is in the target's has_items
- two fixed robots do not exchange an object; a LOCAL step is in the robot's own room
On format errors the robot rewrites its plan ONCE. Steps that still have format errors are excluded
before broadcast and recorded. Meaning (duplicates, infeasible actions, ...) is judged in Stage 4.2.
"""
from __future__ import annotations

from .llm import BaseLLM
from .log import EventLog
from .prompts import PLAN_FIX, PLAN_USER, _j, indexed, plan_system
from .schemas import (ASK_HELP, LOCAL, PASS, PLAN_TYPES, RECEIVE, REQUEST_TYPES, Node, Offer,
                      TaskConfig, action_str, agent_num, match_item, norm)


def _int(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return x
    if isinstance(x, str) and x.strip().lstrip("-").isdigit():
        return int(x.strip())
    return None


def validate(raw_steps: list, agent: str, offers: dict[str, Offer], cfg: TaskConfig
             ) -> tuple[list[dict], list[str]]:
    """Return step dicts (each with its own 'errors' list) and all error strings."""
    me = cfg.agent(agent)
    own = offers[agent]
    others = [x for x in cfg.ids if x != agent]
    raw_steps = raw_steps if isinstance(raw_steps, list) else []
    types = [str(s.get("type", "")).upper().strip() if isinstance(s, dict) else "" for s in raw_steps]
    steps, errors = [], []
    for i, s in enumerate(raw_steps):
        s = s if isinstance(s, dict) else {}
        t = types[i]
        e: list[str] = []
        st = {"_i": i, "type": t, "action": s.get("action", ""),
              "item": str(s["item"]).strip() if s.get("item") else None,
              "target": str(s["target"]).strip().upper() if s.get("target") else None,
              "uses": _int(s.get("uses")), "enables": _int(s.get("enables")),
              "serves": _int(s.get("serves")), "location": me.profile.room}
        if t not in PLAN_TYPES:
            e.append(f"type '{t}' is not allowed (use LOCAL, ASK_HELP, RECEIVE, PASS)")
        if not (st["serves"] is not None and 0 <= st["serves"] < len(own.intends)):
            e.append(f"serves={s.get('serves')} is not an index of your intends (0..{len(own.intends) - 1})")
        if t == LOCAL:
            if not (st["uses"] is not None and 0 <= st["uses"] < len(own.can_do)):
                e.append(f"uses={s.get('uses')} is not an index of your can_do (0..{len(own.can_do) - 1})")
            loc = s.get("location")
            if loc and norm(str(loc)) != norm(me.profile.room):
                e.append(f"LOCAL is in '{loc}', but you work only in your own room ('{me.profile.room}')")
            if not action_str(st["action"]):
                e.append("LOCAL needs an action")
            st["enables"] = None
        if t in REQUEST_TYPES | {PASS}:
            st["uses"] = None
            if st["target"] not in others:
                e.append(f"{t} needs a target among {others}, got {st['target']}")
        if t == ASK_HELP:
            if not action_str(st["action"]):
                e.append("ASK_HELP needs an action")
            en = st["enables"]
            if not (en is not None and i < en < len(raw_steps) and types[en] == LOCAL):
                e.append(f"ASK_HELP needs 'enables' = index of one of YOUR later LOCAL steps (got {s.get('enables')})")
        if t == RECEIVE:
            en = st["enables"]
            if en is not None and not (i < en < len(raw_steps) and types[en] == LOCAL):
                e.append(f"RECEIVE 'enables'={en} is not one of YOUR later LOCAL steps (omit it or fix it)")
            if not st["item"]:
                e.append("RECEIVE needs an item")
            elif st["target"] in offers:
                hit = match_item(st["item"], offers[st["target"]].has_items)
                if hit is None:
                    e.append(f"RECEIVE item '{st['item']}' is not in {st['target']}'s has_items "
                             f"{offers[st['target']].has_items}")
                else:
                    st["item"] = hit
            if st["target"] in cfg.ids and cfg.mover(st["target"], agent) is None:
                e.append(f"{st['target']} and {agent} are both fixed: nobody can move an object between them")
            st["action"] = action_str(st["action"]) or f"receive {st['item']}"
        if t == PASS:
            st["enables"] = None
            if not st["item"]:
                e.append("PASS needs an item from YOUR has_items")
            else:
                hit = match_item(st["item"], own.has_items)
                if hit is None:
                    e.append(f"PASS item '{st['item']}' is not in YOUR has_items {own.has_items}")
                else:
                    st["item"] = hit
            if st["target"] in cfg.ids and cfg.mover(agent, st["target"]) is None:
                e.append(f"{agent} and {st['target']} are both fixed: nobody can move an object between them")
            st["action"] = action_str(st["action"]) or f"pass {st['item']} to {st['target']}"
        st["errors"] = e
        errors += [f"step {i}: {x}" for x in e]
        steps.append(st)
    if not raw_steps:
        errors.append("plan has no steps")
    return steps, errors


async def make_local_plan(cfg: TaskConfig, agent: str, offers: dict[str, Offer], llm: BaseLLM,
                          log: EventLog, max_fix: int = 1) -> tuple[list[Node], dict]:
    me = cfg.agent(agent)
    own = offers[agent]
    system = plan_system(agent, me.profile.room)
    user = PLAN_USER.format(
        task=cfg.task, deadline=cfg.deadline_min, own_offer=_j(own.to_dict()),
        can_do_indexed=indexed(own.can_do), intends_indexed=indexed(own.intends),
        public_offers=_j([o.public() for o in offers.values()]),
        profiles=_j({a.id: {"room": a.profile.room, "mobile": a.profile.mobile,
                            **({"payload_kg": a.profile.payload_kg} if a.profile.payload_kg else {}),
                            "embodiment": a.profile.embodiment} for a in cfg.agents}),
    )
    d = await llm.complete(system, user, key=f"plan:{agent}")
    steps, errors = validate(d.get("steps"), agent, offers, cfg)
    first_errors = list(errors)
    n_fix = 0
    while errors and n_fix < max_fix:          # one self-fix, format errors only
        n_fix += 1
        log.log("plan", agent, "self_fix", errors=len(errors))
        fix_user = user + "\n\nYOUR PREVIOUS PLAN:\n" + _j(d) + "\n\n" + PLAN_FIX.format(
            errors="\n".join(f"- {x}" for x in errors))
        d = await llm.complete(system, fix_user, key=f"plan:{agent}:fix")
        steps, errors = validate(d.get("steps"), agent, offers, cfg)

    # steps with remaining format errors are excluded before broadcast
    kept = [s for s in steps if not s["errors"]]
    excluded = [{"step": s["_i"], "type": s["type"], "text": action_str(s["action"]) or (s["item"] or ""),
                 "errors": s["errors"]} for s in steps if s["errors"]]
    n = agent_num(agent)
    nodes: list[Node] = []
    raw_to_id: dict[int, str] = {}
    for k, s in enumerate(kept, start=1):
        nid = f"r{n}_s{k}"
        raw_to_id[s["_i"]] = nid
        nodes.append(Node(id=nid, agent=agent, type=s["type"], action=s["action"], item=s["item"],
                          target=s["target"], uses=s["uses"], location=s["location"],
                          origin="offer" if s["type"] == PASS else "local",
                          serves=s["serves"], serves_text=own.intends[s["serves"]]))
    for s, node in zip(kept, nodes):
        if s["enables"] is not None:
            node.enables = raw_to_id.get(s["enables"])     # None if the enabled step was excluded
    for x in excluded:
        log.log("plan", agent, "step_excluded", step=x["step"], errors=len(x["errors"]))
    log.log("plan", agent, "broadcast", steps=len(nodes),
            requests=sum(x.type in REQUEST_TYPES for x in nodes),
            offers=sum(x.type == PASS for x in nodes), excluded=len(excluded))
    return nodes, {"reasoning": d.get("reasoning", ""), "fix_rounds": n_fix,
                   "format_errors_first": first_errors, "remaining_errors": errors, "excluded": excluded}

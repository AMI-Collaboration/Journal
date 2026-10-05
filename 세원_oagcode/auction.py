"""
Stage 3 - AUCTION: decentralized candidate proposal (no LLM, no selection).

The Auction does NOT allocate tasks and does NOT select edges.

After every Local Plan has been broadcast, EACH robot, in parallel and on
its own, reads the other robots' requests and asks:

    "Which of these requests can I answer with something I declared in my
     own CAN_PROVIDE?"

    ASK_HELP  <-  my CAN_PROVIDE(type=task)   ->  I propose a HELP step
    RECEIVE   <-  my CAN_PROVIDE(type=item)   ->  I propose a PASS step

A proposal is only made if
    - the request and my offering are semantically similar (embedding),
    - for HELP: the request does not hit my own (private) CANNOT_DO.

Every proposal appends a HELP / PASS step to the END of the proposing
robot's own plan (inactive until Graph Reasoning selects it) and becomes a
candidate edge  provider_step -> request_step.

Graph Reasoning later selects among these self-proposed candidates.
"""

from __future__ import annotations

import re

from dataclasses import asdict, dataclass, field

from runtime import Agent, EventLog
from schemas import CanProvide, LocalPlan, Step, agent_of


REQUEST_TYPES = {"ASK_HELP", "RECEIVE"}

# request type -> (CAN_PROVIDE type, proposed step type)
CHANNEL = {
    "ASK_HELP": ("task", "HELP"),
    "RECEIVE": ("item", "PASS"),
}


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class AuctionResult:
    method: str

    # request_id -> [{"pass": provider_step_id, "score": float}, ...]
    # (key name "pass" kept for compatibility with Graph Reasoning)
    candidates: dict[str, list[dict]]

    # flat list of all proposals
    proposals: list[dict] = field(default_factory=list)

    # requests nobody proposed to answer
    requests_without_candidates: list[str] = field(default_factory=list)

    rounds: int = 1

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Text used for embedding
# ---------------------------------------------------------------------------

def request_text(step: Step) -> str:
    """
    Text representation used when matching a request to CAN_PROVIDE.

    RECEIVE:
        use the physical item itself.

    ASK_HELP:
        include both the requested action and its purpose.
        This preserves GLOBAL_SUBGOAL context instead of matching only
        on the action string.
    """
    if step.type == "RECEIVE" and step.item:
        return step.item

    parts = [step.action]

    if step.purpose:
        parts.append(step.purpose)

    return " ".join(parts)


def offering_text(p: CanProvide) -> str:
    if p.type == "item":
        return p.object or ""

    return " ".join(
        x for x in (p.action, p.object)
        if x
    )


def _norm_tokens(text: str) -> set[str]:
    """Small deterministic lexical fallback for weak/hashed embeddings."""
    import re

    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower(),
        )
    )


def _lexical_score(a: str, b: str) -> float:
    """Action/object-aware lexical fallback.

    Generic action words alone must not create a match.
    A match is allowed only when meaningful task/object words overlap.
    """

    aa = _norm_tokens(a)
    bb = _norm_tokens(b)

    if not aa or not bb:
        return 0.0

    # 너무 일반적인 동작 단어는 매칭 근거로 사용하지 않는다.
    generic_actions = {
        "move",
        "put",
        "place",
        "pick",
        "pickup",
        "take",
        "get",
        "handle",
        "bring",
        "carry",
    }

    aa_content = aa - generic_actions
    bb_content = bb - generic_actions

    # 물체/작업의 핵심 단어가 하나도 겹치지 않으면 매칭하지 않는다.
    overlap = aa_content & bb_content

    if not overlap:
        return 0.0

    # 의미 있는 단어가 겹치는 정도를 lexical score로 사용
    return len(overlap) / max(
        1,
        min(len(aa_content), len(bb_content)),
    )
# ---------------------------------------------------------------------------
# One robot's proposal
# (runs inside that robot, in parallel with others)
# ---------------------------------------------------------------------------

async def propose_responses(
    agent: Agent,
    embedder,
    *,
    min_score: float = 0.40,
    cannot_do_threshold: float = 0.75,
    hint_bonus: float = 0.05,
) -> list[dict]:
    """Let one robot propose HELP / PASS steps for other robots' requests.

    Uses only:
        - other robots' broadcast Local Plans (requests)
        - this robot's own Offer (CAN_PROVIDE, private CANNOT_DO)
    """

    assert agent.plan is not None and agent.offer is not None

    agent.receive()  # other robots' Local Plans

    # deterministic order (agent number, step order), independent of
    # which plan happened to arrive first
    requests = sorted(
        (
            s
            for plan in agent.others_plans.values()
            for s in plan.steps
            if s.type in REQUEST_TYPES
        ),
        key=lambda s: (
            int(s.id.split("-")[0]),
            s.order,
        ),
    )

    offerings = [
        p
        for p in agent.offer.can_provide
        if offering_text(p)
    ]

    proposals: list[dict] = []

    if requests and offerings:

        cannot_texts = [
            " ".join(
                x
                for x in (c.action, c.object)
                if x
            )
            for c in agent.offer.cannot_do
        ]

        emb = embedder.embed(
            [request_text(r) for r in requests]
            + [offering_text(p) for p in offerings]
            + cannot_texts
        )

        n_r = len(requests)
        n_o = len(offerings)

        e_req = emb[:n_r]
        e_off = emb[n_r:n_r + n_o]
        e_cannot = emb[n_r + n_o:]

        for i, req in enumerate(requests):

            provide_type, step_type = CHANNEL[req.type]

            # private capability guard:
            # never volunteer for a task that matches my own CANNOT_DO
            if step_type == "HELP" and any(
                float(e_req[i] @ c) >= cannot_do_threshold
                for c in e_cannot
            ):
                continue

            best_j = None
            best = -1.0

            best_semantic = 0.0
            best_lexical = 0.0

            req_text = request_text(req)

            for j, off in enumerate(offerings):

                # -------------------------------------------------------
                # EMBODIMENT GUARD
                # -------------------------------------------------------
                # Only propose HELP when this robot's physical
                # capability can actually execute the requested action.
                if (
                    req.type == "ASK_HELP"
                    and not _provider_can_execute_request(
                        req,
                        agent,
                        off,
                    )
                ):
                    continue

                if req.type == "RECEIVE":
                    if off.type != "item":
                        continue

                elif req.type == "ASK_HELP":
                    # ASK_HELP는 task/item 모두 후보가 될 수 있다.
                    # 단, item 제공은 요청 객체와 실제 객체가 맞아야 한다.
                    if off.type not in {"task", "item"}:
                        continue

                    if not _object_match(req, off):
                        continue

                else:
                    if off.type != provide_type:
                        continue

                semantic = float(
                    e_req[i] @ e_off[j]
                )

                lexical = _lexical_score(
                    req_text,
                    offering_text(off),
                )

                compatibility = 0.0
                if req.type == "ASK_HELP":
                    compatibility = _object_match_score(req, off)

                # Hash embeddings are useful for deterministic tests but can
                # miss obvious action/object matches. Use the strongest of
                # semantic, lexical, and deterministic category signals while
                # keeping the original embedding score visible in the logs.
                score = max(
                    semantic,
                    lexical,
                    compatibility,
                )

                if score > best:
                    best_j = j
                    best = score

                    best_semantic = semantic
                    best_lexical = lexical

            if best_j is None or best < min_score:
                continue

            requester = agent_of(req.id)

            score = best + (
                hint_bonus
                if req.target == agent.id
                else 0.0
            )

            if step_type == "HELP":

                step = agent.plan.add_proposed_step(
                    type="HELP",
                    action=req.action,
                    serves=req.id,
                    target=requester,
                )

            else:

                item = offerings[best_j].object

                step = agent.plan.add_proposed_step(
                    type="PASS",
                    action=f"Pass the {item}",
                    item=item,
                    serves=req.id,
                    target=requester,
                )

            proposals.append(
                {
                    "request": req.id,
                    "provider": step.id,
                    "type": step_type,
                    "score": round(score, 4),
                    "semantic_score": round(
                        best_semantic,
                        4,
                    ),
                    "lexical_score": round(
                        best_lexical,
                        4,
                    ),
                    "offering": offering_text(
                        offerings[best_j]
                    ),
                }
            )

    agent.log.log(
        "auction",
        agent.id,
        "proposed",
        n=len(proposals),
        proposals=proposals,
    )

    if agent.verbose:

        for p in proposals:
            print(
                f"  [PROPOSE] {agent.id}: "
                f"{p['type']} {p['provider']} -> "
                f"request {p['request']} "
                f"(score={p['score']:.3f}, "
                f"via '{p['offering']}')"
            )

        if not proposals:
            print(
                f"  [PROPOSE] {agent.id}: no proposal"
            )

    agent.bus.broadcast(
        agent.id,
        "proposal",
        {
            "proposals": proposals,
        },
        phase="auction",
    )

    return proposals


# ---------------------------------------------------------------------------
# Collect proposals into candidate edges
# (bookkeeping only, no decision)
# ---------------------------------------------------------------------------


def _normalize_word(word: str) -> str:
    """Normalize simple singular/plural variants for deterministic matching."""
    word = word.lower().strip()
    if len(word) > 3 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


def _category_tags(text: str) -> set[str]:
    """Map concrete household objects / task phrases to coarse categories."""
    tokens = {
        _normalize_word(t)
        for t in re.findall(r"[a-z0-9]+", text.lower())
    }

    tags: set[str] = set()

    heavy_furniture = {
        "sofa", "couch", "chair", "armchair", "table", "desk",
        "tvstand", "shelf", "cabinet", "bed", "dresser", "wardrobe",
    }
    light_items = {
        "dish", "utensil", "glass", "cup", "mug", "plate", "bowl",
        "spoon", "fork", "knife", "bottle", "sponge", "cushion",
        "book", "cd", "cellphone", "credit", "card", "pen", "pencil",
        "keychain", "towel", "handtowel", "soap", "spraybottle",
        "brush", "tomato", "lettuce", "egg", "pan", "potato",
        "cabbage",
    }

    if tokens & heavy_furniture:
        tags.update({"heavy", "furniture"})

    if tokens & light_items:
        tags.add("light")

    if "heavy" in tokens or "furniture" in tokens:
        tags.update({"heavy"} if "heavy" in tokens else {"furniture"})

    if "light" in tokens:
        tags.add("light")

    # Task 10 uses a generic phrase ("all gathered items") but its purpose
    # explicitly says dishes/utensils.  Treat that as a light-item request.
    if ({"gathered", "item"} <= tokens or "dish" in tokens or "utensil" in tokens):
        if "kitchen" in tokens or "house" in tokens:
            tags.add("light")

    return tags


def _provider_capability_class(agent: Agent) -> str:
    """
    Return the robot's movement capability class.

    fixed_gripper : fixed gripper / stationary gripper
    light         : mobile light robot
    heavy         : mobile heavy robot
    unknown       : capability cannot be classified
    """
    capability = (agent.inp.capability or "").lower()

    gripper_keywords = (
        "gripper",
        "fixed-base gripper",
        "fixed base gripper",
        "stationary gripper",
        "fixed manipulator",
        "fixed-base arm",
        "fixed base arm",
    )

    if any(k in capability for k in gripper_keywords):
        return "fixed_gripper"

    heavy_keywords = (
        "mobile heavy robot",
        "heavy-duty mobile robot",
        "heavy duty mobile robot",
        "heavy-duty",
        "heavy duty",
        "can move heavy",
        "move heavy objects",
        "move heavy furniture",
    )

    if any(k in capability for k in heavy_keywords):
        return "heavy"

    light_keywords = (
        "mobile light robot",
        "light-duty mobile robot",
        "light duty mobile robot",
        "mobile robot",
        "light-duty",
        "light duty",
    )

    if any(k in capability for k in light_keywords):
        return "light"

    return "unknown"


def _request_requires_movement(request: Step) -> bool:
    text = " ".join(
        x
        for x in (
            request.action,
            request.item,
            request.purpose,
        )
        if x
    ).lower()

    movement_words = (
        "move",
        "carry",
        "transport",
        "bring",
        "deliver",
        "transfer",
        "navigate",
        "walk to",
        "go to",
        "travel to",
    )

    return any(word in text for word in movement_words)


def _request_is_heavy(request: Step) -> bool:
    text = " ".join(
        x
        for x in (
            request.action,
            request.item,
            request.purpose,
        )
        if x
    ).lower()

    heavy_words = (
        "heavy",
        "furniture",
        "armchair",
        "sofa",
        "couch",
        "tvstand",
        "tv stand",
        "bunk bed",
        "bed",
        "cabinet",
        "table",
    )

    return any(word in text for word in heavy_words)


def _provider_can_execute_request(
    request: Step,
    provider: Agent,
    offering: CanProvide,
) -> bool:
    """
    Embodiment-level guard for Auction proposals.

    This is intentionally checked AFTER the normal CAN_PROVIDE matching
    logic, so an LLM cannot create an invalid HELP proposal merely by
    publishing an overly broad offer.
    """

    capability_class = _provider_capability_class(provider)

    # Unknown capability -> do not invent physical abilities.
    if capability_class == "unknown":
        return False

    # Fixed gripper cannot move between locations or transport objects.
    if (
        capability_class == "fixed_gripper"
        and _request_requires_movement(request)
    ):
        return False

    # Light mobile robots cannot perform heavy-object/furniture movement.
    if (
        capability_class == "light"
        and _request_requires_movement(request)
        and _request_is_heavy(request)
    ):
        return False

    # Heavy mobile robots can perform both light and heavy movement.
    # Fixed gripper has already been filtered above.
    return True


def _object_match_score(request: Step, offering: CanProvide) -> float:
    """
    Return a deterministic compatibility score for ASK_HELP.

    1.0 = explicit object/task token overlap.
    0.75 = compatible coarse category (e.g. sofa <-> heavy objects,
          dishes/utensils <-> light objects).
    0.0 = no reliable compatibility evidence.
    """

    req_text = " ".join(
        x
        for x in (
            request.action,
            request.item,
            request.purpose,
        )
        if x
    ).lower()

    off_text = " ".join(
        x
        for x in (
            offering.object,
            offering.action,
        )
        if x
    ).lower()

    req_tokens = {
        _normalize_word(t)
        for t in re.findall(r"[a-z0-9]+", req_text)
    }
    off_tokens = {
        _normalize_word(t)
        for t in re.findall(r"[a-z0-9]+", off_text)
    }

    generic = {
        "move", "put", "place", "pick", "pickup", "take", "get",
        "handle", "bring", "carry", "close", "open", "shut", "to",
        "from", "another", "location", "the", "a", "an", "away",
        "for", "space", "create", "room", "area", "all", "gathered",
        "item", "house",
    }

    req_content = req_tokens - generic
    off_content = off_tokens - generic

    if req_content & off_content:
        return 1.0

    req_tags = _category_tags(req_text)
    off_tags = _category_tags(off_text)

    if req_tags & off_tags:
        return 0.75

    return 0.0


def _object_match(request: Step, offering: CanProvide) -> bool:
    return _object_match_score(request, offering) > 0.0

def collect_candidates(
    plans: dict[str, LocalPlan],
    all_proposals: list[list[dict]],
    log: EventLog | None = None,
) -> AuctionResult:

    request_ids = [
        s.id
        for plan in plans.values()
        for s in plan.steps
        if s.type in REQUEST_TYPES
    ]

    candidates: dict[str, list[dict]] = {
        rid: []
        for rid in request_ids
    }

    flat: list[dict] = []

    for props in all_proposals:

        for p in props:

            candidates.setdefault(
                p["request"],
                [],
            ).append(
                {
                    "pass": p["provider"],
                    "score": p["score"],
                }
            )

            flat.append(p)

    for rid in candidates:

        candidates[rid].sort(
            key=lambda c: (
                -c["score"],
                c["pass"],
            )
        )

    result = AuctionResult(
        method="decentralized_proposal",
        candidates=candidates,
        proposals=flat,
        requests_without_candidates=[
            r
            for r, c in candidates.items()
            if not c
        ],
    )

    if log:

        log.log(
            "auction",
            "-",
            "done",
            method=result.method,
            n_requests=len(request_ids),
            n_proposals=len(flat),
            requests_without_candidates=len(
                result.requests_without_candidates
            ),
        )

    return result
import json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(os.path.dirname(HERE))  # experiment/

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

METRICS = ["TF", "GF", "SC", "CQ"]
VARIANTS = ["full", "no_offer", "no_edge", "no_graph"]

for run in [1, 2, 3]:
    print(f"\n{'='*70}\n ablation run{run}\n{'='*70}")
    judge_path = os.path.join(HERE, f"ablation_judge_results_run{run}.json")
    judge = load(judge_path) if os.path.exists(judge_path) else {}

    abstract_dir = os.path.join(EXP, "results", "abstract", f"run{run}")

    rows = {v: {m: [] for m in METRICS} for v in VARIANTS}
    times = {v: [] for v in VARIANTS}
    ptoks = {v: [] for v in VARIANTS}
    ctoks = {v: [] for v in VARIANTS}
    n_ok = {v: 0 for v in VARIANTS}

    for t in range(1, 11):
        task = f"task{t}_abstract"

        # full = abstract/run{N} CDA result (raw metrics) + summary_jabung judge
        cda_result_path = None
        for pat in [f"{task}_multi_room_cda_jabung_result.json", f"{task}_multi_room_cda_result.json"]:
            p = os.path.join(abstract_dir, pat)
            if os.path.exists(p):
                cda_result_path = p
                break
        summary_path = os.path.join(abstract_dir, f"{task}_summary_jabung.json")

        if cda_result_path and os.path.exists(summary_path):
            cda_r = load(cda_result_path)
            summ = load(summary_path)
            cda_judge = summ.get("cda", {}).get("track_a_llm_judge")
            if isinstance(cda_judge, dict) and "TF" in cda_judge:
                for m in METRICS:
                    rows["full"][m].append(cda_judge[m])
                met = cda_r.get("metrics", {})
                times["full"].append(met.get("wall_time_sec"))
                ptoks["full"].append(met.get("prompt_tokens"))
                ctoks["full"].append(met.get("completion_tokens"))
                n_ok["full"] += 1

        # ablation raw file for variant metrics (time/tokens)
        abl_path = os.path.join(HERE, f"{task}_ablation_run{run}.json")
        abl = load(abl_path) if os.path.exists(abl_path) else {}

        tj = judge.get(f"task{t}", {})
        for v in ["no_offer", "no_edge", "no_graph"]:
            j = tj.get(v)
            if isinstance(j, dict) and "TF" in j:
                for m in METRICS:
                    rows[v][m].append(j[m])
                met = abl.get(v, {}).get("metrics", {})
                times[v].append(met.get("wall_time_sec"))
                ptoks[v].append(met.get("prompt_tokens"))
                ctoks[v].append(met.get("completion_tokens"))
                n_ok[v] += 1

    print(f"{'variant':10} {'TF':>6} {'GF':>6} {'SC':>6} {'CQ':>6} {'n':>3} {'time(s)':>10} {'p_tok':>10} {'c_tok':>10}")
    for v in VARIANTS:
        n = n_ok[v]
        if n == 0:
            print(f"{v:10} (no data)")
            continue
        avgs = {m: round(st.mean(rows[v][m]), 2) for m in METRICS}
        stds = {m: round(st.pstdev(rows[v][m]), 2) if n > 1 else 0.0 for m in METRICS}
        avg_time = round(st.mean([x for x in times[v] if x is not None]), 1) if any(x is not None for x in times[v]) else None
        avg_p = round(st.mean([x for x in ptoks[v] if x is not None]), 0) if any(x is not None for x in ptoks[v]) else None
        avg_c = round(st.mean([x for x in ctoks[v] if x is not None]), 0) if any(x is not None for x in ctoks[v]) else None
        print(f"{v:10} {avgs['TF']:>6} {avgs['GF']:>6} {avgs['SC']:>6} {avgs['CQ']:>6} {n:>3} {str(avg_time):>10} {str(avg_p):>10} {str(avg_c):>10}")
        print(f"{'  (std)':10} {stds['TF']:>6} {stds['GF']:>6} {stds['SC']:>6} {stds['CQ']:>6}")

import json, os, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))  # experiment/results
METHODS = ["cda", "central", "independent", "lamma_p", "smart_llm"]
METHOD_NAMES = {"cda": "CDA", "central": "Central", "independent": "Independent",
                "lamma_p": "LaMMA-P", "smart_llm": "SMART-LLM"}
METRICS = ["TF", "GF", "SC", "CQ"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def method_raw_path(d, task, m):
    if m == "cda":
        for pat in [f"{task}_multi_room_cda_jabung_result.json", f"{task}_multi_room_cda_result.json"]:
            p = os.path.join(d, pat)
            if os.path.exists(p):
                return p
        return None
    p = os.path.join(d, f"{task}_{m}_result.json")
    return p if os.path.exists(p) else None


def collect(task_dir, tasks):
    """returns {method: {TF:[],GF:[],SC:[],CQ:[], time:[], ptok:[], ctok:[], n:int}}"""
    out = {m: {k: [] for k in METRICS + ["time", "ptok", "ctok"]} for m in METHODS}
    for task in tasks:
        summ_path = os.path.join(task_dir, f"{task}_summary_jabung.json")
        if not os.path.exists(summ_path):
            continue
        summ = load(summ_path)
        for m in METHODS:
            j = summ.get(m, {}).get("track_a_llm_judge")
            if not (isinstance(j, dict) and "TF" in j):
                continue
            for k in METRICS:
                out[m][k].append(j[k])
            rp = method_raw_path(task_dir, task, m)
            if rp:
                met = load(rp).get("metrics", {})
                if met.get("wall_time_sec") is not None:
                    out[m]["time"].append(met["wall_time_sec"])
                if met.get("prompt_tokens") is not None:
                    out[m]["ptok"].append(met["prompt_tokens"])
                if met.get("completion_tokens") is not None:
                    out[m]["ctok"].append(met["completion_tokens"])
    return out


def print_table(title, data):
    print(f"\n{'='*78}\n {title}\n{'='*78}")
    print(f"{'method':12} {'TF':>6} {'GF':>6} {'SC':>6} {'CQ':>6} {'n':>3} {'time(s)':>9} {'p_tok':>9} {'c_tok':>9}")
    for m in METHODS:
        d = data[m]
        n = len(d["TF"])
        if n == 0:
            print(f"{METHOD_NAMES[m]:12} (no data)")
            continue
        avgs = {k: round(st.mean(d[k]), 2) for k in METRICS}
        avg_time = round(st.mean(d["time"]), 1) if d["time"] else None
        avg_p = round(st.mean(d["ptok"]), 0) if d["ptok"] else None
        avg_c = round(st.mean(d["ctok"]), 0) if d["ctok"] else None
        print(f"{METHOD_NAMES[m]:12} {avgs['TF']:>6} {avgs['GF']:>6} {avgs['SC']:>6} {avgs['CQ']:>6} "
              f"{n:>3} {str(avg_time):>9} {str(avg_p):>9} {str(avg_c):>9}")
        stds = {k: round(st.pstdev(d[k]), 2) if n > 1 else 0.0 for k in METRICS}
        print(f"{'  (std)':12} {stds['TF']:>6} {stds['GF']:>6} {stds['SC']:>6} {stds['CQ']:>6}")


# ---- abstract run1/2/3 ----
tasks10 = [f"task{i}_abstract" for i in range(1, 11)]
for run in [1, 2, 3]:
    d = collect(os.path.join(HERE, "abstract", f"run{run}"), tasks10)
    print_table(f"abstract run{run} (n_robots={ {1:4,2:6,3:8}[run] })", d)

# ---- simple ----
tasks10s = [f"task{i}_simple" for i in range(1, 11)]
d = collect(os.path.join(HERE, "simple"), tasks10s)
print_table("simple", d)

# ---- matthor ----
mat_tasks = ["mat_compound", "mat_complex", "mat_vague"]
d = collect(os.path.join(HERE, "matthor"), mat_tasks)
print_table("MAT-THOR (3 scenarios)", d)

# ---- ablation (reuse earlier aggregator logic) ----
ABL = os.path.join(HERE, "ablation")
VARIANTS = ["full", "no_offer", "no_edge", "no_graph"]
for run in [1, 2, 3]:
    print(f"\n{'='*78}\n ablation run{run}\n{'='*78}")
    judge_path = os.path.join(ABL, f"ablation_judge_results_run{run}.json")
    judge = load(judge_path) if os.path.exists(judge_path) else {}
    abstract_dir = os.path.join(HERE, "abstract", f"run{run}")
    rows = {v: {m: [] for m in METRICS} for v in VARIANTS}
    times = {v: [] for v in VARIANTS}
    ptoks = {v: [] for v in VARIANTS}
    ctoks = {v: [] for v in VARIANTS}
    n_ok = {v: 0 for v in VARIANTS}
    for t in range(1, 11):
        task = f"task{t}_abstract"
        cda_result_path = method_raw_path(abstract_dir, task, "cda")
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
        abl_path = os.path.join(ABL, f"{task}_ablation_run{run}.json")
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

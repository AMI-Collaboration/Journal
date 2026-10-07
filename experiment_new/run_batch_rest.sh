#!/bin/bash
# task3~10을 central/independent/lamma_p/smart_llm 4개 방법론으로 순차 실행

cd "$(dirname "$0")"
mkdir -p results

TASKS=(task3_abstract task4_abstract task5_abstract task6_abstract task7_abstract task8_abstract task9_abstract task10_abstract)
TOTAL=${#TASKS[@]}
BATCH_START=$(date +%s)

get_usage_total() {
    python3 -c "
import json, os
path = 'usage_log.json'
if not os.path.exists(path):
    print(0)
else:
    with open(path, encoding='utf-8') as f:
        log = json.load(f)
    print(sum(e.get('total_tokens', e.get('prompt_tokens',0)+e.get('completion_tokens',0)) for e in log))
"
}

save_task_cost(){
    local task="$1"
    local elapsed="$2"
    local task_tokens="$3"
    python3 -c "
import json, os

task = '$task'
elapsed = $elapsed
task_tokens = $task_tokens

usage_path = 'usage_log.json'
with open(usage_path, encoding='utf-8') as f:
    log = json.load(f)

by_method = {}
for e in log:
    if e.get('task_n') != task:
        continue
    m = e.get('method', 'unknown')
    base = m.replace('_convert', '').replace('_grounding', '')
    by_method.setdefault(base, {'prompt_tokens': 0, 'completion_tokens': 0, 'calls': 0})
    by_method[base]['prompt_tokens'] += e.get('prompt_tokens', 0)
    by_method[base]['completion_tokens'] += e.get('completion_tokens', 0)
    by_method[base]['calls'] += e.get('calls', 1)

USD_IN, USD_OUT, KRW = 2.5, 10.0, 1400
for m, d in by_method.items():
    d['total_tokens'] = d['prompt_tokens'] + d['completion_tokens']
    d['cost_krw'] = round((d['prompt_tokens']/1_000_000*USD_IN + d['completion_tokens']/1_000_000*USD_OUT) * KRW, 1)

record = {
    'task_n': task,
    'elapsed_seconds': elapsed,
    'elapsed_display': f'{elapsed//60}분 {elapsed%60}초',
    'total_tokens_this_task': task_tokens,
    'by_method': by_method,
}

out_path = os.path.join('results', f'{task}_cost.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(record, f, ensure_ascii=False, indent=2)
print(f'저장: {out_path}')
"
}

i=0
for task in "${TASKS[@]}"; do
    i=$((i+1))
    TASK_START=$(date +%s)
    TOKENS_BEFORE=$(get_usage_total)

    echo ""
    echo "========================================================="
    echo " [$i/$TOTAL] $task 시작"
    echo "========================================================="

    echo "--- [1/4] Central ---"
    python run_central.py --task "$task" || echo "⚠️ central 실패: $task"

    echo "--- [2/4] Independent ---"
    python run_independent.py --task "$task" || echo "⚠️ independent 실패: $task"

    echo "--- [3/4] LaMMA-P ---"
    python run_lamma_p.py --task "$task" || echo "⚠️ lamma_p 실패: $task"
    python convert_to_joint_plan.py --task "$task" --method lamma_p || echo "⚠️ lamma_p 변환 실패: $task"

    echo "--- [4/4] SMART-LLM ---"
    python run_smart_llm.py --task "$task" || echo "⚠️ smart_llm 실패: $task"
    python convert_to_joint_plan.py --task "$task" --method smart_llm || echo "⚠️ smart_llm 변환 실패: $task"

    TASK_END=$(date +%s)
    TASK_ELAPSED=$((TASK_END - TASK_START))
    TOKENS_AFTER=$(get_usage_total)
    TASK_TOKENS=$((TOKENS_AFTER - TOKENS_BEFORE))

    save_task_cost "$task" "$TASK_ELAPSED" "$TASK_TOKENS"

    MIN=$((TASK_ELAPSED / 60))
    SEC=$((TASK_ELAPSED % 60))

    echo ""
    echo "✅ [$i/$TOTAL] $task 완료  |  소요시간: ${MIN}분 ${SEC}초  |  이번 task 토큰: ${TASK_TOKENS}"
done

BATCH_END=$(date +%s)
BATCH_ELAPSED=$((BATCH_END - BATCH_START))
BATCH_MIN=$((BATCH_ELAPSED / 60))

echo ""
echo "========================================================="
echo " task3~10 완료!  총 소요시간: ${BATCH_MIN}분"
echo "========================================================="

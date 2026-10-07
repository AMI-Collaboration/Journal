#!/bin/bash
# task1~10 전체에 대해 aggregate_results.py(Judge 평가)를 순차 실행

cd "$(dirname "$0")"

TASKS=(task1_abstract task2_abstract task3_abstract task4_abstract task5_abstract task6_abstract task7_abstract task8_abstract task9_abstract task10_abstract)
TOTAL=${#TASKS[@]}
BATCH_START=$(date +%s)

i=0
for task in "${TASKS[@]}"; do
    i=$((i+1))
    TASK_START=$(date +%s)

    echo ""
    echo "========================================================="
    echo " [$i/$TOTAL] $task 평가 시작"
    echo "========================================================="

    python aggregate_results.py --task "$task" || echo "⚠️ 평가 실패: $task"

    TASK_END=$(date +%s)
    TASK_ELAPSED=$((TASK_END - TASK_START))
    MIN=$((TASK_ELAPSED / 60))
    SEC=$((TASK_ELAPSED % 60))

    echo ""
    echo "✅ [$i/$TOTAL] $task 평가 완료  |  소요시간: ${MIN}분 ${SEC}초"
done

BATCH_END=$(date +%s)
BATCH_ELAPSED=$((BATCH_END - BATCH_START))
BATCH_MIN=$((BATCH_ELAPSED / 60))

echo ""
echo "========================================================="
echo " 전체 ${TOTAL}개 task 평가 완료!  총 소요시간: ${BATCH_MIN}분"
echo "========================================================="

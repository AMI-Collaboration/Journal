export PYTHONIOENCODING=utf-8
LAMMA_TASKS="mat_compound mat_compound_3 mat_compound_4 mat_compound_5 mat_compound_6 mat_compound_7 mat_compound_8 mat_compound_9 mat_compound_10 mat_complex mat_complex_2 mat_complex_3 mat_complex_4 mat_complex_5 mat_complex_6 mat_complex_7 mat_complex_8 mat_complex_9 mat_complex_10 mat_vague mat_vague_2 mat_vague_3 mat_vague_4 mat_vague_5 mat_vague_6 mat_vague_7 mat_vague_8 mat_vague_9"
for t in $LAMMA_TASKS; do
  echo "=== convert lamma_p: $t ==="
  python convert_to_joint_plan.py --task $t --method lamma_p
done
echo "=== convert smart_llm: mat_compound ==="
python convert_to_joint_plan.py --task mat_compound --method smart_llm
echo "=== MATTHOR CONVERT BATCH DONE ==="

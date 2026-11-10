export PYTHONIOENCODING=utf-8
TASKS="mat_compound_3 mat_compound_4 mat_compound_5 mat_compound_6 mat_compound_7 mat_compound_8 mat_compound_9 mat_compound_10 mat_complex_2 mat_complex_3 mat_complex_4 mat_complex_5 mat_complex_6 mat_complex_7 mat_complex_8 mat_complex_9 mat_complex_10 mat_vague_2 mat_vague_3 mat_vague_4 mat_vague_5 mat_vague_6 mat_vague_7 mat_vague_8 mat_vague_9"
for t in $TASKS; do
  echo "=== LaMMA-P $t ==="
  python3 run_lamma_p.py --task $t
done
echo "=== MATTHOR LAMMA-P BATCH DONE ==="

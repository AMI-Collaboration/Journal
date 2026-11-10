export PYTHONIOENCODING=utf-8
for run in 1 2 3; do
  for robots in 4 6 8; do
    for t in 1 2 3 4 5 6 7 8 9 10; do
      if [ "$run" = "1" ] && [ "$robots" = "4" ] && [ "$t" = "1" ]; then
        echo "=== skip task${t}_abstract run${run} ${robots}robot (already done as test) ==="
        continue
      fi
      echo "=== no_graph rerun task${t}_abstract run${run} ${robots}robot ==="
      python run_ablation.py --task task${t}_abstract --n-robots $robots --run $run --variants no_graph
    done
  done
done
echo "=== NO_GRAPH RERUN BATCH DONE ==="

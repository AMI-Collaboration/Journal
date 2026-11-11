export PYTHONIOENCODING=utf-8
for t in 1 2 3 4 5 6 7 8 9 10; do
  echo "=== CDA task${t}_simple run4 4robot ==="
  python run_cda_jabung.py --task task${t}_simple --n-robots 4 --run 4
  echo "=== Ablation task${t}_simple run4 4robot ==="
  python run_ablation.py --task task${t}_simple --n-robots 4 --run 4
done
echo "=== SIMPLE TASK1-10 CDA+ABLATION BATCH DONE ==="

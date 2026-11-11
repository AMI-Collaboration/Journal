export PYTHONIOENCODING=utf-8
for t in 6 7 8 9 10; do
  echo "=== CDA task${t}_abstract run4 4robot ==="
  python run_cda_jabung.py --task task${t}_abstract --n-robots 4 --run 4
  echo "=== Ablation task${t}_abstract run4 4robot ==="
  python run_ablation.py --task task${t}_abstract --n-robots 4 --run 4
done
echo "=== TASK6-10 CDA+ABLATION BATCH DONE ==="

#!/bin/sh
# Submit all 6 spin-polarized Ni-MOF-74 geo-opt jobs.
# Run from this directory: bash submit_all.sh
for n in 0 1 2 3 4 5; do
  qsub job_s${n}.sh
done

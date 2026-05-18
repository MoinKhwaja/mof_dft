#!/bin/sh
#$ -cwd
#$ -l node_f=1
#$ -l h_rt=08:00:00
#$ -N r23_74ace65
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

# R2-3 PHVA frequency calculations for 74ace65
# Sequential s0 -> s5. Each step restarts SCF from the parent geo_opt wavefunction.
# Copy/symlink the parent wfn files into this directory before submitting:
#   for s in s0 s1 s2 s3 s4 s5; do
#     ln -sf ../../../../DFT/complete_dft_input/74ace65/${s}-RESTART.wfn   ${s}_freq-RESTART.wfn
#   done

module load cp2k

for STEP in s0 s1 s2 s3 s4 s5; do
  echo "=== $STEP_freq @ $(date) ==="
  mpirun -np 4 cp2k.psmp -i ${STEP}_freq.inp -o ${STEP}_freq.out
done

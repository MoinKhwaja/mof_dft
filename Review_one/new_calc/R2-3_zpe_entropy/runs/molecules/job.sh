#!/bin/sh
#$ -cwd
#$ -l node_f=1
#$ -l h_rt=04:00:00
#$ -N r23_molecules
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

# R2-3 gas-phase RRHO frequencies for CO2 / H2 / H2O / CH4.
# Copy each parent wavefunction next to its freq input before submitting:
#   for m in co2 h2 h2o ch4; do
#     ln -sf ../../../../DFT/complete_dft_input/molecules/${m}-RESTART.wfn ${m}_freq-RESTART.wfn
#   done

module load cp2k

for MOL in co2 h2 h2o ch4; do
  echo "=== $MOL_freq @ $(date) ==="
  mpirun -np 4 cp2k.psmp -i ${MOL}_freq.inp -o ${MOL}_freq.out
done

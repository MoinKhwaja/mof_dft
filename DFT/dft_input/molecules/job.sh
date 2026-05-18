#!/bin/sh
#$ -cwd
# node_f x 1
#$ -l node_f=1
#$ -l h_rt=10:00:00
#$ -N molecules
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

module load cp2k
mpirun -np 4 cp2k.psmp -i ch4.inp -o ch4.out
mpirun -np 4 cp2k.psmp -i h2o.inp -o h2o.out
mpirun -np 4 cp2k.psmp -i h2.inp -o h2.out
mpirun -np 4 cp2k.psmp -i co2.inp -o co2.out
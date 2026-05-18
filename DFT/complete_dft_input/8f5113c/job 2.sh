#!/bin/sh
#$ -cwd
# node_f x 1
#$ -l node_f=1
#$ -l h_rt=4:00:00
#$ -N mof_8f5113c
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

module load cp2k
mpirun -np 4 cp2k.psmp -i s0.inp -o s0.out
mpirun -np 4 cp2k.psmp -i s1.inp -o s1.out
#!/bin/sh
#$ -cwd
# node_q x 1
#$ -l node_q=1
#$ -l h_rt=23:00:00
#$ -N r13_s0
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

module load cp2k
mpirun -np 4 cp2k.psmp -i s0.inp -o s0.out

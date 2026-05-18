#!/bin/sh
#$ -cwd
# node_f x 1
#$ -l node_f=1
#$ -l h_rt=10:00:00
#$ -N mof_52ef7e9
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

module load cp2k
mpirun -np 4 cp2k.psmp -i s2.inp -o s2.out
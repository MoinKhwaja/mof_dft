#!/bin/sh
#$ -cwd
# node_f x 1
#$ -l node_f=1
#$ -l h_rt=20:00:00
#$ -N mof_051e081
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

module load cp2k
mpirun -np 4 cp2k.psmp -i s1.inp -o s1.out
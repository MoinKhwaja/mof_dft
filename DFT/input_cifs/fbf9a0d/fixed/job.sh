#!/bin/sh
#$ -cwd
# node_f x 1
#$ -l node_f=1
#$ -l h_rt=10:00:00
#$ -N fbf9a0d
#$ -m be
#$ -M khwaja.m.aa@m.titech.ac.jp

module load cp2k
mpirun -np 4 cp2k.psmp -i s2.inp -o s2.out
mpirun -np 4 cp2k.psmp -i s3.inp -o s3.out
mpirun -np 4 cp2k.psmp -i s4.inp -o s4.out
mpirun -np 4 cp2k.psmp -i s5.inp -o s5.out
#!/bin/bash
module load mpi
echo "" > log.txt

for NODES in {1..6}; do
    NP=$((NODES * 1))
    echo "=== Running NODES=$NODES (NP=$NP) ===" >> log.txt
    srun --mpi=pmi2 -N $NODES --ntasks-per-node=1 -n $NP \
        ./lmp -sf omp -pk omp 32 -in ../bench/in.lj \
        -var x 2 -var y 2 -var z 2 2>&1 | sed -n '35,47p' >> log.txt
    echo "--- $NODES nodes, $NP tasks ---" >> log.txt
done
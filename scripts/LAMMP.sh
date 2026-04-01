#!/bin/bash
#SBATCH --ntasks-per-node=16      # max MPI ranks you'll test
#SBATCH --cpus-per-task=1         # will be managed manually per run
#SBATCH --hint=nomultithread
#SBATCH --nodes=1

module load mpi

RESULTS="results.txt"
> $RESULTS  # clear previous results

# pairs of (MPI_ranks, OMP_threads) that multiply to 16 cores
MPI_OMP_PAIRS=(
    "1 16"
    "2 8"
    "4 4"
    "8 2"
    "16 1"
)

for pair in "${MPI_OMP_PAIRS[@]}"; do
    MPI=$(echo $pair | awk '{print $1}')
    OMP=$(echo $pair | awk '{print $2}')

    export OMP_NUM_THREADS=$OMP
    export OMP_PROC_BIND=close
    export OMP_PLACES=cores

    echo "=== MPI=$MPI OMP=$OMP ===" >> $RESULTS

    # run and capture output
    mpirun -np $MPI ./lmp -sf omp -pk omp $OMP -in ../bench/in.lj \
        -var x 2 -var y 2 -var z 2 2>&1 | \
        sed -n '35,47p' | \
        sed "s/^/MPI=$MPI OMP=$OMP | /" >> $RESULTS

    echo "" >> $RESULTS
done
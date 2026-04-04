# lammps-analysis

A repository for LAMMPS analysis.

## Repository Layout


| Directory  | Description                                                                                       |
|------------|---------------------------------------------------------------------------------------------------|
| `scripts/` | prof.py profiling script, LAMMPS build setup script, and the in.lj_unbalanced custom input script |
| `raw_data/`| Raw testing data collected from simulations                                                       |

## Setting up LAMMPS

1. **Clone the LAMMPS official repo:**
   ```bash
   git clone https://github.com/lammps/lammps.git
   ```

2. **Create a build directory** inside the LAMMPS home directory:
```text
   lammps/
   ├── build/        ← like this
   ├── src/
   └── ...
```

4. **Copy and run the setup script**
```
   lammps/
      ├── build/
      │   ├── setup.sh   ← setup script goes here
      │   └── ...
      ├── src/
      └── ...
```


The script will automatically apply the required patch and build LAMMPS.

## The Patch

Lammps is built with compiler compatibility macros, they work most of the time but we found a conflict
with the OMP version detection. These macros can be found here: `lammps/src/omp_compat.h`:
```C
#if LAMMPS_OMP_COMPAT == 4
#  define LMP_SHARED(...)
#  define LMP_DEFAULT_NONE default(shared)
#else
#  define LMP_SHARED(...) shared(__VA_ARGS__)
#  define LMP_DEFAULT_NONE default(none)
#endif
```

This does not play well with our cluster version. At line 209 of `lammps/src/OPENMP/fix_nvt_sllod_omp.cpp`:
```C
#pragma omp parallel for LMP_DEFAULT_NONE LMP_SHARED(grad_u) schedule(static)
```
the variable `xmid` is not specified, which throws a compilation error.

We added a patch that simply adds `xmid` to that shared declaration.

## How to use Profiler
This script is meant to run in the build directory at the same level as the ```lmp``` executable:
```
   lammps/
      ├── build/
      │   ├── setup.sh
      |   ├── prof.py      ← profiling script goes here
      |   ├── lmp
      │   └── ...
      ├── src/
      └── ...
```

'prof.py' has two modes: 'profile' runs LAMMPS scaling sweeps and collects timing data, and 'parse' converts existing raw output files to a CSV.

## Running a sweep
```bash
./prof.py profile -in path/to/in.lj -mpi 8 -trials 3 -fmt csv -out ./results
```

this sweeps MPI ranks at powers of 2 (1, 2, 4, 8), over 3 trials per configuration, and writes averaged timings to './results/lmp_timings.csv'

Use ```-sf linear``` to run input size scaling with number of processes ONLY TESTED WITH STOCK in.lj AND  OUR in.lj_unbalanced

to collect raw LAMMPS output instead, specify `-fmt raw`

run ```./prof.py profile -h``` for more info

## Parsing raw output

```bash
./prof.py parse -in ./results -out ./parsed
```

this walks through every 'lmp_omp<omp ranks>_mpi<mpi threads>trial<trial count>.out
averages trials, and write to './parsed/lmp_timings.csv'

run ```./prof.py parse -h``` for more info


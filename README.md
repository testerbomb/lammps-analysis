# lammps-analysis

A repository for LAMMPS simulation setup and analysis.

## Repository Layout

```
lammps-analysis/
├── scripts/       # Testing scripts and the LAMMPS setup script
└── raw_data/      # Raw testing data
```

| Directory  | Description                                      |
|------------|--------------------------------------------------|
| `scripts/` | Testing scripts and the LAMMPS build setup script |
| `raw_data/`| Raw testing data collected from simulations       |

## Setting Up LAMMPS

Follow these steps to build LAMMPS using the provided setup script:

1. **Create a build directory** inside the LAMMPS home directory:
   ```bash
   mkdir build
   cd build
   ```

2. **Copy the setup script** from `scripts/` into the `build` directory (replace `setup_lammps.sh` with the actual script filename):
   ```bash
   cp ../scripts/setup_lammps.sh .
   ```

3. **Run the setup script**:
   ```bash
   bash setup_lammps.sh
   ```

The script will automatically apply the required patch and build LAMMPS.

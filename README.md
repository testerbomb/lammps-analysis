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

2. **Copy the setup script** from `scripts/` into the `build` directory:
   ```bash
   cp ../scripts/setup.sh .
   ```

3. **Run the setup script**:
   ```bash
   bash setup.sh
   ```

The script will automatically apply the required patch and build LAMMPS.

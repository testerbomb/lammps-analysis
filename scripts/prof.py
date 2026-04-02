#!/usr/bin/python3

import os
import argparse
import subprocess
import csv


    
def arg_parser():
    parser = argparse.ArgumentParser(prog="prof.py", description="LAMMPS Profiler")
    subparsers = parser.add_subparsers(dest="mode")

    # Profile
    profile = subparsers.add_parser("profile", help="Run LAMMPS scaling sweeps")
    profile.add_argument("-in", dest="input", required=True, help="Path to LAMMPS input script")
    profile.add_argument("-jm", dest="jm", default="slurm", help="Job manager: slurm | none")
    profile.add_argument("-omp", dest="omp", type=int, default=1, help="Max OMP threads to sweep to")
    profile.add_argument("-mpi", dest="mpi", type=int, default=1, help="Max MPI procs to sweep to")
    profile.add_argument("-step", dest="step", default="pow", help="Sweep mode: pow | linear")
    profile.add_argument("-greedy", dest="greedy", default="n", help="Run more than one trial at a time DISABLES RUNTIME PARSING")
    profile.add_argument("-trials", dest="trials", type=int, default=1, help="Repeats per count for averaging")
    profile.add_argument("-out", dest="out", default="./results", help="Output directory")
    profile.add_argument("-tpn", dest="tpn", type=int, default=1, help="Taks per node")
    profile.add_argument("-fmt", dest="fmt", default="raw", help="raw | csv:  Parsing LAMMPS output into CSV at runtime")

    # Parse
    parse = subparsers.add_parser("parse", help="Parse existing LAMMPS output files")
    parse.add_argument("-in", dest="input", required=True, help="Path to LAMMPS output file or results dir")
    parse.add_argument("-out", dest="out", default="./results", help="Output directory")

    args = parser.parse_args()
    config = vars(args)

    if config["mode"] is None:
        parser.error("must specify a mode: profile | parse")

    return config, profile, parse


def pow2_range(max_val):
    counts = []
    n = 1
    while n < max_val:
        counts.append(n)
        n *= 2
    counts.append(max_val)  # always include the actual max
    return counts

def build_command(config, mpi, omp):
    lammps_args = f"-sf omp -pk omp {omp} -in {config['input']}"
    if config["jm"] == "slurm":
        return f"srun --mpi=pmi2 -n {mpi} --ntasks-per-node={config['tpn']} lmp {lammps_args}"
    elif config["jm"] == "none":
        return f"mpirun -np {mpi} lmp {lammps_args}"

def parse_mpi_timing(output):
    timing = {}
    in_table = False

    for line in output.splitlines():
        line = line.strip()

        if "MPI task timing breakdown:" in line:
            in_table = True
            continue

        if in_table:
            if line.startswith("Section") or line.startswith("---"):
                continue
            if line == "":
                break

            parts = line.split("|")
            if len(parts) < 6:
                break

            section = parts[0].strip()
            avg_time = parts[2].strip()

            try:
                timing[section] = float(avg_time)
            except ValueError:
                timing[section] = None

    return timing

def write_timing_csv(timings, csv_file):
    import csv

    if not timings:
        print("WARNING: no timing data to write")
        return

    sections = [k for k in timings[0].keys() if k not in ("mpi", "omp", "trial")]

    row = {"mpi": timings[0]["mpi"], "omp": timings[0]["omp"]}
    for section in sections:
        vals = [t[section] for t in timings if t[section] is not None]
        row[section] = sum(vals) / len(vals) if vals else None

    file_exists = os.path.exists(csv_file)

    with open(csv_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"timing written to {csv_file}")

def run_sweeps(config, parser):
    if config["step"] == "linear":
        sweep_range = range
    elif config["step"] == "pow":
        sweep_range = pow2_range
    else:
        parser.error("-step must be either linear or pow")

    if config['fmt'] == "csv" and config["greedy"] == "y":
        parser.error("-greedy can not be set to y while runtime formatting of LAMMPS output is selected")
    
    os.makedirs(config["out"], exist_ok=True)
    
    for mpi in sweep_range(config["mpi"]):
        for omp in sweep_range(config["omp"]):
            numbers = []
            
            for trial in range(1, config["trials"] + 1):
                cmd = build_command(config, mpi, omp)
                if config['fmt'] == "raw":
                    out_file = os.path.join(config["out"], f"lmp_omp{omp}_mpi{mpi}trial{trial}.out")
                    with open(out_file, "w") as f:
                        if config['greedy'] == 'y':
                            subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
                            print(f"  LAUNCHED -> {out_file}")
                        else:
                            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            output = result.stdout.decode()
                            print(output)
                            f.write(output)

                            if result.returncode != 0:
                                print(f"  WARNING: run exited with code {result.returncode}")
                            else:
                                print(f"  OK -> {out_file}")
                else:
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    if result.returncode != 0:
                        print(f"WARNING: run exited with code {result.returncode} skipping this configuration... Output as Follows\n{result.stdout.decode()}",end="")
                    output = result.stdout.decode()
                    t = parse_mpi_timing(output)
                    t["mpi"] = mpi
                    t["omp"] = omp
                    numbers.append(t)
                print(f"[mpi={mpi} omp={omp} trial={trial}] {cmd}")
            if config['fmt'] == "csv":
                out_file = os.path.join(config["out"], f"lmp_timings.csv")
                write_timing_csv(numbers, out_file)

                

                


def parse_output(config, parser):
    pass

def main():
    config, profile, parser = arg_parser()
    if profile:
        run_sweeps(config, parser)
    else:
        parse_output(config, parser)

if __name__ == "__main__":
    main()
#!/bin/bash
set -e

# Configure
cmake ../cmake -D PKG_OPENMP=yes -D BUILD_OMP=yes

# Patch line 209
sed -i '209s/#pragma omp parallel for LMP_DEFAULT_NONE LMP_SHARED(grad_u) schedule(static)/#pragma omp parallel for LMP_DEFAULT_NONE LMP_SHARED(grad_u, xmid) schedule(static)/' ../src/OPENMP/fix_nvt_sllod_omp.cpp
echo "xmid patch applied"
# Build
cmake --build . -- -j4

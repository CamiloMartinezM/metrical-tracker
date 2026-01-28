# !/bin/bash

# Source the configuration of micromamba
source configure_environment.sh

# Install the environment.yml
micromamba env create -f environment_py3.10.yml

# See: https://github.com/mattloper/chumpy/issues/56
pip3 install git+https://github.com/mattloper/chumpy.git --no-build-isolation
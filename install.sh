#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda env remove -n envReetm > /dev/null
conda env create -f reetmEnv.yml
#!/bin/bash
sudo apt-get install xclip
sudo apt-get install ffmpeg
source ~/anaconda3/etc/profile.d/conda.sh
conda deactivate
conda env remove -n envReetm
conda env create -f deployment/reetmEnv.yml
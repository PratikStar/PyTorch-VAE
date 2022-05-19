#!/bin/bash
#PJM -g gk77
#PJM -L rscgrp=share-short
#PJM -L gpu=4
#PJM -N Pytorch-VAE
#PJM -j
#PJM -m b
#PJM -m e

# run commands
python3 run.py -c configs/vae-gpu.yaml
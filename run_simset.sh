#!/bin/bash

for seed in {0..9}; do
    data_path=data$seed
    seed=$((143202461+$seed))
    echo "Simulation: path $data_path, seed $seed"
    python3 run_model.py --path $data_path --seed $seed
    
done






#!/bin/bash

for i in {1..20}
do
    output_path="./all_hetero_$i"
    
    seed=$((RANDOM * RANDOM))

    echo "Eseguo: python run_model.py --path $output_path --seed $seed"

    python run_model.py --path "$output_path" --seed "$seed"
done



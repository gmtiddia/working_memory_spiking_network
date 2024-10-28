#!/bin/bash

for i in {1..10}
do
    output_path="./new_base_prova_$i"
    
    seed=$((RANDOM * RANDOM))

    echo "Eseguo: python run_model.py --path $output_path --seed $seed"

    python run_model.py --path "$output_path" --seed "$seed"
done

for i in {1..10}; do
        sed -e "s/__data_path__/new_base_prova_$i/g" \
        -e "s/fig2{panel}\.png/seed_${i}_fig2{panel}\.png/g" analysis.templ > analysis_temp.py

    python analysis_temp.py
done

#!/bin/bash

for i in {1..10}; do
        sed -e "s/__data_path__/main_vth_$i/g" \
        -e "s/fig2{panel}\.png/seed_${i}_fig2{panel}\.png/g" analysis.templ > analysis_temp.py

    python analysis_temp.py
done

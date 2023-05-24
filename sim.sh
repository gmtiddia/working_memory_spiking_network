for i in {200..750..25}; do
    cat run_model_downscaled.templ | sed "s%__path__%data_26mV/data_2A_ds20_$i%" | sed "s/__time__/$i/" > run_model_downscaled.py
    python run_model_downscaled.py
done
# working_memory_spiking_network
Spiking network model and analysis scripts for the preprint "Simulations of Working Memory Spiking Networks driven by Short-Term Plasticity"

--------------------------------------------------------------------------------

## Authors
Gianmarco Tiddia, Bruno Golosio, Viviana Fanti, Pier Stanislao Paolucci

--------------------------------------------------------------------------------

## Outline
The Python scripts in which the model is implemented are in the ``model`` directory.

To properly run the model, [this version](https://github.com/gmtiddia/nest-simulator-3.1) of the NEST simulator is needed. It is the [NEST 3.1 version](https://github.com/nest/nest-simulator/tree/3.1-develop) with the additional synapse model ``tsodyks3_synapse`` implemented.

To run the network model please edit the script ``run_model.py`` using the correct parameters and run the Python script. In default conditions, a directory ``data`` is returned containing the spike times of the selective populations of the model. To reproduce the plots shown in the article please edit and run ``analysis.py``.




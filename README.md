# working_memory_spiking_network
Spiking network model and analysis scripts for the preprint "Simulations of Working Memory Spiking Networks driven by Short-Term Plasticity"

--------------------------------------------------------------------------------

## Authors
Gianmarco Tiddia, Bruno Golosio, Viviana Fanti, Pier Stanislao Paolucci

--------------------------------------------------------------------------------

## Outline
<<<<<<< HEAD
The Python scripts in which the model is implemented are in the ``model`` directory.
In ``model.py`` the class ``WMModel`` which initialize the model is defined. The script ``model_helpers.py`` contains the functions needed to properly run the network model, and in ``default_params.py`` are stored the Python dictionaries with the parameters needed to run the model.
=======
In ``model.py`` the spiking networn model is implemented [this version of the simulator NEST](https://github.com/gmtiddia/nest-simulator-3.1), that is the NEST 3.1 version with the additional synapse model ``tsodyks3_synapse`` implemented. The script ``model_helpers.py`` contains the functions needed to properly run the network model, and in ``default_params.py`` are stored the Python dictionaries with the parameters needed to run the model. 
>>>>>>> 95abdeb9c47172e114e7ed5a8c3b40378110e5e8

To properly run the model, [this version](https://github.com/gmtiddia/nest-simulator-3.1) of the NEST simulator is needed. It is the NEST 3.1 version with the additional synapse model ``tsodyks3_synapse``.

To run the network model please edit the script ``run_model.py`` using the correct parameters and run the Python script. In default conditions, a directory ``data`` is returned containing the spike times of the selective populations of the model. To reproduce the plots shown in the article please edit and run ``analysis.py``.




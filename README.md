# working_memory_spiking_network

Spiking network model and analysis scripts for the publication:

> Tiddia, G., Golosio, B., Fanti, V., & Paolucci, P. S. (2022). Simulations of working memory spiking networks driven by short-term plasticity. Frontiers in Integrative Neuroscience, 16, 972055. https://doi.org/10.3389/fnint.2022.972055

If you use the code, cite us using the citation above.

# Requirements
To run the model, the NEST version of [this repository](https://github.com/gmtiddia/nest-simulator-3.1) is required. It is derived from the [NEST 3.1 version](https://github.com/nest/nest-simulator/tree/3.1-develop), with the addition of the ``tsodyks3_synapse`` model, not present in the standard version of the library. For the installation instructions, follow [this guide](https://nest-simulator.readthedocs.io/en/v3.1/installation/linux_install.html).

Additionally, to run the model and analyze the data, Python and additional packages are required. To produce the data of the aforementioned publication, the following software was used:
- Python 3.9.7
- Pandas 1.3.3
- Numpy 1.22.4
- Matplotlib 3.3.4


# Contents
- The Python scripts in which the model is implemented are in the [model](model/) directory. In particular:
    - [default_params.py](model/default_params.py) contains all the parameters of the model organized as Python dictionaries. This file should not be edited, the simulation parameters can be changed in the running script.
    - [model_helpers.py](model/model_helpers.py) contains two functions used in this model and are needed to properly compute the values of synaptic efficacy and input current. The derivation of the mathematical expressions is discussed in Sections 6 and 7 of the Supplementary Material of the publication.
    - [model.py](model/model.py) introduces the class ``WMModel`` which initializes the model. The script contains all the functions employed to build the model and configure its inputs.

- The [test_synapse_model](test_synapse_model/) directory contains the Python scripts needed to compare the different tsodyks_synapse implementations of the modified version of the NEST simulator previously mentioned. In particular:
    - ```evaluate_tsodyks3_synapse.py``` is based on the NEST example ```evaluate_tsodyks2_synapse.py```, which compares the postsynaptic potentials of two neurons connected to the presynaptic one using two different synaptic models: ```tsodyks_synapse``` and ```tsodyks2_synapse```. In this script, an additional neuron connected using the ```tsodyks3_synapse``` is simulated, and the postsynaptic potentials given by the three synaptic models ```tsodyks_synapse```, ```tsodyks2_synapse``` and ```tsodyks3_synapse``` are saved to a file.
    - ```plot_tsodyks3_evaluation.py``` takes in input the output file of the previous script to produce Figure S5 of the Supplementary Material.

- [run_model.py](run_model.py) simulates the model. In lines [19](run_model.py#L19) and [35](run_model.py#L35), the custom network and the simulation parameters are defined. Not all the parameters should be reported at this stage. The parameters not indicated in these dictionaries that have to be used by the model are taken from [default_params.py](model/default_params.py). In line [64](run_model.py#L64) the model is initialized, and in the following lines, the input is added to the network to reproduce the data of different figures of the publication. After the simulation, a ``data`` directory is returned containing the spike times of the selective populations of the model.

- [analysis.py](analysis.py) reproduces the plots shown in the publication. To reproduce the data edit line [509](analysis.py#L509) of the script with the path in which the data is stored and edit lines [536](analysis.py#L536) and [538](analysis.py#L538) to specify which figure (2 and 3) and panel (A, B, or C) you want to reproduce from the publication.

## Advanced simulations

By typing
```
python3 run_model.py --help
```

you can see that two arguments can be set when running the simulation:
- path, which indicates the name of the directory in which data will be stored
- seed, i.e., the seed for random number generation

These settings are useful in case multiple simulations using different seeds have to be done.

A simple use case is shown in [run_simset.sh](run_simset.sh), which performs a set of 10 simulations changing the seed for random number generation and the path.


# Contact
Gianmarco Tiddia, Department of Physics, University of Cagliary, Italy, Istituto Nazionale di Fisica Nucleare, Sezione di Cagliari, Italy, gianmarco.tiddia@ca.infn.it

# License
GPL 3.0 [license](LICENSE).


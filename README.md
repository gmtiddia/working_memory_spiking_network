# Working Memory spiking network model sustained by short-term facilitation

Spiking network model for the publications:

> Tiddia, G., Golosio, B., Fanti, V., & Paolucci, P. S. (2022). Simulations of working memory spiking networks driven by short-term plasticity. Frontiers in Integrative Neuroscience, 16, 972055. https://doi.org/10.3389/fnint.2022.972055

> Tiddia G, Sergi L, Rubiu S, Incollu A, & Golosio B. Short-term plasticity-based working memory spiking model is resilient to synaptic heterogeneity. In review.

If you use the code, please cite us using the citations above.

# Requirements
To run the model you need both [NEST 3.X](https://github.com/nest/nest-simulator) and [NESTML](https://github.com/nest/nestml) installed. For installation instructions, follow the guides for [NEST](https://nest-simulator.readthedocs.io/en/stable/installation/index.html) and [NESTML](https://nestml.readthedocs.io/en/latest/installation.html).

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

- The [test_synapse_model](test_synapse_model/) directory contains the Python scripts needed to compare the different tsodyks_synapse implementations. In particular:
    - ```evaluate_tsodyks_synapse_implementation.py``` is based on the NEST example ```evaluate_tsodyks2_synapse.py```, which compares the postsynaptic potentials of two neurons connected to the presynaptic one using two different synaptic models: ```tsodyks_synapse``` and ```tsodyks2_synapse```. In this script, an additional neuron connected using the STP synapse created through NESTML is simulated, and the postsynaptic potentials given by the three synaptic models are saved to a file.
    - ```plot_synmodels_evaluation.py``` takes in input the output file of the previous script to produce Figure S5 of the Supplementary Material.

- [run_model.py](run_model.py) simulates the model. After the simulation, a ``data`` directory is returned containing the spike times of the selective populations of the model.


# Data reproducibility

The original implementation of the publication

> Tiddia, G., Golosio, B., Fanti, V., & Paolucci, P. S. (2022). Simulations of working memory spiking networks driven by short-term plasticity. Frontiers in Integrative Neuroscience, 16, 972055. https://doi.org/10.3389/fnint.2022.972055

is available at the [v_tiddia2022](https://github.com/gmtiddia/working_memory_spiking_network/releases/tag/v_tiddia2022) tag. In order for this version of the model to be run, the NEST version of [this repository](https://github.com/gmtiddia/nest-simulator-3.1) is required. It is derived from the [NEST 3.1 version](https://github.com/nest/nest-simulator/tree/3.1-develop), with the addition of the ``tsodyks3_synapse`` model, not present in the standard version of the library. For the installation instructions, follow [this guide](https://nest-simulator.readthedocs.io/en/v3.1/installation/linux_install.html). We verified that the simulations employing the ``tsodyks3_synapse`` model and the NESTML model produce the sam eresults. You can use the scripts contained in [test_synapse_model/comparison_tsodyks3_NESTML](test_synapse_model/comparison_tsodyks3_NESTML/) directory to compare the two implementations.


The current repository enables the eterogeneity of the synaptic parameters and an improved reproducibility thanks to the NESTML implementation of synaptic model, as discussed in

> Tiddia G, Sergi L, Rubiu S, Incollu A, & Golosio B. Short-term plasticity-based working memory spiking model is resilient to synaptic heterogeneity. In review.

# Contact
Gianmarco Tiddia, Istituto Nazionale di Fisica Nucleare, Sezione di Cagliari, Italy, gianmarco.tiddia@dsf.unica.it
Luca Sergi, Physics department, University of Cagliari, Italy, lsergi@dsf.unica.it

# License
GPL 3.0 [license](LICENSE).


# Network Model
In ``model.py`` the class ``WMModel`` which initializes the model is defined.
The script ``model_helpers.py`` contains the functions needed to properly run the network model. The first one converts the synaptic efficacies (given in mV) to pA, so that a post synaptic potential has an amplitude equal to the parameter given in input. The latter, similarly, converts the parameters given to reproduce the external input (given in mV as well).
In ``default_params.py`` are stored the Python dictionaries with the parameters needed to run the model.




# Test tsodyks3_synapse
Here the Python example used to compare the short-term plasticity synaptic models is shown.
The script ``evaluate_tsodyks3_synapse.py`` is based on the NEST example ``evaluate_tsodyks2_synapse.py``, which compare the postsynaptic potentials of
two neurons connected to the presynaptic one using two different synaptic models: ``tsodyks_synapse`` and ``tsodyks2_synapse``. In this script, an additional neuron connected using the ``tsodyks3_synapse`` is simulated, and the postsynaptic potentials given by the three synaptic models ``tsodyks_synapse``, ``tsodyks2_synapse`` and ``tsodyks3_synapse`` are saved to a file.

The script ``plot_tsodyks3_evaluation.py`` takes in input the output file of the previous script to produce the Figure S1 of the Supplementary Material.




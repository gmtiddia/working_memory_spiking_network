# Test NESTML implementation of Tsodyks synapse

Type

```
python3 evaluate_tsodyks_synapse_implementation.py
```

to simulate a network of four neurons, in which the first of them targets each one of the others using a different model of Tsodyks synapse with the same values of depression and facilitation time constant. The simulation produces as output the file ```voltage_data.dat```, containing the membrane potential of the three neurons targeted with different synapse models.

Then type
```
python3 plot_synmodels_evaluation.py
```

to compare the results of the different implementations of the synapse model.


## Compare the NESTML implementation with the NEST implementation

To compare the versions of the synapse model implemented on the source code of the NEST simulator and on NESTML please see the content of the  [comparison_tsodyks3_NESTML](comparison_tsodyks3_NESTML/) directory.

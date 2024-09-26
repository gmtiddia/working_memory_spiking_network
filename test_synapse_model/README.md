# Test tsodyks3_synapse NESTML implementation

Type

```
python3 evaluate_tsodyks3_synapse.py
```

to simulate a network of four neurons, in which the first of them targets each one of the others using a different model of Tsodyks synapse with the same values of depression and facilitation time constant. The simulation produces as output the file ```voltage_data.dat```, containing the membrane potential of the three neurons targeted with different synapse models.

Then type
```
python3 plot_tsodyks3_evaluation.py
```

to reproduce Figure S5 of the Supplementary Material of the publication.


## Compare the NESTML implementation with the NEST implementation

To compare the versions of the synapse model implemented on the source code of the NEST simulator and on NESTML please see the content of the  [comparison_tsodyks3_NESTML](comparison_tsodyks3_NESTML/) directory.

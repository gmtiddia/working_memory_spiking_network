# Test tsodyks3_synapse in NEST and NESTML implementation

> [!NOTE]  
> To run the Python scripts contained in this directory you need to install the NEST 3.1 fork available [here](https://github.com/gmtiddia/nest-simulator-3.1).

Type

```
python3 evaluate_tsodyks3_synapse.py
```

to simulate a network of four neurons, in which the first of them targets each one of the others using a different model of Tsodyks synapse with the same values of depression and facilitation time constant. The simulation produces as output the file ```voltage_data.dat```, containing the membrane potential of the four neurons targeted with different synapse models.

Then type
```
python3 plot_tsodyks3_NEST_vs_NESTML.py
```

to compare the NEST and NESTML implementation of the synapse model.

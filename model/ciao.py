import nest
import numpy as np
import nest.voltage_trace
import matplotlib.pyplot as plt

Nt = 1000

n = nest.Create("iaf_psc_exp", 2)
nest.SetStatus(n, {'tau_syn_ex': 100.0, 'tau_syn_in': 100.0})
print(nest.GetStatus(n))
scg = nest.Create("step_current_generator")
wng = nest.Create("noise_generator")

at = np.linspace(1,Nt, Nt)
av = np.random.normal(100, 10.0, Nt)

nest.SetStatus(scg, {"amplitude_times" : at, "amplitude_values" : av ,"start" : 0})
nest.SetStatus(wng, {"mean" : 100, "std" : 10,"start" : 0})

conn_dict = {"rule": "one_to_one"}
syn_dict = {"weight": 1.0, "delay": 1.0}
nest.Connect(scg, n[0], conn_dict, syn_dict)
nest.Connect(wng, n[1], conn_dict, syn_dict)

voltmeter = nest.Create("voltmeter", 2, params={'interval': 0.1})

nest.Connect(voltmeter[0], n[0])
nest.Connect(voltmeter[1], n[1])


nest.Simulate(1000.0)


plt.figure(1)
nest.voltage_trace.from_device(voltmeter[0])
nest.voltage_trace.from_device(voltmeter[1])
plt.show()
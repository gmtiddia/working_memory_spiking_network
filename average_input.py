import numpy as np

N_exc = 8000
N_inh = 2000
c = 0.2
c_sp = 0.2
p = 5
N_p = 800
Jb = 0.1
Jp = 0.45
JEI = 0.25
nu_s = 0.28
nu_ns = 0.22
nu_i = 3.3

total_connections = c*(N_exc+N_inh - p*N_p) + c_sp*p*N_p

print("Considering a neuron belonging to a selective population")
# 100% at Jp
conn_same_sp = c_sp*N_p/total_connections
# 100% at Jb
conn_other_sp = c*(p-1)*N_p/total_connections
# 10% at Jp and 90% at Jb
conn_nonsp = c*(N_exc - p*N_p)/total_connections
# 100% at JEI
conn_inh = c*N_inh/total_connections

mu = (conn_same_sp*Jp + conn_other_sp*Jb)*nu_s + (conn_nonsp*0.9*Jb + conn_nonsp*0.1*Jp)*nu_ns - (conn_inh*JEI)*nu_i

print("Average input coming from the neurons = {} mV/ms".format(mu))

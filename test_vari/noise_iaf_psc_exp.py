import nest
import math
import numpy as np
import scipy
import matplotlib.pyplot as plt

def noise_params(V_mean, V_std, dt=1.0, tau_m=10., C_m=250.):
    #'Returns mean and std for noise generator for parameters provided; defaults for iaf_psc_alpha.'

    return C_m / tau_m * V_mean, math.sqrt(2/(tau_m*dt))*C_m*V_std

def V_asymptotic(mu, sigma, dt=1.0, tau_m=10., C_m=250.):
    'Returns asymptotic mean and std of V_m'

    V_mean = mu * tau_m / C_m
    V_std = (sigma * tau_m / C_m) * np.sqrt(( 1 - math.exp(-dt/tau_m) ) / ( 1 + math.exp(-dt/tau_m) ))

    return V_mean, V_std

def V_mean(t, mu, tau_m=10., C_m=250.):
    'Returns predicted voltage for given times and parameters.'

    vm, _ = V_asymptotic(mu, sigma, tau_m=tau_m, C_m=C_m)
    return vm * ( 1 - np.exp( - t / tau_m ) )

def V_std(t, sigma, dt=1.0, tau_m=10., C_m=250.):
    'Returns predicted variance for given times and parameters.'

    _, vms = V_asymptotic(mu, sigma, dt=dt, tau_m=tau_m, C_m=C_m)
    return vms * np.sqrt(1 - np.exp(-2*t/tau_m))

def simulate(mu, sigma, dt=1.0, tau_m=10., C_m=250., N=1000, t_max=100.):
    '''
    Simulate an ensemble of N iaf_psc_alpha neurons driven by noise_generator.

    Returns
    - voltage matrix, one column per neuron
    - time axis indexing matrix rows
    - time shift due to delay, time at which first current arrives
    '''

    resolution = 0.1
    delay = 1.0

    nest.ResetKernel()
    nest.resolution = resolution
    ng = nest.Create('noise_generator', params={'mean': mu, 'std': sigma, 'dt': dt})
    vm = nest.Create('voltmeter', params={'interval': resolution})
    nrns = nest.Create('iaf_psc_exp', N, params={'E_L': 0., 'V_m': 0., 'V_th': 1e6,
                                                   'tau_m': tau_m, 'C_m': C_m})
    nest.Connect(ng, nrns, syn_spec={'delay': delay})
    nest.Connect(vm, nrns)

    nest.Simulate(t_max)

    # convert data into time axis vector and matrix with one column per neuron
    t, s, v = vm.events['times'], vm.events['senders'], vm.events['V_m']
    tix = np.array(np.round(( t - t.min() ) / resolution), dtype=int)
    sx = np.unique(s)
    assert len(sx) == N
    six = s - s.min()
    V = np.zeros((tix.max()+1, N))
    for ix, vm in enumerate(v):
        V[tix[ix], six[ix]] = vm

    # time shift due to delay and onset after first step
    t_shift = delay + resolution
    return V, np.unique(t), t_shift


'''
dt = 1.0
mu, sigma = noise_params(10, 0.0, dt=dt)
print("mu = {:.2f}, sigma = {:.2f}".format(mu, sigma))

V, t, ts = simulate(mu, sigma, dt=dt)
V_mean_th = V_mean(t, mu)
V_std_th = V_std(t, sigma, dt=dt)

plt.plot(t, V.mean(axis=1), 'b-', label=r'$\bar{V_m}$')
plt.plot(t + ts, V_mean_th, 'b--', label=r'$\langle V_m \rangle$')
plt.plot(t, V.std(axis=1), 'r-',  label=r'$\sqrt{\bar{\Delta V_m^2}}$')
plt.plot(t + ts, V_std_th, 'r--', label=r'$\sqrt{\langle (\Delta V_m)^2 \rangle}$')

'''
dt = 0.1
mu, sigma = noise_params(10, 1, dt=dt)
print("mu = {:.2f}, sigma = {:.2f}".format(mu, sigma))

V, t, ts = simulate(mu, sigma, dt=dt)
V_mean_th = V_mean(t, mu)
V_std_th = V_std(t, sigma, dt=dt)

plt.plot(t, V.mean(axis=1), 'g-', label=r'$\bar{V_m}$')
plt.plot(t + ts, V_mean_th, 'g--', label=r'$\langle V_m \rangle$')
plt.plot(t, V.std(axis=1), 'k-',  label=r'$\sqrt{\bar{\Delta V_m^2}}$')
plt.plot(t + ts, V_std_th, 'k--', label=r'$\sqrt{\langle (\Delta V_m)^2 \rangle}$')


plt.legend()
plt.xlabel('Time $t$ [ms]')
plt.ylabel('Membrane potential $V_m$ [mV]')
#plt.xlim(0, 50)

plt.show()

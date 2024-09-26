import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys
import pandas as pd


def load_spike_data(overlap = False):
    if(overlap==False):
        srs = [np.loadtxt(data_path + "spikedata"+str(i)+".dat") for i in range(network_params["p"])]
        
    # change neuron id so that each selective population has ids [800*(i-1), 800*i]
    else:
        sr0_dum = np.loadtxt(data_path + "spikedata0.dat")
        sr1_dum = np.loadtxt(data_path + "spikedata1.dat")
        sr2_dum = np.loadtxt(data_path + "spikedata2.dat")
        sr3_dum = np.loadtxt(data_path + "spikedata3.dat")
        sr4_dum = np.loadtxt(data_path + "spikedata4.dat")
        old_data = [sr0_dum, sr1_dum, sr2_dum, sr3_dum, sr4_dum]
        ids = np.loadtxt(data_path + "selective_pop_ids.dat")
        srs = []
        for i in range(len(old_data)):
            sorted_ids = np.sort(ids[:,i]) + 1
            sr = old_data[i]
            for idx in sorted_ids:
                pos_old_ids = np.where(old_data[i][:,0]==idx)
                if(list(pos_old_ids[0])!=[]):
                    for r in list(pos_old_ids[0]):
                        sr[r,0]=np.where(sorted_ids==idx)[0][0] + 800*i
            srs.append(sr)
    
    return(srs)

def raster_plot():
    labelsize=19
    titlesize=20
    f = network_params["f"]
    N_E = network_params["N_exc"]
    # number of neurons belonging to a selective populaiton
    n_E = int(N_E * f)
    n_E_frac = int(n_E * 0.1)
    colors = ["blue", "red", "green", "orange", "olive", "cornflowerblue", "salmon", "lime", "gold", "yellowgreen"]
    fig, ax = plt.subplots(figsize=(15,10))
    for i in range(len(srs)):
        dum = srs[i]
        dumx = []
        dumy = []
        for j in range(len(dum[:,0])):
            if(srs[i][j,0]<n_E_frac+n_E*i):
                dumx.append(dum[j,1])
                dumy.append(dum[j,0]-(n_E-n_E_frac)*i)
        ax.plot(dumx, dumy, '.', color=colors[i])
    ax.set_ylabel("# cell", fontsize=labelsize)
    ax.set_xlabel("Time [ms]", fontsize=labelsize)
    ax.set_xlim(0,20000)
    ax.set_ylim(0,n_E_frac*len(srs))
    ax.tick_params(labelsize=labelsize)
    for i in range(network_params["item_loading"]["nstim"]):
        ax.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], (1./len(srs))*i, (1./len(srs))*(i+1), alpha=0.5, color='grey')
    if("nonspecific_readout_signals" in network_params):
        for i in range(network_params["nonspecific_readout_signals"]["nstim"]):
            if(i==0):
                ax.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='cornflowerblue', label="Readout signal")
            else:
                ax.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='cornflowerblue')
    if("nonspecific_noise" in network_params):
        for i in range(network_params["nonspecific_noise"]["nstim"]):
            if(i==0):
                ax.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='turquoise', label="Noise")
            else:
                ax.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='turquoise')
    plt.subplots_adjust(left=0.07, right=0.976, top=0.925, bottom=0.1)
    plt.savefig(simulation_params['data_path']+"raster_plot_analysis.png")
    plt.draw()


def firing_rate(t_start, t_stop):
    
    SE = sr0
    dum = SE[:,1]
    dum = (dum > t_start) & (dum < t_stop )
    print("Start firing rate calculation at {} ms and stop at {} ms".format(t_start, t_stop))
    # neuron that emitted the spikes in that range
    senders = [i for (i, dum) in zip(SE[:,0], dum) if dum]
    N_neurons_recorded = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["fraction_pop_recorded"])
    ids = np.arange(np.min(senders),np.min(senders)+N_neurons_recorded)
    #print(len(ids))
    # count firing rate for each neuron
    occ = [[x,1000.0*senders.count(x)/(t_stop-t_start)] for x in ids]
    print("Average firing rate: {:.2} Hz".format((len(senders)*1000.0/(t_stop-t_start))/len(ids)))
    #dum = SE["times"]
    return(occ)


def firing_rate_hist(t_start1, t_stop1, t_start2, t_stop2, plot):
    occurrencies1 = firing_rate(t_start1, t_stop1, spike_recorder)
    occurrencies2 = firing_rate(t_start2, t_stop2, spike_recorder)
    SE = sr0
    dum = np.min(SE[:,0])
    N_neurons_recorded = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["fraction_pop_recorded"])
    ids = np.arange(dum,dum+N_neurons_recorded)
    delta_fr = [[id, occurrencies1[id-1][1]-occurrencies2[id-1][1]] for id in ids]
    if plot == True:
        labelsize=19
        titlesize=20
        df_hist = [delta_fr[i-1][1] for i in ids]
        plt.figure()
        plt.title(r"$\Delta$ fr between delay period and spontaneous state in the target population", fontsize=titlesize)
        plt.hist(df_hist, color = "crimson",bins="auto", density=True)
        plt.xlabel("Firing rate difference [Hz]", fontsize=labelsize)
        plt.ylabel("Fraction of cells", fontsize=labelsize)
        plt.tick_params(labelsize=labelsize)
        plt.draw()


def get_firing_rate_plot():
    
    spike_recorder = spike_recorders[0]
    # spontaneous rate
    t_start2 = simulation_params["recording_params"]["spike_recording_params"]["start"]
    t_stop2 = network_params["item_loading"]["origin"][0]
    # delay period
    t_start1 = network_params["item_loading"]["origin"][0] + network_params["stimulation_params"]["T_cue"]
    if("nonspecific_readout_signals" in network_params):
        t_stop1 = network_params["nonspecific_readout_signals"]["origin"][0]
    if("nonspecific_noise" in network_params):
        t_stop1 = network_params["nonspecific_noise"]["origin"][0]
    if("nonspecific_readout_signals" in network_params and "nonspecific_noise" in network_params):
        t_stop1 = min(network_params["nonspecific_readout_signals"]["origin"][0], network_params["nonspecific_noise"]["origin"][0])
    else:
        t_stop1 = simulation_params["eta_end_origin"]
    
    
    firing_rate_hist(spike_recorder, t_start1, t_stop1, t_start2, t_stop2, plot=True)
    #fr_diff = fr_difference(sr1, item_origin + stim_params["T_cue"], 3000.0, 20, item_origin,  True)


def figure2(stp = False, t=[], x=[], u=[], panel="A"):
    labelsize=19
    titlesize=20
    f, (ax0, ax1) = plt.subplots(1, 2, figsize=(15,4.2), gridspec_kw={'wspace': 0.4,'width_ratios': [2.5, 1]})

    for i in range(network_params["item_loading"]["nstim"]):
        if(i==0):
            ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey', label="Item Loading")
        else:
            ax1.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey')
    if("nonspecific_readout_signals" in network_params):
        for i in range(network_params["nonspecific_readout_signals"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey', label="Readout signal")
            else:
                ax0.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey')
    if("nonspecific_noise" in network_params):
        for i in range(network_params["nonspecific_noise"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise', label="Noise")
            else:
                ax0.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise')
    if("periodic_sequence" in network_params):
            for i in range(len(network_params["periodic_sequence"]["times"])):
                if(i==0):
                    ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey', label="Periodic stimuli")
                else:
                    ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey')
    
    #plt.title("Raster plot for a subset of Pop {} and Pop {} neurons".format(simulation_params["recording_params"]["pop_recorded"][0], simulation_params["recording_params"]["pop_recorded"][1]), fontsize=titlesize)
    ax0.plot(sr0[:,1], sr0[:,0], '.', color = "limegreen", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][0]))
    ax0.plot(sr1[:,1], sr1[:,0]-[800 for i in sr1[:,0]], '.', color = "k", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][1]))
    ax0.set_ylabel("# cell", color="k", fontsize=labelsize)
    ax0.set_xlabel("Time [ms]", fontsize=labelsize)
    ax0.tick_params(labelsize=labelsize, pad=10, axis ='x')
    ax0.tick_params(labelsize=labelsize, axis ='y')
    ax0.set_yticks([0,80])
    ax0.set_ylim(0.0, 80.0)
    x_min = 2000.0
    x_max=6000.0
    ax0.set_xlim(x_min, x_max)
    ax0.set_yticklabels(['0','80'])
    ax0.text(-0.095,1.0,panel, transform=ax0.transAxes, weight="bold", fontsize=labelsize+3)
    ax02=ax0.twinx()
    ax02.set_navigate(False)
    if(stp==True):
        ax02.plot(t, x, 'r', linewidth = 2.5, label="x")
        ax02.plot(t, u, "b", linewidth = 2.5, label="u")
        ax02.set_ylim(0,1.0)
    
    #ax02.set_ylabel("x, u", fontsize=labelsize)
    plt.text(1.085, 0.65, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.35, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)
    

    ax02.tick_params(labelsize=labelsize)
    ax02.tick_params(axis ='y')


    # spontaneous rate
    t_start2 = simulation_params["recording_params"]["spike_recording_params"]["start"] + 450.0
    t_stop2 = network_params["item_loading"]["origin"][0]
    # delay period
    t_start1 = network_params["item_loading"]["origin"][0] + network_params["stimulation_params"]["T_cue"]
    if("nonspecific_readout_signals" in network_params):
        t_stop1 = network_params["nonspecific_readout_signals"]["origin"][0]
    elif("nonspecific_noise" in network_params):
        t_stop1 = network_params["nonspecific_noise"]["origin"][0]
    elif("nonspecific_readout_signals" in network_params and "nonspecific_noise" in network_params):
        t_stop1 = min(network_params["nonspecific_readout_signals"]["origin"][0], network_params["nonspecific_noise"]["origin"][0])
    else:
        t_stop1 = simulation_params["eta_end_origin"]

    # put arrows indicating spontaneous activity and delay periods
    ax0.hlines(y=0.0, xmin=t_start1, xmax=t_stop1, color="orange", linewidth=7)
    ax0.hlines(y=0.0, xmin=t_start2, xmax=t_stop2, color="skyblue", linewidth=7)

    occurrencies1 = firing_rate(t_start1, t_stop1)
    occurrencies2 = firing_rate(t_start2, t_stop2)
    SE = sr0
    dum = int(np.min(SE[:,0]))
    N_neurons_recorded = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["fraction_pop_recorded"])
    ids = np.arange(dum,dum+N_neurons_recorded)
    delta_fr = [[id, occurrencies1[id-1][1]-occurrencies2[id-1][1]] for id in ids]
    df_hist = [delta_fr[i-1][1] for i in ids]
    counts, bins = np.histogram(df_hist, bins=40, range=(-5,15))
    norm = np.sum(counts)
    counts = [counts[i]/norm for i in range(len(counts))]
    #a1.title(r"$\Delta$ fr between delay period and spontaneous state in the target population", fontsize=titlesize)
    ax1.bar(bins[:-1], counts, width = bins[1] - bins[0], color="cornflowerblue", align="center", linewidth=0.2, edgecolor="w")
    ax1.set_xlabel("Firing rate difference [Hz]", fontsize=labelsize)
    ax1.set_ylabel("Fraction of cells", fontsize=labelsize)
    if(panel=="A"):
        ax1.set_xlim(-1,10)
        ax1.set_xticks([-5,0,5,10])
    else:
        ax1.set_xlim(-1,15)
        ax1.set_xticks([0,5,10,15])
    ax1.tick_params(labelsize=labelsize)
    plt.subplots_adjust(left=0.06, right=0.976, top=0.925, bottom=0.207)
    #plt.subplots_adjust(left=0.06, right=0.976, top=0.89, bottom=0.207)
    #plt.suptitle("multapses and autapses disabled", fontsize=labelsize)
    plt.savefig(simulation_params['data_path']+"fig2{panel}.png".format(panel=panel))
    
    #plt.draw()

def figure3(stp=False, stp0= [], stp1 =[], panel="A"):
    labelsize=19
    titlesize=20
    f, (ax0) = plt.subplots(1, 1, figsize=(15,6.))

    for i in range(network_params["item_loading"]["nstim"]):
        if(i==0):
            ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0, 0.5, alpha=0.5, color='grey', label="Item Loading")
        else:
            ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0.5, 1, alpha=0.5, color='grey')
    if("nonspecific_readout_signals" in network_params):
        for i in range(network_params["nonspecific_readout_signals"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey', label="Readout signal")
            else:
                ax0.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey')
    if("nonspecific_noise" in network_params):
        for i in range(network_params["nonspecific_noise"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise', label="Noise")
            else:
                ax0.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise')
    if("periodic_sequence" in network_params):
            for i in range(len(network_params["periodic_sequence"]["times"])):
                if(i==0):
                    ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey', label="Periodic stimuli")
                else:
                    ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey')

    ax0.plot(sr0[:,1], sr0[:,0]-[720 for i in sr0[:,0]], '.', color = "limegreen", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][0]))
    ax0.plot(sr1[:,1], sr1[:,0]-[720 for i in sr1[:,0]], '.', color = "k", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][1]))
    ax0.set_ylabel("# cell", color="k", fontsize=labelsize)
    ax0.set_xlim(2000.0, 8000.0)
    if network_params["overlap"]:
        ax0.set_xlim(2000.0, 8000.0)
    ax0.tick_params(labelsize=labelsize, pad=10, axis ='x')
    ax0.tick_params(labelsize=labelsize, axis ='y')
    ax0.set_yticks([0,80,160])
    ax0.set_yticklabels(['0','80', '160'])
    ax0.set_ylim(0.0, 160.0)
    if network_params["overlap"]==False:
        ax0.text(-0.095,1.0,panel, transform=ax0.transAxes, weight="bold", fontsize=labelsize+3)
    ax02=ax0.twinx()
    ax02.set_navigate
    (False)
    ax02.set_ylim(0,2.0)
    ax02.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0])
    ax02.set_yticklabels(["0.0", "0.25", "0.5", "0.75", "1.0", "0.25", "0.5", "0.75", "1.0"])
    ax02.tick_params(labelsize=labelsize)
    if(stp==True):
        t0 = stp0[0]
        x0 = stp0[1]
        u0 = stp0[2]
        t1 = stp1[0]
        x1 = stp1[1]
        u1 = stp1[2]
        ax02.plot(t0, x0, 'r', linewidth = 2.5)
        ax02.plot(t0, u0, "blue", linewidth = 2.5)
        ax02.plot(t1, x1+[1.0 for i in t1], 'r', linewidth = 2.5)
        ax02.plot(t1, u1+[1.0 for i in t1], "blue", linewidth = 2.5)
    ax0.set_xlabel("Time [ms]", fontsize=labelsize)
    plt.text(1.085, 0.35, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.15, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.85, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.65, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)

    plt.draw()
    plt.subplots_adjust(left=0.088, right=0.9, top=0.95, bottom=0.136)
    plt.savefig(simulation_params['data_path']+"fig3{panel}.png".format(panel=panel))


def figure4(stp=False, stp0= [], stp1 =[], stp2 = []):
    labelsize=19
    titlesize=20
    f, (ax0) = plt.subplots(1, 1, figsize=(15,9.))

    for i in range(network_params["item_loading"]["nstim"]):
        if(i==0):
            ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0, 0.33, alpha=0.5, color='grey', label="Item Loading")
        elif(i==1):
            ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0.33, 0.66, alpha=0.5, color='grey')
        else:
            ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0.66, 1., alpha=0.5, color='grey')
    if("nonspecific_readout_signals" in network_params):
        for i in range(network_params["nonspecific_readout_signals"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey', label="Readout signal")
            else:
                ax0.axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey')
    if("nonspecific_noise" in network_params):
        for i in range(network_params["nonspecific_noise"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise', label="Noise")
            else:
                ax0.axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise')
    if("periodic_sequence" in network_params):
            for i in range(len(network_params["periodic_sequence"]["times"])):
                if(i==0):
                    ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey', label="Periodic stimuli")
                else:
                    ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey')

    x0 = []; y0 = []
    x1 = []; y1 = []
    x2 = []; y2 = []

    for i in range(len(sr0[:,1])):
        if(sr0[i,0]<80):
            x0.append(sr0[i,1])
            y0.append(sr0[i,0])
    for i in range(len(sr1[:,1])):
        if(sr1[i,0]<880):
            x1.append(sr1[i,1])
            y1.append(sr1[i,0] - 720)
    for i in range(len(sr2[:,1])):
        if(sr2[i,0]<1680):
            x2.append(sr2[i,1])
            y2.append(sr2[i,0] - 1440)
        
    ax0.plot(x0, y0, '.', color = "limegreen", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][0]))
    ax0.plot(x1, y1, '.', color = "k", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][1]))
    ax0.plot(x2, y2, '.', color = "steelblue", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][1]))
    ax0.set_ylabel("# cell", color="k", fontsize=labelsize)
    ax0.set_xlim(1500.0, 11000.0)
    ax0.tick_params(labelsize=labelsize, pad=10, axis ='x')
    ax0.tick_params(labelsize=labelsize, axis ='y')
    ax0.set_yticks([0,80,160,240])
    ax0.set_yticklabels(['0','80', '160', '240'])
    ax0.set_ylim(0.0, 240.0)
    #ax0.text(-0.095,1.0,panel, transform=ax0.transAxes, weight="bold", fontsize=labelsize+3)
    ax02=ax0.twinx()
    ax02.set_navigate(False)
    ax02.set_ylim(0,3.0)
    ax02.set_yticks([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    ax02.set_yticklabels(["0.0", "0.5", "1.0", "0.5", "1.0", "0.5", "1.0"])
    ax02.tick_params(labelsize=labelsize)
    if(stp==True):
        t0 = stp0[0]
        x0 = stp0[1]
        u0 = stp0[2]
        t1 = stp1[0]
        x1 = stp1[1]
        u1 = stp1[2]
        t2 = stp2[0]
        x2 = stp2[1]
        u2 = stp2[2]
        ax02.plot(t0, x0, 'r', linewidth = 2.5)
        ax02.plot(t0, u0, "blue", linewidth = 2.5)
        ax02.plot(t1, x1+[1.0 for i in t1], 'r', linewidth = 2.5)
        ax02.plot(t1, u1+[1.0 for i in t1], "blue", linewidth = 2.5)
        ax02.plot(t2, x2+[2.0 for i in t2], 'r', linewidth = 2.5)
        ax02.plot(t2, u2+[2.0 for i in t2], "blue", linewidth = 2.5)
    ax0.set_xlabel("Time [ms]", fontsize=labelsize)
    plt.text(1.065, 0.1, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.065, 0.23, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.065, 0.43, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.065, 0.56, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.065, 0.76, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.065, 0.9, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)

    plt.draw()
    plt.subplots_adjust(left=0.088, right=0.9, top=0.91, bottom=0.11)
    plt.savefig(simulation_params['data_path']+"fig4.png")


def evolution(t_start = 0.0, t_stop = 1.0, x_start = 1.0, u_start = 0.3, dt = 0.1):
    t = np.arange(t_start, t_stop, dt)
    x = 1.0 + (x_start - 1.0)*np.exp(-(t - t_start)/tauD)
    u = U + (u_start - U)*np.exp(-(t-t_start)/tauF)
    return(t,x,u)


def save_stp_data(npop):
    record_interval = simulation_params["recording_params"]["stp_record_interval"]
    sim_steps = np.arange(record_interval, simulation_params["t_sim"]+record_interval, record_interval)
    stp_pop_rec = simulation_params["recording_params"]["stp_pop_recorded"]
    fn = "stp_params_tot_"+str(npop)+".csv"
    lenght = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["stp_fraction_recorded"])
    xtot = np.zeros((lenght, len(sim_steps)))
    utot = np.zeros((lenght, len(sim_steps)))
    t_last_spike = np.zeros((lenght, len(sim_steps)+1))
    
    df = pd.read_csv(data_path + "stp_params/" + fn)

    for step, time in enumerate(sim_steps):
        dum = df[df["time"] == time]
        t_last_spike[:, step] = list(dum["t_last_spike"])
        xtot[:, step] = list(dum["x"])
        utot[:, step] = list(dum["u"])
    
    t_last_spike[:, step+1] = [simulation_params["t_sim"] for i in range(len(dum["t_last_spike"]))]
            
    np.savetxt(data_path + "stp_params/" + "std_x_"+str(npop)+".dat", xtot)
    np.savetxt(data_path + "stp_params/" + "std_u_"+str(npop)+".dat", utot)
    np.savetxt(data_path + "stp_params/" + "stp_t_last_spike_"+str(npop)+".dat", t_last_spike)


def get_stp_data_evol(xtot, utot, t_last):
    record_interval = simulation_params["recording_params"]["stp_record_interval"]
    sim_steps = np.arange(record_interval, simulation_params["t_sim"]+record_interval, record_interval)
    lenght = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["stp_fraction_recorded"])
    t = np.arange(0.0, simulation_params["t_sim"], 0.1)
    xnew = np.ones((lenght, len(t)))
    unew = np.ones((lenght, len(t)))
    for row in range(lenght):
        print("{}/{}".format(row, lenght), end = '\r')
        x = xtot[row,:]
        u = utot[row,:]
        t_last[row][0] = 0.0   
        diffx = np.diff(x)
        diffx_null = (diffx != 0)
        ids = []
        for i in range(len(diffx_null)):
            if diffx_null[i]:
                ids.append(i)

        ids.append(len(diffx_null))
        ids[0]=0
        times = []
        x1 = []
        u1 = []
        for i in ids:
            times.append(round(t_last[row][i],1))
            x1.append(x[i])
            u1.append(u[i])

        times.append(simulation_params["t_sim"])

        x2 = np.asarray([])
        u2 = np.asarray([])
        for timestep in range(len(times)-1):
            t_start = times[timestep]
            t_stop = times[timestep+1]
            x_start = x1[timestep]
            u_start = u1[timestep]
            tdum, xdum, udum = evolution(t_start, t_stop, x_start, u_start)
            x2 = np.concatenate([x2, xdum], axis=0)
            u2 = np.concatenate([u2, udum], axis=0)
        
        xnew[row,:] = x2[0:len(t)]
        unew[row,:] = u2[0:len(t)]

    return(xnew, unew)


def stp_data(npop):
    sim_steps = np.arange(0.0, simulation_params["t_sim"], 0.1)
    xtot = np.loadtxt(data_path + "stp_params/" + "std_x_"+str(npop)+".dat")
    utot = np.loadtxt(data_path + "stp_params/" + "std_u_"+str(npop)+".dat")
    t_last = np.loadtxt(data_path + "stp_params/" + "stp_t_last_spike_"+str(npop)+".dat")

    xnew, unew = get_stp_data_evol(xtot, utot, t_last)

    xavg = np.zeros(len(sim_steps))
    uavg = np.zeros(len(sim_steps))
    for i in range(len(sim_steps)):
        xavg[i] = np.mean(xnew[:,i])
        uavg[i] = np.mean(unew[:,i])

    return(sim_steps, xavg, uavg)




data_path = os.path.join(os.getcwd(), "data/")


### import network and simulation parameters

with open(data_path+'network_params.json', 'r') as f:
    network_params = json.load(f)

with open(data_path+'simulation_params.json', 'r') as f:
    simulation_params = json.load(f)


tauD = network_params["stp_params"]["tau_D"]
tauF = network_params["stp_params"]["tau_F"]
U = network_params["stp_params"]["U"]


# loading spike data
overlap = network_params["overlap"]
srs = load_spike_data(overlap)
sr0 = srs[0]
sr1 = srs[1]
sr2 = srs[2]
sr3 = srs[3]
sr4 = srs[4]

raster_plot()

figure = 2
stp = simulation_params["recording_params"]["stp_recording"]
panel = "B"


if figure == 4:
    if stp:
        save_stp_data(0)
        save_stp_data(1)
        save_stp_data(2)
        t0, x0, u0 = stp_data(0)
        t1, x1, u1 = stp_data(1)
        t2, x2, u2 = stp_data(2)
        figure4(stp, stp0 = [t0, x0, u0], stp1 = [t1, x1, u1], stp2 = [t2, x2, u2])
    else:
        print("Please load correct data.")
        sys.exit()


if figure == 3:
    if stp:
        save_stp_data(0)
        save_stp_data(1)
        t0, x0, u0 = stp_data(0)
        t1, x1, u1 = stp_data(1)
        figure3(stp, stp0 = [t0, x0, u0], stp1 = [t1, x1, u1], panel=panel)
    else:
        figure3(stp, panel=panel)


if figure == 2:
    if stp:
        save_stp_data(0)
        t, x, u = stp_data(0)
        figure2(stp = True, t=t, x=x, u=u, panel=panel)
    else:
        figure2(stp = False, panel=panel)


plt.show()


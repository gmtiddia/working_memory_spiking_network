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

def raster_plot(data_path):
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
    #plt.savefig(simulation_params['data_path']+"raster_plot_analysis.png")
    plt.savefig(data_path+"raster_plot_analysis.png")
    plt.draw()


def firing_rate(t_start, t_stop, sr):
    
    SE = sr
    dum = SE[:,1]
    dum = (dum > t_start) & (dum < t_stop )
    print("Start firing rate calculation at {} ms and stop at {} ms".format(t_start, t_stop))
    # neuron that emitted the spikes in that range
    senders = [i for (i, dum) in zip(SE[:,0], dum) if dum]
    N_neurons_recorded = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["fraction_pop_recorded"])
    ids = np.arange(np.min(senders), np.min(senders)+N_neurons_recorded)
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


def figure2(stp = False, t=[], x=[], u=[], xstd=[], ustd=[], panel="A", data_path = "data/"):

    labelsize=19
    titlesize=20


    #f, axs = plt.subplots(ncols=2, nrows=2, figsize=(15,8), gridspec_kw={'wspace': 0.4,'width_ratios': [3, 1]})

    f, axs = plt.subplot_mosaic([['upper_left', 'right'], ['lower_left', 'right']], figsize=(18,8), gridspec_kw={'wspace': 0.3,'width_ratios': [3, 1.8], 'height_ratios' : [3, 3]})

    fr0 = sr0[:,1]
    fr1 = sr1[:,1]
    fr2 = sr2[:,1]
    fr3 = sr3[:,1]
    fr4 = sr4[:,1]
    binwidth = 25.0 #ms
    frmax0 = np.max(np.abs(fr0))
    lim = (int(frmax0/binwidth) + 1) * binwidth
    bins = np.arange(0, lim + binwidth, binwidth)
    
    axs['upper_left'].set_ylabel("rate [Hz]", color="k", fontsize=labelsize)
    axs['upper_left'].tick_params(axis="x", labelbottom=False)
    axs['upper_left'].tick_params(labelsize=labelsize, axis ='y')
    h0 = np.histogram(fr0, bins=bins)[0:2]
    fr0 = (h0[0]/(binwidth/1000.0))/(network_params["N_exc"]*network_params["f"])
    axs['upper_left'].plot([(h0[1][i]+h0[1][i+1])/2.0 for i in range(len(h0[0]))], fr0, color = "limegreen", alpha=0.5)  
    h1 = np.histogram(fr1, bins=bins)[0:2]
    fr1 = h1[0]/(binwidth/1000.0)/(network_params["N_exc"]*network_params["f"])
    axs['upper_left'].plot([(h1[1][i]+h1[1][i+1])/2.0 for i in range(len(h1[0]))], fr1, color = "black", alpha=0.5)
    h2 = np.histogram(fr2, bins=bins)[0:2]
    fr2 = h2[0]/(binwidth/1000.0)/(network_params["N_exc"]*network_params["f"])
    axs['upper_left'].plot([(h2[1][i]+h2[1][i+1])/2.0 for i in range(len(h2[0]))], fr2, color = "blue", alpha=0.5)
    h3 = np.histogram(fr3, bins=bins)[0:2]
    fr3 = h3[0]/(binwidth/1000.0)/(network_params["N_exc"]*network_params["f"])
    axs['upper_left'].plot([(h3[1][i]+h3[1][i+1])/2.0 for i in range(len(h3[0]))], fr3, color = "red", alpha=0.5)
    h4 = np.histogram(fr4, bins=bins)[0:2]
    fr4 = h4[0]/(binwidth/1000.0)/(network_params["N_exc"]*network_params["f"])
    axs['upper_left'].plot([(h4[1][i]+h4[1][i+1])/2.0 for i in range(len(h4[0]))], fr4, color = "orange", alpha=0.5)


    # usual plot of fig 2

    if("item_loading" in network_params):
        for i in range(network_params["item_loading"]["nstim"]):
            if(i==0):
                axs['lower_left'].axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey', label="Item Loading")
            else:
                axs['lower_left'].axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey')
    if("seq_item_loading" in network_params):
            for i in range(network_params["seq_item_loading"]["nstim"]):
                if(i==0):
                    axs['lower_left'].axvspan(network_params["seq_item_loading"]["origin"][i], network_params["seq_item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey', label="Item Loading")
                else:
                    axs['lower_left'].axvspan(network_params["seq_item_loading"]["origin"][i], network_params["seq_item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey')
    if("nonspecific_readout_signals" in network_params):
        for i in range(network_params["nonspecific_readout_signals"]["nstim"]):
            if(i==0):
                axs['lower_left'].axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey', label="Readout signal")
            else:
                axs['lower_left'].axvspan(network_params["nonspecific_readout_signals"]["origin"][i], network_params["nonspecific_readout_signals"]["origin"][i]+network_params["stimulation_params"]["T_reac"], alpha=0.5, color='lightgrey')
    if("nonspecific_noise" in network_params):
        for i in range(network_params["nonspecific_noise"]["nstim"]):
            if(i==0):
                axs['lower_left'].axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise', label="Noise")
            else:
                axs['lower_left'].axvspan(network_params["nonspecific_noise"]["origin"][i], network_params["nonspecific_noise"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise')
    if("periodic_sequence" in network_params):
            for i in range(len(network_params["periodic_sequence"]["times"])):
                if(i==0):
                    axs['lower_left'].axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey', label="Periodic stimuli")
                else:
                    axs['lower_left'].axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey')
    
    #plt.title("Raster plot for a subset of Pop {} and Pop {} neurons".format(simulation_params["recording_params"]["pop_recorded"][0], simulation_params["recording_params"]["pop_recorded"][1]), fontsize=titlesize)
    axs['lower_left'].plot(sr0[:,1], sr0[:,0], '.', color = "limegreen", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][0]))
    axs['lower_left'].plot(sr1[:,1], sr1[:,0]-[network_params["N_exc"]*network_params["f"] for i in sr1[:,0]], '.', color = "k", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][1]))
    axs['lower_left'].set_ylabel("# cell", color="k", fontsize=labelsize)
    axs['lower_left'].set_xlabel("Time [ms]", fontsize=labelsize)
    axs['lower_left'].tick_params(labelsize=labelsize, pad=10, axis ='x')
    axs['lower_left'].tick_params(labelsize=labelsize, axis ='y')
    axs['lower_left'].set_yticks([0,network_params["N_exc"]*network_params["f"]])
    axs['lower_left'].set_ylim(0.0, network_params["N_exc"]*network_params["f"])
    x_min = 2000.0
    x_max = 6000.0
    axs['lower_left'].set_xlim(x_min, x_max)
    axs['upper_left'].set_xlim(x_min, x_max)
    axs['lower_left'].set_yticklabels(['0',str(int(network_params["N_exc"]*network_params["f"]))])
    axs['lower_left'].text(-0.095,2.3,panel, transform=axs['lower_left'].transAxes, weight="bold", fontsize=labelsize+3)
    if(stp==True):
        axs2=axs['lower_left'].twinx()
        axs2.set_navigate(False)
        axs2.plot(t, x, 'r', linewidth = 2.5, label="x")
        plt.fill_between(t, x-xstd, x+xstd, color="red", alpha = 0.25)
        axs2.plot(t, u, "b", linewidth = 2.5, label="u")
        plt.fill_between(t, u-ustd, u+ustd, color="blue", alpha = 0.25)
        #axs2.plot(t, np.asarray(x)*np.asarray(u), "purple", linewidth = 2.5, label="x*u")
        axs2.set_ylim(0,1.0)
    
        #axs2.set_ylabel("x, u", fontsize=labelsize)
        plt.text(1.085, 0.65, 'x', color='red', transform=axs2.transAxes, fontsize=labelsize+5)
        plt.text(1.085, 0.35, 'u', color='blue', transform=axs2.transAxes, fontsize=labelsize+5)

        axs2.tick_params(labelsize=labelsize)
        axs2.tick_params(axis ='y')


    # spontaneous rate
    t_start2 = simulation_params["recording_params"]["spike_recording_params"]["start"] + 450.0
    if("item_loading" in network_params):
        t_stop2 = network_params["item_loading"]["origin"][0]
    if("seq_item_loading" in network_params):
        t_stop2 = network_params["seq_item_loading"]["origin"][0]
    #t_stop2 = network_params["item_loading"]["origin"][0]
    # delay period
    t_start1 = t_stop2 + network_params["stimulation_params"]["T_cue"]
    if("nonspecific_readout_signals" in network_params):
        t_stop1 = network_params["nonspecific_readout_signals"]["origin"][0]
    elif("nonspecific_noise" in network_params):
        t_stop1 = network_params["nonspecific_noise"]["origin"][0]
    elif("nonspecific_readout_signals" in network_params and "nonspecific_noise" in network_params):
        t_stop1 = min(network_params["nonspecific_readout_signals"]["origin"][0], network_params["nonspecific_noise"]["origin"][0])
    else:
        t_stop1 = simulation_params["eta_end_origin"]

    # put arrows indicating spontaneous activity and delay periods
    axs['lower_left'].hlines(y=0.0, xmin=t_start1, xmax=t_stop1, color="orange", linewidth=7)
    axs['lower_left'].hlines(y=0.0, xmin=t_start2, xmax=t_stop2, color="skyblue", linewidth=7)
    
    occurrencies1 = firing_rate(t_start1, t_stop1, sr0)
    occurrencies2 = firing_rate(t_start2, t_stop2, sr0)

    print("Non-selective population")
    occurrencies_dum = firing_rate(t_start2, t_stop2, srs[-2])
    print("Inhibitory population")
    occurrencies_dum = firing_rate(t_start2, t_stop2, srs[-1])

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
    axs['right'].bar(bins[:-1], counts, width = bins[1] - bins[0], color="cornflowerblue", align="center", linewidth=0.2, edgecolor="w")
    axs['right'].set_xlabel("Firing rate difference [Hz]", fontsize=labelsize)
    axs['right'].set_ylabel("Fraction of cells", fontsize=labelsize)
    if(panel=="A"):
        axs['right'].set_xlim(-1,10)
        axs['right'].set_xticks([-5,0,5,10])
    else:
        axs['right'].set_xlim(-1,15)
        #axs['right'].set_xticks([0,5,10,15])
        axs['right'].set_xticks([-5,0,5,10])
    axs['right'].tick_params(labelsize=labelsize)


    plt.subplots_adjust(left=0.06, right=0.976, top=0.925, bottom=0.207)
    #plt.subplots_adjust(left=0.06, right=0.976, top=0.89, bottom=0.207)
    #plt.suptitle("multapses and autapses disabled", fontsize=labelsize)
    plt.savefig(data_path+"fig2{panel}.png".format(panel=panel))
    
    plt.draw()


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


def get_weights_distrib(npop):
    """
        Get synaptic weights of the tsodyks3_synapse connections having the neurons of npop as source.

        Parameters
            npop : int
                The id of the selective population
        Returns:
            total_weights : Pandas Series
                Collection of the synaptic weights from all the connections recorded
            within_pop_weights: Pandas Series
                Collection of the synaptic weights targeting neurons belonging
                to the same selective population
            outgoing_weights : Pandas Series
                Collection of the synaptic weights targeting neurons not belonging
                to the selective populations
    """

    # import the synaptic data recorded
    fn = "stp_pop_"+str(npop)+".csv"
    df = pd.read_csv(data_path + "stp_params/" + fn)
    total_weights = df["weight"]
    
    #select the weights with target inside the same population from the others
    min_source = df["source"].min()
    max_source = df["source"].max()
    # weights of the self connections
    within_pop_weights = df.loc[(df["target"] > min_source) & (df["target"] <= max_source), "weight"]
    # weights of the connections targeting neurons not belonging to the same population
    outgoing_weights = df.loc[(df["target"] < min_source) | (df["target"] > max_source), "weight"]

    return(total_weights, within_pop_weights, outgoing_weights)


def evolution(t_start = 0.0, t_stop = 1.0, x_start = 1.0, u_start = 0.3, dt = 0.1, tauD=1500.0, tauF=200.0):
    """
        Evolves the STP variables x and u.

        Parameters
            t_start : float
                Time at which we start the time evolution (in ms).
            t_start : float
                Time at which we stop the time evolution (in ms).
            x_start : float
                Value of x at t_start.
            u_start : float
                Value of u at t_start.
            dt : float
                Time step for evolution.
            tauD : float
                Time constant for depression (STD).
            tauF : float
                Time constant for facilitation (STF).
        Returns:
            t : list of floats
                List of spike times.
            x : list of floats
                List of x values.
            u : list of floats
                List of u values.
    """
    t = np.arange(t_start, t_stop, dt)
    t = np.asarray([round(float(i), 1) for i in t])
    x = 1.0 + (x_start - 1.0)*np.exp(-(t - t_start)/tauD)
    u = U + (u_start - U)*np.exp(-(t-t_start)/tauF)
    return(t,x,u)


def get_neuron_spiketimes(sr, nid):
    """
        Get spike times of a neuron belonging to a certain population.

        Parameters
            sr : array
                Array of spikes recorded from a population
            nid : int
                Neuron id
        Returns:
            spike_times : list of floats
                List of spike times
    """

    sr = sr.T
    df = pd.DataFrame({"id": list(map(int, sr[0])), "time": sr[1]})
    spike_times = df.loc[(df["id"] == nid), "time"]
    
    return(list(spike_times))
    

def get_stp_data_evol(sr, popid, dt, subset_targets=True, targets=1):
    """
        Get STP variables correctly evolved for all the simulation for each neuron connection.

        Parameters
            sr : array
                Array of spikes recorded from a population
            popid : int
                Population id
            dt: float
                Time step for STP data evolution
            subset_targets: bool
                Enables the computation of the variables only for a subset of connections per neuron
            targets: int
                If subset_targets is True, determines how many connections per neuron have to be considered
        Returns:
            xnew : list of floats
                List of values of x evolved for all the simulation obtained for all the neurons recorded and all its connections
            unew : list of floats
                List of values of u evolved for all the simulation obtained for all the neurons recorded and all its connections
    """

    neurons_recorded = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["stp_fraction_recorded"])
    # time array, starts at the time at which the spike recording starts
    time = np.arange(simulation_params["recording_params"]["spike_recording_params"]["start"], simulation_params["t_sim"], dt)
    time = [round(float(t), 1) for t in time]
    # arrays for stp data
    xnew = []
    unew = []
    # ID recorded neurons (i.e., source ID)
    nids = [i+1+popid*800 for i in range(neurons_recorded)]
    U = network_params["stp_params"]["U"]

    # prepare the array for putting the stp data
    df = pd.read_csv(data_path + "stp_params/stp_pop_" + str(popid) + ".csv")

    for n in nids:
        st = [simulation_params["recording_params"]["spike_recording_params"]["start"]] + get_neuron_spiketimes(sr, n)
        st.append(simulation_params["t_sim"])
        st = [round(float(t), 1) for t in st]
        # list (a value for each target neuron)
        x0 = df[df["source"]==n]["x"].tolist()
        u0 = df[df["source"]==n]["u"].tolist()
        tauF = df[df["source"]==n]["tau_F"].tolist()
        tauD = df[df["source"]==n]["tau_D"].tolist()

        # diminish the dataset size (useful to save RAM and to average the STP variables using the same amount of data per neuron)
        if(subset_targets==True):
            if(len(x0)>targets):
                x0 = x0[0:targets]
                u0 = u0[0:targets]
                tauF = tauF[0:targets]
                tauD = tauD[0:targets]
            else:
                pass

        # list to store the lists for x and u evolved
        xlist = []
        ulist = []
        tlist = []

        # get values of x and u for every synaptic contact
        for i in range(len(x0)):
            # first of all, append the values recorded
            x = [x0[i]]
            u = [u0[i]]
            t = [simulation_params["recording_params"]["spike_recording_params"]["start"]]
            # and then evolve according to the spike times of the source neuron
            for timestep in range(1,len(st)-1):
                t_start = round(float(st[timestep-1]+dt), 1)
                t_stop = round(float(st[timestep]), 1)
                x_start = x[-1]
                u_start = u[-1]
                dumt, dumx, dumu = evolution(t_start, t_stop, x_start, u_start, dt, tauD[i], tauF[i])
                x.extend(list(dumx))
                u.extend(list(dumu))
                t.extend(list(dumt))
                # a spike is emitted! Edit the values...
                u.append(u[-1] + U*(1.0 - u[-1]))
                x.append(x[-1] - u[-1]*x[-1])
                t.append(round(float(st[timestep]), 1))
            
            # last evolution, from the last spike to the end of the simulation
            dumt, dumx, dumu = evolution(st[-2], st[-1], x[-1], u[-1], dt, tauD[i], tauF[i])
            x.extend(list(dumx))
            u.extend(list(dumu))
            t.extend(list(dumt))

            # sometimes some duplicates may appear. The solution is to round the time values and
            # discard the duplicates, both in the time list and in the x and u ones.
            t = [round(i, 1) for i in t]
            duplicates = (np.diff(t)==0.0)
            # ids to remove
            ids = []
            for i in range(len(duplicates)):
                if duplicates[i]:
                    ids.append(i)
            
            for i in range(len(ids)):
                del t[ids[i]]
                del x[ids[i]]
                del u[ids[i]]
                
            if (len(x)>len(time)):
                xlist.append(x[1:])
                ulist.append(u[1:])
            else:
                xlist.append(x)
                ulist.append(u)

        xnew.append(xlist)
        unew.append(ulist)
        
    
    # empty everything
    xlist = []
    ulist = []
    df = {}

    return(time, xnew, unew)


def average_stp_data(sr, popid, dt, single_neuron=False, neuronid=0):
    """
        Get averaged STP variables for a neuron of a selective population.

        Parameters
            sr : array
                Array of spikes recorded from a population
            popid : int
                Population id
            dt: float
                Time step for STP data evolution
            neuron: bool
                Returns the STP variables averaged over the connections of a single neuron. If False, averages over the population.
            neuronid: int
                ID of the neuron to be taken as a reference. The value of STP variables will be averaged over its connections.
        Returns:
            t : list of floats
                Time axis, in ms.
            xavg : list of floats
                List of values of x averaged over the connections.
            uavg : list of floats
                List of values of u averaged over the connections.
            xstd : list of floats
                Standard deviation for the values of x in each timestep.
            ustd : list of floats
                Standard deviation for the values of u in each timestep.
    """

    t, xnew, unew = get_stp_data_evol(sr, popid, dt)

    neurons_recorded = int(network_params["N_exc"]*network_params["f"]*simulation_params["recording_params"]["stp_fraction_recorded"])

    if(single_neuron):
        # take a neuron as a reference and average over its connections
        xnew = np.asarray(xnew[neuronid])
        unew = np.asarray(unew[neuronid])

        xavg = np.mean(xnew, axis=0)
        uavg = np.mean(unew, axis=0)
        xstd = np.std(xnew, axis=0)
        ustd = np.std(unew, axis=0)

        return(t, xavg, uavg, xstd, ustd)
    
    else:
        xavg_sn = []
        uavg_sn = []
        # average over the connection of each neuron
        for n in range(neurons_recorded):
            xavg_sn.append(np.mean(xnew[n], axis=0))
            uavg_sn.append(np.mean(unew[n], axis=0))
        
        xavg_sn = np.asarray(xavg_sn)
        uavg_sn = np.asarray(uavg_sn)
        
        # average over the neurons
        xavg = np.mean(xavg_sn, axis=0)
        uavg = np.mean(uavg_sn, axis=0)
        xstd = np.std(xavg_sn, axis=0)
        ustd = np.std(uavg_sn, axis=0)

        return(t, xavg, uavg, xstd, ustd)
    
# n is the number of data folder (data0, data1, ...., data<n-1>)
# if n = 1 then there is only one data folder and its name is data
n = 1
for i in range(0, n):
    #data_path = "data" + str(i) + "/"

    data_path = "data" + "/"
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
    
    
    raster_plot(data_path)
    
    figure = 2
    stp = simulation_params["recording_params"]["stp_recording"]
    panel = "B"
    
    
    if figure == 4:
        if stp:
            t0, x0, u0, xstd0, ustd0  = average_stp_data(sr0, 0, 0.1, True, 0)
            t1, x1, u1, xstd1, ustd1  = average_stp_data(sr1, 1, 0.1, True, 0)
            t2, x2, u2, xstd2, ustd2  = average_stp_data(sr2, 2, 0.1, True, 0)
            figure4(stp, stp0 = [t0, x0, u0], stp1 = [t1, x1, u1], stp2 = [t2, x2, u2])
        else:
            print("Please load correct data.")
            sys.exit()
    
    
    if figure == 3:
        if stp:
            t0, x0, u0, xstd0, ustd0  = average_stp_data(sr0, 0, 0.1, True, 0)
            t1, x1, u1, xstd1, ustd1  = average_stp_data(sr1, 1, 0.1, True, 0)
            figure3(stp, stp0 = [t0, x0, u0], stp1 = [t1, x1, u1], panel=panel)
        else:
            figure3(stp, panel=panel)
    
    
    if figure == 2:
        if stp:
            t, xmean, umean, xstd, ustd  = average_stp_data(sr0, 0, 0.1, False, 5)
            figure2(stp = True, t=t, x=xmean, u=umean, xstd=xstd, ustd=ustd, panel=panel, data_path = data_path)
        else:
            figure2(stp = False, panel=panel, data_path = data_path)
    

    #total, within, outgoing = get_weights_distrib(0)

    #print("total:", total)
    #print("within:", within)
    #print("outgoing:", outgoing)
    
    #fig, ax = plt.subplots()
    #fig1, ax1 = plt.subplots()
    #fig2, ax2 = plt.subplots()
    #ax.hist(total, bins = 30)
    #ax1.hist(within, bins = 30)
    #ax2.hist(outgoing, bins = 30)
    
    plt.show()


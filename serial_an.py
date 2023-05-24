import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys
import pandas as pd
from scipy.signal import find_peaks


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
                        sr[r,0]=np.where(sorted_ids==idx)[0][0] + int(network_params["N_exc"]*network_params["f"])*i
            srs.append(sr)
    
    return(srs)


def firing_rate(t_start, t_stop):
    
    SE = sr0
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


def testPS(panel="A"):

    overlap = network_params["overlap"]
    if("item_loading" in network_params):
        targeted_sp = network_params["item_loading"]["pop_id"]
    elif("seq_item_loading" in network_params):
        targeted_sp = network_params["seq_item_loading"]["pop_id"]
    else:
        print("No item loading signal.")
        sys.exit()
    spike_times = load_spike_data(overlap)
    #print(spike_times)

    data = {"panel": panel, "amplitude": network_params["A_eta"], "frequence": network_params["fr_eta"], "targeted_pop": targeted_sp[0]}

    # get start and end of delay period
    if("item_loading" in network_params):
        origin = network_params["item_loading"]["origin"]
    if("seq_item_loading" in network_params):
        origin = network_params["seq_item_loading"]["origin"]
    start_delay_period = origin[0] + network_params["stimulation_params"]["T_cue"]
    if(panel=="A"):
        end_delay_period = network_params["nonspecific_readout_signals"]["origin"][0]
    else:
        end_delay_period = simulation_params["eta_end_origin"]

    print("Targeted selective population {}".format(targeted_sp))
    
    for sp in range(len(spike_times)):
        st = spike_times[sp]
        print("Selective population {}".format(sp))
        fr = st[:,1]
        frmax = np.max(np.abs(fr))
        binwidth = 25.0 #ms
        lim = (int(frmax/binwidth) + 1) * binwidth
        bins = np.arange(0, lim + binwidth, binwidth)
        h0 = np.histogram(fr, bins=bins)[0:2]
        fr = (h0[0]/(binwidth/1000.0))/(network_params["N_exc"]*network_params["f"])

        # find peaks
        thr = 20.0
        idxs = find_peaks(fr, height=thr)[0]
        peak_times = idxs*binwidth

        
        new_peak_times = peak_times[peak_times>start_delay_period]
    
        
        ps_before_ils = 0
        # first control: PS before the item loading signal
        if(len(new_peak_times)!=len(peak_times)):
            if(len(new_peak_times[new_peak_times<origin[0]])):
                print("\tThere is a PS before the item loading signal.")
                ps_before_ils += 1
            peak_times = new_peak_times
            del(new_peak_times)

        
        number_of_ps = len(peak_times)
        time_last_ps = peak_times[-1] if(number_of_ps>0) else np.nan
        # second control: number of PS
        if(panel=="B"):
            # number of PS
            print("\tThere are {} PS".format(len(peak_times)))
            rate_ps = 1000.0*len(peak_times)/(end_delay_period-start_delay_period)
            if(len(peak_times)>1.0):
                # time interval between PS
                PSinterval = np.diff(peak_times)
                av_interval = np.mean(PSinterval)
                std_interval = np.std(PSinterval)
                print("\tAverage interval between PS: {:.4} +/- {:.4}".format(av_interval, std_interval))
                print("\tThere are {:.2} PS per second of delay period".format(rate_ps))
            else:
                PSinterval = np.nan
                av_interval = np.nan
                std_interval = np.nan
            
            data["pop_"+str(sp)] = {"ps_before_item": ps_before_ils, "ps": number_of_ps, "time_of_last_ps": time_last_ps, "sim_time": simulation_params["t_sim"],
                                    "av_dt_PS": av_interval, "std_dt_PS": std_interval, "PS_per_second": rate_ps}
        if(panel=="A"):
            # number of PS
            if(len(peak_times)==1):
                print("\tThere is a PS, as it should.")
            else:
                print("\tThere are {} PS!".format(len(peak_times)))
            
            # check the position of the PS
            start_readout_signal = network_params["nonspecific_readout_signals"]["origin"][0]
            stop_readout_signal = start_readout_signal + network_params["stimulation_params"]["T_reac"]

            ps_before_ro = len(peak_times[peak_times<start_readout_signal])
            ps_after_ro = len(peak_times[peak_times>start_readout_signal])
            if(len(peak_times[peak_times<start_readout_signal])!=0):
                print("\tThere is at least one PS before the readout signal!")
            if(len(peak_times[peak_times>stop_readout_signal])!=0):
                print("\tThere is at least one PS after the readout signal!")

            peak_times = peak_times[peak_times<=stop_readout_signal]
            peak_times = peak_times[peak_times>=start_readout_signal]
            ps_during_ro = len(peak_times)
            print("\tThere is {} PS during the readout signal".format(len(peak_times)))

            data["pop_"+str(sp)] = {"ps_before_item": ps_before_ils, "ps": number_of_ps, "time_of_last_ps": time_last_ps, "sim_time": simulation_params["t_sim"],
                                    "ps_before_test": ps_before_ro, "ps_after_test": ps_after_ro, "ps_during_test": ps_during_ro}
        
        #print(data)

    return data


def figure2(stp = False, t=[], x=[], u=[], xstd=[], ustd=[], xs=[], us=[], panel="A"):

    labelsize=19
    titlesize=20


    #f, axs = plt.subplots(ncols=2, nrows=2, figsize=(15,8), gridspec_kw={'wspace': 0.4,'width_ratios': [3, 1]})

    f, axs = plt.subplot_mosaic([['upper_left', 'right'], ['lower_left', 'right']], figsize=(18,8), gridspec_kw={'wspace': 0.3,'width_ratios': [3, 1]})

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
    x_max = 7000.0
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
        axs2.set_ylim(0,1.0)
    
        #axs2.set_ylabel("x, u", fontsize=labelsize)
        plt.text(1.085, 0.65, 'x', color='red', transform=axs2.transAxes, fontsize=labelsize+5)
        plt.text(1.085, 0.35, 'u', color='blue', transform=axs2.transAxes, fontsize=labelsize+5)
    
        if(len(xs)!=0 and len(us)!=0):
            axs2.plot(t, xs, 'r--', linewidth = 2.0, alpha=0.85, label="x_sample")
            axs2.plot(t, us, "b--", linewidth = 2.0, alpha=0.85, label="u_sample")

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
    plt.savefig(simulation_params['data_path']+"fig2{panel}.png".format(panel=panel))
    
    plt.draw()


def figure3(stp=False, stp0= [], stp1 =[], panel="A"):
    labelsize=19
    titlesize=20
    f, ax0 = plt.subplots(1, 1, figsize=(15,6.))

    if("item_loading" in network_params):
        for i in range(network_params["item_loading"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey', label="Item Loading")
            else:
                ax0.axvspan(network_params["item_loading"]["origin"][i], network_params["item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey')
    if("seq_item_loading" in network_params):
        for i in range(network_params["seq_item_loading"]["nstim"]):
            if(i==0):
                ax0.axvspan(network_params["seq_item_loading"]["origin"][i], network_params["seq_item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0, 0.5, alpha=0.5, color='grey', label="Item Loading")
            else:
                ax0.axvspan(network_params["seq_item_loading"]["origin"][i], network_params["seq_item_loading"]["origin"][i]+network_params["stimulation_params"]["T_cue"], 0.5, 1.0, alpha=0.5, color='grey')
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
                    if(network_params["periodic_sequence"]["popid"][i]==0):
                        ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], 0, 1.0, alpha=0.5, color='lightgrey', label="Periodic stimuli")
                    else:
                        ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], 0.5, 1.0, alpha=0.5, color='lightgrey', label="Periodic stimuli")
                else:
                    if(network_params["periodic_sequence"]["popid"][i]==0):
                        ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], 0, 1.0, alpha=0.5, color='lightgrey')
                    else:
                        ax0.axvspan(network_params["periodic_sequence"]["times"][i], network_params["periodic_sequence"]["times"][i]+network_params["stimulation_params"]["T_period_reac"], 0.5, 1.0, alpha=0.5, color='lightgrey')

    dum = int(network_params["N_exc"] * (1.0 -network_params["f"]))
    ax0.plot(sr0[:,1], sr0[:,0], '.', color = "limegreen", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][0]))
    ax0.plot(sr1[:,1], sr1[:,0], '.', color = "k", label="Sel Pop {}".format(simulation_params["recording_params"]["pop_recorded"][1]))
    ax0.set_ylabel("# cell", color="k", fontsize=labelsize)
    ax0.set_xlim(2000.0, 10000.0)
    if network_params["overlap"]:
        ax0.set_xlim(2000.0, 8000.0)
    ax0.tick_params(labelsize=labelsize, pad=10, axis ='x')
    ax0.tick_params(labelsize=labelsize, axis ='y')
    #ax0.set_yticks([0,80,160])
    #ax0.set_yticklabels(['0','80', '160'])
    #ax0.set_ylim(0.0, 160.0)
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
        x0avg = stp0[1]
        u0avg = stp0[2]
        x0std = stp0[3]
        u0std = stp0[4]
        t1 = stp1[0]
        x1avg = stp1[1]
        u1avg = stp1[2]
        x1std = stp1[3]
        u1std = stp1[4]

        ax02.plot(t0, x0avg, 'r', linewidth = 2.5, label="x")
        plt.fill_between(t0, x0avg-x0std, x0avg+x0std, color="red", alpha = 0.25)
        ax02.plot(t0, u0avg, "b", linewidth = 2.5, label="u")
        plt.fill_between(t0, u0avg-u0std, u0avg+u0std, color="blue", alpha = 0.25)

        ax02.plot(t1, x1avg+[1.0 for i in t1], 'r', linewidth = 2.5, label="x")
        plt.fill_between(t1, x1avg-x1std+[1.0 for i in t1], x1avg+x1std+[1.0 for i in t1], color="red", alpha = 0.25)
        ax02.plot(t1, u1avg+[1.0 for i in t1], "b", linewidth = 2.5, label="u")
        plt.fill_between(t1, u1avg-u1std+[1.0 for i in t1], u1avg+u1std+[1.0 for i in t1], color="blue", alpha = 0.25)

        #ax02.plot(t1, x1+[1.0 for i in t1], 'r', linewidth = 2.5)
        #ax02.plot(t1, u1+[1.0 for i in t1], "blue", linewidth = 2.5)
    ax0.set_xlabel("Time [ms]", fontsize=labelsize)
    plt.text(1.085, 0.35, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.15, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.85, 'x', color='red', transform=ax02.transAxes, fontsize=labelsize+5)
    plt.text(1.085, 0.65, 'u', color='blue', transform=ax02.transAxes, fontsize=labelsize+5)

    plt.draw()
    plt.subplots_adjust(left=0.088, right=0.9, top=0.95, bottom=0.136)
    plt.savefig(simulation_params['data_path']+"fig3{panel}.png".format(panel=panel))


def get_stp_data_from_spikes(x_start, u_start, sr, npop, dt, t_start, t_stop):
    if(os.path.exists(data_path + "stp_params/" + "std_x_avg_" + str(npop) + ".dat")):
        print("Loading exixting data for {} population".format(npop))
        xavg = np.loadtxt(data_path + "stp_params/" + "std_x_avg_"+str(npop)+".dat")
        uavg = np.loadtxt(data_path + "stp_params/" + "std_u_avg_"+str(npop)+".dat")
        xstd = np.loadtxt(data_path + "stp_params/" + "std_x_std_"+str(npop)+".dat")
        ustd = np.loadtxt(data_path + "stp_params/" + "std_u_std_"+str(npop)+".dat")
        times = np.loadtxt(data_path + "stp_params/" + "stp_time_"+str(npop)+".dat")

        return(times, xavg, uavg, xstd, ustd)

    else:
        print("Getting data for {} population".format(npop))
        if(simulation_params['recording_params']["stp_recording"]==False and os.path.exists(simulation_params['data_path']+"stp_params")==False):
            os.mkdir(simulation_params['data_path']+"stp_params")
        spikes = [[0.0] for i in range(int(network_params["N_exc"]*network_params["f"]))]
        for s in sr:
            id = int(s[0])-1-int(network_params["N_exc"]*network_params["f"]*npop)
            # dt = 0.1
            time = round(s[1], 1)
            spikes[id].append(time)
        
        N = int(network_params["N_exc"]*network_params["f"])

        x = [[x_start] for i in range(N)]
        u = [[u_start] for i in range(N)]

        
        for n in range(N):
            print("{}/{}".format(n, N), end = '\r')
            # list of spiketimes of the neuron n
            spikelist = spikes[n]
            # start counting for the time
            times = [0.0]

            for t in range(1,len(spikelist)):
                # evolving from t0 to t1 without spikes
                #print("\nSpikes at {} and {} ms".format(spikelist[t-1], spikelist[t]))
                t0 = spikelist[t-1]+dt
                t1 = spikelist[t]
                #print("Computing time evolution from  {} to {} ms".format(t0, t1))
                #print("There should be {} points computed".format(int((t1 - t0)/dt)))
                if t==1:
                    x0 = x_start
                    u0 = u_start
                else:
                    x0 = x[n][-1]
                    u0 = u[n][-1]
                tdum, xdum, udum = evolution(t0, t1, x0, u0, dt = dt)
                #print("Computed from {} to {} ms".format(round(tdum[0], 1), round(tdum[-1], 1)))
                # adding the computed values to the lists
                times.extend(list(np.arange(t0, t1, dt)))
                x[n].extend(list(xdum))
                u[n].extend(list(udum))
                #print("Adding the variables spike-driven update")
                times.append(spikelist[t])
                # computing the spike-related change in x and u
                U = network_params["stp_params"]["U"]
                u[n].append(u[n][-1] + U*(1.0 - u[n][-1]))
                x[n].append(x[n][-1] - u[n][-1]*x[n][-1])
            #print("Computing time evolution from  {} to {} ms".format(t1, t_stop))
            tdum, xdum, udum = evolution(spikelist[-1]+dt, t_stop, x[n][-1], u[n][-1], dt = dt)
            x[n].extend(list(xdum))
            u[n].extend(list(udum))
            times.extend(list(np.arange(spikelist[-1]+dt, t_stop, dt)))
            # sometimes some duplicates may appear. The solution is to round the time values and
            # discard the duplicates, both in the time list and in the x and u ones.
            times = [round(i, 1) for i in times]
            duplicates = (np.diff(times)==0.0)
            # ids to remove
            ids = []
            for i in range(len(duplicates)):
                if duplicates[i]:
                    ids.append(i)
            for i in range(len(ids)):
                del times[ids[i]]
                del x[n][ids[i]]
                del u[n][ids[i]]
            # now the x and u are of the same lenght for all the neurons

        print("Averaging the STP variables")
        xavg = np.zeros(len(times))
        uavg = np.zeros(len(times))
        xstd = np.zeros(len(times))
        ustd = np.zeros(len(times))

        for i in range(len(times)):
            xavg[i] = np.mean([x[n][i] for n in range(N)])
            uavg[i] = np.mean([u[n][i] for n in range(N)])
            xstd[i] = np.std([x[n][i] for n in range(N)])
            ustd[i] = np.std([u[n][i] for n in range(N)])


        

        np.savetxt(data_path + "stp_params/" + "std_x_avg_"+str(npop)+".dat", xavg)
        np.savetxt(data_path + "stp_params/" + "std_u_avg_"+str(npop)+".dat", uavg)
        np.savetxt(data_path + "stp_params/" + "std_x_std_"+str(npop)+".dat", xstd)
        np.savetxt(data_path + "stp_params/" + "std_u_std_"+str(npop)+".dat", ustd)
        np.savetxt(data_path + "stp_params/" + "stp_time_"+str(npop)+".dat", times)

        return(times, xavg, uavg, xstd, ustd)


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


def stp_data(npop, sample):
    sim_steps = np.arange(0.0, simulation_params["t_sim"], 0.1)
    xtot = np.loadtxt(data_path + "stp_params/" + "std_x_"+str(npop)+".dat")
    utot = np.loadtxt(data_path + "stp_params/" + "std_u_"+str(npop)+".dat")
    t_last = np.loadtxt(data_path + "stp_params/" + "stp_t_last_spike_"+str(npop)+".dat")

    xnew, unew = get_stp_data_evol(xtot, utot, t_last)

    #plt.plot(sim_steps, xnew[0,:], "r--")
    #plt.plot(sim_steps, unew[0,:], "b--")
    #plt.draw()

    xavg = np.zeros(len(sim_steps))
    uavg = np.zeros(len(sim_steps))
    xstd = np.zeros(len(sim_steps))
    ustd = np.zeros(len(sim_steps))

    if(sample):
        xsam = np.zeros(len(sim_steps))
        usam = np.zeros(len(sim_steps))

        for i in range(len(sim_steps)):
            xavg[i] = np.mean(xnew[:,i])
            uavg[i] = np.mean(unew[:,i])
            xstd[i] = np.std(xnew[:,i])
            ustd[i] = np.std(unew[:,i])
            xsam[i] = xnew[10,i]
            usam[i] = unew[10,i]
        plt.figure()
        for j in range(2):
            plt.plot(sim_steps, unew[j,:])
        plt.draw()


        return(sim_steps, xavg, uavg, xstd, ustd, xsam, usam)
    
    else:
        for i in range(len(sim_steps)):
            xavg[i] = np.mean(xnew[:,i])
            uavg[i] = np.mean(unew[:,i])
            xstd[i] = np.std(xnew[:,i])
            ustd[i] = np.std(unew[:,i])
        return(sim_steps, xavg, uavg, xstd, ustd, [], [])


times=np.arange(200,775,25)
print(times)
for t in times:
    print("Time = {} ms".format(t))
    data_path = "data_26mV/data_2A_ds20_"+str(t)+"/"

    ### import network and simulation parameters
    panel = "A"
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

    figure = 2
    stp = simulation_params["recording_params"]["stp_recording"]


    dataPS = testPS(panel)

    with open(data_path + "PS_data.json", 'w') as fp:
        json.dump(dataPS, fp)

    get_stp = True
    plot = False
    
    if figure == 2:
        if(get_stp):
            t, x, u, xstd, ustd = get_stp_data_from_spikes(1.0, 0.19, sr0, 0, 0.1, 0.0, simulation_params["t_sim"])
            if plot:
                figure2(stp = True, t=t, x=x, u=u, xstd=xstd, ustd=ustd, panel=panel)
        else:
            if plot:
                figure2(stp = False, panel=panel)

    if figure == 3:
        if(get_stp):
            t0, x0, u0, xstd0, ustd0 = get_stp_data_from_spikes(1.0, 0.19, sr0, 0, 0.1, 0.0, simulation_params["t_sim"])
            t1, x1, u1, xstd1, ustd1 = get_stp_data_from_spikes(1.0, 0.19, sr1, 1, 0.1, 0.0, simulation_params["t_sim"])
            if plot:
                figure3(get_stp, stp0 = [t0, x0, u0, xstd0, ustd0], stp1 = [t1, x1, u1, xstd1, ustd1], panel=panel)
        else:
            if plot:
                figure3(get_stp, panel=panel)

    if plot:
        plt.show()


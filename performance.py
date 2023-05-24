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

def testPS(panel="A"):
    if(os.path.exists(data_path + "PS_data.json")):
        with open(data_path+'PS_data.json', 'r') as f:
            data = json.load(f)
        return(data)
    #a = 0
    #if(a>1):
    #    data = 0
    #    return(data)

    else:
        overlap = network_params["overlap"]
        targeted_sp = network_params["item_loading"]["pop_id"]
        spike_times = load_spike_data(overlap)
        #print(spike_times)

        data = {"panel": panel, "amplitude": network_params["A_eta"], "frequence": network_params["fr_eta"], "targeted_pop": targeted_sp[0]}

        # get start and end of delay period
        start_delay_period = network_params["item_loading"]["origin"][0] + network_params["stimulation_params"]["T_cue"]
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
            idxs = find_peaks(fr, threshold=thr)[0]
            peak_times = idxs*binwidth
            
            new_peak_times = peak_times[peak_times>start_delay_period]
        
            
            ps_before_ils = 0
            # first control: PS before the item loading signal
            if(len(new_peak_times)!=len(peak_times)):
                if(len(new_peak_times[new_peak_times<network_params["item_loading"]["origin"][0]])):
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
                    print("\tThere are {} PS!")
                
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

                data["pop_"+str(sp)] = {"ps_before_item": ps_before_ils, "ps": number_of_ps, "time_of_last_ps": peak_times[-1], "sim_time": self.simulation_params["t_sim"],
                                        "ps_before_test": ps_before_ro, "ps_after_test": ps_after_ro, "ps_during_test": ps_during_ro}
            
        with open(data_path + "PS_data.json", 'w') as fp:
            json.dump(data, fp)

        return data

def performance_evaluation(panel):
    print("Getting the data...")
    data = testPS(panel)

    #print(data)
    
    print("Performance evaluation")
    print("Survival time test...")
    targeted_pop = data["targeted_pop"]

    # survival time test
    avg_interval = data["pop_"+str(targeted_pop)]["av_dt_PS"]
    std_interval = data["pop_"+str(targeted_pop)]["std_dt_PS"]
    sim_time = data["pop_"+str(targeted_pop)]["sim_time"]
    surv_time = data["pop_"+str(targeted_pop)]["time_of_last_ps"]
    
    surv_time_th = sim_time - avg_interval - std_interval
    # if there is no PS in the last <Dt>+sigma t
    if(surv_time > surv_time_th):
        print("The memory information is correctly stored")
    else:
        print("The memory information is lost after {:.5}s in a {:.5}s simulation.".format(surv_time, sim_time))

    # PS before item loading
    print("Check for PS before item loading...")
    dum_PS = 0
    for i in range(network_params["p"]):
        dum_PS += data["pop_"+str(targeted_pop)]["ps_before_item"]
    
    print("There are in total {} PS before item loading".format(dum_PS))

    # PS from other populations than the targeted one
    print("Check for false positives (i.e. PS in non-targeted populations)...")
    FP = 0
    for i in range(network_params["p"]):
        if(i!=targeted_pop):
            FP += data["pop_"+str(i)]["ps"]

    print("There are {} false positives in {}s of delay period".format(FP, sim_time - network_params["item_loading"]["origin"][0] - network_params["stimulation_params"]["T_cue"]))

    





    return 0

#data_path = "data_test_noSTPrec/"
#data_path = "data_test_STPrec/"
#data_path = "data_test_2B_150/"
#data_path = "data_test_2B_100/"
#data_path = "data_2A_usual/"
#data_path = "data_2A_ac/"
#data_path = "data_2A_ac_prova/"
#data_path = "data_2A_ac_15Hz/"
#data_path = "data_2A_ac_20Hz/"
#data_path = "data_2A_ac_30Hz/"
#data_path = "data_2B/"
#data_path = "data_2C/"
#data_path = "data_test_2B_50/"

for i in [0, 2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30]:
    data_path = "data_2A_ac_" + str(i) + "Hz/"

    print("\nFrequency {}Hz".format(i))
    ### import network and simulation parameters

    with open(data_path+'network_params.json', 'r') as f:
        network_params = json.load(f)

    with open(data_path+'simulation_params.json', 'r') as f:
        simulation_params = json.load(f)


    panel = "B"

    performance_evaluation(panel)





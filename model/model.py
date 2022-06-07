"""
Working Memory Network Model
==============

Network class to instantiate and administer instances of the
working memory model by Mongillo et al. (2018).

"""

import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib import gridspec
import nest
import os
import shutil
import sys
import json
import pandas as pd
import time
from copy import deepcopy
from model.default_params import default_network_params, default_simulation_params
from model.default_params import update_params, check_params
from model.model_helpers import get_weight, noise_params


class WMModel:
    def __init__(self, network_spec, sim_spec):
        """
        Working Memory Model class.
        An instance of the model with the given parameters.

        Parameters
        ----------
        network_spec : dict
            Specify the network to be simulated. The parameters defined
            in the dictionary overwrite the default parameters defined in
            default_params.py.
        sim_spec : dict
            Specify simulation and recording parameters. The parameters defined
            in the dictionary overwrite the default parameters defined in
            default_params.py.
            
        """
        # dictionaries set up
        self.network_params = deepcopy(default_network_params)
        if isinstance(network_spec, dict):
            print("Initializing network with custom parameters.")
            check_params(network_spec, self.network_params)
            self.network_custom_params = network_spec
            update_params(self.network_params, self.network_custom_params)
            #print("Used parameters: ", self.network_params)
        else:
            raise TypeError("network_spec must be a dict.")
        
        self.simulation_params = deepcopy(default_simulation_params)
        if isinstance(sim_spec, dict):
            print("Initializing simulation with custom parameters.")
            check_params(sim_spec, self.simulation_params)
            self.simulation_custom_params = sim_spec
            update_params(self.simulation_params, self.simulation_custom_params)
            #print("Used parameters: ", self.simulation_params)
        else:
            raise TypeError("sim_spec must be a dict.")
        
        self.data_path = self.simulation_params["data_path"]        
        if os.path.isdir(self.simulation_params["data_path"]):
            if(self.simulation_params['overwrite_files']==False):
                print("Data directory already exists and cannot be overwritten.\nPlease remove the folder %s" % self.data_path)
                sys.exit()
            if(self.simulation_params['overwrite_files']==True):
                ow = input("Data directory {} will be overwritten. Press any key to continue.".format(self.data_path))
                shutil.rmtree(self.simulation_params['data_path'])
                os.mkdir(self.simulation_params['data_path'])
                if(self.simulation_params['recording_params']["stp_recording"]==True):
                    os.mkdir(self.simulation_params['data_path']+"stp_params")
        else:
            os.mkdir(self.simulation_params['data_path'])
            if(self.simulation_params['recording_params']["stp_recording"]==True):
                os.mkdir(self.simulation_params['data_path']+"stp_params")
            print('Data directory created.')
        print('Data will be written to %s' % self.data_path)
        
        self.c = self.network_params["c"]
        self.p = self.network_params["p"]
        self.f = self.network_params["f"]
        

    def print_params(self):
        print("Network parameters dict:", self.network_params)
        print("Simulation parameters dict:", self.simulation_params)


    def save_params(self):
        """
        Save network and simulation dicts in json files.

        """

        print("Writing dict params to file...", end = " ")
        with open(self.simulation_params['data_path'] + "network_params.json", 'w') as fp:
            json.dump(self.network_params, fp)
        with open(self.simulation_params['data_path'] + "simulation_params.json", 'w') as fp:
            json.dump(self.simulation_params, fp)
        
        print("Done")


    def save_spike_data(self):
        """
        Save spike data in files named 'spikedataX.dat' where X is the pop recorded id
        (i.e. the id of the excitatory selective sub-population)

        """

        if(self.simulation_params["recording_params"]["save_to_file"]):
            for i, sr in enumerate(self.spike_recorders):
                fn = "spikedata" + str(self.simulation_params["recording_params"]["pop_recorded"][i])+".dat"
                spikes = np.array([sr.get("events")["senders"], sr.get("events")["times"]])
                spikes = spikes.T
                np.savetxt(self.simulation_params['data_path'] + fn, spikes)


    def add_background_input(self, start=0.0, stop=1000.0, origin = 1000.0):
        """
        Add backround input to the network using the parameters previously given.

        Parameters
        ----------
        start : float
            Specify the stimulus start (in ms).
        stop : float
            Specify the stimulus stop (in ms).

        """

        background_input = {
            'start': start,
            'stop': stop
        }
        print("\n ##### NETWORK INPUTS #####\n")
        print("Background input added:\nStart [ms]: {}\nStop [ms]: {}\nmu_exc [mV]: {}\nmu_inh [mv]: {}".format(start, stop, self.network_params["mu_exc"], self.network_params["mu_inh"]))

        self.network_params.update({'background_input': background_input})


    def add_item_loading_signals(self, pop_id=[0], origin=[1000.0]):
        """
        Add item loading signal to the pop_id-th excitatory population using the parameters previously given.

        Parameters
        ----------
            pop_id : list of int
                The population to which the items are loaded
            origin : list of float
                The origin of the item loading stimulations (in ms)

        """

        if len(pop_id) != len(origin):
            raise ValueError("pop_id and origin must have the same dimension.")
        else:
            item_loading = {
                'nstim': len(pop_id) ,
                'pop_id': pop_id,
                'origin': origin
                }

            self.network_params.update({'item_loading': item_loading})
        
        print("\nItems loading:")
        for i in range(len(pop_id)):
            print("Item loaded to sub-population {} at {} ms.".format(pop_id[i], origin[i]))
        

    def add_nonspecific_readout_signal(self, origin = [2000.0]):
        """
        Add nonspecific readout signal to the whole excitatory population using the parameters previously given.

        Parameters
        ----------
            origin : list of float
                The origin of the nonspecific stimulations (in ms)

        """

        nonspecific_readout_signal = {
            'nstim' : len(origin),
            'origin' : origin
        }


        self.network_params.update({'nonspecific_readout_signals': nonspecific_readout_signal})
        
        print("\nNonspecific readout signals:")
        for i in range(len(origin)):
            print("Nonspecific readout signal added at {} ms.".format(origin[i]))


    def add_random_nonspecific_noise(self, origin = [1500.0], frac = 0.15):
        """
        Add random nonspecific noise signal to a fraction of the excitatory population using the parameters previously given.

        Parameters
            origin : list of float
                The origin of the item loading stimulations (in ms).
            frac : float
                Fraction of excitatory neurons simulated by the stimulus.

        """
        nonspecific_noise = {
            'nstim' : len(origin),
            'origin': origin,
            'frac' : frac
        }

        print("\nNonspecific noise signals:")
        for i in range(len(origin)):
            print("Nonspecific noise signal added at {} ms.\n".format(origin[i]))

        self.network_params.update({'nonspecific_noise': nonspecific_noise})

    
    def add_periodic_sequence(self, intervals = [[1000.0, 1500.0]]):
        """
        Add nonspecific signal-like periodic sequence to the excitatory population. 
        Similar to the nonspecific readout signal, it is shorter in time.

        Parameters
            times : list containing the beginning of each periodic stimuli
        """

        times = []
        for i in range(len(intervals)):
            t0 = intervals[i][0]
            t1 = intervals[i][1]
            nstim = int((t1-t0)/self.network_params["stimulation_params"]["period"]) + 1
            for n in range(nstim):
                times.append(t0+n*self.network_params["stimulation_params"]["period"])

        periodic_sequence = {
            'times': times
        }

        print("\nPeriodic sequences:")
        print("Periodic sequences added at {} ms.\n".format(times))

        self.network_params.update({'periodic_sequence': periodic_sequence})
    
    
    def prepare_nest(self):
        """
        Prepare NEST Kernel.

        """
        nest.ResetKernel()
        nest.SetKernelStatus({"print_time" : True,
                              "resolution": self.simulation_params["dt"],
                              "local_num_threads": self.simulation_params["threads"]})
    

    def create_populations(self):
        """
        Creates neuron populations.

        """
        print("Creating neuron populations...", end = ' ')

        # list of exc sub-populations
        self.exc_populations = []

        # whole exc neurons
        self.exc_population = nest.Create("iaf_psc_exp", self.network_params["N_exc"])
        nest.SetStatus(self.exc_population, {"tau_m": self.network_params["neur_params"]["tau"][0],
                                             "t_ref": self.network_params["neur_params"]["t_ref"][0],
                                             "V_th": self.network_params["neur_params"]["V_th"][0],
                                             "V_reset": self.network_params["neur_params"]["V_reset"][0],
                                             "E_L": self.network_params["neur_params"]["E_L"][0],
                                             "V_m": self.network_params["neur_params"]["V_m"][0]})
        
        #whole inh neurons
        self.inh_population = nest.Create("iaf_psc_exp", self.network_params["N_inh"])
        nest.SetStatus(self.inh_population, {"tau_m" : self.network_params["neur_params"]["tau"][1],
                                             "t_ref" : self.network_params["neur_params"]["t_ref"][1],
                                             "V_th" : self.network_params["neur_params"]["V_th"][1],
                                             "V_reset" : self.network_params["neur_params"]["V_reset"][1],
                                             "E_L" : self.network_params["neur_params"]["E_L"][1],
                                             "V_m" : self.network_params["neur_params"]["V_m"][1]})
        
        
        if(self.network_params["overlap"]):
            # subpopulations chosen randomly
            pop_index = np.arange(self.network_params["N_exc"])
            # here we collect all the id of neurons belonging to selective populations
            selective_pop_ids = []
            for i in range(self.p):
                #print("Getting selective population {}".format(i))
                pop_id_dum = pop_index
                ids = []
                for j in range(int(self.f*self.network_params["N_exc"])):
                    id = int(random.choice(pop_id_dum))
                    selective_pop_ids.append(id)
                    ids.append(id)
                    # delete the id to avoid repetition within the same selective population
                    pop_id_dum = np.delete(pop_id_dum, np.where(pop_id_dum==id))
                dum = self.exc_population[np.sort(ids)]
                self.exc_populations.append(dum)
            
            # collect the ids of neurons belonging to selective populaitons
            sel_ids = np.zeros((int(self.f*self.network_params["N_exc"]), self.p))
            #sel_ids = [selective_pop_ids[i*int(self.f*self.network_params["N_exc"]):(i+1)*int(self.f*self.network_params["N_exc"])] for i in range(self.p)]
            for i in range(self.p):
                sel_ids[:,i] = selective_pop_ids[i*int(self.f*self.network_params["N_exc"]):(i+1)*int(self.f*self.network_params["N_exc"])]
            # the ids not present in selective_pop_ids go to the non-selective population
            ids = list(set(selective_pop_ids))
            nonselec_ids = pop_index
            for i in ids:
                nonselec_ids = np.delete(nonselec_ids, np.where(nonselec_ids==i))
            dum = self.exc_population[np.sort(nonselec_ids)]
            self.exc_populations.append(dum)

            if(self.simulation_params["recording_params"]["save_to_file"]):
                np.savetxt(self.simulation_params['data_path'] + "selective_pop_ids.dat", sel_ids)
                    
        else:
            pop_index = 0
            for i in range(self.p):
                dum = self.exc_population[pop_index:pop_index+int(self.f*self.network_params["N_exc"])]
                pop_index += int(self.f*self.network_params["N_exc"])
                self.exc_populations.append(dum)
                
            self.exc_populations.append(self.exc_population[pop_index:self.network_params["N_exc"]])
        
        print("Done")
    

    def create_background_input(self):
        """
        Computes the non-specific background input for the network.

        Returns exc_bkg_input and inh_bkg_input, lists containing respectively:
        ----------
        exc_bkg_input
            ng_exc_E : Node
                excitatory noise for exc pop
        inh_bkg_input
            ng_exc_I : Node
                excitatory noise for inh pop

        """

        mu_exc = self.network_params["mu_exc"]
        mu_inh = self.network_params["mu_inh"]
        mu_exc_end = self.network_params["mu_exc_end"]
        sigma_exc = self.network_params["sigma_exc"]
        sigma_inh = self.network_params["sigma_inh"]
        start = self.network_params["background_input"]["start"]
        stop = self.network_params["background_input"]["stop"]

        mean_I_ext_exc, stdI_ext_exc = noise_params(mu_exc, sigma_exc, self.network_params["neur_params"]["tau"][0], dt=self.network_params["stimulation_params"]["dt_external_stim"])

        ng_exc_E = nest.Create("noise_generator")
        nest.SetStatus(ng_exc_E, {"mean" : mean_I_ext_exc,
                                  "std" : stdI_ext_exc,
                                  "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                  "start" : start,
                                  "stop" : stop})

        mean_I_ext_inh, stdI_ext_inh = noise_params(mu_inh, sigma_inh, self.network_params["neur_params"]["tau"][1], dt=self.network_params["stimulation_params"]["dt_external_stim"])

        ng_inh_I = nest.Create("noise_generator")
        nest.SetStatus(ng_inh_I, {"mean" : mean_I_ext_inh,
                                  "std" : stdI_ext_inh,
                                  "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                  "start" : start,
                                  "stop" : stop})

        #print("\nBKG to inh pop")
        #print("I EXC [pA]: {:.2f} +/- {:.2f}".format(mean_I_ext_exc, stdI_ext_exc))
        #print("I INH [pA]: {:.2f} +/- {:.2f}".format(-mean_I_ext_inh, stdI_ext_inh))

        mean_I_ext_exc_end, stdI_ext_exc_end = noise_params(mu_exc_end, 0.0, self.network_params["neur_params"]["tau"][1], dt=self.network_params["stimulation_params"]["dt_external_stim"])

        ng_offset = nest.Create("noise_generator")
        nest.SetStatus(ng_offset, {"mean" : mean_I_ext_exc_end,
                                  "std" : stdI_ext_exc_end,
                                  "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                  "origin" : self.simulation_params["mu_end_origin"]})


        self.exc_bkg_input = ng_exc_E
        self.inh_bkg_input = ng_inh_I
        self.exc_offset = ng_offset

        
    def create_item_loading_signals(self):
        """
        Computes item loading signals.

        Returns the list item_loading_signals contaning the item loading input currents.

        """

        self.item_loading_signals = []

        mu_exc = self.network_params["mu_exc"]
        sigma_exc = 0.0 #self.network_params["sigma_exc"] #0.0
        origin = self.network_params["item_loading"]["origin"]

        for item in range(self.network_params["item_loading"]["nstim"]):
            cue, std_cue = noise_params(mu_exc*(self.network_params["stimulation_params"]["A_cue"]-1.0), sigma_exc, self.network_params["neur_params"]["tau"][0], dt=self.network_params["stimulation_params"]["dt_external_stim"])
            I_cue = nest.Create("noise_generator")
            nest.SetStatus(I_cue, {"mean" : cue,
                                   "std" : std_cue,
                                   "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                   "origin" : origin[item],
                                   "start" : 0.0,
                                   "stop" : self.network_params["stimulation_params"]["T_cue"]})
            
            self.item_loading_signals.append(I_cue)

        
    def create_nonspecific_readout_signals(self):
        """
        Computes the signals injected into the exc populations to reactivate the selective population.

        Returns the list nonspecific_readout_signals contaning the nonspecific readout signal inputs.

        """

        self.nonspecific_readout_signals = []

        mu_exc = self.network_params["mu_exc"]
        sigma_exc = 0.0 #self.network_params["sigma_exc"] #0.0
        origin = self.network_params["nonspecific_readout_signals"]["origin"]

        # create the stimulus
        for i in range(self.network_params["nonspecific_readout_signals"]["nstim"]):
            cue, std_cue = noise_params(mu_exc*(self.network_params["stimulation_params"]["A_reac"]-1.0), sigma_exc, self.network_params["neur_params"]["tau"][0], dt=self.network_params["stimulation_params"]["dt_external_stim"])
            I_cue = nest.Create("noise_generator")
            nest.SetStatus(I_cue, {"mean" : cue,
                                   "std" : std_cue,
                                   "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                   "origin" : origin[i],
                                   "start" : 0.0,
                                   "stop" : self.network_params["stimulation_params"]["T_reac"]})

            self.nonspecific_readout_signals.append(I_cue)


    def create_random_nonspecific_noise(self):
        """
        Creation of the noisy input injected in a subset of the excitatory neurons

        Returns the list random_noise contaning the nonspecific noise signal injected into a fraction of the excitatory neurons.

        """

        self.random_noise = []

        mu_exc = self.network_params["mu_exc"]
        sigma_exc = 0.0 #self.network_params["sigma_exc"] #0.0
        origin = self.network_params["nonspecific_noise"]["origin"]

        for i in range(self.network_params["nonspecific_noise"]["nstim"]):
        # create the stimulus
            cue, std_cue = noise_params(mu_exc*(self.network_params["stimulation_params"]["A_cue"]-1.0), sigma_exc, self.network_params["neur_params"]["tau"][0], dt=self.network_params["stimulation_params"]["dt_external_stim"])
            I_noise = nest.Create("noise_generator")
            nest.SetStatus(I_noise, {"mean" : cue,
                                     "std" : std_cue,
                                     "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                     "origin" : origin[i],
                                     "start" : 0.0,
                                     "stop" : self.network_params["stimulation_params"]["T_cue"]})
            
            self.random_noise.append(I_noise)
    

    def create_periodic_sequence(self):
        """
        Creation of the periodic sequence of nonspecific readout signals.

        Returns the list periodic_sequence contaning the periodic signals to be injected into the network.

        """

        self.periodic_sequence = []

        mu_exc = self.network_params["mu_exc"]
        sigma_exc = 0.0 #self.network_params["sigma_exc"]
        times = self.network_params["periodic_sequence"]["times"]

        for i in range(len(times)):
        # create the stimulus
            cue, std_cue = noise_params(mu_exc*(self.network_params["stimulation_params"]["A_period_reac"]-1.0), sigma_exc, self.network_params["neur_params"]["tau"][0], dt=self.network_params["stimulation_params"]["dt_external_stim"])
            I_nspec_signal = nest.Create("noise_generator")
            nest.SetStatus(I_nspec_signal, {"mean" : cue,
                                    "std" : std_cue,
                                    "dt" : self.network_params["stimulation_params"]["dt_external_stim"],
                                    "origin" : times[i],
                                    "start" : 0.0,
                                    "stop" : self.network_params["stimulation_params"]["T_period_reac"]})
            
            self.periodic_sequence.append(I_nspec_signal)


    def create_external_inputs(self):
        """
        Creation of the whole external inputs using the previous functions.

        """

        print("Creating network external inputs...", end = ' ')
        self.create_background_input()
        self.create_item_loading_signals()
        if("nonspecific_readout_signals" in self.network_params):
            self.create_nonspecific_readout_signals()
        if("nonspecific_noise" in self.network_params):
            self.create_random_nonspecific_noise()
        if("periodic_sequence" in self.network_params):
            self.create_periodic_sequence()
        print("Done")

    
    def create_recording_devices(self):
        """
        Creation of the recording devices (i.e. spike recorders)

        """

        print("Creating network external inputs...", end = ' ')
        
        self.spike_recorders = []
        for sr in range(len(self.simulation_params["recording_params"]["pop_recorded"])):
            s = nest.Create("spike_recorder")
            nest.SetStatus(s, {"start" : self.simulation_params["recording_params"]["spike_recording_params"]["start"]})

            self.spike_recorders.append(s)

        print("Done")

    
    def connect_populations(self):
        """
        Creation of the connections between neuron populations.

        """

        #print option to be implemented
        more_print = False
        print("Connecting the neuron populations...", end = ' ')
        for i in range(self.p):
            if more_print:
                print("\nTarget: selective population ", i+1)
            # indegrees from the exc selective pops
            for j in range(self.p):
                if more_print:
                    print("\tSource: selective population ", j+1)
                con_dict = {'rule': 'fixed_indegree', 
                            'indegree': int(self.f*self.c*self.network_params["N_exc"])}
                if i==j:
                    syn_dict = {"synapse_model": "tsodyks3_synapse",
                                "weight": get_weight(self.network_params["syn_params"]["J_p"], self.network_params["neur_params"]["tau"][0]),
                                "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                                "tau_rec": self.network_params["stp_params"]["tau_D"],
                                "tau_fac": self.network_params["stp_params"]["tau_F"],
                                "U": self.network_params["stp_params"]["U"],
                                "u": self.network_params["stp_params"]["u0"],
                                "x": self.network_params["stp_params"]["x0"]}
                    nest.Connect(self.exc_populations[j], self.exc_populations[i], con_dict, syn_dict)
                else:
                    syn_dict = {"synapse_model": "tsodyks3_synapse",
                                "weight": get_weight(self.network_params["syn_params"]["J_b"], self.network_params["neur_params"]["tau"][0]),
                                "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                                "tau_rec": self.network_params["stp_params"]["tau_D"],
                                "tau_fac": self.network_params["stp_params"]["tau_F"],
                                "U": self.network_params["stp_params"]["U"],
                                "u": self.network_params["stp_params"]["u0"],
                                "x": self.network_params["stp_params"]["x0"]}
                    nest.Connect(self.exc_populations[j], self.exc_populations[i], con_dict, syn_dict)
            
            # indegrees from the other exc neurons
            if more_print:
                print("\tSource: non-selective exc pop")
            con_dict = {'rule': 'fixed_indegree', 'indegree': int((1.0-self.network_params["syn_params"]["gamma_0"])*self.c*(1.0-self.f*self.p)*self.network_params["N_exc"])}
            syn_dict = {"synapse_model": "tsodyks3_synapse",
                        "weight": get_weight(self.network_params["syn_params"]["J_b"], self.network_params["neur_params"]["tau"][0]),
                        "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                        "tau_rec": self.network_params["stp_params"]["tau_D"],
                        "tau_fac": self.network_params["stp_params"]["tau_F"],
                        "U": self.network_params["stp_params"]["U"],
                        "u": self.network_params["stp_params"]["u0"],
                        "x": self.network_params["stp_params"]["x0"]}
            nest.Connect(self.exc_populations[-1], self.exc_populations[i], con_dict, syn_dict)

            con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.network_params["syn_params"]["gamma_0"]*self.c*(1.0-self.f*self.p)*self.network_params["N_exc"])}
            syn_dict = {"synapse_model": "tsodyks3_synapse",
                        "weight": get_weight(self.network_params["syn_params"]["J_p"], self.network_params["neur_params"]["tau"][0]),
                        "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                        "tau_rec": self.network_params["stp_params"]["tau_D"],
                        "tau_fac": self.network_params["stp_params"]["tau_F"],
                        "U": self.network_params["stp_params"]["U"],
                        "u": self.network_params["stp_params"]["u0"],
                        "x": self.network_params["stp_params"]["x0"]}
            nest.Connect(self.exc_populations[-1], self.exc_populations[i], con_dict, syn_dict)

            # indegrees from the inh pop
            if more_print:
                print("\tSource: inh pop")
            con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.c*self.network_params["N_inh"])}
            syn_dict = {"synapse_model": "static_synapse",
                        "weight": get_weight(-self.network_params["syn_params"]["J_EI"], self.network_params["neur_params"]["tau"][1]),
                        "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1])}
            nest.Connect(self.inh_population, self.exc_populations[i], con_dict, syn_dict)

        # connections for the inhibitory population
        if more_print:
            print("\nTarget: inhibitory population")
        # indegrees from the populations
        for i in range(self.p):
            if more_print:
                print("\tSource: selective population ", i+1)
            con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.f*self.c*self.network_params["N_exc"])}
            syn_dict = {"synapse_model": "static_synapse",
                        "weight": get_weight(self.network_params["syn_params"]["J_IE"], self.network_params["neur_params"]["tau"][1]),
                        "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1])}    
            nest.Connect(self.exc_populations[i], self.inh_population, con_dict, syn_dict)

        # indegrees from the other exc neurons
        if more_print:
            print("\tSource: non-selective exc pop")
        con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.c*(1.0-self.f*self.p)*self.network_params["N_exc"])}
        syn_dict = {"synapse_model": "static_synapse",
                    "weight": get_weight(self.network_params["syn_params"]["J_IE"], self.network_params["neur_params"]["tau"][0]),
                    "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1])}  
        nest.Connect(self.exc_populations[-1], self.inh_population, con_dict, syn_dict)

        # indegrees from inh pop itself
        if more_print:
            print("\tSource: inh pop")
        con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.c*self.network_params["N_inh"])}
        syn_dict = {"synapse_model": "static_synapse",
                    "weight": get_weight(-self.network_params["syn_params"]["J_II"], self.network_params["neur_params"]["tau"][1]),
                    "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1])} 
        nest.Connect(self.inh_population, self.inh_population, con_dict, syn_dict)

        # connection for the non-specific exc population
        if more_print:
            print("\nTarget: non-specific excitatory population")
        # indegrees from the selective populations
        for i in range(self.p):
            if more_print:
                print("\tSource: selective population ", i+1)
            con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.f*self.c*self.network_params["N_exc"])}
            syn_dict = {"synapse_model": "tsodyks3_synapse",
                        "weight": get_weight(self.network_params["syn_params"]["J_b"], self.network_params["neur_params"]["tau"][0]),
                        "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                        "tau_rec": self.network_params["stp_params"]["tau_D"],
                        "tau_fac": self.network_params["stp_params"]["tau_F"],
                        "U": self.network_params["stp_params"]["U"],
                        "u": self.network_params["stp_params"]["u0"],
                        "x": self.network_params["stp_params"]["x0"]}
            nest.Connect(self.exc_populations[i], self.exc_populations[-1], con_dict, syn_dict)

        # indegrees from the rest of the exc pop
        if more_print:
            print("\tSource: non-selective exc pop")
        con_dict = {'rule': 'fixed_indegree', 'indegree': int((1.0-self.network_params["syn_params"]["gamma_0"])*self.c*(1.0-self.f*self.p)*self.network_params["N_exc"])}
        syn_dict = {"synapse_model": "tsodyks3_synapse",
                    "weight": get_weight(self.network_params["syn_params"]["J_b"], self.network_params["neur_params"]["tau"][0]),
                    "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                    "tau_rec": self.network_params["stp_params"]["tau_D"],
                    "tau_fac": self.network_params["stp_params"]["tau_F"],
                    "U": self.network_params["stp_params"]["U"],
                    "u": self.network_params["stp_params"]["u0"],
                    "x": self.network_params["stp_params"]["x0"]}
        nest.Connect(self.exc_populations[-1], self.exc_populations[-1], con_dict, syn_dict)

        con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.network_params["syn_params"]["gamma_0"]*self.c*(1.0-self.f*self.p)*self.network_params["N_exc"])}
        syn_dict = {"synapse_model": "tsodyks3_synapse",
                    "weight": get_weight(self.network_params["syn_params"]["J_p"], self.network_params["neur_params"]["tau"][0]),
                    "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1]),
                    "tau_rec": self.network_params["stp_params"]["tau_D"],
                    "tau_fac": self.network_params["stp_params"]["tau_F"],
                    "U": self.network_params["stp_params"]["U"],
                    "u": self.network_params["stp_params"]["u0"],
                    "x": self.network_params["stp_params"]["x0"]}
        nest.Connect(self.exc_populations[-1], self.exc_populations[-1], con_dict, syn_dict)

        # indegrees from the inh pop
        if more_print:
            print("\tSource: inh pop")
        con_dict = {'rule': 'fixed_indegree', 'indegree': int(self.c*self.network_params["N_inh"])}
        syn_dict = {"synapse_model": "static_synapse",
                    "weight": get_weight(-self.network_params["syn_params"]["J_EI"], self.network_params["neur_params"]["tau"][1]),
                    "delay": nest.random.uniform(min=self.network_params["syn_params"]["delay"][0], max=self.network_params["syn_params"]["delay"][1])}
        nest.Connect(self.inh_population, self.exc_populations[-1], con_dict, syn_dict)

        print("Done")
    
    
    def connect_external_inputs(self):
        """
        Creation of the connections between neurons and external inputs.

        """
        print("Connecting external inputs...", end = ' ')
        
        # background input connection
        nest.Connect(self.exc_bkg_input, self.exc_population, syn_spec={"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])})
        nest.Connect(self.inh_bkg_input, self.inh_population, syn_spec={"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])})
        # connect offset to diminish bkg exc input
        nest.Connect(self.exc_offset, self.exc_population, syn_spec={"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])})

        # item loading connection
        #self.item_loading_signals
        for i in range(self.network_params["item_loading"]["nstim"]):
            nest.Connect(self.item_loading_signals[i], self.exc_populations[self.network_params["item_loading"]["pop_id"][i]],
                         syn_spec={"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])})

        # nonspecific readout signals connection
        if("nonspecific_readout_signals" in self.network_params):
            for i in range(self.network_params["nonspecific_readout_signals"]["nstim"]):
                nest.Connect(self.nonspecific_readout_signals[i], self.exc_population, 
                            syn_spec={"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])})

        # random nonspecific noise
        if("nonspecific_noise" in self.network_params):
            con_dict = {'rule': 'fixed_total_number', 'N': int(self.network_params["nonspecific_noise"]["frac"]*self.network_params["N_exc"])}
            syn_dict = {"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])}
            for i in range(self.network_params["nonspecific_noise"]["nstim"]):
                nest.Connect(self.random_noise[i], self.exc_population, con_dict, syn_dict)
        
        if("periodic_sequence" in self.network_params):
            for i in range(len(self.network_params["periodic_sequence"]["times"])):
                nest.Connect(self.periodic_sequence[i], self.exc_population, 
                             syn_spec={"delay": nest.random.uniform(min=self.network_params["syn_params"]["delay_ext"][0], max=self.network_params["syn_params"]["delay_ext"][1])})


        print("Done")


    def connect_recording_devices(self):
        """
        Creation of the connections between neurons and recording devices.

        """
        print("Connecting recording devices...", end = ' ')
        #self.spike_recorders
        for i in range(len(self.spike_recorders)):
            pop_id = self.simulation_params["recording_params"]["pop_recorded"][i]
            N_neurons_recorded = int(self.network_params["N_exc"]*self.f*self.simulation_params["recording_params"]["fraction_pop_recorded"])
            #print(self.exc_populations[pop_id][0:N_neurons_recorded])
            nest.Connect(self.exc_populations[pop_id][0:N_neurons_recorded], self.spike_recorders[i])

        print("Done")
    
    
    def build_network(self):
        """
        Network build, in which neurons, external inputs and recording devices are created and connected.

        """
        self.prepare_nest()
        print("\n### NETWORK BUILD ###\n")
        t0 = time.time()
        print("Creating nodes...", end = " ")
        self.create_populations()
        self.create_external_inputs()
        self.create_recording_devices()
        t1 = time.time()
        print("Nodes created in {:.2} s.".format(t1-t0))
        print("Connecting nodes...")
        self.connect_populations()
        self.connect_external_inputs()
        self.connect_recording_devices()
        t2 = time.time()
        print("Nodes connected in {:.3} s.".format(t2-t1))
        print("Network built in {:.3} s.".format(t2-t0))


    def simulate_network(self):
        """
        Network simulation. If STP params are not recorded the network is simply simulated.
        Otherwise the simulation proceeds in steps in order to record STP params.

        """
        print("\n### NETWORK SIMULATION ###")

        if(self.simulation_params["recording_params"]["stp_recording"]==False):
            t0 = time.time()
            nest.Simulate(self.simulation_params["t_sim"])
            t1 = time.time()
            print("Network simulated in {} s.".format(t1-t0))
        else:
            nest.SetKernelStatus({"print_time" : False})
            t0 = 0.0
            t_rec = 0.0
            record_interval = self.simulation_params["recording_params"]["stp_record_interval"]
            self.sim_steps = np.arange(record_interval, self.simulation_params["t_sim"]+record_interval, record_interval)
            for s in range(len(self.sim_steps)):
                print("\nStep {}/{} ({} s / {} s)".format(s+1, len(self.sim_steps), self.sim_steps[s], self.sim_steps[-1]))
                dum_start = time.time()
                nest.Simulate(record_interval)
                t0 += time.time() - dum_start
                dum_start = time.time()
                self.record_std_params(dt = self.sim_steps[s])
                t_rec +=  time.time() - dum_start
            dum_start = time.time()
            self.merge_std_data()
            t_rec +=  time.time() - dum_start
            print("\nRecording of STP params in {} s.".format(t_rec))
            print("Network simulated in {} s.".format(t0))
            print("Overall simulation took {} s.".format(t0+t_rec))


    def record_std_params(self, dt = 0.0):
        """
        Recording function for the STP params. It is possible to record a fraction of the neuron population.
        Only a synapse per neuron is recorded since the STP parameters are the same for all the synapses of the neuron.

        Returns a csv file for every simulation step in the folder 'data_path/stp_params'
        """
        print("\nExtracting stp params...", end = ' ')
        start = time.time()
        dum = int(self.network_params["N_exc"]*self.f*self.simulation_params["recording_params"]["stp_fraction_recorded"])
        for npop in self.simulation_params["recording_params"]["stp_pop_recorded"]:
            neuronpop = self.exc_populations[npop][0:dum]
            x = []; u = []; target = []; source = []; t = []; t_lastspike =[]
            for i in range(dum):
                conn = nest.GetConnections(synapse_model="tsodyks3_synapse", source=neuronpop[i])[0]
                x.append(conn.get("x"))
                u.append(conn.get("u"))
                target.append(conn.get("target"))
                source.append(conn.get("source"))
                t.append(dt)
                t_lastspike.append(nest.GetStatus(neuronpop[i], "t_spike")[0])
            dataset = {"time": t, "source": source, "target": target, "x": x, "u": u, "t_last_spike": t_lastspike}
            data = pd.DataFrame(dataset)
            data.to_csv(self.simulation_params['data_path'] +"stp_params/"+ "stp_pop_"+str(npop)+"_"+str(int(dt))+".csv", index=False)
        
        stop = time.time()
        print("Done in {} s: ".format(stop-start))
    

    def merge_std_data(self):
        """
        Merges the STD csv files that are produced for every step into a single csv file per selective population recorded.
        Finally removes the old csv data.

        """
        for npop in self.simulation_params["recording_params"]["stp_pop_recorded"]:
            csvlist = [self.simulation_params['data_path'] +"stp_params/"+ "stp_pop_"+str(npop)+"_"+str(int(self.sim_steps[s]))+".csv" for s in range(len(self.sim_steps))]
            df = pd.concat(map(pd.read_csv, csvlist), ignore_index=True)
            df.to_csv(self.simulation_params['data_path'] +"stp_params/"+"stp_params_tot_"+str(npop)+".csv")
            [os.remove(oldcsv) for oldcsv in csvlist]
            

    def raster_plot(self):
        """
        Simple raster plot of the excitatory selective population.
        Also the external inputs are indicated by using vertical shading.

        """
        axfont=19
        title=20
        fig, ax = plt.subplots()
        plt.title("Raster plot", fontsize=title)
        colors = ["blue", "red", "green", "orange", "olive"]
        for i in range(len(self.spike_recorders)):
            sr = self.spike_recorders[i].get("events")
            ax.plot(sr["times"], sr["senders"], '.', color = colors[i%len(colors)], label="Selective population {}".format(self.simulation_params["recording_params"]["pop_recorded"][i]))
        ax.set_ylabel("# cell", fontsize=axfont)
        ax.set_xlabel("Time [ms]", fontsize=axfont)
        ax.tick_params(labelsize=axfont)
        for i in range(self.network_params["item_loading"]["nstim"]):
            if(i==0):
                ax.axvspan(self.network_params["item_loading"]["origin"][i], self.network_params["item_loading"]["origin"][i]+self.network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey', label="Item Loading")
            else:
                ax.axvspan(self.network_params["item_loading"]["origin"][i], self.network_params["item_loading"]["origin"][i]+self.network_params["stimulation_params"]["T_cue"], alpha=0.5, color='grey')
        if("nonspecific_readout_signals" in self.network_params):
            for i in range(self.network_params["nonspecific_readout_signals"]["nstim"]):
                if(i==0):
                    ax.axvspan(self.network_params["nonspecific_readout_signals"]["origin"][i], self.network_params["nonspecific_readout_signals"]["origin"][i]+self.network_params["stimulation_params"]["T_reac"], alpha=0.5, color='cornflowerblue', label="Readout signal")
                else:
                    ax.axvspan(self.network_params["nonspecific_readout_signals"]["origin"][i], self.network_params["nonspecific_readout_signals"]["origin"][i]+self.network_params["stimulation_params"]["T_reac"], alpha=0.5, color='cornflowerblue')
        if("nonspecific_noise" in self.network_params):
            for i in range(self.network_params["nonspecific_noise"]["nstim"]):
                if(i==0):
                    ax.axvspan(self.network_params["nonspecific_noise"]["origin"][i], self.network_params["nonspecific_noise"]["origin"][i]+self.network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise', label="Noise")
                else:
                    ax.axvspan(self.network_params["nonspecific_noise"]["origin"][i], self.network_params["nonspecific_noise"]["origin"][i]+self.network_params["stimulation_params"]["T_cue"], alpha=0.5, color='turquoise')
        if("periodic_sequence" in self.network_params):
            for i in range(len(self.network_params["periodic_sequence"]["times"])):
                if(i==0):
                    ax.axvspan(self.network_params["periodic_sequence"]["times"][i], self.network_params["periodic_sequence"]["times"][i]+self.network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey', label="Periodic stimuli")
                else:
                    ax.axvspan(self.network_params["periodic_sequence"]["times"][i], self.network_params["periodic_sequence"]["times"][i]+self.network_params["stimulation_params"]["T_period_reac"], alpha=0.5, color='lightgrey')


        lines, labels = ax.get_legend_handles_labels()
        ax.legend(lines, labels, fontsize=axfont, loc = 'upper right')
        fig.set_size_inches(32, 18)
        if(self.simulation_params["recording_params"]["save_to_file"]==True):
            plt.savefig(self.simulation_params['data_path'] + "raster_plot.png", format='png')
        plt.draw()
    



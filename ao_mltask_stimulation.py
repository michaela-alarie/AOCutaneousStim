#!/usr/bin/env python3

import ao_comm as ao
from ao_input_param import ao_input_param
from ao_data_stream import grab_block, grab_codes
from msvcrt import kbhit, getch
import numpy as np
import time
import os
import pickle as pkl
import scipy.signal as sps
import scipy.io as sio 

class ReadCodes:
    def __init__(self, stimop='randomtrackingpenstim'):
        self.stimop = stimop
        self.codes = self.read_codes()

    def read_codes(self):
        """
        test function used to grab behavioral codes from codes.txt files
        """
        cwd = os.getcwd()
        prjdir = os.path.join(cwd, 'codes', self.stimop)
        if os.path.isdir(prjdir):
            cdir = os.path.join(prjdir, 'codes.txt')
        else:
            print('*** Stimulation option does not have codes file! ***')
            return

        cfile = open(cdir, 'r')
        cdict = {}
        for x in cfile:
            line = x.split('\t')
            if line[0] == 'Code':
                continue
            cdict[line[-1][:-1]] = int(line[0])

        self.cdict=cdict
        return self.cdict

def ao_trial_stream_stim(code_input, behav_input, side, stim_ch, ret_ch, ntrial, train_freq, number_of_pulses):

    # load behavioral codes
    codes = ReadCodes().codes
    # print(codes)

    # determine acquisition parameters for each data type
    code_param = ao_input_param(code_input, side)
    behav_param = ao_input_param(behav_input, side)

    # connect to omega
    ao.connect_start(side)

    # find channel id for stim channel
    #stim_ch = ao.channel_id(stim_ch, len(stim_ch))
    #ret_ch = ao.channel_id(ret_ch, len(ret_ch))
    
    # make buffer channels on the neuroOmega
    for ch in code_param['ch_id']:
        ao.buffer_set(ch)
    for ch in behav_param['ch_id']:
        ao.buffer_set(ch)

    # clear the buffer(s)
    ao.buffer_clear()

    # specify how much data we want to save for codes ... (not saving for offline analysis)
    code_sec = 5
    code_size = round(code_param['samp_rate'] * code_sec)

    # ... behavioral data (RTPDM typically has a ~20 second trial)
    behav_sec = 35
    behav_size = round(behav_param['samp_rate'] * behav_sec)

    for tr in range(ntrial):
        # reset trial data
        xtr = {
            'code_param': code_param,
            'behav_param': behav_param,
        }


        code_data = np.zeros(code_size)
        behav_data = np.zeros((behav_param['n_ch'], behav_size))
        ttarget_on = None
        ttarget_off = None

        # wait for initial 'trial start' (9) behavioral code
        wait = True
        print('waiting for trial {:02d}/{:02d} to start'.format(tr+1, ntrial))

        while wait:
            try:
                code_data = grab_codes(code_param, code_data)
            except:
                print('error with data pull')

            if codes['TrialStart'] in code_data:
                t0 = time.time()
                print('trial start')
                ao.stim_set_and_start(10031, 0, -1.2, 0.5, 0, 1.2, 0.5, train_freq, (number_of_pulses/train_freq)-0.1*(number_of_pulses/train_freq), 10030)
                wait = False
    return

if __name__ == '__main__':
    # listening to behavioral sync codes
    code_input = 'behav'

    # saving cursor and target behavioral data
    behav_input = 'cursor+target'

    # which omega
    side = 'l'

    # Task Information 
    ntrial= 400;

    # Stimulation Information
    stim_ch = 'ECOG LF 1 / 16' 
    ret_ch ='ECOG LF 1 / 15'
    train_freq=80 # the frequency between the pulses (for example 100Hz)
    number_of_pulses=30 # number of pulses in every train 

    ao_trial_stream_stim(code_input, behav_input, side, stim_ch, ret_ch, ntrial, train_freq, number_of_pulses)

import ao_comm as ao
import ao_stim_param
from msvcrt import kbhit, getch
import numpy as np
import time

def ao_MakeConnection(side, iter=100, delay=1):
    print('\n---ao_time_test.py---\n')

    # connect to omegas
    ao.connect_start(side)
    
def ao_stim(side,number_of_bursts, number_of_pulses, stim_amplitudes, train_freq, burst_freq, stim_ch, ret_ch, pw):
    """
    function used to test sending a stimulation train (more dynamic stimulation parameters)
    """
    print('\n---ao_stim_test.py---\n')
    stimop = 'stim'
    ao.stim_stop(stim_ch)
    for k in range(len(pw)):
        print(train_freq)
        print(pw[k])
        duration = (number_of_pulses/train_freq)-0.1*(number_of_pulses/train_freq)
        for x in range(len(stim_amplitudes)):
            print(stim_amplitudes[x])
            waveform_settings = {
                'stim': {
                    'first_phase_amp_mA': -stim_amplitudes[x],
                    'second_phase_amp_mA': stim_amplitudes[x],
                    'freq_hz': train_freq,
                    'duration_sec': duration,
                    'stim_ch': stim_ch,
                    'return_ch': ret_ch,
                    'first_phase_width_ms': pw[k],
                    'first_phase_delay_ms': 0,
                    'second_phase_delay_ms': 0,
                    'second_phase_width_ms': pw[k],
                    },
                }
            param = waveform_settings[stimop]
            
            ao.stim_set(
			param['first_phase_amp_mA'],
			param['first_phase_width_ms'],
			param['second_phase_amp_mA'],
			param['second_phase_width_ms'],
			param['freq_hz'],
			param['duration_sec'],
			param['return_ch'],
			param['stim_ch'],
			param['first_phase_delay_ms'],
			param['second_phase_delay_ms'],
			)

            while True:
                key = ord(getch())
                if key == 13: #enter key
                    ao.stim_set(
						param['first_phase_amp_mA'],
						param['first_phase_width_ms'],
						param['second_phase_amp_mA'],
						param['second_phase_width_ms'],
						param['freq_hz'],
						param['duration_sec'],
						param['return_ch'],
						param['stim_ch'],
						param['first_phase_delay_ms'],
						param['second_phase_delay_ms'],
						)
                        
                    for y in range(number_of_bursts):
                        ao.stim_start(param['stim_ch'])
                        time.sleep((1/burst_freq));
                        
                elif key == 27: # ESC
                    print('\n# Stopping all stimulation ...')
                    # stops stimulating on all channels, to be safe
                    ao.stim_stop(-1)
                    break

if __name__ == '__main__':
    # connect to omega
    side = 'l'
    ao_MakeConnection(side)

    #stim param
    numpulses=160 # number of pulses in every train 
    burst_freq=0.25; # burst frequency between the trains (for example 10Hz)
    numbursts=3; # total number of bursts
    stim_amp=[0.5, 0.7, 1.0, 0.001, 1.1, 0.7, 0.001, 1.0, 1.1, 0.001, 1.3, 1.5] #np.arange(0.5, 1.6, 0.2);
    pw=np.arange(0.5, 0.55, 0.1);
    train_freq=80; # the frequency between the pulses (for example 100Hz)
    ao_stim(side, numbursts, numpulses, stim_amp, train_freq, burst_freq, 10031, 10030,pw)
    #ao_stim(side, numbursts, numpulses, stim_amp, train_freq, burst_freq, 10030, 10031,pw)
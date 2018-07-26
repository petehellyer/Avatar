import numpy as np
from scipy.signal import butter, lfilter


def get_distance_wall(simulation):

    # Transform Unity coordinates and rescale it.
    psx = (simulation['posx'] - 1000) / 7
    psz = (simulation['posz'] - 1000) / 7

    # Calculate the minimum distance to all 4 walls and save it
    mindist = np.zeros(simulation['posx'].shape[1])
    aa = abs(  1 - psx)
    bb = abs(- 1 - psx)
    cc = abs(  1 - psz)
    dd = abs(- 1 - psz)
    for t in range(simulation['posx'].shape[1]):
        mindist[t] = min(aa[0, t], bb[0, t], cc[0, t], dd[0, t])
    return mindist

def exclude_input_nodes(simulation):
    # exclude input and ouput nodes
    input_output_nodes = [20, 20 + 33, 9, 9 + 33, 21, 21 + 33, 22, 22 + 33]
    bool_m = np.ones(66, dtype=bool)
    bool_m[input_output_nodes] = False

    # discard input nodes for all parmeters
    simulation['ws'] = simulation['ws'][:, bool_m]
    simulation['hs'] = simulation['hs'][:, bool_m]
    simulation['xs'] = simulation['xs'][:, bool_m]
    return simulation

def discard_warm_up_time(simulation):
    # chop initial time points necessary for the statibilisation of the model
    simulation['ws'] = simulation['ws'][5000:, :, 0]
    simulation['hs'] = simulation['hs'][5000:, :, 0]
    simulation['xs'] = simulation['xs'][5000:, :]

    # Note: The behavioural measures simulation['posx'] and simulation[posz']
    # remains the same as they already start from 5000
    return simulation

def low_pass_filter(cutoff, fs, order, data):
    # demean data
    x = data - np.mean(data)

    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

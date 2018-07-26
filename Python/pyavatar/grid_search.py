#!/usr/bin/env python

#SBATCH -p short

import os
import pickle
from argparse import ArgumentParser
import numpy as np
import scipy.io
from scipy.stats.stats import pearsonr
import pdb


from utilities import get_distance_wall, exclude_input_nodes, \
    discard_warm_up_time, low_pass_filter

def run_behavioural_analysis(simulation_file, behaviour):

    tmp_results = {}
    # Define settings for the low pass filter
    # Note: The sampling rate and cut-off frequency were predetermined using
    # other experiments
    fs = 300 # Hz
    cutoff = 0.6 # Hz
    order = 2
    # load simulation
    simulation = scipy.io.loadmat(simulation_file)
    # Clean the simulation by discarding the input nodes and removing the
    # initial time points
    simulation = discard_warm_up_time(simulation)
    simulation = exclude_input_nodes(simulation)

    # Get mean activity over the nodes
    tmp_results['mean_activity_over_time'] = np.mean(simulation['xs'], axis=1)

    if behaviour:
        # get distance from the wall
        min_dist = get_distance_wall(simulation)
         # filter the distance from the wall so that it is less noisy
        min_dist = low_pass_filter(cutoff, fs, order, min_dist)
        # save filtered distance from the wall
        tmp_results['distance_wall'] = min_dist
        # Calculate the mean ws for each time point
        mean_ws = np.mean(simulation['ws'], axis=1)
        tmp_results['mean_ws_over_time'] = mean_ws
        # find correlation between the mean ws over all nodes and the
        # distance from the wall
        tmp_results['correlation_ws_mean_nodes'] = pearsonr(mean_ws, min_dist)[0]

        # Get the correlation between each node and the distance from the
        # wall separatly
        tmp_results['correlation_ws_single_nodes'] = np.zeros(58)
        for n in range(58):
            tmp_results['correlation_ws_single_nodes'][n] = \
            pearsonr(simulation['ws'][:, n], min_dist)[0]
        tmp_results['correlation_ws_single_nodes_mean'] = \
        np.mean(tmp_results['correlation_ws_single_nodes'])

    return tmp_results

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Run Grid Search pararelly'
    )
    parser.add_argument(
        '--alpha',
        dest='alpha',
        type=float,
        help='Alpha for the current iteration'
    )
    parser.add_argument(
        '--target1',
        dest='target1',
        type=float,
        help='Lower bound for the target'
    )
    parser.add_argument(
        '--target2',
        dest='target2',
        type=float,
        help='Upper bound for the target'
    )
    parser.add_argument(
        '--step_target',
        dest='step_target',
        type=float,
        help='Steps of the target'
    )
    parser.add_argument(
        '--spath',
        dest='simulation_path',
        type=str,
        help='simulation path'
        )
    parser.add_argument(
        '--dpath',
        dest='dynamic_path',
        type=str,
        help='Dynamic analysis path'
    )
    parser.add_argument(
        '--behaviour',
        dest='behaviour',
        action='store_true',
        help='Pass this flag if the simulation includes behaviour'
    )
    parser.add_argument(
        '--analysis_type',
        dest='analysis_type',
        type=str,
        help='Type of analysis to be conducted'
    )

    args = parser.parse_args()

    # Check if dynamic_analysis folder exists, otherwise create it (simulation
    # path already exists)
    if not os.path.exists(args.dynamic_path):
        os.makedirs(args.dynamic_path)

    results = {}
    if args.analysis_type == 'ddw_ws_corr':
        # noise_range = range(1,2011,10)
        noise_range = np.arange(0, 1, .02)

        for noise in noise_range:
            results[noise] = {}
            simulation_file = os.path.join(args.simulation_path,
                    'noise_%.2f.mat' %noise)
            results[noise] = run_behavioural_analysis(simulation_file, args.behaviour)

        # dump the results
        with open(os.path.join(args.dynamic_path, 'behaviour_analysis.pickle'),
                'wb') as fh:
            pickle.dump(results, fh)

    elif args.analysis_type == 'gridsearch':
        for target_i in np.arange(args.target1, args.target2, args.step_target):
            # format target correctly
            target = '%.02f' %target_i
            results[target] = {}
            # load the simulation for current alpha and target
            simulation_file = os.path.join(args.simulation_path, '%d_%.05f_%.02f.mat' %(1,
                args.alpha, target_i))
            results[target] = run_behavioural_analysis(simulation_file,
                    args.behaviour)

        # dump the results
        with open(os.path.join(args.dynamic_path, 'gridsearch_%.05f.pickle'
            %(args.alpha)), 'wb') as fh:
            pickle.dump(results, fh)

    elif args.analysis_type == 'dmn_permutation':
        # get array of nodes and exclude the input nodes
        all_nodes = range(33)
        input_nodes = [20, 21, 23]
        nodes = np.delete(all_nodes, input_nodes)
        for node1 in nodes:
            results[node1] = {}
            for node2 in nodes:
                if node1 == node2:
                    continue
                simulation_file = os.path.join(args.simulation_path,
                        'simulation_%d_%d.mat' %(node1, node2))
                results[node1][node2] = run_behavioural_analysis(simulation_file,
                        args.behaviour)

            #dump results
            with open(os.path.join(args.dynamic_path,
                'dynamic_analysis_dmn_permutation.pickle'), 'wb') as fh:
                pickle.dump(results, fh)


#!/usr/bin/env python

import os
import pickle
import subprocess
import numpy as np
from argparse import ArgumentParser
import logging
import matplotlib
# allow generation of images without user interface
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pdb
from tvb.simulator.common import get_logger


def get_save_paths(behaviour, analysis_type, noise, homeostasis):

    if not behaviour:
        if analysis_type == 'g_bifurcation':
            log_simulation_path = os.path.join(os.path.dirname(os.getcwd()), 'logs',
                    'simulation', 'without_behaviour', 'g_bifurcation', 'noise_%.02e'
                    %noise)
            simulation_path = os.path.join(os.path.dirname(os.getcwd()), 'Output',
                    'simulation', 'without_behaviour', 'g_bifurcation', 'noise_%.02e'
                    %noise)
            log_dynamic_analysis_path = os.path.join(os.path.dirname(os.getcwd()),
                    'logs', 'dynamic_analysis', 'g_bifurcation', 'without_behaviour',
                    'noise_%.02e' %noise)
            dynamic_analysis_path = os.path.join(os.path.dirname(os.getcwd()),
                    'Output', 'dynamic_analysis', 'g_bifurcation',
                    'without_behaviour', 'noise_%.02e' %noise)
        elif analysis_type == 'gridsearch':
            log_simulation_path = os.path.join(os.path.dirname(os.getcwd()),
                    'logs', 'simulation', 'without_behaviour', 'noise_%.02e' %noise)
            simulation_path = os.path.join(os.path.dirname(os.getcwd()), 'Output',
                    'simulation', 'without_behaviour', 'gridsearch')
            log_dynamic_analysis_path = os.path.join(os.path.dirname(os.getcwd()),
                    'logs', 'dynamic_analysis', 'without_behaviour', 'noise_%.02e'
                    %noise)
            dynamic_analysis_path = os.path.join(os.path.dirname(os.getcwd()),
                    'Output', 'dynamic_analysis', 'without_behaviour', 'noise_%.02e'
                    %noise)

    else:
            log_simulation_path = os.path.join(os.path.dirname(os.getcwd()),
                    'logs', 'simulation', 'with_behaviour', homeostasis,
                    analysis_type)
            simulation_path = os.path.join(os.path.dirname(os.getcwd()),
                    'Output', 'simulation', 'with_behaviour', homeostasis,
                    analysis_type)
            log_dynamic_analysis_path = os.path.join(os.path.dirname(os.getcwd()),
                    'logs', 'dynamic_analysis', 'with_behaviour',
                    homeostasis, analysis_type)
            dynamic_analysis_path = os.path.join(os.path.dirname(os.getcwd()),
                    'Output', 'dynamic_analysis', 'with_behaviour',
                    homeostasis, analysis_type)


    # Check if paths exists, otherwise create it
    if not os.path.exists(log_dynamic_analysis_path):
        os.makedirs(log_dynamic_analysis_path)
    if not os.path.exists(log_simulation_path):
        os.makedirs(log_simulation_path)
    if not os.path.exists(dynamic_analysis_path):
        os.makedirs(dynamic_analysis_path)

    return simulation_path, dynamic_analysis_path, log_simulation_path, log_dynamic_analysis_path

############################################################################
# Argument parsing
############################################################################
parser = ArgumentParser(
    description='Analysis of the rww model.'
)
# Analysis type
parser.add_argument(
    '-bg',
    action='store_true', dest='bifurcation_g',
    help='Run simulation of the model. The function will iterate over different \
    Gs but keep alpha and target fixed.'
)
parser.add_argument(
    '-sbg',
    action='store_true', dest='selected_bifurcation_g',
    help='Run simulation of the model. The function will iterate over different \
    Gs but keep alpha and target fixed.'
)
parser.add_argument(
    '--behaviour',
    action='store_true', dest='behaviour',
    help='Specify if the current model includes or not behaviour.'
)
parser.add_argument(
    '--homeostasis',
    action='store_true', dest='homeostasis',
    help='Specify if the current model includes or not homeostasis.'
)
parser.add_argument(
    '-gg',
    action='store_true', dest='gridsearch2',
    help='Calculate bifurcation plot for target activation value'
)
parser.add_argument(
    '--step_alpha',
    dest='step_alpha',
    type=float,
    help='Step size for parameter iteration'
)
parser.add_argument(
    '--step_target',
    dest='step_target',
    type=float,
    help='Step size for parameter iteration'
)
parser.add_argument(
    '--grids_alpha',
    dest='gridsearch_alpha',
    nargs='+',
    type=float,
    help='Pass list of values to be used as lower and max value on gridsearch'
)
parser.add_argument(
    '--grids_target',
    dest='gridsearch_target',
    nargs='+',
    type=float,
    help='Pass list of values to be used as lower and max value on gridsearch'
)
parser.add_argument(
    '--analysis_type',
    dest='analysis_type',
    help='Type of dynamic analysis'
)
parser.add_argument(
    '--testn',
    dest='testn',
    type=int,
    help='Test number',
)
parser.add_argument(
    '--noise',
    dest='noise',
    type=float,
    help='Noise of the computational model',
)

args = parser.parse_args()

############################################################################
# Analysis
############################################################################
if args.gridsearch2:
    print('Running Grid search 2:')

    if args.homeostasis:
        homeostasis = 'with_homeostasis'
    else:
        homeostasis = 'without_homeostasis'

    # get folder where to save the logs and the grid search output
    simulation_path, dynamic_analysis_path, _, log_dynamic_analysis_path = \
    get_save_paths(args.behaviour, args.analysis_type, args.noise, homeostasis)

    if args.analysis_type == 'ddw_ws_corr':
        print('Running ddw_ws_corr analysis:')
        # Note: this step assumes that the simulation has already been run. In
        # this analysis the steps were:
        DMN_error = os.path.join(log_dynamic_analysis_path, 'with_DMN',
                'error_%j')
        no_DMN_error = os.path.join(log_dynamic_analysis_path, 'without_DMN',
                'error_%j')
        DMN_output = os.path.join(log_dynamic_analysis_path, 'with_DMN',
                'output_%j')
        no_DMN_output = os.path.join(log_dynamic_analysis_path, 'without_DMN',
                'output_%j')
        # check if those folders exist, otherwise create them
        if not os.path.exists(os.path.dirname(DMN_error)):
            os.makedirs(os.path.dirname(DMN_error))
        if not os.path.exists(os.path.dirname(no_DMN_error)):
            os.makedirs(os.path.dirname(no_DMN_error))


        DMN_simulation_path = os.path.join(simulation_path, 'with_DMN')
        no_DMN_simulation_path = os.path.join(simulation_path, 'without_DMN')
        DMN_dynamic_analysis_path = os.path.join(dynamic_analysis_path,
                'with_DMN')
        no_DMN_dynamic_analysis_path = os.path.join(dynamic_analysis_path,
                'without_DMN')
        print('Output paths are:')
        print('    with DMN: %s' %DMN_dynamic_analysis_path)
        print('    without DMN: %s:' %no_DMN_dynamic_analysis_path)

        cmd_DMN = 'sbatch -p short --output={0} --error={1} --mem 5G grid_search.py \
                --spath {2} --dpath {3} --behaviour --analysis_type {4}'.format(
                        DMN_output, DMN_error,
                        DMN_simulation_path, DMN_dynamic_analysis_path, 'ddw_ws_corr')
        cmd_no_DMN = 'sbatch -p short --output={0} --error={1} --mem 5G grid_search.py \
                --spath {2} --dpath {3} --behaviour --analysis_type {4}'.format(
                        no_DMN_output, no_DMN_error,
                        no_DMN_simulation_path, no_DMN_dynamic_analysis_path, 'ddw_ws_corr')
        subprocess.call(cmd_DMN, shell=True)
        subprocess.call(cmd_no_DMN, shell=True)

    elif args.analysis_type == 'gridsearch':
        # calculate the dynamic measure of interest
        # Note: To improve the I/O every job calculates the gridsearch for all targets. This avoid the cluster from having I/O
        # difficulties
        error = os.path.join(log_dynamic_analysis_path, 'error_%j')
        output = os.path.join(log_dynamic_analysis_path,'output_%j')
        # If we are running gridsearch on the simulation generated for the bifurcation plot:
        simulation_path = os.path.join(simulation_path, 'testn_%d' %args.testn)
        dynamic_analysis_path = os.path.join(dynamic_analysis_path,
                 'testn_%d' %args.testn, 'gridsearch2')

        for alpha_i in np.arange(args.gridsearch_alpha[0], args.gridsearch_alpha[1],
                args.step_alpha):
            if args.behaviour:
                cmd = 'sbatch --output={0} --error={1} --mem 5G grid_search.py \
                        --alpha {2} --target1 {3} --target2 {4} --step_target {5} \
                        --spath {6} --dpath {7} --behaviour --analysis_type {8} '.format(
                                output, error,
                                alpha_i, args.gridsearch_target[0],
                                args.gridsearch_target[1], args.step_target,
                                simulation_path, dynamic_analysis_path,
                                'gridsearch')
            else:
                cmd = 'sbatch --output={0} --error={1} --mem 5G grid_search.py \
                        --alpha {2} --target1 {3} --target2 {4} --step_target {5} \
                        --spath {6} --dpath {7} --analysis_type {8}'.format(output, error,
                                alpha_i, args.gridsearch_target[0],
                                args.gridsearch_target[1], args.step_target,
                                simulation_path, dynamic_analysis_path,
                                'gridsearch')
            subprocess.call(cmd, shell=True)

    elif args.analysis_type == 'dmn_permutation':
        error = os.path.join(log_dynamic_analysis_path, 'error_%j')
        output = os.path.join(log_dynamic_analysis_path, 'output_%j')
        # If we are running gridsearch on the simulation generated for the bifurcation plot:

        if args.behaviour:
            cmd = 'sbatch --output={0} --error={1} --mem 5G grid_search.py \
                    --spath {2} --dpath {3} --behaviour --analysis_type {4} '.format(
                            output, error,
                            simulation_path, dynamic_analysis_path,
                            'dmn_permutation')
            subprocess.call(cmd, shell=True)


if args.bifurcation_g:
    target = .20
    g_min = 0
    g_max = .5
    g_step = .01
    testn = 0

    for alpha_i in np.arange(args.gridsearch_alpha[0], args.gridsearch_alpha[1], args.step_alpha):

        log_path = os.path.join(os.path.dirname(os.getcwd()), 'logs',
                'dynamic_analysis', 'without_behaviour',
                'g_bifurcation', 'noise_%.2e' %args.noise, 'testn_%d' %testn)
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        error = os.path.join(log_path, 'error_%j')
        output = os.path.join(log_path, 'output_%j')

        cmd = 'sbatch --output={0} --error={1} --mem 5G pca_analysis.py --alpha {2} --target {3} --testn {4} --gmin {5} --gmax {6} --gstep {7} --noise {8}'.format(
                output, error, alpha_i, target, testn, g_min, g_max, g_step, args.noise)
        subprocess.call(cmd, shell=True)
        testn += 1

if args.selected_bifurcation_g:
    target = .20
    g_min = 0
    g_max = .5
    g_step = .002
    testn = 98
    # According to previous analysis fix alpha to 0
    alpha_i = 0

    log_path = os.path.join(os.path.dirname(os.getcwd()), 'logs',
            'dynamic_analysis', 'without_behaviour',
            'g_bifurcation', 'noise_%.2e' %args.noise, 'testn_%d' %testn)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    error = os.path.join(log_path, 'error_%j')
    output = os.path.join(log_path, 'output_%j')

    cmd = 'sbatch --output={0} --error={1} --mem 5G pca_analysis.py --alpha {2} --target {3} --testn {4} --gmin {5} --gmax {6} --gstep {7} --noise {8}'.format(
            output, error, alpha_i, target, testn, g_min, g_max, g_step, args.noise)
    subprocess.call(cmd, shell=True)

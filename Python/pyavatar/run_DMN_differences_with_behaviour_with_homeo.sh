#!/usr/bin/env bash

# stop when there is an error
set -e

source activate tvb-env
output_with_DMN_path=../Output/simulation/with_behaviour/with_homeostasis/ddw_ws_corr/with_DMN
output_without_DMN_path=../Output/simulation/with_behaviour/with_homeostasis/ddw_ws_corr/without_DMN
logs_with_DMN_path=../logs/simulation/with_behaviour/with_homeostasis/ddw_ws_corr/with_DMN
logs_without_DMN_path=../logs/simulation/with_behaviour/with_homeostasis/ddw_ws_corr/without_DMN

mkdir -p ${output_with_DMN_path}
mkdir -p ${output_without_DMN_path}
mkdir -p ${logs_with_DMN_path}
mkdir -p ${logs_without_DMN_path}

# define parameters that will not change
export AVATAR_G=0.27
export AVATAR_NOUNITY='False'
export AVATAR_TARGET=.25
export AVATAR_ALPHA=.00022


for i in $(seq 0 .02 1);
do
    export AVATAR_INITIAL_COND=${i}
    # Settings for the analysis with DMN
    export AVATAR_DMN='True'
    export AVATAR_SAVENAME=${output_with_DMN_path}'/noise_'${i}'.mat'
    sbatch -p verylong \
                       --output=${logs_with_DMN_path}'/out-'${i} \
                       --error=${logs_with_DMN_path}'/error-'${i} \
                       --mem 5G server.py -behaviour -homeostasis

    # Settings for the analysis without DMN
    export AVATAR_DMN='False'
    export AVATAR_SAVENAME=${output_without_DMN_path}'/noise_'${i}'.mat'
    sbatch -p verylong \
                       --output=${logs_without_DMN_path}'/out-'${i} \
                       --error=${logs_without_DMN_path}'/error-'${i} \
                       --mem 5G server.py -behaviour -homeostasis
done


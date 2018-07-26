#!/usr/bin/env bash
# Fix target and search over alpha to find a good variation of w.
# stop when there is an error
set -e

source activate tvb-env

# General model settings
export AVATAR_NOUNITY='False' # with behaviour
export AVATAR_DMN='False'
export AVATAR_TARGET=0.25
export AVATAR_G=0.27

behaviour='with_behaviour'
max_alpha=.0002
step_alpha=.000005
testn=18

# if folder does not exists create them
mkdir -p ../logs/simulation/${behaviour}/w_search/testn_${testn}
mkdir -p ../Output/simulation/${behaviour}/w_search/testn_${testn}

for j in $(seq 0 ${step_alpha} ${max_alpha});
do
    export AVATAR_ALPHA=`bc <<< 'scale=3; '${j}`
    export AVATAR_SAVENAME='../Output/simulation/'${behaviour}'/w_search/testn_'${testn}'/alpha_'${j}'.mat'
    echo ${AVATAR_SAVENAME}
    sbatch -p verylong \
    --output='../logs/simulation/'${behaviour}'/w_search/testn_'${testn}'/out_'${j} \
    --error='../logs/simulation/'${behaviour}'/w_search/testn_'${testn}'/error_'${j} \
    --mem 5G server.py -homeostasis -behaviour
done


#!/usr/bin/env bash

# stop when there is an error
set -e
alpha=0
noise=(0.00001)

target=0.20
export AVATAR_TARGET=`bc <<< 'scale=3; '${target}`

min_g=.15
max_g=.35
step_g=.006

source activate tvb-env

for i in "${noise[@]}"
do
    testn=90
    export AVATAR_NOISE=`bc <<< 'scale=3; '${i}`
    # if folder does not exists create them
    mkdir -p ../logs/simulation/without_behaviour/g_bifurcation/noise_${i}/testn_${testn}
    mkdir -p ../Output/simulation/without_behaviour/g_bifurcation/noise_${i}/testn_${testn}
    export AVATAR_ALPHA=`bc <<< 'scale=3; '${alpha}`
    for k in $(seq ${min_g} ${step_g} ${max_g});
    do
        # run simulation for different G
        export AVATAR_G=`bc <<< 'scale=3; '${k}`
        export AVATAR_SAVENAME='../Output/simulation/without_behaviour/g_bifurcation/noise_'${i}'/testn_'${testn}'/'${alpha}'_'${target}'_'${k}'.mat'
        echo ${AVATAR_SAVENAME}
        sbatch -p short \
        --output='../logs/simulation/without_behaviour/g_bifurcation/noise_'${i}'/testn_'${testn}'/out_'${alpha}'_'${target}'_'${k} \
        --error='../logs/simulation/without_behaviour/g_bifurcation/noise_'${i}'/testn_'${testn}'/error_'${alpha}'_'${target}'_'${k} \
        --mem 5G server.py
    done
    ((testn+=1))
done

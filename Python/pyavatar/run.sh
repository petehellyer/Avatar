#!/usr/bin/env bash

# stop when there is an error
set -e
step_alpha=.00001
max_alpha=.0003
step_target=.05
max_target=.8
testn=20
behaviour='with_behaviour'

# Lunch headleass Unity application if the analysis include behaviour
if [ $behaviour == 'with_behaviour' ]
then
    export AVATAR_NOUNITY='False'
else
    export AVATAR_NOUNITY='True'
fi

# According to the bifurcation plot set the values for G
export AVATAR_G=0.27
source activate tvb-env
# if folder does not exists create them
mkdir -p ../logs/simulation/${behaviour}/gridsearch/testn_${testn}
mkdir -p ../Output/simulation/${behaviour}/gridsearch/testn_${testn}
for k in $(seq 0 ${step_target} ${max_target});
do
    for j in $(seq 0 ${step_alpha} ${max_alpha});
    do
        for i in {1..1};
        do

            # run simulation for different targets and alphas
            export AVATAR_TARGET=`bc <<< 'scale=3; '${k}`
            export AVATAR_ALPHA=`bc <<< 'scale=3; '${j}`
            export AVATAR_SAVENAME='../Output/simulation/'${behaviour}'/gridsearch/testn_'${testn}'/'${i}'_'${j}'_'${k}'.mat'
            echo ${AVATAR_SAVENAME}
            sbatch -p verylong \
            --output='../logs/simulation/'${behaviour}'/gridsearch/testn_'${testn}'/out_'${i}'_'${j}'_'${k} \
            --error='../logs/simulation/'${behaviour}'/gridsearch/testn_'${testn}'/error_'${i}'_'${j}'_'${k} \
            --mem 5G server.py -homeostasis -behaviour
        done
    done
done

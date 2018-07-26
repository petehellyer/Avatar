#!/usr/bin/env bash

# stop when there is an error
set -e

source activate tvb-env
output_DMN_path=../Output/simulation/with_behaviour/with_homeostasis/dmn_permutation
logs_DMN_path=../logs/simulation/with_behaviour/with_homeostasis/dmn_permutation

mkdir -p ${output_DMN_path}
mkdir -p ${logs_DMN_path}

# define parameters that will not change
export AVATAR_G=0.27
export AVATAR_NOUNITY='False'
export AVATAR_TARGET=.25
export AVATAR_ALPHA=.00022
export AVATAR_DMN='True'

# List of nodes
nodes=($(seq 0 1 32))
# delete TP nodes
delete=(20 21 23)
for del in ${delete[@]};
    do unset "nodes[$del]";
    done
echo "${nodes[@]}"

# iterate over all possible combinations of node and generate the simulation
for n1 in ${nodes[@]}; do
    for n2 in ${nodes[@]}; do
        # ignore the cases where n1 == n2. As one node can only receive one
        # stimulus
        if [ $n1 -eq $n2 ]; then
            continue
        fi
        # pass the new combination to your bash script
        export AVATAR_DMN_VISUAL=${n1}
        export AVATAR_TP_VISUAL=${n2}
        export AVATAR_SAVENAME=${output_DMN_path}'/simulation_'${n1}'_'${n2}'.mat'
        sbatch -p verylong \
                           --output=${logs_DMN_path}'/out-'${n1}'_'${n2} \
                           --error=${logs_DMN_path}'/error-'${n1}'_'${n2} \
                           --mem 5G server.py -behaviour -homeostasis
    done
done


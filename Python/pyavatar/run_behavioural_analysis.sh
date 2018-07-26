#!/usr/bin/env bash

# stop when there is an error
set -e
source activate tvb-env

behaviour='with_behaviour'
logfolder=../logs/simulation/${behaviour}/behavioural_analysis/3e-06-noDMN
outputfolder=../Output/simulation/${behaviour}/behavioural_analysis/3e-06-noDMN
mkdir -p ${logfolder}
mkdir -p ${outputfolder}
##############################################################################
##                 No behaviour and no Homeostasis
##############################################################################
# Create log and output folder
testn=00

export AVATAR_NOUNITY='False'
export AVATAR_G=0.27
export AVATAR_DMN='True'
export AVATAR_SAVENAME=${outputfolder}'/results_testn_'${testn}.mat

sbatch -p short \
       --output=${logfolder}'/output_testn_'${testn} \
       --error=${logfolder}'/error_testn_'${testn} \
       --mem 5G server.py

testn=01

export AVATAR_NOUNITY='False'
export AVATAR_G=0.27
export AVATAR_DMN='False'
export AVATAR_SAVENAME=${outputfolder}'/results_testn_'${testn}.mat

sbatch -p short \
       --output=${logfolder}'/output_testn_'${testn} \
       --error=${logfolder}'/error_testn_'${testn} \
       --mem 5G server.py
##############################################################################
##                          First Analysis
##############################################################################
# Create log and output folder
testn=0

export AVATAR_NOUNITY='False'
export AVATAR_ALPHA=0.000003
export AVATAR_TARGET=0.25
export AVATAR_G=0.27
export AVATAR_DMN='False'
export AVATAR_SAVENAME=${outputfolder}'/results_testn_'${testn}.mat

sbatch -p short \
       --output=${logfolder}'/output_testn_'${testn} \
       --error=${logfolder}'/error_testn_'${testn} \
       --mem 5G server.py -behaviour -homeostasis

##############################################################################
##                          Second Analysis
##############################################################################
# Create log and output folder
testn=1

export AVATAR_NOUNITY='False'
export AVATAR_ALPHA=0.000024
export AVATAR_TARGET=0.25
export AVATAR_G=0.27
export AVATAR_DMN='False'
export AVATAR_SAVENAME=${outputfolder}'/results_testn_'${testn}.mat

sbatch -p short \
       --output=${logfolder}'/output_testn_'${testn} \
       --error=${logfolder}'/error_testn_'${testn} \
       --mem 5G server.py -behaviour -homeostasis

##############################################################################
##                          Third Analysis
##############################################################################
# Create log and output folder
testn=2

export AVATAR_NOUNITY='False'
export AVATAR_ALPHA=0.000003
export AVATAR_TARGET=0.6
export AVATAR_G=0.27
export AVATAR_DMN='False'
export AVATAR_SAVENAME=${outputfolder}'/results_testn_'${testn}.mat

sbatch -p short \
       --output=${logfolder}'/output_testn_'${testn} \
       --error=${logfolder}'/error_testn_'${testn} \
       --mem 5G server.py -behaviour -homeostasis

##############################################################################
##                          Fourth Analysis
##############################################################################
# Create log and output folder
testn=3

export AVATAR_NOUNITY='False'
export AVATAR_ALPHA=0.000024
export AVATAR_TARGET=0.6
export AVATAR_G=0.27
export AVATAR_DMN='False'
export AVATAR_SAVENAME=${outputfolder}'/results_testn_'${testn}.mat

sbatch -p short \
       --output=${logfolder}'/output_testn_'${testn} \
       --error=${logfolder}'/error_testn_'${testn} \
       --mem 5G server.py -behaviour -homeostasis


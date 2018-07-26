#!/usr/bin/env bash

source activate tvb-env

## bad
export AVATAR_NOUNITY='False'
export AVATAR_TARGET=.7
export AVATAR_ALPHA=2e-05
export AVATAR_DMN='True'
export AVATAR_SAVENAME='tmp_bad1_with_DMN.mat'

sbatch -p verylong --mem 5G server.py -behaviour -homeostasis

## bad
export AVATAR_NOUNITY='False'
export AVATAR_TARGET=.25
export AVATAR_ALPHA=2e-05
export AVATAR_DMN='True'
export AVATAR_SAVENAME='tmp_bad2_with_DMN.mat'

sbatch -p verylong --mem 5G server.py -behaviour -homeostasis

## good
export AVATAR_NOUNITY='False'
export AVATAR_TARGET=.25
export AVATAR_ALPHA=2e-04
export AVATAR_DMN='True'
export AVATAR_SAVENAME='tmp_good1_with_DMN.mat'

sbatch -p verylong --mem 5G server.py -behaviour -homeostasis

## good
export AVATAR_NOUNITY='False'
export AVATAR_TARGET=.7
export AVATAR_ALPHA=2e-04
export AVATAR_DMN='True'
export AVATAR_SAVENAME='tmp_good2_with_DMN.mat'

sbatch -p verylong --mem 5G server.py -behaviour -homeostasis

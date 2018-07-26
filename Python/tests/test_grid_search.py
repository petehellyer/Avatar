#!/usr/bin/env python

import unittest
import os
import shutil
import pickle

from deepdiff import DeepDiff

from pyavatar.grid_search import run_behavioural_analysis


class TestRunBehaviouralAnalysis(unittest.TestCase):

    def setUp(self):
        self.simulation_path = 'tests/data/1_0.00000_0.40.mat'
        self.golden = 'tests/golden/behaviour_analysis.pickle'
        self.dpath = 'tests/output/'
        # remove output file and create it again
        if os.path.exists(self.dpath):
            shutil.rmtree(self.dpath)
        os.makedirs(self.dpath)

    def test_run_behavioural_analysis_with_behaviour(self):
        behaviour = True
        results = run_behavioural_analysis(self.simulation_path, behaviour)
        # compare results with the golden truth
        with open(self.golden, 'rb') as fh:
            golden_results = pickle.load(fh)
        self.assertEqual(DeepDiff(results, golden_results), {})


    def test_run_behavioural_analysis_without_behaviour(self):
        behaviour = False
        results = run_behavioural_analysis(self.simulation_path, behaviour)
        # As there is no behaviour, the only entry of the dictionary should be
        # 'men_activity_over_time'
        keys_no_behaviour = ['mean_activity_over_time']
        keys_results = results.keys()
        self.assertEqual(keys_results, keys_no_behaviour)


if __name__ == '__main__':
    unittest.main()

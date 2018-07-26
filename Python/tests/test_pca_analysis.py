#!/usr/bin/env python

import unittest
import os
import shutil
import pickle

from deepdiff import DeepDiff

from pyavatar.pca_analysis import run_pca_analysis

class TestRunPcaAnalysis(unittest.TestCase):

    def setUp(self):
        self.simulation = 'tests/data/1_0.00000_0.40.mat'
        self.golden = 'tests/golden/PCA_results.pickle'

    def test_run_pca_analysis(self):
        results = {}
        ncomponent, result = run_pca_analysis(self.simulation)
        results['ncomponents'] = ncomponent
        results['max_hs'] = result
        # compare results with the golden truth
        with open(self.golden, 'rb') as fh:
            golden_results = pickle.load(fh)
        self.assertEqual(DeepDiff(results, golden_results), {})
        # all_results = {}
        # all_results['ncomponents'] = ncomponent
        # all_results['max_hs'] = result
        # pickle.dump(all_results, open(os.path.join('tests', 'output',
        # 'PCA_results.pickle'), 'wb'))

if __name__ == '__main__':
    unittest.main()

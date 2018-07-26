#!/usr/bin/env python

import unittest
import scipy.io
import numpy as np
from copy import deepcopy

from pyavatar.utilities import (get_distance_wall, exclude_input_nodes,
                           discard_warm_up_time, low_pass_filter)


class TestUtilities(unittest.TestCase):

    def setUp(self):
        path_simulation = 'tests/data/1_0.00000_0.40.mat'
        self.simulation = scipy.io.loadmat(path_simulation)

    def test_max_distance_wall(self):
        mindist = get_distance_wall(self.simulation)
        self.assertTrue(np.max(mindist) <= 1)

    def test_min_distance_wall(self):
        mindist = get_distance_wall(self.simulation)
        self.assertTrue(np.min(mindist) >= -1)

    def test_exclude_input_nodes(self):
        original_simulation = deepcopy(self.simulation)
        no_input_nodes_simulation = exclude_input_nodes(self.simulation)
        self.assertEqual(original_simulation['ws'].shape[1] - 8,
                         no_input_nodes_simulation['ws'].shape[1])
        self.assertEqual(original_simulation['hs'].shape[1] - 8,
                         no_input_nodes_simulation['hs'].shape[1])
        self.assertEqual(original_simulation['xs'].shape[1] - 8,
                         no_input_nodes_simulation['xs'].shape[1])


    def test_discard_warm_up_time(self):
        original_simulation = deepcopy(self.simulation)
        no_warm_up_simulation = discard_warm_up_time(self.simulation)
        self.assertEqual(len(original_simulation['ws']) - 5000,
                         len(no_warm_up_simulation['ws']))
        self.assertEqual(len(original_simulation['hs']) - 5000,
                         len(no_warm_up_simulation['hs']))
        self.assertEqual(len(original_simulation['xs']) - 5000,
                         len(no_warm_up_simulation['xs']))

if __name__ == '__main__':
    unittest.main()

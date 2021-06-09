# some imports
import random

import numpy

from tvb.simulator import simulator
from tvb.simulator import integrators
from tvb.simulator import coupling
from tvb.simulator import monitors
from tvb.datatypes import connectivity
from tvb.simulator import noise
from tvb.analyzers import fmri_balloon
from tvb.datatypes import time_series
from Python.pyavatar.virtualbrain import ExtReducedWongWang
from skopt import gp_minimize
import numpy as np
from scipy.io.matlab import loadmat
import random


def evalOneMax(individual):
    # set coupling etc
    coup = coupling.Linear()

    dat = loadmat('Human_66.mat')
    # Create and scale connectivity
    conn = connectivity.Connectivity()
    conn.weights = dat['C']
    conn.tract_lengths = dat['C']
    conn.weights = conn.scaled_weights('region')  # scale the weights? does this work?
    conn.weights = conn.weights > individual[2]
    conn.speed = np.inf

    # and Noise
    noi = noise.Additive()
    noi.nsig = float(individual[1])

    # fire up an integrator
    integ = integrators.EulerStochastic()
    integ.dt = 0.05

    integ.noise = noi

    # import form of the model
    rww = ExtReducedWongWang()
    rww.w = 0.9
    rww.I_o = 0.33

    coup.a = float(individual[0])
    rww.alpha = 0.01
    rww.local_homeo = False
    rww.target = 1  # individual[-1]

    # create monitor
    monit = monitors.Raw()

    # create simulator
    sim = simulator.Simulator()
    sim.model = rww
    sim.connectivity = conn
    sim.coupling = coup
    sim.integrator = integ
    sim.monitors = monit
    sim.simulation_length = 1000  # 60 seconds....?
    sim.configure()

    data = sim.run()

    # baloon windkessel?
    datts = time_series.TimeSeries()
    datts.data = np.array(data[0][1])
    datts.time = np.array(data[0][0])
    bwk = fmri_balloon.BalloonModel()
    bwk.dt = integ.dt
    bwk.time_series = datts
    bold = bwk.evaluate()

    data = bold.data[:, 0, :, 0].squeeze()
    data = data[int(np.ceil((data.shape[0] / 2))):, :]

    cf = np.corrcoef(data.T)[np.triu_indices(66, 0)]
    fc = dat['FC_emp'][np.triu_indices(66, 0)]
    ans = np.corrcoef(cf, fc)[1][0]
    print('{0}'.format(ans), )
    return -ans


def main():
    res = gp_minimize(evalOneMax, [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)], verbose=True,
                      acq_optimizer='lbfgs',
                      acq_func="EI",
                      n_calls=100,
                      n_random_starts=50,
                      random_state=123)
    print('Done!')


if __name__ == "__main__":
    main()

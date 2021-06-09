# some imports
import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from tvb.simulator import simulator
from tvb.simulator import integrators
from tvb.simulator import coupling
from tvb.simulator import monitors
from tvb.datatypes import connectivity
from tvb.simulator import noise
from tvb.analyzers import fmri_balloon
from tvb.datatypes import time_series
from tvb.basic.traits.types_basic import Float
from Python.pyavatar.virtualbrain import ExtReducedWongWang
import numpy as np
from scipy.io.matlab import loadmat
import random


def evalOneMax(individual):
    # set coupling etc
    coup = coupling.Linear()

    dat = loadmat('Human_200.mat')
    # Create and scale connectivity
    conn = connectivity.Connectivity()
    conn.weights = dat['C']
    conn.tract_lengths = dat['C']
    conn.weights = conn.scaled_weights('region')  # scale the weights? does this work?
    conn.speed = np.inf

    # and Noise
    noi = noise.Additive()
    noi.nsig = 1E-6

    # fire up an integrator
    integ = integrators.EulerStochastic()
    integ.dt = 0.1

    integ.noise = noi

    # import form of the model
    rww = ExtReducedWongWang()
    rww.w = 0.9
    rww.I_o = 0.33

    coup.a = 0.2 #individual[-2]
    rww.alpha = 0.2 # individual[:-2]
    rww.local_homeo = False
    rww.target = 1# individual[-1]

    # create monitor
    monit = monitors.Raw()

    # create simulator
    sim = simulator.Simulator()
    sim.model = rww
    sim.connectivity = conn
    sim.coupling = coup
    sim.integrator = integ
    sim.monitors = monit
    sim.simulation_length = 60 * (1e2)  # 60 seconds....?
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

    cf = np.corrcoef(data.T)[np.triu_indices(188, 1)]
    fc = dat['FC'][np.triu_indices(188, 1)]
    ans = np.corrcoef(cf, fc)[1][0]
    print('{0}'.format(ans), )
    return ans,


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_bool", random.random)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=190)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def cxTwoPointCopy(ind1, ind2):
    size = len(ind1)
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
        = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()

    return ind1, ind2


toolbox.register("evaluate", evalOneMax)
toolbox.register("mate", cxTwoPointCopy)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)


def main():
    # random.seed(64)

    pop = toolbox.population(n=20)

    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(1, similar=numpy.array_equal)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=100, stats=stats,
                        halloffame=hof)

    return pop, stats, hof


if __name__ == "__main__":
    main()

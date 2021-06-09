# some imports

from copy import deepcopy
from tvb.simulator import simulator
from tvb.simulator import integrators
from tvb.simulator import coupling
from tvb.simulator import monitors
from tvb.datatypes import connectivity
from tvb.simulator import noise
from Python.pyavatar.virtualbrain import ExtReducedWongWang
from tvb.simulator.models import ReducedWongWang, WilsonCowan
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


class sim:
    def __init__(self, i):
        coup = coupling.Linear()
        coup.a = i

        # Create and scale connectivity
        conn = connectivity.Connectivity.from_file(source_file="connectivity_66.zip")
        conn.weights = conn.scaled_weights('region')  # scale the weights? does this work?
        conn.speed = np.inf

        # and Noise
        noi = noise.Additive()
        noi.nsig = 1E-6

        # fire up an integrator
        integ = integrators.EulerStochastic()
        integ.dt = 0.05

        integ.noise = noi

        # import form of the model
        rww = ReducedWongWang()
        rww.w = 0.9
        rww.I_o = 0.33

        # homeostatic variables.
        rww.local_homeo = False
        rww.alpha = 0.01
        rww.target = 0.3

        # create monitor
        monit = monitors.Raw()
        # create simulator
        self.sim = simulator.Simulator()
        self.sim.model = rww
        self.sim.connectivity = conn
        self.sim.coupling = coup
        self.sim.integrator = integ
        self.sim.monitors = monit
        self.sim.simulation_length = 30 * (1e3)  # 30 seconds....?

        self.sim.configure()

    def run(self):
        return self.sim.run()


hists = np.zeros((99, 50))  # set coupling etc

for n, i in (enumerate(tqdm(np.linspace(0.0001, 0.06, hists.shape[1])))):
    stmp = sim(i)
    data = stmp.run()
    try:
        hists[:, n], bins = np.histogram((data[0][1][-5000:, 0, :, :]).flatten(), np.linspace(0, 1, 100))
    except ValueError:
        hists[:, n] = 0

plt.imshow(hists)
plt.savefig('%s.png' % __name__)
print('done!')

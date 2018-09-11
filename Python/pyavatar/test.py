# some imports

from tvb.simulator import simulator
from tvb.simulator import integrators
from tvb.simulator import coupling
from tvb.simulator import monitors
from tvb.datatypes import connectivity
from tvb.simulator import noise
from Python.pyavatar.virtualbrain import ExtReducedWongWang
from pylab import *
from tqdm import tqdm
import copy

hists_alpha = np.zeros((99, 50))

for n, i in (enumerate(tqdm(np.linspace(0.0001, 0.025, 50)))):

    # set coupling etc
    coup = coupling.Linear()

    # Create and scale connectivity
    conn = connectivity.Connectivity.from_file(source_file="connectivity_66.zip")
    conn.weights = conn.scaled_weights('region')  # scale the weights? does this work?
    conn.speed = np.inf

    # and Noise
    noi = noise.Additive()
    noi.nsig = 1E-6

    # fire up an integrator
    integ = integrators.EulerStochastic()
    integ.dt = 0.5

    integ.noise = noi

    # import form of the model
    rww = ExtReducedWongWang()
    rww.w = 0.9
    rww.I_o = 0.33

    coup.a = 0.03
    rww.alpha = i
    rww.local_homeo = True
    rww.target = 0.3

    # create monitor
    monit = monitors.Raw()

    # create simulator
    sim = simulator.Simulator()
    sim.model = rww
    sim.connectivity = conn
    sim.coupling = coup
    sim.integrator = integ
    sim.monitors = monit
    sim.simulation_length = 10 * (1e3)  # 10 seconds....?
    sim.configure()





    data = sim.run()
    try:
        hists_alpha[:, n], bins = np.histogram((data[0][1][5000:5500, 0, :, :]).flatten(), np.linspace(0, 1, 100))
    except ValueError:
        hists_alpha[:, n] = 0

imshow(hists_alpha)
print('done!')

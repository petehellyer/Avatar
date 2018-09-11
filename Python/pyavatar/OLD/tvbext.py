# coding=utf-8

from tvb.simulator import simulator, models
from tvb.datatypes import connectivity
from tvb.simulator import integrators, coupling, monitors, noise

# A thread that holds the computational model
class Thread(threading.Thread):  # this thread actually runs the model
    def __init__(self, savename, target, alpha, behaviour, G, initial_conditions, event, DMN):
        super(Thread, self).__init__()
        self.savename = savename
        ml = scmat.loadmat('Human_66.mat')
        self.Locations = ml['talairach_66']
        self.event = event

        conn = connectivity.Connectivity.from_file(source_file="connectivity_66.zip")
        conn.speed = np.inf

        rww = ReducedWongWang()
        rww.a = 0.27
        rww.w = (np.ones((66, 1)) * 0.8)
        rww.I_o = (np.ones((66, 1)) * 0.3)
        rww.target = target
        rww.fwdmod = 1  # modifiers for movement calculation
        rww.rotmod = 1  # modifiers for movement calculation
        rww.alpha = alpha
        rww.DMN = DMN
        rww.behaviour = behaviour
        rww.event = event


        self.noise_i = 0.00001
        my_rng = np.random.RandomState(seed=1)

        self.sim = Simulator()

        self.sim.initial_conditions = initial_conditions
        self.sim.model = rww
        self.sim.connectivity = conn

        self.sim.coupling = coupling.Linear()
        self.sim.coupling.a = G

        self.sim.integrator = integrators.EulerStochastic
        self.sim.integrator.dt = 1

        self.sim.integrator.noise = noise.Additive()
        self.sim.integrator.noise.nsig = self.noise_i
        self.sim.integrator.noise.random_stream = my_rng

        self.sim.monitors = monitors.TemporalAverage()
        self.sim.simulation_length = 3e4
        self._is_running = False

        self.sim.configure()

    def stop(self):
        self._is_running = False

    def run(self):
        self._is_running = True
        # this should theoretically run forever or until codebase is dead.
        (ts, xs, hs, data, rot, fwd, posx, posz, ws) = self.sim.run()
        self._is_running = False
        return ts, xs, hs, data, rot, fwd, posx, posy, ws


def _numpy_dfun(self, state_variables, coupling, local_coupling=0.0):
    r"""
    Equations taken from [DPA_2013]_ , page 11242

    .. math::
             x_k       &=   w\,J_N \, S_k + I_o + J_N \mathbf\Gamma(S_k, S_j, u_{kj}),\\
             H(x_k)    &=  \dfrac{ax_k - b}{1 - \exp(-d(ax_k -b))},\\
             \dot{S}_k &= -\dfrac{S_k}{\tau_s} + (1 - S_k) \, H(x_k) \, \gamma

    """
    # Note: if we consider each node separately we need to reshape both parameters iof interest..
    self.w = np.reshape(self.w, (self.w.size, 1))
    self.I_o = np.reshape(self.I_o, (self.I_o.size, 1))

    S = state_variables[0, :]
    S[S < 0] = 0.
    S[S > 1] = 1.
    c_0 = coupling[0, :]

    # if applicable
    lc_0 = local_coupling * S

    # Self I_O - external input
    # self w - local excitatory reccurrrence.
    x = self.w * self.J_N * S + self.I_o + self.J_N * c_0 + self.J_N * lc_0
    H = (self.a * x - self.b) / (1 - np.exp(-self.d * (self.a * x - self.b)))
    dS = - (S / self.tau_s) + (1 - S) * H * self.gamma

    # need to do something that prevents DMN nodes from having a negative firing rate.
    # !!!! make sure that where current state is 0, the derivative cant possibly be anything other than zero....
    # todo: if this were less of a hack, that would be nice....
    dS[S == 0] = 0

    derivative = np.array([dS])

    return derivative


class ReducedWongWang(models.ReducedWongWang):
    # Extend Model class as required (for sticking extra bits into the computational model, somehow?
    def dfun(self, x, c, local_coupling=0.0):
        deriv, h = _numpy_dfun(self, x, c, local_coupling=0.0)
        # save the population firing rate (h)
        self.h = h
        return deriv


class Simulator(simulator.Simulator):
    def __init__(self):
        super(Simulator, self).__init__()
        self.Excitatory = 1
        self.Inhibitory = 0
        self.threshold = 13  # if current state is higher then this value than consider node active

        self.nodes_FWD_R = 15
        self.nodes_FWD_L = 15 + 33
        self.nodes_ROT_R = 23
        self.nodes_ROT_L = 23 + 33
        self.Locations = []

        self.movedecay = 10.0  # Decay rate for movement (i.e. how many steps to zero..., ~roughly..)
        self.rot = 0.0  # placeholder for rotation
        self.fwd = 0.0  # placeholder for fwd

        # set input and output nodes.
        self.nodes_vis_R = TP_visual
        self.nodes_vis_L = TP_visual + 33
        self.nodes_vis_R_DMN = DMN_visual
        self.nodes_vis_L_DMN = DMN_visual + 33
        self.nodes_col_R = 21
        self.nodes_col_L = 21 + 33
        self.nodes_col_R_DMN = 22
        self.nodes_col_L_DMN = 22 + 33

        self.vis_L = False
        self.vis_R = False
        self.col_L = False
        self.col_R = False

        # Pass initial coordinates of the avatar
        self.posz = 1000
        self.posx = 1000

        self.next_unity_condition = True
        self.next_simulation = 0

    def __call__(self, simulation_length=None, random_state=None):
        """
        Return an iterator which steps through simulation time, generating monitor outputs.

        See the run method for a convenient way to collect all output in one call.

        :param simulation_length: Length of the simulation to perform in ms.
        :param random_state:  State of NumPy RNG to use for stochastic integration.
        :return: Iterator over monitor outputs.
        """

        self.calls += 1
        if simulation_length is not None:
            self.simulation_length = simulation_length

        # intialization
        self._guesstimate_runtime()
        self._calculate_storage_requirement()
        self._handle_random_state(random_state)
        n_reg = self.connectivity.number_of_regions
        local_coupling = self._prepare_local_coupling()
        stimulus = self._prepare_stimulus()

        # check if time point has already been defined (e.g. by loading a pickle). If no previous time points are present
        # start the simulation from zero, otherwise start from the saved time point.
        if not hasattr(self.model, 't'):
            print "\nStarting Simulation"
            self.model.t = 0

        while self.model.t < int(self.simulation_length):

            # Only start the unity server, after the python model has reached stability (t = 5000)
            if self.model.t == 5000 and args.behaviour:
                self.model.event.set()
            # if there is no unity behaviour this condition should always be true
            # if self.model.t > 5000:
            #     pdb.set_trace()
            if self.next_unity_condition:
                # needs implementing by hsitory + coupling?
                node_coupling = self._loop_compute_node_coupling(self.model.t)
                self._loop_update_stimulus(self.model.t, stimulus)
                next_state = self.integrator.scheme(self.current_state, self.model.dfun, node_coupling, local_coupling,
                                                    stimulus)
                # bound next_state between 0 and 1
                next_state[next_state < 0] = 0
                next_state[next_state > 1] = 1
                self._loop_update_history(self.model.t, n_reg, next_state)
                output = self._loop_monitor_output(self.model.t, next_state)
                if output is not None:
                    self.current_state = next_state
                    yield output
                self.model.t += 1
        print('Finished Simulation')

    def run(self, **kwds):
        # Extend Simulator to expose bits we actually want from the integrator.
        # Sadly that means re-writing the entire 'run' section, but does fundamentally expose the right bit, so I
        # suppose beggars can't be choosers..
        " Convenience method to call the simulator with **kwds and collect output data."
        ts, xs, hs, rot, fwd, ws, posz, posx = [], [], [], [], [], [], [], []
        for _ in self.monitors:
            ts.append([])
            xs.append([])
        for data in self(**kwds):
            for tl, xl, t_x in zip(ts, xs, data):
                if t_x is not None:
                    t, x = t_x  # <------ THIS RIGHT HERE IS THE CURRENT STATE

                    _x = np.reshape(x, self.model.w.shape)
                    # _w = self.model.alpha * (_x - self.model.target) * 1e05
                    _w = self.model.alpha * (_x - self.model.target)
                    self.model.w = self.model.w - _w
                    self.model.w[self.model.w < 0] = 0  # heaviside this

                    if self.model.DMN:
                        if self.vis_L:
                            self.current_state[:, self.nodes_vis_L_DMN, :] = 0
                        if self.vis_R:
                            self.current_state[:, self.nodes_vis_R_DMN, :] = 0
                        if self.col_L:
                            self.current_state[:, self.nodes_col_L_DMN, :] = 0
                        if self.col_R:
                            self.current_state[:, self.nodes_col_R_DMN, :] = 0

                    tl.append(t)
                    xl.append(x)

            hs.append(self.model.h)
            ws.append(self.model.w)

            # Send updated values to Unity, only if Unity active and simulation time is bigger than that required
            # for the stabilisation of the model
            if self.model.behaviour and self.model.t >= 5000:
                # decay movement by a bit
                self.rot *= ((self.movedecay - 1) / self.movedecay)
                self.fwd *= ((self.movedecay - 1) / self.movedecay)

                # forward
                self.fwd += (float(self.model.h[self.nodes_FWD_L] * 100)) * self.model.fwdmod
                self.fwd += (float(self.model.h[self.nodes_FWD_R] * 100)) * self.model.fwdmod

                # rotation
                self.rot += (float(self.model.h[self.nodes_ROT_L] * 900)) * self.model.rotmod
                self.rot += - (float(self.model.h[self.nodes_ROT_R] * 900)) * self.model.rotmod

                rot.append(self.rot)
                fwd.append(self.fwd)
                posx.append(self.posx)
                posz.append(self.posz)

                self.next_unity_condition = False
                self.next_simulation += 1

        for i in range(len(ts)):
            ts[i] = np.array(ts[i])
            xs[i] = np.array(xs[i])

        # transform output to correct format
        ts = np.squeeze(ts)
        xs = np.squeeze(np.asarray(xs))

        return ts, xs, hs, data, rot, fwd, posx, posz, ws

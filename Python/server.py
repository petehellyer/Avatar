#!/usr/bin/env python
import os
import sys

import threading
from scipy.io import savemat
from subprocess import Popen, STDOUT
import numpy as np
sys.modules['mtrand'] = np.random.mtrand
from avatar_interop import AvatarIO
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from tvb.simulator import simulator, integrators, coupling, monitors, models
from tvb.datatypes import connectivity
from tvb.simulator import noise
import scipy.io.matlab as scmat
import platform
import signal
from argparse import ArgumentParser

import pdb
import tempfile

parser = ArgumentParser(
    description='Create Server and run model with or without the Unity model'
)
# Analysis type
parser.add_argument(
    '-behaviour',
    action='store_true',
    dest='behaviour',
    help='Runs the simulation with the Unity interface'
)
parser.add_argument(
    '-homeostasis',
    action='store_true',
    dest='homeostasis',
    help='Runs the simulation with the Unity interface'
)
args = parser.parse_args()


def str_to_bool(s):
    """
    Get inpunt string True/False and transform it into boolean
    :param s: String with True or False
    :return: Boolen correpondent for the string
    """

    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError

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

    return derivative, H


class ExtReducedWongWang(models.ReducedWongWang):
    # Extend Model class as required (for sticking extra bits into the computational model, somehow?
    def dfun(self, x, c, local_coupling=0.0):
        deriv, h = _numpy_dfun(self, x, c, local_coupling=0.0)
        # save the population firing rate (h)
        self.h = h
        return deriv


class ExtendedSimulator(simulator.Simulator):
    def __init__(self):
        super(ExtendedSimulator, self).__init__()
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
        print 'TP  nodes are:'
        print 'visual: %d and %d' %(self.nodes_vis_R, self.nodes_vis_L)
        print '   col: %d and %d' %(self.nodes_col_R, self.nodes_col_R)
        print 'DMN nodes are:'
        print 'visual: %d and %d' %(self.nodes_vis_R_DMN, self.nodes_vis_L_DMN)
        print '   Col: %d and %d' %(self.nodes_col_R_DMN, self.nodes_col_L_DMN)


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
                next_state = self.integrator.scheme(self.current_state, self.model.dfun, node_coupling, local_coupling, stimulus)
                # bound next_state between 0 and 1
                next_state[next_state < 0] = 0
                next_state[next_state > 1] = 1
                self._loop_update_history(self.model.t, n_reg, next_state)
                output = self._loop_monitor_output(self.model.t, next_state)
                if output is not None:
                    self.current_state = next_state
                    yield output
                self.model.t += 1
        print 'Finished Simulation'

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
                    # only run homeostatic rule when passed as parameter
                    if args.homeostasis:
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
                self.rot +=   (float(self.model.h[self.nodes_ROT_L] * 900)) * self.model.rotmod
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


class ModelThread(threading.Thread):
    def __init__(self, savename, target, alpha, behaviour,G,
            initial_conditions, event, DMN, DMN_visual, TP_visual):
        super(ModelThread, self).__init__()
        self.savename = savename
        ml = scmat.loadmat('Human_66.mat')
        self.Locations = ml['talairach_66']
        self.event = event

        conn = connectivity.Connectivity.from_file(source_file="connectivity_66.zip")
        conn.speed = np.inf

        rww = ExtReducedWongWang(a=0.27)
        rww.w = (np.ones((66, 1)) * 0.8)
        rww.I_o = (np.ones((66, 1)) * 0.3)
        rww.target = target
        rww.fwdmod = 1  # modifiers for movement calculation
        rww.rotmod = 1  # modifiers for movement calculation
        rww.alpha = alpha
        rww.DMN = DMN
        rww.behaviour = behaviour
        rww.event = event

        my_rng = np.random.RandomState(seed=1)
        self.sim = ExtendedSimulator(
            initial_conditions=initial_conditions,
            model=rww,
            connectivity=conn,
            coupling=coupling.Linear(a=G),
            integrator=integrators.EulerStochastic(dt=1,
                noise=noise.Additive(nsig=noise_i, random_stream=my_rng)),
            monitors=monitors.TemporalAverage(),
            simulation_length=3e4).configure()  # todo: make this less idiotic somehow... - maybe refactor up the code

    def stop(self):
        self._is_running = False

    def run(self):
        self._is_running = True
        (ts, xs, hs, data, rot, fwd, posx,
         posz, ws) = self.sim.run()  # this should theoretically run forever or until codebase is dead.
        savemat(self.savename,
                {'ts': ts, 'xs': xs, 'hs': hs, 'rot': rot, 'fwd': fwd, 'posx': posx, 'posz': posz, 'ws': ws})
        os.kill(os.getpid(), signal.SIGINT)



class AvatarIOHandler(object):
    def __init__(self, savename, alpha, target, behaviour, G, event, DMN,
            initial_condition, DMN_visual, TP_visual):
        if behaviour:
            print("G:%s, Alpha:%s, Target:%s, Name:%s" % (G, alpha, target, savename))
            print("Behaviour will be assessed with Unity")
        else:
            print("G:%s, Name:%s" % (G, savename))
        initial_conditions = np.ones((1, 1, 66, 1)) * initial_condition

        self.model = ModelThread(savename, target, alpha, behaviour, G,
                initial_conditions, event, DMN, DMN_visual, TP_visual)
        self.model.daemon = True  # make it a daemon!
        self.model.start()  # start the computational model!

    def RewardSignal(self, sig):
        self.PrintStatic('RewardSignal(%s)' % sig)
        return True

    def SalienceSignal(self, sig):
        self.PrintStatic('SalienceSignal(%s)' % sig)
        return True

    def Visual_L(self, vis1):
        self.model.sim.vis_L = vis1

        # set the input to the left visual node to 1, if the Avatar is less than 2 units away from the all, otherwise set
        # the input to the standard defined value for the simulation
        #    Note: I am assuming that the values of the first node will not change over time

        if vis1:
            self.model.sim.model.I_o[self.model.sim.nodes_vis_L] = vis1
        else:
            self.model.sim.model.I_o[self.model.sim.nodes_vis_L] = self.model.sim.model.I_o[0]
        return True

    def Somatosensory_L(self, somat1):
        self.model.sim.col_L = somat1

        # set the input to the left somatosensory node to 1, if the Avatar is less than 2 units away from the all, otherwise set
        # the input to the standard defined value for the simulation
        #    Note: I am assuming that the values of the first node will not change over time

        if somat1:
            self.model.sim.model.I_o[self.model.sim.nodes_col_L] = somat1
        else:
            self.model.sim.model.I_o[self.model.sim.nodes_col_L] = self.model.sim.model.I_o[0]
        return True

    def Visual_R(self, vis1):
        self.model.sim.vis_R = vis1

        # set the input to the right visual node to 1, if the Avatar is less than 2 units away from the all, otherwise set
        # the input to the standard defined value for the simulation
        #    Note: I am assuming that the values of the first node will not change over time

        if vis1:
            self.model.sim.model.I_o[self.model.sim.nodes_vis_R] = vis1
        else:
            self.model.sim.model.I_o[self.model.sim.nodes_vis_R] = self.model.sim.model.I_o[0]
        return True

    def Somatosensory_R(self, somat1):
        self.model.sim.col_R = somat1

        # set the input to the right somatosensory node to 1, if the Avatar is less than 2 units away from the all, otherwise set
        # the input to the standard defined value for the simulation
        #    Note: I am assuming that the values of the first node will not change over time

        if somat1:
            self.model.sim.model.I_o[self.model.sim.nodes_col_R] = somat1
        else:
            self.model.sim.model.I_o[self.model.sim.nodes_col_R] = self.model.sim.model.I_o[0]
        return True

    def GetStates(self):
        return np.squeeze(self.model.sim.current_state).tolist()

    def GetFwd(self):
        # self.PrintStatic('GetFwd')
        return self.model.sim.fwd

    def GetRot(self):
        # self.PrintStatic('GetRot')
        return self.model.sim.rot

    def SendPosition(self, posz, posx):
        self.PrintStatic('Position(%.2f,%.2f)' % (posz, posx))
        self.model.sim.posz = posz
        self.model.sim.posx = posx
        return True

    def GetNodeLocation(self, nodeid):
        return self.model.Locations[nodeid, :]

    def GetNodeNumber(self):
        return self.model.Locations.shape[0]

    def PrintStatic(self, a_string=''):
        return None

    def NextSimulation(self):
        return self.model.sim.next_simulation

    def SendNextUnityCondition(self, condition):
        self.model.sim.next_unity_condition = condition
        return condition

class AvatarThread(threading.Thread):  # create a thread for the unity model.
    def __init__(self, event, port=None):
        super(AvatarThread, self).__init__()
        self.port = port
        self.sub = None
        self.event = event

    def stop(self):
        self._is_running = False

    def run(self):

        print('Wait for computational model to warm up.')
        self.event.wait()
        self.event.clear()

        self._is_running = True

        # check the current OS and use the correct path for the unity
        # application
        if platform.system() == 'Linux':
            app = os.getenv('UNITY_PATH', '../../Unity/build/lnx.x86_64')
        elif platform.system() == 'Darwin':
            app = os.getenv('UNITY_PATH', '../../Unity/build/mac.app/Contents/MacOS/mac')

        # Check if the unity app exists otherwise raise an Error
        if os.path.exists(app):
            print 'App path: ' + app
            runtime = '%s -port=%s' % (app, self.port)
            # string to encapsulate the runtime for the unity model which on the
            # c3nl cluster should be compiled as 'headless x86_64') note the -port
            # command line option.
        else:
            raise IOError('The unity app %s is not availiable for this \
                          platform or its path is incorrect' %app)

        # os.system(runtime)
        print '\n'  # runtime
        FNULL = open(os.devnull, 'w')
        self.sub = Popen(runtime, shell=True, stdout=FNULL, stderr=STDOUT)  # no output to make life confusing.

        # (time, data, hs), = self.sim.run()  # actually run the simulation.


class TSimpleServer(TServer.TSimpleServer):
    """Simple single-threaded server that just pumps around one transport."""

    def serve(self):
        self.serverTransport.listen()
        while True:
            client = self.serverTransport.accept()
            if not client:
                continue
            itrans = self.inputTransportFactory.getTransport(client)
            otrans = self.outputTransportFactory.getTransport(client)
            iprot = self.inputProtocolFactory.getProtocol(itrans)
            oprot = self.outputProtocolFactory.getProtocol(otrans)
            try:
                while True:
                    self.processor.process(iprot, oprot)
            except TTransport.TTransportException:
                pass
            except Exception as x:
                # logger.exception(x)
                pass

            itrans.close()
            otrans.close()


if __name__ == '__main__':

    savename = 'tmp_optimal.mat'
    target = 0.25
    alpha = .0000175
    G = 0.27
    noise_i = 0.00001
    DMN = False
    initial_condition = .5
    # Those nodes correpond to DMN nodes on empirical data
    DMN_visual = 9
    TP_visual = 20

    # Get variables from bash
    if "AVATAR_SAVENAME" in os.environ:
        savename = os.getenv('AVATAR_SAVENAME')
    if "AVATAR_ALPHA" in os.environ:
        alpha = float(os.getenv('AVATAR_ALPHA'))
    if "AVATAR_TARGET" in os.environ:
        target = float(os.getenv('AVATAR_TARGET'))
    if "AVATAR_G" in os.environ:
        G = float(os.getenv('AVATAR_G'))
    if "AVATAR_NOISE" in os.environ:
        noise_i = float(os.getenv('AVATAR_NOISE'))
    if "AVATAR_DMN" in os.environ:
        DMN = str_to_bool(os.getenv('AVATAR_DMN'))
    if "AVATAR_INITIAL_COND" in os.environ:
        initial_condition = float(os.getenv('AVATAR_INITIAL_COND'))
    if "AVATAR_DMN_VISUAL" in os.environ:
        DMN_visual = int(os.getenv("AVATAR_DMN_VISUAL"))
    if "AVATAR_TP_VISUAL" in os.environ:
        TP_visual = int(os.getenv("AVATAR_TP_VISUAL"))

    # instantiate event that will signal the communcation between processes
    event = threading.Event()

    if args.homeostasis:
        print "\nSimulating with Homeostatic Rule"
    else:
        print "\nSimulating without Homeostatic Rule"

    # in case the behaviour flag is active run the Unity thread
    if args.behaviour:
        print "\nSimulating Behaviour"
        handler = AvatarIOHandler(savename, alpha, target, args.behaviour, G,
                event, DMN, initial_condition, DMN_visual, TP_visual)  # create thread for Avatar IO.
        processor = AvatarIO.Processor(handler)

        unity = None
        # Run unity with Graphics interface if AVATAR_NOUNITY is true (n.b. you
        # need to compile without clickling headless)
        if not str_to_bool(os.getenv('AVATAR_NOUNITY')):
            # Lazilly create thread for Unity Avatar
            # create temporary file to use as socket for communication with unity. Note, this ONLY works on UNIX systems...... For now.....
            f = "/tmp/Avatar_%s" % next(tempfile._get_candidate_names())
            print "\nSocket name %s" % f
            unity = AvatarThread(event, port=f)
            unity.daemon = True  # make it a daemon!
            unity.start()  # start the unity thread
            transport = TSocket.TServerSocket(unix_socket=f)
        else:
            transport = TSocket.TServerSocket(port=9090)
            print "Using port 9090"

        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        server = TSimpleServer(processor, transport, tfactory, pfactory)

        print "\nStarting python server..."
        try:
            server.serve()
        except KeyboardInterrupt:
            if unity is not None:  # try and terminate unity if it's open., almost certainly a neater way to do this exists..
                print 'Terminating Unity'
                unity.sub.terminate()
            exit()
    else:
        print "\nSimulating without the behaviour"
        handler = AvatarIOHandler(savename, alpha, target, args.behaviour, G,
                event, DMN, initial_condition, DMN_visual, TP_visual)  # create thread for Avatar IO.
        processor = AvatarIO.Processor(handler)
        f = "/tmp/Avatar_%s" % next(tempfile._get_candidate_names())
        print "/nSocket name %s" % f
        transport = TSocket.TServerSocket(unix_socket=f)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

        print "\nStarting python server..."
        try:
            server.serve()
        except KeyboardInterrupt:
            print "Terminating"



# coding=utf-8
import threading, platform, os
from subprocess import Popen, STDOUT


class Thread(threading.Thread):  # create a thread for the unity model.
    def __init__(self, event, port=None):
        super(Thread, self).__init__()
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
                          platform or its path is incorrect' % app)

        # os.system(runtime)
        FNULL = open(os.devnull, 'w')
        self.sub = Popen(runtime, shell=True, stdout=FNULL, stderr=STDOUT)  # no output to make life confusing.


class IOHandler(object):  # THIS IS THE KEY TO EVERYTHING!

    def __init__(self, savename, alpha, target, behaviour, G, event, DMN,
                 initial_condition, DMN_visual, TP_visual):

        initial_conditions = np.ones((1, 1, 66, 1)) * initial_condition

        self.model = Thread(savename, target, alpha, behaviour, G,
                                 initial_conditions, event, DMN, DMN_visual, TP_visual)
        self.model.daemon = True  # make it a daemon!
        self.model.start()  # start the computational model!

    # from here on down, this handles the conditions of the IO handl

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
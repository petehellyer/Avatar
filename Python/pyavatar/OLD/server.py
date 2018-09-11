#!/usr/bin/env python
# coding=utf-8
import os
import signal
import sys
import tempfile
import threading
import numpy as np

import scipy.io.matlab as scmat

from scipy.io import savemat
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport




from pyavatar.thrift import AvatarIO
from pyavatar.unity import IOHandler, Thread

from pyavatar.utils import str_to_bool

sys.modules['mtrand'] = np.random.mtrand





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


def main():
    # here's some settings that ight be over-written by env variables.
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
    behaviour = True
    autorun = True  # automatically start the Unity Daemon

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
    if "AVATAR_BEHAVIOUR" in os.environ:
        behavior = str_to_bool(os.getenv("AVATAR_BEHAVIOR"))
    if "AVATAR_UNITY_AUTORUN" in os.environ:
        autorun = str_to_bool(os.getenv('AVATAR_UNITY_AUTORUN'))



    # instantiate event that will signal the communcation between processes
    event = threading.Event()

    handler = AvatarIOHandler(savename, alpha, target, behaviour, G,
                              event, DMN, initial_condition, DMN_visual, TP_visual)  # create thread for Avatar IO.
    processor = AvatarIO.Processor(handler)

    if behaviour:
        print("\n Using Unity interactions.")

        unity = None
        # Run unity with Graphics interface if AVATAR_NOUNITY is true (n.b. you
        # need to compile without clickling headless)
        if autorun:  # by default we'll spawn our own unity model, but if we don't listen on port 9090
            #  Generate a UNIX socket for the Avatar to Communicate on.
            f = "/tmp/Avatar_%s" % next(tempfile._get_candidate_names())
            print("\nSocket name %s" % f)
            unity = AvatarThread(event, port=f)
            unity.daemon = True  # make it a daemon!
            unity.start()  # start the unity thread
            transport = TSocket.TServerSocket(unix_socket=f)
        else:
            transport = TSocket.TServerSocket()  # 9090
            print("Using port 9090")

        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        server = TSimpleServer(processor, transport, tfactory, pfactory)

        print("\nStarting python server...")
        try:
            server.serve()
        except KeyboardInterrupt:
            if unity is not None:  # try and terminate unity if it's open, and keyboard operation happens.
                print('Terminating Unity')
                unity.sub.terminate()
            exit()
    else:
        try:
            print("\nSimulating without behavioural model")

        except KeyboardInterrupt:
            print("Terminating")


# the actual code that runs dammit.
if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

""" This Module contains extended versions of the virtual brain models and simulators
NO threading code should be in this module, only extensions of TVB."""

from tvb.simulator.models.base import Model, numpy, basic, arrays, Model, LOG, numpy, basic, arrays
import numpy as np


class ExtWilsonCowan(Model):
    r"""
    **References**:

    .. [WC_1972] Wilson, H.R. and Cowan, J.D. *Excitatory and inhibitory
        interactions in localized populations of model neurons*, Biophysical
        journal, 12: 1-24, 1972.
    .. [WC_1973] Wilson, H.R. and Cowan, J.D  *A Mathematical Theory of the
        Functional Dynamics of Cortical and Thalamic Nervous Tissue*

    .. [D_2011] Daffertshofer, A. and van Wijk, B. *On the influence of
        amplitude on the connectivity between phases*
        Frontiers in Neuroinformatics, July, 2011

    Used Eqns 11 and 12 from [WC_1972]_ in ``dfun``.  P and Q represent external
    inputs, which when exploring the phase portrait of the local model are set
    to constant values. However in the case of a full network, P and Q are the
    entry point to our long range and local couplings, that is, the  activity
    from all other nodes is the external input to the local population.

    The default parameters are taken from figure 4 of [WC_1972]_, pag. 10

    In [WC_1973]_ they present a model of neural tissue on the pial surface is.
    See Fig. 1 in page 58. The following local couplings (lateral interactions)
    occur given a region i and a region j:

      E_i-> E_j
      E_i-> I_j
      I_i-> I_j
      I_i-> E_j


    +---------------------------+
    |          Table 1          |
    +--------------+------------+
    |                           |
    |  SanzLeonetAl,   2014     |
    +--------------+------------+
    |Parameter     |  Value     |
    +==============+============+
    | k_e, k_i     |    1.00    |
    +--------------+------------+
    | r_e, r_i     |    0.00    |
    +--------------+------------+
    | tau_e, tau_i |    10.0    |
    +--------------+------------+
    | c_1          |    10.0    |
    +--------------+------------+
    | c_2          |    6.0     |
    +--------------+------------+
    | c_3          |    1.0     |
    +--------------+------------+
    | c_4          |    1.0     |
    +--------------+------------+
    | a_e, a_i     |    1.0     |
    +--------------+------------+
    | b_e, b_i     |    0.0     |
    +--------------+------------+
    | theta_e      |    2.0     |
    +--------------+------------+
    | theta_i      |    3.5     |
    +--------------+------------+
    | alpha_e      |    1.2     |
    +--------------+------------+
    | alpha_i      |    2.0     |
    +--------------+------------+
    | P            |    0.5     |
    +--------------+------------+
    | Q            |    0       |
    +--------------+------------+
    | c_e, c_i     |    1.0     |
    +--------------+------------+
    | alpha_e      |    1.2     |
    +--------------+------------+
    | alpha_i      |    2.0     |
    +--------------+------------+
    |                           |
    |  frequency peak at 20  Hz |
    |                           |
    +---------------------------+


    The parameters in Table 1 reproduce Figure A1 in  [D_2011]_
    but set the limit cycle frequency to a sensible value (eg, 20Hz).

    Model bifurcation parameters:
        * :math:`c_1`
        * :math:`P`



    The models (:math:`E`, :math:`I`) phase-plane, including a representation of
    the vector field as well as its nullclines, using default parameters, can be
    seen below:

        .. _phase-plane-WC:
        .. figure :: img/WilsonCowan_01_mode_0_pplane.svg
            :alt: Wilson-Cowan phase plane (E, I)

            The (:math:`E`, :math:`I`) phase-plane for the Wilson-Cowan model.

    .. automethod:: WilsonCowan.__init__

    The general formulation for the \textit{\textbf{Wilson-Cowan}} model as a
    dynamical unit at a node $k$ in a BNM with $l$ nodes reads:

    .. math::
            \dot{E}_k &= \dfrac{1}{\tau_e} (-E_k  + (k_e - r_e E_k) \mathcal{S}_e (\alpha_e \left( c_{ee} E_k - c_{ei} I_k  + P_k - \theta_e + \mathbf{\Gamma}(E_k, E_j, u_{kj}) + W_{\zeta}\cdot E_j + W_{\zeta}\cdot I_j\right) ))\\
            \dot{I}_k &= \dfrac{1}{\tau_i} (-I_k  + (k_i - r_i I_k) \mathcal{S}_i (\alpha_i \left( c_{ie} E_k - c_{ee} I_k  + Q_k - \theta_i + \mathbf{\Gamma}(E_k, E_j, u_{kj}) + W_{\zeta}\cdot E_j + W_{\zeta}\cdot I_j\right) )),

    """
    _ui_name = "Wilson-Cowan"
    ui_configurable_parameters = ['c_ee', 'c_ei', 'c_ie', 'c_ii', 'tau_e', 'tau_i',
                                  'a_e', 'b_e', 'c_e', 'a_i', 'b_i', 'c_i', 'r_e',
                                  'r_i', 'k_e', 'k_i', 'P', 'Q', 'theta_e', 'theta_i',
                                  'alpha_e', 'alpha_i', 'target', 'alpha_learn']
    local_homeo = False
    # Define traited attributes for this model, these represent possible kwargs.
    c_ee = arrays.FloatArray(
        label=":math:`c_{ee}`",
        default=numpy.array([12.0]),
        range=basic.Range(lo=11.0, hi=16.0, step=0.01),
        doc="""Excitatory to excitatory  coupling coefficient""",
        order=1)

    c_ie = arrays.FloatArray(
        label=":math:`c_{ei}`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=15.0, step=0.01),
        doc="""Inhibitory to excitatory coupling coefficient""",
        order=2)

    c_ei = arrays.FloatArray(
        label=":math:`c_{ie}`",
        default=numpy.array([13.0]),
        range=basic.Range(lo=2.0, hi=22.0, step=0.01),
        doc="""Excitatory to inhibitory coupling coefficient.""",
        order=3)

    c_ii = arrays.FloatArray(
        label=":math:`c_{ii}`",
        default=numpy.array([11.0]),
        range=basic.Range(lo=2.0, hi=15.0, step=0.01),
        doc="""Inhibitory to inhibitory coupling coefficient.""",
        order=4)

    tau_e = arrays.FloatArray(
        label=r":math:`\tau_e`",
        default=numpy.array([10.0]),
        range=basic.Range(lo=0.0, hi=150.0, step=0.01),
        doc="""Excitatory population, membrane time-constant [ms]""",
        order=5)

    tau_i = arrays.FloatArray(
        label=r":math:`\tau_i`",
        default=numpy.array([10.0]),
        range=basic.Range(lo=0.0, hi=150.0, step=0.01),
        doc="""Inhibitory population, membrane time-constant [ms]""",
        order=6)

    a_e = arrays.FloatArray(
        label=":math:`a_e`",
        default=numpy.array([1.2]),
        range=basic.Range(lo=0.0, hi=1.4, step=0.01),
        doc="""The slope parameter for the excitatory response function""",
        order=7)

    b_e = arrays.FloatArray(
        label=":math:`b_e`",
        default=numpy.array([2.8]),
        range=basic.Range(lo=1.4, hi=6.0, step=0.01),
        doc="""Position of the maximum slope of the excitatory sigmoid function""",
        order=8)

    c_e = arrays.FloatArray(
        label=":math:`c_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=1.0, hi=20.0, step=1.0),
        doc="""The amplitude parameter for the excitatory response function""",
        order=9)

    theta_e = arrays.FloatArray(
        label=r":math:`\theta_e`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=60., step=0.01),
        doc="""Excitatory threshold""",
        order=10)

    a_i = arrays.FloatArray(
        label=":math:`a_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""The slope parameter for the inhibitory response function""",
        order=11)

    b_i = arrays.FloatArray(
        label=r":math:`b_i`",
        default=numpy.array([4.0]),
        range=basic.Range(lo=2.0, hi=6.0, step=0.01),
        doc="""Position of the maximum slope of a sigmoid function [in
        threshold units]""",
        order=12)

    theta_i = arrays.FloatArray(
        label=r":math:`\theta_i`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=60.0, step=0.01),
        doc="""Inhibitory threshold""",
        order=13)

    c_i = arrays.FloatArray(
        label=":math:`c_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=1.0, hi=20.0, step=1.0),
        doc="""The amplitude parameter for the inhibitory response function""",
        order=14)

    r_e = arrays.FloatArray(
        label=":math:`r_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Excitatory refractory period""",
        order=15)

    r_i = arrays.FloatArray(
        label=":math:`r_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Inhibitory refractory period""",
        order=16)

    k_e = arrays.FloatArray(
        label=":math:`k_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.5, hi=2.0, step=0.01),
        doc="""Maximum value of the excitatory response function""",
        order=17)

    k_i = arrays.FloatArray(
        label=":math:`k_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=2.0, step=0.01),
        doc="""Maximum value of the inhibitory response function""",
        order=18)

    P = arrays.FloatArray(
        label=":math:`P`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the excitatory population.
        Constant intensity.Entry point for coupling.""",
        order=19)

    Q = arrays.FloatArray(
        label=":math:`Q`",
        default=numpy.array([0.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the inhibitory population.
        Constant intensity.Entry point for coupling.""",
        order=20)

    alpha_e = arrays.FloatArray(
        label=r":math:`\alpha_e`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the excitatory population.
        Constant intensity.Entry point for coupling.""",
        order=21)

    alpha_i = arrays.FloatArray(
        label=r":math:`\alpha_i`",
        default=numpy.array([1.0]),
        range=basic.Range(lo=0.0, hi=20.0, step=0.01),
        doc="""External stimulus to the inhibitory population.
        Constant intensity.Entry point for coupling.""",
        order=22)

    target = arrays.FloatArray(
        label=r":math:`target`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Learning Target""",
        order=6)

    alpha_learn = arrays.FloatArray(
        label=r":math:`alpha`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Learning Rate""",
        order=6)

    # Used for phase-plane axis ranges and to bound random initial() conditions.
    state_variable_range = basic.Dict(
        label="State Variable ranges [lo, hi]",
        default={"E": numpy.array([0.0, 1.0]),
                 "I": numpy.array([0.0, 1.0]),
                 "CIE": numpy.array([0.0, 1.0])},
        doc="""The values for each state-variable should be set to encompass
        the expected dynamic range of that state-variable for the current
        parameters, it is used as a mechanism for bounding random inital
        conditions when the simulation isn't started from an explicit history,
        it is also provides the default range of phase-plane plots.""",
        order=23)

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["E", "I", "E + I", "E - I", "CIE"],
        default=["E"],
        select_multiple=True,
        doc="""This represents the default state-variables of this Model to be
               monitored. It can be overridden for each Monitor if desired. The
               corresponding state-variable indices for this model are :math:`E = 0`
               and :math:`I = 1`.""",
        order=24)

    state_variables = 'E I CIE'.split()
    _nvar = 3
    cvar = numpy.array([0, 1, 3], dtype=numpy.int32)

    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""

        .. math::
            \tau \dot{x}(t) &= -z(t) + \phi(z(t)) \\
            \phi(x) &= \frac{c}{1-exp(-a (x-b))}

        """

        E = state_variables[0, :]
        I = state_variables[1, :]
        CIE = state_variables[2, :]

        if not self.local_homeo:
            CIE = self.c_ie

        derivative = numpy.empty_like(state_variables)

        # long-range coupling
        c_0 = coupling[0, :]

        # short-range (local) coupling
        lc_0 = local_coupling * E
        lc_1 = local_coupling * I

        x_e = self.alpha_e * (self.c_ee * E - self.c_ei * I + self.P  - self.theta_e +  c_0 + lc_0 + lc_1)
        x_i = self.alpha_i * (CIE * E - self.c_ii * I + self.Q  - self.theta_i + lc_0 + lc_1)

        s_e = self.c_e / (1.0 + numpy.exp(-self.a_e * (x_e - self.b_e)))
        s_i = self.c_i / (1.0 + numpy.exp(-self.a_i * (x_i - self.b_i)))

        if self.local_homeo:
            dW = self.alpha_learn * (I * (E - self.target))
        else:
            dW = 0

        derivative[0] = (-E + (self.k_e - self.r_e * E) * s_e) / self.tau_e
        derivative[1] = (-I + (self.k_i - self.r_i * I) * s_i) / self.tau_i
        derivative[2] = dW

        return derivative




class ExtReducedWongWang(Model):
    r"""
    .. [WW_2006] Kong-Fatt Wong and Xiao-Jing Wang,  *A Recurrent Network
                Mechanism of Time Integration in Perceptual Decisions*.
                Journal of Neuroscience 26(4), 1314-1328, 2006.

    .. [DPA_2013] Deco Gustavo, Ponce Alvarez Adrian, Dante Mantini, Gian Luca
                  Romani, Patric Hagmann and Maurizio Corbetta. *Resting-State
                  Functional Connectivity Emerges from Structurally and
                  Dynamically Shaped Slow Linear Fluctuations*. The Journal of
                  Neuroscience 32(27), 11239-11252, 2013.



    .. automethod:: ReducedWongWang.__init__

    Equations taken from [DPA_2013]_ , page 11242

    .. math::
                 x_k       &=   w\,J_N \, S_k + I_o + J_N \mathbf\Gamma(S_k, S_j, u_{kj}),\\
                 H(x_k)    &=  \dfrac{ax_k - b}{1 - \exp(-d(ax_k -b))},\\
                 \dot{S}_k &= -\dfrac{S_k}{\tau_s} + (1 - S_k) \, H(x_k) \, \gamma

    """
    _ui_name = "Extended Reduced Wong-Wang"
    ui_configurable_parameters = ['a', 'b', 'd', 'gamma', 'tau_s', 'w', 'J_N', 'I_o']
    local_homeo = False # this will be important later, but breaks stuff if it is traited.
    # Define traited attributes for this model, these represent possible kwargs.
    a = arrays.FloatArray(
        label=":math:`a`",
        default=numpy.array([0.270, ]),
        range=basic.Range(lo=0.0, hi=0.270, step=0.01),
        doc="[n/C]. Input gain parameter, chosen to fit numerical solutions.",
        order=1)

    b = arrays.FloatArray(
        label=":math:`b`",
        default=numpy.array([0.108, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="[kHz]. Input shift parameter chosen to fit numerical solutions.",
        order=2)

    d = arrays.FloatArray(
        label=":math:`d`",
        default=numpy.array([154., ]),
        range=basic.Range(lo=0.0, hi=200.0, step=0.01),
        doc="""[ms]. Parameter chosen to fit numerical solutions.""",
        order=3)

    gamma = arrays.FloatArray(
        label=r":math:`\gamma`",
        default=numpy.array([0.641, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Kinetic parameter""",
        order=4)

    tau_s = arrays.FloatArray(
        label=r":math:`\tau_S`",
        default=numpy.array([100., ]),
        range=basic.Range(lo=50.0, hi=150.0, step=1.0),
        doc="""Kinetic parameter. NMDA decay time constant.""",
        order=5)

    w = arrays.FloatArray(
        label=r":math:`w`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Excitatory recurrence""",
        order=6)

    target = arrays.FloatArray(
        label=r":math:`w`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Learning Target""",
        order=6)

    alpha = arrays.FloatArray(
        label=r":math:`w`",
        default=numpy.array([0.6, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""Learning Rate""",
        order=6)

    J_N = arrays.FloatArray(
        label=r":math:`J_{N}`",
        default=numpy.array([0.2609, ]),
        range=basic.Range(lo=0.2609, hi=0.5, step=0.001),
        doc="""Excitatory recurrence""",
        order=7)

    I_o = arrays.FloatArray(
        label=":math:`I_{o}`",
        default=numpy.array([0.33, ]),
        range=basic.Range(lo=0.0, hi=1.0, step=0.01),
        doc="""[nA] Effective external input""",
        order=8)

    sigma_noise = arrays.FloatArray(
        label=r":math:`\sigma_{noise}`",
        default=numpy.array([0.000000001, ]),
        range=basic.Range(lo=0.0, hi=0.005),
        doc="""[nA] Noise amplitude. Take this value into account for stochatic
        integration schemes.""",
        order=-1)

    state_variable_range = basic.Dict(
        label="State variable ranges [lo, hi]",
        default={"S": numpy.array([0.0, 1.0]),
                 "W": numpy.array([0.0, 1.0])},
        doc="Population firing rate, and Excitatory recurrance.",
        order=9
    )

    variables_of_interest = basic.Enumerate(
        label="Variables watched by Monitors",
        options=["S", "W"],
        default=["S", "W"],
        select_multiple=True,
        doc="""default state variables to be monitored""",
        order=10)

    state_variables = 'S W'.split()
    _nvar = 2
    cvar = numpy.array([0, 1], dtype=numpy.int32)

    def dfun(self, state_variables, coupling, local_coupling=0.0):
        r"""
        Equations taken from [DPA_2013]_ , page 11242

        .. math::
                 x_k       &=   w\,J_N \, S_k + I_o + J_N \mathbf\Gamma(S_k, S_j, u_{kj}),\\
                 H(x_k)    &=  \dfrac{ax_k - b}{1 - \exp(-d(ax_k -b))},\\
                 \dot{S}_k &= -\dfrac{S_k}{\tau_s} + (1 - S_k) \, H(x_k) \, \gamma

        """
        S = state_variables[0, :]
        if self.local_homeo:
            W = state_variables[1, :]
        else:
            W = self.w  # this is whatever W was supposed to be dammit!
        derivative = numpy.empty_like(state_variables)

        S[S < 0] = 0.
        S[S > 1] = 1.
        c_0 = coupling[0, :]

        # if applicable
        lc_0 = local_coupling * S

        x = W * self.J_N * S + self.I_o + self.J_N * c_0 + self.J_N * lc_0
        H = (self.a * x - self.b) / (1 - numpy.exp(-self.d * (self.a * x - self.b)))
        dS = - (S / self.tau_s) + (1 - S) * H * self.gamma

        if self.local_homeo:
            dW = - W * (self.alpha * (S - self.target))
        else:
            dW = 0;

        # self.model.alpha * (_x - self.model.target)
        # self.model.w = self.model.w - _w
        # self.model.w[self.model.w < 0] = 0  # heaviside this
        #
        derivative[0] = numpy.array([dS])
        derivative[1] = numpy.array([dW])
        return derivative

    def rww_compute_h(self, x):
        ''' This is a function to recover H. As it's important...'''
        h = (self.a * x - self.b) / (1 - np.exp(-self.d * (self.a * x - self.b)))
        return h




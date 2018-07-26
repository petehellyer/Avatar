#!/usr/bin/env python
#SBATCH -p verylong

import os
from argparse import ArgumentParser
import pickle
import numpy as np
from sklearn.decomposition import PCA
from sklearn.utils import check_random_state
from sklearn.utils.extmath import randomized_svd, svd_flip
from scipy import linalg

import scipy.io
import seaborn as sns
sns.set_style("darkgrid")

from utilities import discard_warm_up_time


# redefine sklearn's PCA so that it does not demean data
class notDemeanedPCA(PCA):

    def _fit_truncated(self, X, n_components, svd_solver):
        """Fit the model by computing truncated SVD (by ARPACK or randomized)
        on X
        """
        n_samples, n_features = X.shape

        if isinstance(n_components, six.string_types):
            raise ValueError("n_components=%r cannot be a string "
                             "with svd_solver='%s'"
                             % (n_components, svd_solver))
        elif not 1 <= n_components <= n_features:
            raise ValueError("n_components=%r must be between 1 and "
                             "n_features=%r with svd_solver='%s'"
                             % (n_components, n_features, svd_solver))
        elif svd_solver == 'arpack' and n_components == n_features:
            raise ValueError("n_components=%r must be stricly less than "
                             "n_features=%r with svd_solver='%s'"
                             % (n_components, n_features, svd_solver))

        random_state = check_random_state(self.random_state)

        if svd_solver == 'arpack':
            # random init solution, as ARPACK does it internally
            v0 = random_state.uniform(-1, 1, size=min(X.shape))
            U, S, V = linalg.svds(X, k=n_components, tol=self.tol, v0=v0)
            # svds doesn't abide by scipy.linalg.svd/randomized_svd
            # conventions, so reverse its outputs.
            S = S[::-1]
            # flip eigenvectors' sign to enforce deterministic output
            U, V = svd_flip(U[:, ::-1], V[::-1])

        elif svd_solver == 'randomized':
            # sign flipping is done inside
            U, S, V = randomized_svd(X, n_components=n_components,
                                     n_iter=self.iterated_power,
                                     flip_sign=True,
                                     random_state=random_state)

        self.n_samples_, self.n_features_ = n_samples, n_features
        self.components_ = V
        self.n_components_ = n_components

        # Get variance explained by singular values
        self.explained_variance_ = (S ** 2) / n_samples
        total_var = np.var(X, axis=0)
        self.explained_variance_ratio_ = \
            self.explained_variance_ / total_var.sum()
        if self.n_components_ < n_features:
            self.noise_variance_ = (total_var.sum() -
                                    self.explained_variance_.sum())
        else:
            self.noise_variance_ = 0.

        return U, S, V

    def _fit_full(self, X, n_components):
        """Fit the model by computing full SVD on X"""
        n_samples, n_features = X.shape

        if n_components == 'mle':
            if n_samples < n_features:
                raise ValueError("n_components='mle' is only supported "
                                 "if n_samples >= n_features")
        elif not 0 <= n_components <= n_features:
            raise ValueError("n_components=%r must be between 0 and "
                             "n_features=%r with svd_solver='full'"
                             % (n_components, n_features))

        U, S, V = linalg.svd(X, full_matrices=False)
        # flip eigenvectors' sign to enforce deterministic output
        U, V = svd_flip(U, V)

        components_ = V

        # Get variance explained by singular values
        explained_variance_ = (S ** 2) / n_samples
        total_var = explained_variance_.sum()
        explained_variance_ratio_ = explained_variance_ / total_var

        # Postprocess the number of components required
        if 0 < n_components < 1.0:
            # number of components for which the cumulated explained
            # variance percentage is superior to the desired threshold
            ratio_cumsum = explained_variance_ratio_.cumsum()
            n_components = np.searchsorted(ratio_cumsum, n_components) + 1

        # Compute noise covariance using Probabilistic PCA model
        # The sigma2 maximum likelihood (cf. eq. 12.46)
        if n_components < min(n_features, n_samples):
            self.noise_variance_ = explained_variance_[n_components:].mean()
        else:
            self.noise_variance_ = 0.

        self.n_samples_, self.n_features_ = n_samples, n_features
        self.components_ = components_[:n_components]
        self.n_components_ = n_components
        self.explained_variance_ = explained_variance_[:n_components]
        self.explained_variance_ratio_ = \
            explained_variance_ratio_[:n_components]

        return U, S, V


def run_pca_analysis(simulation):

    # delete the first time points necessary for the model to reach a
    # stabilisation and adjust shape of the matrix
    simulation = discard_warm_up_time(simulation)
    X = simulation['hs']
    svd = notDemeanedPCA(n_components=.95, random_state=0)
    X2 = svd.fit_transform(X)
    ncomponent = X2.shape[1]

    # Get the maximung firing rate. Save the maximum firing rate for the first
    # two compoments
    result = []
    result.append(np.max(X2[:, 0], axis=0))
    # If there are more then 2 components save the firing rate of the second
    # compoment. Otherwise just save 0
    if X2.shape[1] > 1:
        result.append(np.max(X2[:, 1], axis=0))
    else:
        result.append(0)
    return ncomponent, result

if __name__ == '__main__':
    parser = ArgumentParser(
    description='Run Grid Search pararelly'
    )
    parser.add_argument(
        '--alpha',
        dest='alpha',
        type=float,
        help='Alpha for the current iteration'
    )
    parser.add_argument(
        '--target',
        dest='target',
        type=float,
        help='Target for the current iteration'
    )
    parser.add_argument(
        '--testn',
        dest='testn',
        type=int,
        help='Test number'
    )
    parser.add_argument(
        '--gmax',
        dest='g_max',
        type=float,
        help='Max G'
    )
    parser.add_argument(
        '--gmin',
        dest='g_min',
        type=float,
        help='Min G'
    )
    parser.add_argument(
        '--gsteps',
        dest='g_steps',
        type=float,
        help='Range of g to iterate over'
    )
    parser.add_argument(
        '--noise',
        dest='noise',
        type=float,
        help='Noise to add to the system'
    )

    args = parser.parse_args()

    print args.alpha, args.target, args.g_max, args.g_min, args.g_steps

    # initial conditions
    initial_condtions = np.arange(0, 1.25, .25) # 1.25 cause np.arange is last exclisive
    n_initial_conditions = len(initial_condtions)

    g_range = np.arange(args.g_min, args.g_max, args.g_steps)
    base_path = os.path.join(os.path.dirname(os.getcwd()), 'Output',
            'simulation', 'without_behaviour', 'without_homeostasis', 'bifurcation')
    print ('Using mat file from: %s' %base_path)

    results = np.zeros((2, g_range.shape[0]))
    ncomponents = np.zeros((g_range.shape[0]))

    all_results = {}
    # load the mat data with the simulation
    for idx_g, g_i in enumerate(g_range):
        tmp_simulation = {}
        tmp_simulation['hs'] = 0
        tmp_simulation['xs'] = 0
        tmp_simulation['ws'] = 0
        for initial_condition in initial_condtions:
            matfile = os.path.join(base_path, '%.02f_%.02f_%.03f.mat' % (initial_condition, args.target, g_i))
            simulation = scipy.io.loadmat(matfile)
            tmp_simulation['hs'] += simulation['hs']
            tmp_simulation['xs'] += simulation['xs']
            tmp_simulation['ws'] += simulation['ws']
        tmp_simulation['hs'] /= len(initial_condtions)
        tmp_simulation['ws'] /= len(initial_condtions)
        tmp_simulation['ws'] /= len(initial_condtions)
        ncomponents[idx_g], results[:, idx_g] = run_pca_analysis(tmp_simulation)

    print 'done iterating over all gs'
    all_results['ncomponents'] = ncomponents
    all_results['max_hs'] = results
    pickle.dump(all_results,
                open(os.path.join(base_path, 'PCA_results.pickle'),
                             'wb'))
    print 'Done all this!'



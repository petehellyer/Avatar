import os
import numpy as np
from sklearn.mixture import GaussianMixture

from scipy.io import loadmat


def binner(A, dt):
    binned = []
    end = len(A)
    for t in range(0, A.shape[0], dt):
        binned = np.append(binned, sum(A[t:min(t + dt, end)]))
    return binned


def critical_stats(sizes):
    # calculates avalanche statistics
    critical = {}
    critical['branching_parameter'] = np.zeros((len(sizes)))
    critical['lengths_hist'] = np.zeros(len(sizes))
    critical['lengths'] = []
    critical['starts'] = []
    critical['event_size'] = []
    counter = 0
    for k in range(len(sizes)):
        if sizes[k] > 0:
            if counter == 0:
                critical['starts'] = np.append(critical['starts'], k)
            counter += 1
            if 1 < counter < 3:
                critical['branching_parameter'][k] = np.divide(sizes[k], sizes[k-1])
        if sizes[k] == 0 and counter > 0:
            critical['lengths_hist'][counter - 1] += 1
            critical['lengths'] = np.append(critical['lengths'], counter)
            critical['event_size'] = np.append(critical['event_size'], sum(sizes[k - counter:k]))
            counter = 0
        if k == len(sizes) - 1 and counter > 0:
            critical['lengths_hist'][counter - 1] += 1
            critical['lengths'] = np.append(critical['lengths'], counter)
            critical['event_size'] = np.append(critical['event_size'], sum(sizes[max(0, k - counter):k]))
            counter = 0
    # loop through events
    for i in range(len(critical['starts'])):
        critical['ava_shape'][i] = sizes[critical['starts'][i]:
                                         critical['starts'][i] + critical['lengths'][i]]

def pointprocess(data, k, thres, cluster):

    pp = data * 0
    if cluster == 'gmm':
        # get binary time series using Gaussian Mixture Model
        # reshape data into correct format to pass to Gaussian Mixture model
        X = np.expand_dims(np.ndarray.flatten(data, order='F'), 1)
        # number of components
        gmm = GaussianMixture(n_components=k)
        gmm.fit(X)
        posterior = gmm.predict_proba(X)
        # get index of max value
        i_mu = np.argmax(gmm.means_)
        # reshape data to have 4 columns
        data = posterior[:, i_mu].reshape((data.shape)) > thres

        # Discretise time series with bins of duration DT
        for n in range(data.shape[0]):
            tmp = np.transpose(data[n, :])
            # check if there are adjacent activity
            tmp = (np.diff(tmp) == 1)*1
            # diff returns n-1, so the next line inserts a 0 to the begin of the array
            pp[n, :] = np.insert(tmp, 0, 0)
        return pp
    elif cluster == 'kmeans':
        # do something else
        return

    return

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------
thres = 0.95
k = 2
BinWidth = 10

# get data
data = loadmat('mydata.mat')
data = data['original_data']

sizes = sum(pointprocess(data, k, thres, 'gmm'))
sizes = binner(sizes, BinWidth)
critical = critical_stats(sizes)

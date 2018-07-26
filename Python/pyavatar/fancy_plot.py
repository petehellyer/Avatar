import matplotlib
matplotlib.use('TKAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import scipy.io.matlab as scmat

# Load the data
#ml = scmat.loadmat('1_0.0000015_0.20.mat')
#ml = scmat.loadmat('tmp_two_no_beh.mat') #does not have spatial data
#ml = scmat.loadmat('tmp.mat')# 2e-05
ml = scmat.loadmat('results_testn_0.mat')

psx = (ml['posx'] - 1000)/7
psz = (ml['posz'] - 1000)/7

xs = ml['xs']
t = np.squeeze(ml['ts'])

# Size of tray of the avatar, or amount of points plots
window_size = 200
# because we have too many data, we are down sampling the array.
slicing_step = 1

# Process the position and firing rate of the avatar to be plotted in a
# meaninfull way
psx_sliced = psx[0, 370000:570000:slicing_step]
psz_sliced = psz[0, 370000:570000:slicing_step]

xs_sliced = xs[370000:570000:slicing_step]
# get mean activity over all nodes for each instance of time
xs_sliceded_mean = np.mean(xs_sliced, axis=1)
t_sliced = t[370000:570000:slicing_step]

# create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(2,1)

# intialize two line objects (one in each axes)
graph1, = ax1.plot([], [], 'o')
graph2, = ax2.plot([], [], '-')
graph = [graph1, graph2]

# axes initalization
ax1.set_ylim(-1, 1)
ax1.set_xlim(-1, 1)
# Force first plot to be square
x0,x1 = ax1.get_xlim()
y0,y1 = ax1.get_ylim()
ax1.set_aspect(abs(x1-x0)/abs(y1-y0))
ax1.grid()

ax2.set_ylim(0, 1)
ax2.set_xlim(0, psx_sliced.shape[0])
ax2.grid()


def animate(i):
    graph[0].set_data(psx_sliced[i:i+window_size],
                      psz_sliced[i:i+window_size])
    graph[1].set_data(np.arange(0, i+window_size),
                      xs_sliceded_mean[0:i+window_size])


ani = FuncAnimation(fig, animate, np.arange(psx_sliced.shape[0] - window_size),
                    interval=1, repeat=False)
plt.show()


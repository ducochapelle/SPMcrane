from numpy.random import uniform, seed
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import numpy as np
# make up data.
#npts = int(raw_input('enter # of random points to plot:'))
# seed(0)
# npts = 200
# x = uniform(-2, 2, npts)
# y = uniform(-2, 2, npts)
# z = x*np.exp(-x**2 - y**2)
# define grid.
# xi = np.linspace(-2.1, 2.1, 100)
# yi = np.linspace(-2.1, 2.1, 200)
# grid the data.
# zi = griddata(x, y, z, xi, yi, interp='linear')
# contour the gridded data, plotting dots at the nonuniform data points.
# CS = plt.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
# CS = plt.contourf(xi, yi, zi, 15, cmap=plt.cm.rainbow,
#                   vmax=abs(zi).max(), vmin=-abs(zi).max())
# plt.colorbar()  # draw colorbar
# plot data points.
# plt.scatter(x, y, marker='o', c='b', s=5, zorder=10)
# plt.xlim(-2, 2)
# plt.ylim(-2, 2)
# plt.title('griddata test (%d points)' % npts)
# plt.show()

import csv
data,xs,zs,ts = [],[],[],[]
xmin, xmax, zmin, zmax = 0,35000,-10000,35000
offset = 1000
with open("spm.out",'r') as f:
    header = f.next()
    units = f.next()
    metadata = dict(zip(header.split(),units.split()))
    for r in f:
        data.append(dict(zip(header.split(), r.split())))
for record in filter(lambda r: r["load"]=="3.",data):
    x = record["reach-X"]
    z = record["reach-Z"]
    smlr = lambda r: r["reach-X"] == x and r["reach-Z"] == z
    maxr = lambda r: (max([r["fbmax"],r["fbmin"],r["fbbuc"],r["fjmax"],r["fjmin"],r["fjbuc"]]),r)
    p = map(maxr,filter(smlr, data))
    p.sort()
    p.reverse()
    for p2 in p:
        if float(p2[0])<=1.: 
            xs += [float(x)]
            zs += [float(z)]
            ts += [float(p2[1]["load"])]
            break

xi = np.linspace(xmin-offset,xmax+offset, 2000)
zi = np.linspace(zmin-offset,zmax+offset, 2000)
ti = griddata(xs, zs, ts, xi, zi, interp='linear')
ti.set_fill_value(0.0)
CS = plt.contour(xi, zi, ti, [0,3,5,10], linewidths=1, colors='k')
CS = plt.contourf(xi, zi, ti,[0,3,5,10], cmap=plt.cm.rainbow,
                  vmax=abs(ti).max(), vmin=-abs(ti).max())
plt.colorbar()  # draw colorbar
plt.scatter(xs, zs, marker='o', c='b', s=5, zorder=10)
plt.xlim(xmin, xmax)
plt.ylim(zmin, zmax)

npts = 3
plt.title('load curve (%d points)' % len(xs))
plt.show()

# meh

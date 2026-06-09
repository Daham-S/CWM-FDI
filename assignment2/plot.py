# !/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt


# parameters to modify 
filename="data_03.txt"
label='Python'
xlabel = 'Time (ns)'
ylabel = 'CDF (Prob of being less than T)'
title='CDF of Ping RTT over 1000 iterations, interval 0.0001'
fig_name='my_graph.png'
bins=100 #adjust the number of bins to your plot

## load data from input file
t = np.loadtxt(filename, delimiter=" ", dtype="float")


## if your data is "X Y" (2 cols), use the following line
#plt.plot(t[:,0], t[:,1], label=label)  # Plot some data on the (implicit) axes.

## if your data is "X" (1 col), use the following line
#plt.plot(t, label=label)  # Plot some data on the (implicit) axes.

## comment the lines above and uncomment the line below to plot a simple CDF
#plt.hist(t[:], bins, density=True, histtype='step', cumulative=True, label=label)

## comment the lines above and uncomment the 4 lines below for a nicer CDF
n = np.arange(1,len(t)+1) / float(len(t))
ts = np.sort(t)
fig, ax = plt.subplots()
ax.step(ts,n)

# important values
min = ts[0]
max = ts[-1]
mean = np.mean(ts)
median = np.median(ts)
percentile_90 = np.percentile(ts,90)
percentile_99 = np.percentile(ts,99)

print(f"Mean is {mean: .2f}")
print(f"Median is {median: .2f}")
print(f"90th Percentile is {percentile_90: .2f}")
print(f"99th Percentile is {percentile_99: .2f}")
print(f"Maximum is {max: .2f}")
print(f"Minimum is {min: .2f}")







plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.legend()
plt.savefig(fig_name)
plt.show()

import numpy as np
import matplotlib.pyplot as plt

ticksize = 13
labelsize = 15

# voltage traces
voltage = np.loadtxt("voltage_data.dat")

f,(ax,ax2) = plt.subplots(1,2, facecolor='w')
ax.plot(voltage[0,:], voltage[1,:], linewidth=2.0, color="royalblue", label="V_m tsodyks_synapse")
ax.plot(voltage[0,:], voltage[2,:], "--", linewidth=2.0, color="red", label="V_m tsodyks2_synapse")
ax.plot(voltage[0,:], voltage[3,:], "-.", linewidth=2.0, color="orange", label="V_m tsodyks3_synapse")
ax2.plot(voltage[0,:], voltage[1,:], linewidth=2.0, color="royalblue", label="V_m tsodyks_synapse")
ax2.plot(voltage[0,:], voltage[2,:], "--", linewidth=2.0, color="red", label="V_m tsodyks2_synapse")
ax2.plot(voltage[0,:], voltage[3,:], "-.", linewidth=2.0, color="orange", label="V_m tsodyks3_synapse")

ax.set_xlim(0,600)
ax2.set_xlim(1490,1950)

ax.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax.yaxis.tick_left()
ax.set_ylabel(r"$V_m$ [mV]", fontsize=labelsize)
ax.tick_params(labelsize=ticksize)
ax2.yaxis.tick_right()
ax2.tick_params(labelright='on', labelsize=ticksize)
ax2.yaxis.set_label_position("right")
ax2.set_ylabel(r"$V_m$ [mV]", fontsize=labelsize)
ax.xaxis.set_label_coords(1.05, -0.075)
ax.set_xlabel("Time [ms]", fontsize=labelsize)


d = .015 
kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
ax.plot((1-d,1+d), (-d,+d), **kwargs)
ax.plot((1-d,1+d),(1-d,1+d), **kwargs)

kwargs.update(transform=ax2.transAxes) 
ax2.plot((-d,+d), (1-d,1+d), **kwargs)
ax2.plot((-d,+d), (-d,+d), **kwargs)

ax.grid()
ax2.grid()
ax.legend(fontsize=labelsize, loc = "upper left")
plt.show()




























plt.show()
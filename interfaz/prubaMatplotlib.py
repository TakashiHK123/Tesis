import matplotlib.pyplot as plt


plt.rc('font', size=12)          # controls default text sizes
plt.rc('axes', titlesize=16)     # fontsize of the axes title
plt.rc('axes', labelsize=16)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=14)    # fontsize of the tick labels
plt.rc('ytick', labelsize=13)    # fontsize of the tick labels

plt.figure(1)
b=plt.plot([69,42],[42,69])
plt.figure(2)
a=plt.plot([690,420,8],[420,690,0])

print(plt.figure(2))
# plt.clf()
#plt.plot([1,2],[1,2])
#plt.show()
print(plt.gcf())
a=plt.gcf()
a.savefig("adhabhdha.png")
# plt.show()


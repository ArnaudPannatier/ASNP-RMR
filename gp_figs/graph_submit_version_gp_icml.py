##################################################################
# graph drawing
##################################################################
import os, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

#plt_style = 'ggplot'
plt_style = 'seaborn-paper'
plt.style.use(plt_style)

img_name = 'gp_graph.png'

time_printing = True
#time_printing = False

###############################################################################
# task a option

prefix = '../logs_gp_a/'
dirs_a = [
    '10-17,15:46:54.040597', #NP(h=128)
    '11-06,17:25:05.183065', #NP(h=512)
    '09-06,17:57:54.062946', #ANP(h=128)
    '11-06,17:25:09.696126', #ANP(h=512)
    '10-17,15:46:57.296676', #SNP(h=128)
    '11-06,17:25:03.213940', #SNP(h=512)
    '01-27,10:40:58.274395', #SNP(h=1024)
    '11-07,12:05:24.432223', #SNPK(h=128,K=1)
    '11-11,18:17:46.241572', #SNPK(h=128,K=3)
    '11-11,18:16:58.774438', #SNPK(h=128,K=5)
    '11-11,18:59:57.248192', #SNPK(h=128,K=inf)
    '09-06,17:57:56.149375', #ASNP(h=128,K=25)
    ]
for i in range(len(dirs_a)):
    dirs_a[i] = prefix+dirs_a[i]

###############################################################################
# task b option

prefix = '../logs_gp_b/'
dirs_b = [
    '10-17,15:46:57.525708', #NP(h=128)
    '11-11,10:29:11.869916', #NP(h=512)
    '09-06,17:58:00.855880', #ANP(h=128)
    '11-11,10:29:08.790430', #ANP(h=512)
    '10-17,15:47:08.129047', #SNP(h=128)
    '11-11,10:31:23.813602', #SNP(h=512)
    '11-11,10:31:23.813602', #SNP(h=512)
    '11-06,17:19:09.386418', #SNPK(h=128,K=1)
    '11-11,19:00:33.852374', #SNPK(h=128,K=3)
    '11-11,18:16:46.436511', #SNPK(h=128,K=5)
    '11-11,18:16:48.435383', #SNPK(h=128,K=inf)
    '09-06,17:58:05.845190', #ASNP(h=128,K=25)
     ]
for i in range(len(dirs_b)):
    dirs_b[i] = prefix+dirs_b[i]

###############################################################################
# task c option

prefix = '../logs_gp_c/'
dirs_c = [
    '10-17,10:09:58.476452', #NP(h=128)
    '11-11,10:29:08.816456', #NP(h=512)
    '09-06,18:01:10.611041', #ANP(h=128)
    '11-11,10:29:11.249562', #ANP(h=512)
    '10-17,10:09:56.252036', #SNP(h=128)
    '01-28,21:03:11.882055', #SNP(h=512)
    '01-27,10:40:52.881457', #SNP(h=1024)
    '11-06,17:19:10.271166', #SNPK(h=128,K=1)
    '11-11,18:17:58.070309', #SNPK(h=128,K=3)
    '11-11,18:17:44.161261', #SNPK(h=128,K=5)
    '11-11,18:17:54.618255', #SNPK(h=128,K=inf)
    '09-06,17:59:54.232008', #ASNP(h=128,K=25)
     ]
for i in range(len(dirs_c)):
    dirs_c[i] = prefix+dirs_c[i]

###############################################################################

smoothing = 100

labels = [
    'NP(h=128)',
    'NP(h=512)',
    'ANP(h=128)',
    'ANP(h=512)',
    'SNP(h=128)',
    'SNP(h=512)',
    'SNP(h=1024)',
    'SNPK(h=128,K=1)',
    'SNPK(h=128,K=3)',
    'SNPK(h=128,K=5)',
    'SNPK(h=128,K=inf)',
    'ASNP(h=128,K=25)',
          ]

# get data from Tensorboard logs
vals_a, iters_a = [], []
min_iter_a = 10000000000
for d_idx, dir_name in enumerate(dirs_a):
    print(dir_name)
    summ = [EventAccumulator(dir_name).Reload()]

    tags = summ[0].Tags()['scalars']

    out = defaultdict(list)
    steps = []

    for tag in tags:
        for events in zip(*[acc.Scalars(tag) for acc in summ]):
            out[tag].append([e.value for e in events])
    steps = [e.step for e in summ[0].Scalars(tag)]

    if time_printing:
        times = np.array([e.wall_time for e in summ[0].Scalars(tag)])
        times = times - times[0]
        tnll = out['TargetNLL/Nll']
        outstr = ''
        for t_idx, (t, nll) in enumerate(zip(times,tnll)):
            if t_idx % 50 == 0:
                outstr+='('+str(t)+','+str(nll[0])+')'
        print('task a',labels[d_idx])
        print(outstr)

    vals_a.append(out)
    iters_a.append(steps)

    if steps[-1] < min_iter_a:
        min_iter_a = steps[-1]

vals_b, iters_b = [], []
min_iter_b = 10000000000
for d_idx, dir_name in enumerate(dirs_b):
    print(dir_name)
    summ = [EventAccumulator(dir_name).Reload()]

    tags = summ[0].Tags()['scalars']

    out = defaultdict(list)
    steps = []

    for tag in tags:
        for events in zip(*[acc.Scalars(tag) for acc in summ]):
            out[tag].append([e.value for e in events])
    steps = [e.step for e in summ[0].Scalars(tag)]

    if time_printing:
        times = np.array([e.wall_time for e in summ[0].Scalars(tag)])
        times = times - times[0]
        tnll = out['TargetNLL/Nll']
        outstr = ''
        for t_idx, (t, nll) in enumerate(zip(times,tnll)):
            if t_idx % 50 == 0:
                outstr+='('+str(t)+','+str(nll[0])+')'
        print('task b',labels[d_idx])
        print(outstr)

    vals_b.append(out)
    iters_b.append(steps)

    if steps[-1] < min_iter_b:
        min_iter_b = steps[-1]

vals_c, iters_c = [], []
min_iter_c = 10000000000
for d_idx, dir_name in enumerate(dirs_c):
    print(dir_name)
    summ = [EventAccumulator(dir_name).Reload()]

    tags = summ[0].Tags()['scalars']

    out = defaultdict(list)
    steps = []

    for tag in tags:
        for events in zip(*[acc.Scalars(tag) for acc in summ]):
            out[tag].append([e.value for e in events])
    steps = [e.step for e in summ[0].Scalars(tag)]

    if time_printing:
        times = np.array([e.wall_time for e in summ[0].Scalars(tag)])
        times = times - times[0]
        tnll = out['TargetNLL/Nll']
        outstr = ''
        for t_idx, (t, nll) in enumerate(zip(times,tnll)):
            if t_idx % 50 == 0:
                outstr+='('+str(t)+','+str(nll[0])+')'
        print('task c',labels[d_idx])
        print(outstr)

    vals_c.append(out)
    iters_c.append(steps)

    if steps[-1] < min_iter_c:
        min_iter_c = steps[-1]

if time_printing:
    exit(1)

# smoothing
tag_list_ab = []
for i in range(20):
    tag_list_ab.append('TargetNLL/nll_'+str(i))
tag_list_c = []
for i in range(50):
    tag_list_c.append('TargetNLL/nll_'+str(i))

data_a = []
for val, iteration in zip(vals_a, iters_a):
    _data = []
    for tag in tag_list_ab:
        iter_idx = iteration.index(min_iter_a)
        #_data.append(np.mean(val[tag][(iter_idx-smoothing):iter_idx]))
        _data.append(np.mean(val[tag][-smoothing:]))
    data_a.append(_data)

data_b = []
for val, iteration in zip(vals_b, iters_b):
    _data = []
    for tag in tag_list_ab:
        iter_idx = iteration.index(min_iter_b)
        #_data.append(np.mean(val[tag][(iter_idx-smoothing):iter_idx]))
        _data.append(np.mean(val[tag][-smoothing:]))
    data_b.append(_data)

data_c = []
for val, iteration in zip(vals_c, iters_c):
    _data = []
    for tag in tag_list_c:
        iter_idx = iteration.index(min_iter_c)
        #_data.append(np.mean(val[tag][(iter_idx-smoothing):iter_idx]))
        _data.append(np.mean(val[tag][-smoothing:]))
    data_c.append(_data)

cm = plt.cm.get_cmap('tab20').colors
line_color_map = [cm[0]]*len(labels)
#line_color_map = [
#                  cm[0],
#                  cm[4],
#                  cm[6],
#                  cm[8],
#                  cm[10],
#                 ]

linestyle = ['-']*len(labels)
#linestyle = ['-','-','-','-','-']

# plotting
top = 0.09
bottom = 0.14
height = 1 - top - bottom
width = 0.278
wspace = 0.048
left1 = 0.066
left2 = left1 + width + wspace
wspace = 0.048
left3 = left2 + width + wspace

rec1 = [left1, bottom, width, height]
rec2 = [left2, bottom, width, height]
rec3 = [left3, bottom, width, height]


plt.figure(figsize=(6.4*3, 4.8))
ax1 = plt.axes(rec1)
#plt.subplot(1,4,1)
for i in range(len(dirs_a)):
    #plt.plot(list(range(1,len(tag_list_ab)+1)),
    ax1.plot(list(range(1,len(tag_list_ab)+1)),
             data_a[i],
             color=line_color_map[i],
             label=labels[i],
             linewidth=2,
             linestyle=linestyle[i])
    print("task a")
    print(labels[i])
    d_str = ""
    for j in range(1,len(tag_list_ab)+1):
        d_str+= "("
        d_str+=str(j)+","
        d_str+= str(data_a[i][j-1])
        d_str+= ")"
    print(d_str)

# make plot pretty
#plt.grid(True)
ax1.grid(True)
axes = plt.gca()
#axes = ax1.gca()
#plt.yticks(list(range(-0.2,1.4,0.2)),fontsize=12)
plt.yticks(fontsize=18)
#ax1.set_yticklabels(list(range(-0.2,1.4,0.2)),fontsize=13)
#axes.set_ylim([-0.5, 1.3])
plt.xticks(list(range(1,26,3)),fontsize=18)
#ax1.set_xticklabels(list(range(1,26,2)),fontsize=13)
#axes.set_xlim([1.0, 20.0])
ax1.set_xlim([1.0, 20.0])
#plt.xlabel('Time',fontsize=14)
ax1.set_xlabel('Time',fontsize=19)
#plt.ylabel('Target NLL',fontsize=14)
ax1.set_ylabel('Target NLL',fontsize=19)
#legend = plt.legend(bbox_to_anchor=(0.08, 0.99), title="Model (setting)", loc=2, ncol=1, fontsize=14)
#legend = ax1.legend(bbox_to_anchor=(0.08, 1.02), title="Model", loc=2, ncol=1, fontsize=19)
#plt.setp(legend.get_title(),fontsize=19)
#ax1.setp(legend.get_title(),fontsize=14)
ax1.set_title('Scenario (a)', fontsize=20)

ax2 = plt.axes(rec2)
for i in range(len(dirs_b)):
    #plt.plot(list(range(1,len(tag_list_ab)+1)),
    ax2.plot(list(range(1,len(tag_list_ab)+1)),
             data_b[i],
             color=line_color_map[i],
             label=labels[i],
             linewidth=2,
             linestyle=linestyle[i])
    print("task b")
    print(labels[i])
    d_str = ""
    for j in range(1,len(tag_list_ab)+1):
        d_str+= "("
        d_str+=str(j)+","
        d_str+= str(data_b[i][j-1])
        d_str+= ")"
    print(d_str)

# make plot pretty
#plt.grid(True)
ax2.grid(True)
axes = plt.gca()
#axes = ax2.gca()
#plt.yticks(list(range(-0.2,1.4,0.2)),fontsize=12)
plt.yticks(fontsize=18)
#ax2.yticks(fontsize=13)
#axes.set_ylim([-0.5, 1.3])
#plt.xticks(list(range(1,50,5)),fontsize=18)
plt.xticks(list(range(1,26,3)),fontsize=18)
#ax2.set_xticklabels(list(range(1,50,3)),fontsize=13)
axes.set_xlim([1.0, 20.0])
#plt.xlabel('Time',fontsize=14)
ax2.set_xlabel('Time',fontsize=19)
#plt.ylabel('Target NLL',fontsize=14)
#legend = plt.legend(bbox_to_anchor=(0.08, 0.99), title="Model (setting)", loc=2, ncol=1, fontsize=14)
#legend = ax2.legend(bbox_to_anchor=(0.08, 1.02), title="Model", loc=2, ncol=1, fontsize=19)
#plt.setp(legend.get_title(),fontsize=19)
#ax2.setp(legend.get_title(),fontsize=14)
ax2.set_title('Scenario (b)', fontsize=20)


# plotting
#plt.subplot(1,4,2)
ax3 = plt.axes(rec3)
for i in range(len(dirs_c)):
    #plt.plot(list(range(1,len(tag_list_c)+1)),
    ax3.plot(list(range(1,len(tag_list_c)+1)),
             data_c[i],
             color=line_color_map[i],
             label=labels[i],
             linewidth=2,
             linestyle=linestyle[i])
    print("task c")
    print(labels[i])
    d_str = ""
    for j in range(1,len(tag_list_c)+1,3):
        d_str+= "("
        d_str+=str(j)+","
        d_str+= str(data_c[i][j-1])
        d_str+= ")"
    print(d_str)

# make plot pretty
#plt.grid(True)
ax3.grid(True)
axes = plt.gca()
#axes = ax2.gca()
#plt.yticks(list(range(-0.2,1.4,0.2)),fontsize=12)
plt.yticks(fontsize=18)
#ax2.yticks(fontsize=13)
#axes.set_ylim([-0.5, 1.3])
plt.xticks(list(range(1,50,5)),fontsize=18)
#ax2.set_xticklabels(list(range(1,50,3)),fontsize=13)
axes.set_xlim([1.0, 50.0])
#plt.xlabel('Time',fontsize=14)
ax3.set_xlabel('Time',fontsize=19)
#plt.ylabel('Target NLL',fontsize=14)
#legend = plt.legend(bbox_to_anchor=(0.08, 0.99), title="Model (setting)", loc=2, ncol=1, fontsize=14)
legend = ax3.legend(bbox_to_anchor=(0.48, 1.02), title="Model", loc=2, ncol=1, fontsize=19)
plt.setp(legend.get_title(),fontsize=19)
#ax2.setp(legend.get_title(),fontsize=14)
ax3.set_title('Scenario (c)', fontsize=20)

plt.savefig(img_name)
plt.close()


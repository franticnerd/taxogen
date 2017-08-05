import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

sns.set(font_scale=3,
        palette="deep",
        style='ticks',
        rc={'font.family': 'sans-serif',
            'font.serif': 'Helvetica',
            'pdf.fonttype': 42}
        )

labels = ['HClus', 'NoAC', 'NoLE', 'AdaTax']

overall = [1.996514, 1.939001, 2.008682, 1.906742]
level_1 = [1.751910, 1.751735, 1.740692, 1.74117]
level_2 = [1.919940, 1.974107, 1.889726, 1.917602]
level_3 = [2.021613, 1.93947, 2.043193, 1.911193]

out_dir = '/Users/chao/data/projects/local-embedding/dblp/results/'

plt.figure()
df = pd.DataFrame(overall)
ax = df.plot(kind='bar', xticks=df.index, rot=0, ylim=(1.5, 2.2), legend=False)
ax.set_xticklabels(labels)
ax.set_ylabel('Davies-Bouldin Index')
plt.savefig(out_dir + 'overall.pdf', bbox_inches='tight')

plt.figure()
df = pd.DataFrame(level_1)
ax = df.plot(kind='bar', xticks=df.index, rot=0, ylim=(1.5, 2.2), legend=False)
ax.set_xticklabels(labels)
ax.set_ylabel('Davies-Bouldin Index')
plt.savefig(out_dir + 'level-1.pdf', bbox_inches='tight')

plt.figure()
df = pd.DataFrame(level_2)
ax = df.plot(kind='bar', xticks=df.index, rot=0, ylim=(1.5, 2.2), legend=False)
ax.set_xticklabels(labels)
ax.set_ylabel('Davies-Bouldin Index')
plt.savefig(out_dir + 'level-2.pdf', bbox_inches='tight')

plt.figure()
df = pd.DataFrame(level_3)
ax = df.plot(kind='bar', xticks=df.index, rot=0, ylim=(1.5, 2.2), legend=False)
ax.set_xticklabels(labels)
ax.set_ylabel('Davies-Bouldin Index')
plt.savefig(out_dir + 'level-3.pdf', bbox_inches='tight')

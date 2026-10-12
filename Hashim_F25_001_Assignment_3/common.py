from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from scipy import stats
from vizlib import PALETTE, style_defaults, save_fig
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
SOURCE='Source: synthetic CDB601220 Week 3 course data; not real-world evidence.'
C=PALETTE['series']
style_defaults()
def read(name): return pd.read_csv(ROOT/'data'/f'{name}.csv')
def finish(fig,name,note=''):
    for a in fig.axes:
        for side in ['top','right']: a.spines[side].set_visible(False)
    fig.tight_layout()
    from io import BytesIO
    fig.text(.01,-.035,SOURCE+'\n'+note,fontsize=7,color=PALETTE['ink_soft'],ha='left',va='top')
    buffer=BytesIO()
    fig.savefig(buffer,format='png',dpi=300,bbox_inches='tight',facecolor='white')
    path=OUT/f'{name}.png'
    tmp=path.with_suffix('.tmp')
    tmp.write_bytes(buffer.getvalue())
    tmp.replace(path)
    plt.show()
    plt.close(fig)
def table_plot(frame,title,name):
    fig, ax=plt.subplots(figsize=(12,3.3));ax.axis('off');ax.set_title(title)
    t=ax.table(cellText=frame.round(3).astype(str).values,rowLabels=frame.index,colLabels=frame.columns,loc='center');t.auto_set_font_size(False);t.set_fontsize(8);t.scale(1,1.6)
    finish(fig,name,'SD uses ddof=0; slope is ordinary least squares.')
def summaries(df,group,x,y):
    return pd.DataFrame({k:{'n':len(g),'mean_x':g[x].mean(),'mean_y':g[y].mean(),'sd_x':g[x].std(ddof=0),'sd_y':g[y].std(ddof=0),'r':g[x].corr(g[y]),'slope':np.polyfit(g[x],g[y],1)[0]} for k,g in df.groupby(group)})

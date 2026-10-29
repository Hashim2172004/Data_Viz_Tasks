"""Run from the assignment folder. D entry points regenerate all three final figures."""
from pathlib import Path
import json, itertools, math, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import poisson, chi2
from sklearn.decomposition import PCA
import geolib as g
import vizlib as v
from IPython.display import display, Markdown
ROOT=Path.cwd(); DATA=ROOT/'data'; OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
v.style_defaults(dpi=100)
plt.rcParams.update({'font.size':9,'axes.titlesize':11})
h=pd.read_csv(DATA/'health_indicators.csv')
d=pd.read_csv(DATA/'district_health.csv'); d['rate']=d.cases/d.population*1e5
flat=pd.read_csv(DATA/'case05_flat_rates.csv'); flat['rate']=flat.cases/flat.population*1e5
s=pd.read_csv(DATA/'smallarea_cases.csv'); s['rate']=s.cases/s.population*1e5
crime=pd.read_csv(DATA/'county_crime.csv'); crime['rate']=crime.crimes_reported/crime.population*1e5
profiles=pd.read_csv(DATA/'region_profiles.csv'); dense=pd.read_csv(DATA/'scatter_dense.csv')
feats=g.read_geojson(DATA/'districts.geojson')
cols=['gdp_pc','healthcare_access','urban_pct','median_age','cases_per_100k']
chain=g.corr_chain(h,cols)
SOURCE='Synthetic CDB601220 Week 5 data; supplied boundaries, year unspecified; accessed 28 Oct 2026.'
MAPNOTE='Lambert cylindrical equal-area; shared reference latitude. No units suppressed unless stated.'
audit=pd.DataFrame([{'file':p.name,'rows':len(pd.read_csv(p)), 'missing_cells':int(pd.read_csv(p).isna().sum().sum())} for p in DATA.glob('*.csv')])
display(audit)
assert h.country.is_unique and d.code.is_unique
assert set(d.code)=={f['code'] for f in feats}
print('District join: 24 matched, 0 data failures, 0 unmatched polygons. No rows removed.')
def finish(fig,name,note=''):
    fig.text(.01,.005, SOURCE+'\n'+note,fontsize=7,va='bottom')
    fig.tight_layout(rect=(0,.065,1,1))
    if name.startswith('partC_map_'): fig.axes[0].set_position([.08,.15,.52,.72])
    v.save_fig(fig,OUT/(name+'.png'))
    from IPython.display import Image as DisplayImage
    display(DisplayImage(filename=str(OUT/(name+'.png')),width=900))
    plt.close(fig)
def mapplot(ax,frame,value,title,scheme='natural',fs=None):
    fs=feats if fs is None else fs
    edges=g.choropleth(ax,fs,dict(zip(frame.code,frame[value])),scheme=scheme,k=5,cmap='Blues',fmt='{:,.2f}',legend_title=title,legend_anchor=(1,1))
    return edges
notes={}
def diagnose(n,text):
    notes[n]=text
    display(Markdown(text))
# Range-limited, affine area encoding; disclosed because area ratios are compressed.
lo,hi=24.,650.
def bubble_size(pop): return lo+(np.asarray(pop)-h.pop_m.min())/(h.pop_m.max()-h.pop_m.min())*(hi-lo)
def bubble(ax):
    colors=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#555555']
    for reg,col in zip(sorted(h.region.unique()),colors):
        z=h[h.region==reg]; ax.scatter(z.gdp_pc,z.healthcare_access,s=bubble_size(z.pop_m),c=col,label=reg,alpha=.7,edgecolors='white',linewidths=.5)
    ax.set(xscale='log',ylim=(0,100),xlabel='GDP per capita (USD, log scale)',ylabel='Healthcare access (0–100)')
    leg=ax.legend(title='Region',loc='upper left',bbox_to_anchor=(1.01,1)); ax.add_artist(leg)
    refs=[h.pop_m.min(),h.pop_m.median(),h.pop_m.max()]
    handles=[ax.scatter([],[],s=bubble_size(x),c='#888888',label=f'{x:g} M') for x in refs]
    ax.legend(handles=handles,title='Population (million)\nAffine area: 24–650 pt²',loc='lower left',bbox_to_anchor=(1.01,0),labelspacing=2)
    ix=set([h.gdp_pc.idxmax(),h.pop_m.idxmax(),h.healthcare_access.idxmin(),h.healthcare_access.idxmax()])
    for i in ix: ax.annotate(h.loc[i,'country'],(h.loc[i,'gdp_pc'],h.loc[i,'healthcare_access']),xytext=(4,5),textcoords='offset points',fontsize=8)
def rankpcp(ax):
    g.pcp(ax,h,chain,how='rank',highlight=h.region.eq('Andara'))
    ax.set_title('Access and incidence oppose each other; Andara highlighted\nPercentile ranks: robust to GDP outlier; grey = other regions',fontsize=10)
    ax.set_ylabel('Percentile rank (0–1); endpoint labels show raw extrema')

cf=[f for f in feats if f['code'] in set(crime.code)]
print('County table matches:',len(cf),'unmatched county records:',len(set(crime.code)-{f['code'] for f in feats}),'excluded boundary codes:',sorted({f['code'] for f in feats}-set(crime.code)))
for value,label,stem in [('crimes_reported','Reported crimes (count)','partC_map_A'),('rate','Reported crimes per 100,000 residents','partC_map_B')]:
    fig,ax=plt.subplots(figsize=(8,6)); mapplot(ax,crime,value,label,scheme='quantile',fs=cf)
    # County labels so readers can name their choices without an answer key.
    ref=np.mean([p[1] for f in cf for p in f['ring']]); names=crime.set_index('code').county
    for f in cf:
        x,y=g.equal_area_xy(*g.representative_point(f['ring']),lat_ts=ref)
        ax.text(x,y,names[f['code']],ha='center',va='center',fontsize=6,color='black',bbox={'facecolor':'white','alpha':.7,'edgecolor':'none','pad':1})
    ax.set_title('Map '+('A' if value=='crimes_reported' else 'B')+' — reported crime by county')
    finish(fig,stem,'Five quantile classes, Blues, identical geometry/projection. Excluded D21–D24: no county records. '+MAPNOTE)
print('Count/pop correlation:',crime.crimes_reported.corr(crime.population))
print('Top count:',crime.nlargest(3,'crimes_reported').county.tolist(),'Top rate:',crime.nlargest(3,'rate').county.tolist())
cr=crime.assign(count_rank=crime.crimes_reported.rank(ascending=False,method='min'),rate_rank=crime.rate.rank(ascending=False,method='min'))
print('Rank shifts >=3:',int((abs(cr.count_rank-cr.rate_rank)>=3).sum()))
cr.to_csv(ROOT/'partC_county_ranking_audit.csv',index=False)
results_path=ROOT/'partC_reader_results.csv'
if not results_path.exists():
    pd.DataFrame(columns=['reader_id','A1','A2','A3','B1','B2','B3','reason_A','reason_B','overlap_count']).to_csv(results_path,index=False)
results=pd.read_csv(results_path)
valid_names=set(crime.county)
if len(results):
    overlaps=[]
    for _,row in results.iterrows():
        aa=[row[k] for k in ['A1','A2','A3']]; bb=[row[k] for k in ['B1','B2','B3']]
        assert len(set(aa))==3 and len(set(bb))==3 and set(aa+bb)<=valid_names, 'Use three distinct exact county names per map.'
        overlaps.append(len(set(aa)&set(bb)))
    assert results.reader_id.is_unique
    results['overlap_count']=overlaps; results.to_csv(results_path,index=False)
    print('Real readers:',len(results),'Mean overlap:',results.overlap_count.mean())
    if len(results)<5: print('At least five real readers are required; collection is incomplete.')
else:
    print('PENDING: no reader responses supplied. Mean overlap is undefined, not zero. No experimental observations have been invented.')
display(Markdown('**Protocol:** Recruit at least five real readers, separately. Show only `partC_map_A.png`; ask “Which three counties would you send extra police to, and why?” Record A1–A3 and reason_A. Lock that answer. Then show `partC_map_B.png`, repeat and record B1–B3 and reason_B. Save one row per reader in `partC_reader_results.csv` and rerun this section. Map A shows reported workload, strongly related to population; Map B shows reported crimes per resident. Neither measures unreported crime or establishes how police should be allocated. The computed top-three overlap is zero, but this is **not** a reader-experiment result.'))
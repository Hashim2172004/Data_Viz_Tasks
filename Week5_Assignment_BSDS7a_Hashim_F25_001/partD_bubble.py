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

fig,ax=plt.subplots(figsize=(10,5.8)); bubble(ax); ax.set_title('Healthcare access differs widely even at similar GDP')
finish(fig,'partD_bubble','GDP outlier Aldonia retained on log x. All 60 rows. Affine population area 24–650 pt² (not proportional ratios); six regions, no Other bucket.')
display(h.sort_values('region')[['country','region','gdp_pc','healthcare_access','pop_m']])
h.to_csv(ROOT/'partD_accessible_data_table.csv',index=False)
colors=['#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#555555']
for kind in [None,'deutan','protan','tritan']:
    print('Region palette worst pair',kind,v.worst_pair(colors,kind=kind))
print('Six hues cannot guarantee universal separation: exact region identities are available in the accessible table.')
fig,ax=plt.subplots(figsize=(11,5)); rankpcp(ax); finish(fig,'partD_pcp','Computed greedy |Pearson r| order: '+' → '.join(chain)+'. Andara orange, all others grey; 60 countries, no removal.')
print('Adjacent-axis Pearson relationships:')
for c1,c2 in zip(chain,chain[1:]): print(c1,c2,h[c1].corr(h[c2]))
print('Interpretation: access–incidence is inverse (crossings); incidence–urbanisation is also inverse (r=-0.619). Ranks preserve ordering, not raw distances.')
# Same-row multivariate conjunction visible as complete polylines.
br=h[h.region.eq('Andara')]; med=h[cols].median()
mask=br.healthcare_access.gt(med.healthcare_access)&br.cases_per_100k.lt(med.cases_per_100k)&br.urban_pct.gt(med.urban_pct)
print('Andara countries above median access and urban share AND below median incidence:',br.loc[mask,'country'].tolist())
print('A PCP links this three-way conjunction within each country; unlinked pairwise panels do not preserve that path identity.')
scores=pd.DataFrame([{'scheme':sch,'GVF':g.gvf(d.rate,g.breaks(d.rate,sch,5)),'breaks':g.breaks(d.rate,sch,5)} for sch in ['equal','quantile','natural']]); display(scores)
fig,axs=plt.subplots(1,2,figsize=(12,6.5),gridspec_kw={'width_ratios':[1.5,1]})
# Publication rule: counts under 5 are not shown as rates. Current district data has none.
supp=d.cases.lt(5); pub=d[~supp]; fs=[f for f in feats if f['code'] in set(pub.code)]
edges=mapplot(axs[0],pub,'rate','Cases per 100,000 residents',fs=fs); axs[0].set_title('Highest incidence is not highest workload')
z=pub.sort_values('cases'); axs[1].barh(z.code,z.cases,color='#0072B2'); axs[1].set(xlabel='Confirmed cases (count)',title='D17 carries the largest case load')
finish(fig,'partD_choropleth',f'24 districts, 0 join failures. Jenks natural breaks (5), right-inclusive upper bounds. Suppress counts <5: {supp.sum()} units. '+MAPNOTE)
print('Pooled rate:',d.cases.sum()/d.population.sum()*1e5,'legend breakpoints:',edges)
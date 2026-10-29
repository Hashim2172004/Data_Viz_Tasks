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
pooled=s.cases.sum()/s.population.sum()*1e5
fig,ax=plt.subplots(figsize=(10,4)); z=s.sort_values('rate',ascending=False); ax.bar(z.iloc[:,0],z.rate,color='#0072B2'); ax.axhline(pooled,color='#D55E00',label=f'Pooled {pooled:.2f}'); ax.tick_params(axis='x',rotation=90); ax.legend(); ax.set(ylabel='Cases per 100,000 residents',title='Recipe: U32 appears to be the extreme hotspot'); finish(fig,'A06_original','All 40 units; unsuppressed diagnostic exercise.')
def funnel(ax):
    grid=np.geomspace(s.population.min(),s.population.max(),400); lim=g.funnel_limits(grid,pooled)
    ax.fill_between(lim.population,lim.lo,lim.hi,color='#d9e8f2',label='95% normal-approx. Poisson limits')
    ax.axhline(pooled,color='#777777',lw=1); ax.scatter(s.population,s.rate,c='#0072B2',s=26)
    u=s.iloc[s.rate.argmax()]; ax.annotate(str(u.iloc[0]),(u.population,u.rate),xytext=(6,0),textcoords='offset points')
    ax.set(xlabel='Population (residents)',ylabel='Cases per 100,000 residents',title='Small populations have the widest expected variation'); ax.legend(fontsize=8)
fig,ax=plt.subplots(figsize=(9,4.7)); funnel(ax); finish(fig,'A06_redesign','All units retained for stability audit; do not interpret rank as true risk. Approximate limits, not proof of equality.')
u=s.iloc[s.rate.argmax()]
diagnose(6,f'Conclusion: U32 has almost five times the true risk. Decoy: the arithmetic is correct: {u.cases:g}/{u.population:g} × 100,000 = {u.rate:.1f}, versus pooled {pooled:.2f}. Mechanism: random-count variance divided by a small population gives highly unstable rates. The data dictionary explicitly states every unit has the same true rate. U32 has only nine observed cases. A funnel communicates expected uncertainty; even an outlier warrants investigation rather than a causal hotspot label. No observations are removed from this diagnostic chart.')

from contextlib import redirect_stdout
import io
report=io.StringIO()
with redirect_stdout(report):
    print('B1: affine area range:',(lo,hi),'pt²; diameter ratio:',np.sqrt(hi/lo))
    print('24 pt² keeps small marks visible; 650 pt² limits overlap. s, not radius, is linear in population.')
    print('True proportional 650*population/max would give a minimum area of',650*h.pop_m.min()/h.pop_m.max(),'pt²; rejected for readability.')
    print('B3: GDP under each scaling:')
    for how in ['minmax','zscore','rank']:
        q=g.scale_frame(h,cols,how).gdp_pc
        print(how,{'min':q.min(),'median':q.median(),'max':q.max(),'SD':q.std(ddof=0),'below_0.1':int((q<.1).sum())})
    pca=PCA().fit(g.scale_frame(h,cols,'zscore'))
    print('PCA first two explained variance ratios:',pca.explained_variance_ratio_[:2])
    print('Variance omitted by 2-D PCA:',1-pca.explained_variance_ratio_[:2].sum())
    print('PCA variance is not information in a causal sense; standardisation weights each variable equally.')
    def shoelace(ring):
        ar=np.asarray(ring); return .5*abs(np.dot(ar[:,0],np.roll(ar[:,1],-1))-np.dot(ar[:,1],np.roll(ar[:,0],-1)))
    ar=pd.DataFrame([{'code':f['code'],'latitude':np.mean(np.array(f['ring'])[:,1]),'sphere_km2':g.polygon_area_km2(f['ring']),'raw_deg2':shoelace(f['ring'])} for f in feats])
    ar['sphere_share']=ar.sphere_km2/ar.sphere_km2.sum(); ar['degree_share']=ar.raw_deg2/ar.raw_deg2.sum(); ar['distortion_pp']=100*(ar.degree_share-ar.sphere_share)
    north=ar.nlargest(4,'latitude')
    print('B4 four northernmost:',north.code.tolist(),'shares spherical/degrees:',north.sphere_share.sum(),north.degree_share.sum())
    print('Largest absolute share distortion:',ar.loc[ar.distortion_pp.abs().idxmax()].to_dict())
    lat=np.array([p[1] for f in feats for p in f['ring']]); inflation=1/np.cos(np.deg2rad([lat.min(),lat.max()]))**2
    print('Mercator local area inflation at south/north edges:',inflation)
    actual=[]
    for f in feats:
        x,y=g.mercator_xy(*zip(*f['ring'])); actual.append(shoelace(np.c_[x,y])/g.polygon_area_km2(f['ring']))
    print('Polygon Mercator/spherical area ratios:',min(actual),max(actual))
    print('Mercator preserves local angles but inflates area by sec(latitude)^2, not sec(latitude) as the supplied comment says; equal-area preserves visual land shares.')
    lim=g.funnel_limits(np.unique(s.population),pooled).set_index('population')
    low=lim.loc[s.population,'lo'].to_numpy(); high=lim.loc[s.population,'hi'].to_numpy()
    outside=(s.rate.to_numpy()<low)|(s.rate.to_numpy()>high)
    print('B5 normal-approximate 95% funnel outliers:',outside.sum(),'of',len(s),s.loc[outside].iloc[:,0].tolist())
    exactlo=poisson.ppf(.025,pooled*s.population/1e5)/s.population*1e5
    exacthi=poisson.ppf(.975,pooled*s.population/1e5)/s.population*1e5
    print('Exact discrete central Poisson funnel outliers:',int(((s.rate<exactlo)|(s.rate>exacthi)).sum()))
    print('Random extremes can occur under the common-rate data generation; 40 pointwise checks also create multiplicity.')
    # Define distinguishable as 18 above the upper normal-approximate 95% control limit under null 9.
    threshold=math.floor(1.96**2*9*1e5/(18-9)**2)+1
    nonoverlap=math.floor(1.96**2*1e5*(np.sqrt(9)+np.sqrt(18))**2/(18-9)**2)+1
    print('Minimum integer population for 18 > upper 95% null-9 limit:',threshold)
    print('If instead requiring two non-overlapping approximate 95% intervals:',nonoverlap,'per group. These are precision criteria, not a power calculation.')
print(report.getvalue()); (ROOT/'partB_output.txt').write_text(report.getvalue())
ar.to_csv(ROOT/'partB_area_audit.csv',index=False)
fig,axs=plt.subplots(2,2,figsize=(10,8))
axs[0,0].scatter(dense.x,dense.y,s=9,alpha=1,color='#0072B2'); axs[0,0].set_title('Opaque: cluster visible, density saturated')
axs[0,1].scatter(dense.x,dense.y,s=9,alpha=.07,color='#0072B2'); axs[0,1].set_title('Transparent: cluster becomes visible (alpha .07)')
hexes=axs[1,0].hexbin(dense.x,dense.y,gridsize=45,mincnt=1,cmap='Blues'); fig.colorbar(hexes,ax=axs[1,0],label='Points per hexagon'); axs[1,0].set_title('Hexbin: local density is explicit (grid 45)')
sns.kdeplot(data=dense,x='x',y='y',fill=True,cmap='Blues',levels=12,bw_adjust=.7,gridsize=100,ax=axs[1,1]); axs[1,1].set_title('KDE: cluster visible but smoothed (bandwidth × .7)')
for ax in axs.flat:
    ax.set(xlabel='x',ylabel='y'); ax.annotate('Target (3.1, 3.0)',(3.1,3.0),xytext=(-2,3.7),arrowprops={'arrowstyle':'->'},fontsize=8)
finish(fig,'partB_overplotting','9,000 points; s=9 pt², alpha=1/.07; hexbin grid=45; Gaussian KDE, Scott bandwidth × .7, grid=100, levels=12.')
visibility=pd.DataFrame({'method':['opaque','transparent','hexbin','KDE'],'800-point cluster':['Visible isolated cluster; internal density saturated','Visible density patch','Visible dense hexagons','Visible smoothed peak'],'publish':['No','Possible','Yes: quantitative count legend','Supplement: bandwidth sensitive']})
display(visibility); visibility.to_csv(ROOT/'partB_visibility.csv',index=False)
fig,ax=plt.subplots(figsize=(9,4.5)); funnel(ax); finish(fig,'partB_funnel','95% toolkit normal-approximation Poisson funnel; exact-discrete check printed separately. No suppression in diagnostic exercise.')
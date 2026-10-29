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

fig,ax=plt.subplots(figsize=(9,5))
ax.scatter(h.gdp_pc,h.healthcare_access,s=h.pop_m**2,alpha=.45)
ax.set(xscale='log',xlabel='GDP per capita (USD)',ylabel='Healthcare access',title='Recipe rebuild: squared population dominates the chart')
finish(fig,'A01_original','Deliberately misleading recipe: s = population² (million²); no usable size legend in recipe.')
ratio=(h.pop_m.max()/h.pop_m.min())**2
print('Marks:',len(h),'actual area ratio:',ratio,'under 1 pt²:',int((h.pop_m**2<1).sum()),'population <2 M:',int((h.pop_m<2).sum()))
fig,ax=plt.subplots(figsize=(10,5.5)); bubble(ax); ax.set_title('Readable areas retain small countries and the GDP outlier')
finish(fig,'A01_redesign','Outlier retained on log x. Affine area 24–650 pt² compresses population ratios; no removals.')
diagnose(1,f'Conclusion: population seems unrelated to access because large marks appear everywhere. Decoy: a linear GDP axis is not the cause; the recipe already specifies log GDP. Mechanism: s is area, so squaring population produces an area ratio of {ratio:,.0f}, not the brief’s 589. The latter is the population ratio. Only {(h.pop_m**2<1).sum()} marks are below one point-squared; {(h.pop_m<2).sum()} are below 2 M. The supplied self-check mixes these thresholds. Redesign: bounded affine areas with a calibrated legend, log GDP and a full table for exact values; the bounded range is a readability trade-off, not proportional population area.')

fig,ax=plt.subplots(figsize=(7,5)); mapplot(ax,d,'cases','Cases (raw count)'); ax.set_title('Recipe: populous districts dominate counts'); finish(fig,'A02_original',MAPNOTE)
fig,ax=plt.subplots(figsize=(7,5)); mapplot(ax,d,'rate','Cases per 100,000 residents'); ax.set_title('Rates identify a different set of districts'); finish(fig,'A02_redesign',MAPNOTE)
print('Total cases/population:',d.cases.sum(),d.population.sum()); print('Top count:',d.nlargest(3,'cases').code.tolist(),'Top rate:',d.nlargest(3,'rate').code.tolist())
diagnose(2,f'Conclusion: the capital-area districts have the greatest outbreak risk. Decoy: failed joins cannot explain this; all 24 codes match and all counts are retained. Mechanism: population is the hidden denominator. Counts correlate with population at r={d.cases.corr(d.population):.3f}. Count leaders D17, D13 and D09 are replaced by rate leaders D19, D20 and D21. Counts remain relevant for workload; rates answer relative risk. Total: {d.cases.sum():,} cases in {d.population.sum():,} residents.')

fig,ax=plt.subplots(figsize=(10,4.7)); g.pcp(ax,h,cols,'minmax'); ax.set_title('Recipe: min–max GDP looks almost flat; file axis order'); finish(fig,'A03_original','All five axes min–max scaled; all 60 countries retained.')
fig,ax=plt.subplots(figsize=(10,4.7)); g.pcp(ax,h,cols,'rank'); ax.set_title('Percentile ranks reveal GDP ordering; file axis order'); finish(fig,'A03_redesign','Rank scaling discards gap magnitude; no brushing, to isolate the scaling change.')
mm=g.scale_frame(h,cols,'minmax').gdp_pc
print('Below 0.10:',(mm<.1).sum(),'Median:',mm.median(),'GDP range:',h.gdp_pc.min(),h.gdp_pc.max())
diagnose(3,f'Conclusion: GDP hardly varies. Decoy: GDP does not have a narrow raw range; it spans ${h.gdp_pc.min():,}–${h.gdp_pc.max():,}. Mechanism: the largest observation controls the min–max denominator, leaving {(mm<.1).sum()} of 60 countries below 0.10 and the median at {mm.median():.3f}. Rank scaling makes order visible without deleting the outlier, while sacrificing distances between observations.')

fig,ax=plt.subplots(figsize=(10,4.7)); g.pcp(ax,h,cols,'minmax'); ax.set_title('Recipe: access and incidence are three axes apart'); finish(fig,'A04_original','Min–max scaling; file order: '+' → '.join(cols))
fig,ax=plt.subplots(figsize=(10,4.7)); g.pcp(ax,h,chain,'minmax'); ax.set_title('Computed adjacency exposes access–incidence crossings'); finish(fig,'A04_redesign','Min–max scaling unchanged; greedy absolute Pearson correlation order: '+' → '.join(chain))
print('Computed chain:',chain); display(h[cols].corr().round(3))
diagnose(4,f'Conclusion: access and incidence are unrelated. Decoy: lack of numerical association is ruled out by r={h.healthcare_access.corr(h.cases_per_100k):.3f}. Mechanism: their file-order positions differ by three; a crossing can only be read locally between adjacent axes. The computed greedy order puts them together while holding min–max scaling constant. The inverse relationship now produces an X-shaped waist.')

fig,ax=plt.subplots(figsize=(7,5)); edges=mapplot(ax,flat,'rate','Cases per 100,000 residents','quantile'); ax.set_title('Recipe: five quantile bins amplify a narrow spread'); finish(fig,'A05_original',MAPNOTE+' Five quantile classes.')
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
fig,ax=plt.subplots(figsize=(7,5)); patches=[]
lat_ts=np.mean([p[1] for f in feats for p in f['ring']]); vals=flat.set_index('code').rate
for f in feats:
    x,y=g.equal_area_xy(*zip(*f['ring']),lat_ts=lat_ts); patches.append(Polygon(np.c_[x,y]))
pc=PatchCollection(patches,cmap='Blues',norm=Normalize(0,40),edgecolor='white'); pc.set_array(np.array([vals[f['code']] for f in feats])); ax.add_collection(pc); ax.autoscale_view(); ax.set_aspect('equal'); ax.axis('off')
fig.colorbar(pc,ax=ax,label='Cases per 100,000 residents (continuous, 0–40)'); ax.set_title('Incidence varies only slightly around 32 per 100,000'); finish(fig,'A05_redesign',MAPNOTE+' Fixed zero-based 0–40 rate scale; no classification.')
print('Quantile edges:',edges,'rate min/max:',flat.rate.min(),flat.rate.max(),'spread %:',flat.rate.ptp() if hasattr(flat.rate,'ptp') else np.ptp(flat.rate)/flat.rate.mean()*100)
diagnose(5,f'Conclusion: five distinct incidence levels form a strong gradient. Decoy: the sequential blue palette is appropriate; rainbow hue is not the problem. Mechanism: quantiles force approximately equal occupancy across five colours even though rates span {flat.rate.min():.2f}–{flat.rate.max():.2f}, only {np.ptp(flat.rate)/flat.rate.mean()*100:.1f}% of the mean. A fixed continuous 0–40 scale preserves the small magnitude. Class membership is not evidence of five real risk regimes.')

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

coarse=g.read_geojson(DATA/'districts_coarse.geojson')
rows=[]
for f in coarse:
    z=d[d.code.isin(f['members'].split(','))]
    rows.append({'zone':f['code'],'income':np.average(z.income_pc_usd,weights=z.population),'rate':z.cases.sum()/z.population.sum()*1e5,'population':z.population.sum(),'cases':z.cases.sum()})
zones=pd.DataFrame(rows)
fig,ax=plt.subplots(figsize=(7,4.5)); ax.scatter(d.income_pc_usd,d.rate); ax.set(xlabel='Income per person (USD)',ylabel='Cases per 100,000 residents',title=f'Recipe: district correlation r = {d.income_pc_usd.corr(d.rate):.3f}'); finish(fig,'A07_original','24 original districts, no removals.')
fig,axs=plt.subplots(1,2,figsize=(10,4.5))
axs[0].scatter(d.income_pc_usd,d.rate); axs[1].scatter(zones.income,zones.rate)
for ax in axs: ax.set(xlabel='Population-weighted income (USD)',ylabel='Cases per 100,000 residents')
axs[0].set_title(f'24 districts: r={d.income_pc_usd.corr(d.rate):.3f}'); axs[1].set_title(f'6 supplied zones: r={zones.income.corr(zones.rate):.3f}')
finish(fig,'A07_redesign','MAUP scale sensitivity; cases/population summed, income population-weighted. Same total population and cases.')
assert zones.cases.sum()==d.cases.sum() and zones.population.sum()==d.population.sum()
display(zones)
diagnose(7,f'Conclusion: income and incidence are intrinsically weakly related. Decoy: mismatched totals are ruled out; aggregation conserves all {d.cases.sum():,} cases and {d.population.sum():,} residents. Mechanism: the modifiable areal unit problem (MAUP). Correlation changes from {d.income_pc_usd.corr(d.rate):.3f} for 24 districts to {zones.income.corr(zones.rate):.3f} for six supplied zones. Rates are recomputed from pooled counts, never averaged unweighted. The alternate 24-unit GeoJSON has no corresponding observations or crosswalk; exact alternative-zone rates cannot be inferred without an allocation assumption. No areal interpolation is presented as measured data, and neither aggregate correlation establishes individual risk.')

fig,ax=plt.subplots(figsize=(7,5)); e=mapplot(ax,d,'rate','Cases per 100,000 residents'); ax.set_title('Recipe: dark land looks like most of the outbreak'); finish(fig,'A08_original',MAPNOTE)
fig,axs=plt.subplots(1,2,figsize=(12,6),gridspec_kw={'width_ratios':[1.4,1]}); mapplot(axs[0],d,'rate','Cases per 100,000 residents'); z=d.sort_values('cases'); axs[1].barh(z.code,z.cases,color='#0072B2'); axs[1].set(xlabel='Cases (count)',title='Count shows service workload'); axs[0].set_title('Rate shows local incidence'); fig.subplots_adjust(wspace=.7); finish(fig,'A08_redesign',MAPNOTE)
top=d.nlargest(5,'population'); cl=g.class_of(d.rate,e); high=d[cl>=3]
print('Top-five population land/pop shares:',top.area_km2.sum()/d.area_km2.sum(),top.population.sum()/d.population.sum()); print('Top-two classes land/pop/case shares:',*[high[c].sum()/d[c].sum() for c in ['area_km2','population','cases']])
diagnose(8,f'Conclusion: a rural outbreak dominates because much of the map is dark. Decoy: raw counts are not the cause here; this recipe already maps rates correctly. Mechanism: large rural polygons occupy visual area disproportionate to their population. The five largest populations account for {top.area_km2.sum()/d.area_km2.sum():.1%} of land and {top.population.sum()/d.population.sum():.1%} of residents. A rate map plus a zero-based sorted count bar separates risk from workload. Darkness over land does not establish the fraction of patients living there.')

a=profiles.region_a.to_numpy(); b=profiles.region_b.to_numpy()
def radar_area(x): return .5*np.sin(2*np.pi/len(x))*np.sum(x*np.roll(x,-1))
theta=np.linspace(0,2*np.pi,6,endpoint=False)
fig,ax=plt.subplots(figsize=(7,5),subplot_kw={'projection':'polar'})
for x,c,label in [(a,'#0072B2','Region A'),(b,'#D55E00','Region B')]:
    ax.plot(np.r_[theta,theta[0]],np.r_[x,x[0]],c=c,label=label); ax.fill(np.r_[theta,theta[0]],np.r_[x,x[0]],c=c,alpha=.2)
ax.set_xticks(theta); ax.set_xticklabels(profiles.indicator,fontsize=8); ax.set_ylim(0,100); ax.legend(loc='upper right',bbox_to_anchor=(1.4,1.1)); ax.set_title('Recipe: Region A encloses more area'); finish(fig,'A09_original','Six indicators in original file order; 0–100 on each axis.')
fig,ax=plt.subplots(figsize=(8,4.5)); yy=np.arange(6)
ax.hlines(yy,np.minimum(a,b),np.maximum(a,b),color='#bbbbbb'); ax.scatter(a,yy,c='#0072B2',label='Region A'); ax.scatter(b,yy,c='#D55E00',marker='s',label='Region B'); ax.set_yticks(yy); ax.set_yticklabels(profiles.indicator); ax.set(xlim=(0,100),xlabel='Indicator score (0–100)',title='Nearly equal means conceal different strengths'); ax.legend(); finish(fig,'A09_redesign','File indicator order; shared position scale replaces polygon area.')
perms=[p for p in itertools.permutations(range(6)) if p[0]==0]
diffs=np.array([radar_area(a[list(p)])-radar_area(b[list(p)]) for p in perms])
print('Means:',a.mean(),b.mean(),'areas:',radar_area(a),radar_area(b),'area difference over orders:',diffs.min(),diffs.max(),'A wins:',(diffs>0).sum(),'of',len(perms))
diagnose(9,f'Conclusion: Region A is stronger overall. Decoy: different measurement scales are ruled out; all six scores share 0–100, with means {a.mean():.2f} and {b.mean():.2f}. Mechanism: radar area sums adjacent products, so arbitrary order changes area without changing any score. Original areas are {radar_area(a):,.0f} and {radar_area(b):,.0f}; over 120 rotation-fixed orders A-minus-B ranges from {diffs.min():,.0f} to {diffs.max():,.0f}, reversing the apparent winner. Aligned dots permit accurate per-indicator comparison; a single overall winner requires explicit weights.')
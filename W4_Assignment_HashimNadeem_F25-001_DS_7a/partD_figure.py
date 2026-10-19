# %%
from common import *
# Fix the seven-day window before examining alternative outcomes: it targets the weekly cycle.
WINDOW=7
d,h,daily,coverage,cleanlog=clean_sessions()
c,pos,neg,g,catlog=clean_catalogue()
# %%
# Collector gaps remain missing; totals with sentinel interpolation are explicitly marked.
rolling=daily.rolling(WINDOW,min_periods=WINDOW).mean()
print('Strict complete-case seven-day estimates:',rolling.notna().sum(),'of',len(daily))
fig,axs=plt.subplots(2,2,figsize=(17,11))
a=axs[0,0];a.plot(daily.index,daily,color='#b6bcc3',lw=.8,label='Daily totals (x = estimated hours)')
estimated=h.estimated.resample('D').sum().reindex(daily.index).gt(0)
a.scatter(daily.index[estimated],daily[estimated],marker='x',s=9,color='#8b929b',label='Contains interpolated sentinel hour(s)')
a.plot(rolling.index,rolling,color=COL[0],label='7-day trailing rolling mean')
a.set(title='Weekly rhythm filtered; missing days stay visible\n7-day trailing rolling mean',ylabel='Sessions per day (sum)',xlabel='Date');a.legend(fontsize=8);dateaxis(a)
heat=d[d.index<daily.index.max()+pd.Timedelta(days=1)].copy();heat['weekday']=heat.index.dayofweek;heat['hour']=heat.index.hour
piv=heat.pivot_table(index='weekday',columns='hour',values='sessions',aggfunc='mean').reindex(index=range(7),columns=range(24))
a=axs[0,1];im=a.imshow(piv,cmap=vizlib.PALETTE['sequential'],aspect='auto');a.set(yticks=range(7),yticklabels=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],xticks=range(0,24,3),xlabel='Hour (Pakistan local time)',ylabel='Day of week',title='Traffic varies systematically by day and hour')
fig.colorbar(im,ax=a,label='Sessions/hour (mean of valid observations)',shrink=.85)
# Nested rectangles explicitly encode category -> subcategory containment.
import squarify
from matplotlib.patches import Rectangle
parents=g.groupby('category').value.sum().sort_values(ascending=False);colors=dict(zip(parents.index,COL))
a=axs[1,0];rects=squarify.squarify(squarify.normalize_sizes(parents.values,100,100),0,0,100,100)
for (parent,total),r in zip(parents.items(),rects):
    a.add_patch(Rectangle((r['x'],r['y']),r['dx'],r['dy'],facecolor='white',edgecolor=colors[parent],lw=2))
    a.text(r['x']+1,r['y']+2,parent,va='top',fontsize=9,fontweight='bold',color=colors[parent])
    sub=g[g.category==parent].sort_values('value',ascending=False)
    sr=squarify.squarify(squarify.normalize_sizes(sub.value,r['dx']-2,r['dy']-9),r['x']+1,r['y']+8,r['dx']-2,r['dy']-9)
    for row,q in zip(sub.itertuples(),sr):
        a.add_patch(Rectangle((q['x'],q['y']),q['dx']-.3,q['dy']-.3,facecolor=colors[parent],edgecolor='white'))
        a.text(q['x']+q['dx']/2,q['y']+q['dy']/2,f'{row.subcategory}\n{row.value:,.1f}',ha='center',va='center',fontsize=9,color='white')
a.set(xlim=(0,100),ylim=(100,0),title='Mobile holds the largest positive net-revenue block\nCategory → subcategory; PKR million (sum)');a.axis('off')
a=axs[1,1];s=g.sort_values('value');a.barh(s.subcategory,s.value,color=[colors[x] for x in s.category]);a.bar_label(a.containers[0],fmt='%.1f',padding=3,fontsize=9);a.set(xlim=(0,s.value.max()*1.22),xlabel='Positive SKU net revenue, PKR million (sum)',title='Phones lead; bars reveal exact size differences')
for ax in axs.flat:
    for spine in ax.spines.values():spine.set_visible(False)
finish(fig,'partD_figure.png',f'Figure 17×11 in. 7-day trailing window; {cleanlog["daily_gaps"]} unavailable daily totals. Sep 2025 partial month excluded. No Other bucket; 8 subcategories. Negative SKUs: {catlog["negative_net"]:.4f} PKR m, shown separately.')
# %%
fig,ax=plt.subplots(figsize=(9,4));ns=neg.groupby('subcategory').net_revenue_pkr_m.sum().sort_values();ax.barh(ns.index,ns.values,color=COL[1]);ax.axvline(0,color='black',lw=.8);ax.set(title='Seven negative SKUs are separate from positive areas',xlabel='Negative SKU net revenue, PKR million (sum)');finish(fig,'negative_revenue.png','9×4 in. Signed total = positive area + negative adjustment.')
# CVD evidence uses the supplied toolkit, with direct labels supplementing the fourth hue.
print('CVD function:',__import__('inspect').signature(vizlib.simulate_cvd))
daily.to_csv(OUT/'clean_daily_sessions.csv',header=['sessions']);coverage.to_csv(OUT/'daily_valid_hour_counts.csv')
(OUT/'cleaning_audit.json').write_text(json.dumps({'sessions':cleanlog,'catalogue':catlog},indent=2,default=str))

from matplotlib.colors import to_rgb
fig,axs=plt.subplots(1,3,figsize=(10,2.5))
for ax,kind in zip(axs,['normal','deutan','protan']):
    rgb=np.array([to_rgb(x) for x in COL]);rgb=rgb if kind=='normal' else vizlib.simulate_cvd(rgb,kind=kind)
    ax.imshow(rgb[None,:,:]);ax.set(xticks=range(4),xticklabels=list(colors),yticks=[],title=kind);ax.tick_params(axis='x',labelsize=7)
finish(fig,'palette_cvd.png','10×2.5 in. Fourth hue needs direct labels; no identity depends on hue alone.')

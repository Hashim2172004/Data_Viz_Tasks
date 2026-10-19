from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tslib, vizlib
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
vizlib.style_defaults()
COL=vizlib.PALETTE['series']+[vizlib.PALETTE['series_4th']]
SOURCE='Synthetic course data: CDB601220, Superior University Lahore, Week 4.'
def read(name): return pd.read_csv(DATA/name)
def temporal(name,col,freq,fmt=None):
    d=read(name);d[col]=pd.to_datetime(d[col],format=fmt);d=d.set_index(col)
    print(name, 'before sorting:',tslib.audit_index(d,freq))
    return d.sort_index()
def finish(fig,name,note='',show=True):
    fig.text(.02,.005,SOURCE+' '+note,fontsize=7)
    fig.tight_layout(rect=(0,.035,1,1))
    fig.savefig(OUT/name,dpi=300,bbox_inches='tight')
    if show:
        from IPython.display import display
        display(fig)
    plt.close(fig)
def dateaxis(ax):
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3,maxticks=6))
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
def clean_sessions(verbose=True):
    d=read('sessions_hourly.csv')
    if verbose:
        d.info(); print(d.describe().T);print(d.device.value_counts());print(d.ts.head(10).tolist())
    slash=d.ts.str.contains('/')
    t=pd.Series(pd.NaT,index=d.index,dtype='datetime64[ns]')
    t.loc[slash]=pd.to_datetime(d.loc[slash,'ts'],format='%d/%m/%Y %H:%M')
    t.loc[~slash]=pd.to_datetime(d.loc[~slash,'ts'],format='%Y-%m-%d %H:%M:%S')
    d['timestamp']=t;d['device']=d.device.str.strip().str.lower()
    # Duplicate log entries must agree after timestamps and device tags are normalised.
    for _,g in d[d.timestamp.duplicated(False)].groupby('timestamp'):
        assert len(g[['sessions','orders','revenue_pkr','device']].drop_duplicates())==1
    log={'input_rows':len(d),'slash_format_rows':int(slash.sum()),'raw_sessions_sum':int(d.sessions.sum()),'raw_sentinel_rows':int((d.sessions<0).sum())}
    d=d.set_index('timestamp');log['before']=tslib.audit_index(d,'h')
    d=d[~d.index.duplicated(keep='first')].sort_index()
    log['duplicate_rows_removed']=12670-len(d);log['after_dedup_sum']=int(d.sessions.sum());log['sentinels_to_nan']=int((d.sessions<0).sum())
    d.loc[d.sessions<0,'sessions']=np.nan
    log['valid_observed_sum']=float(d.sessions.sum());log['hourly_audit']=tslib.audit_index(d,'h')
    h=d.reindex(pd.date_range(d.index.min(),d.index.max(),freq='h'))
    # Interpolate sentinel hours only; absent collector hours remain missing.
    coverage=h.sessions.resample('D').count();log['incomplete_days']=int((coverage<24).sum())
    sentinel=d.index[d.sessions.isna()]
    candidate=h.sessions.interpolate(method='time',limit_area='inside')
    h['estimated']=False
    fill=sentinel[candidate.reindex(sentinel).notna()]
    h.loc[fill,'sessions']=candidate.loc[fill];h.loc[fill,'estimated']=True
    log['sentinel_hours_interpolated']=len(fill)
    daily=h.sessions.resample('D').sum(min_count=24)
    log['estimated_daily_totals']=int((h.estimated.resample('D').sum().gt(0)&daily.notna()).sum())
    final_start=daily.index[-1].replace(day=1)
    log['partial_month']=str(final_start.date());log['partial_month_hour_rows']=int((d.index>=final_start).sum())
    daily=daily.loc[daily.index<final_start]
    log['analysis_days']=len(daily);log['daily_gaps']=int(daily.isna().sum());log['daily_complete']=int(daily.notna().sum())
    log['full_day_sum']=float(daily.sum());log['period_end']=str(daily.index.max().date())
    if verbose: print(json.dumps(log,indent=2,default=str));print('Daily audit:',tslib.audit_index(daily,'D'))
    return d,h,daily,coverage,log

def clean_catalogue(verbose=True):
    c=read('revenue_catalogue.csv');dup=c[c.sku.duplicated(False)]
    # Conflicting parent is resolved by SKU display prefix AUDIO vs WEAR; original Audio row retained.
    assert len(dup)==2 and dup.sku_name.str.startswith('AUDI').all()
    c=c.drop_duplicates('sku',keep='first')
    assert c.groupby('subcategory').category.nunique().max()==1
    assert np.allclose(c.revenue_pkr_m-c.returns_pkr_m,c.net_revenue_pkr_m,atol=.00011)
    neg=c[c.net_revenue_pkr_m<0].copy();pos=c[c.net_revenue_pkr_m>=0].copy()
    g=pos.groupby(['category','subcategory']).net_revenue_pkr_m.sum().rename('value').reset_index()
    shares=g.set_index('subcategory').value/g.value.sum()*100
    ref=read('shares_eight.csv').set_index('subcategory').share_pct
    check=pd.concat([shares.rename('computed_pct'),ref.rename('reference_pct')],axis=1);check['difference_pp']=check.computed_pct-check.reference_pct
    assert abs(shares.sum()-100)<1e-6 and check.difference_pp.abs().max()<.3
    log={'input_rows':345,'duplicates_removed':1,'duplicate_value':float(dup.net_revenue_pkr_m.iloc[0]),'dedup_rows':len(c),'negative_rows_separated':len(neg),'negative_net':float(neg.net_revenue_pkr_m.sum()),'positive_area_total':float(g.value.sum()),'signed_net_total':float(c.net_revenue_pkr_m.sum())}
    if verbose: print('Duplicate evidence:\n',dup.to_string(index=False));print(log);print(check)
    neg.to_csv(OUT/'negative_skus.csv',index=False);check.to_csv(OUT/'hierarchy_share_check.csv')
    return c,pos,neg,g,log

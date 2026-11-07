"""Task A: reproducible raw-file audit and cleaning. Never edits data/."""
from pathlib import Path
import contextlib, json, sys
import numpy as np
import pandas as pd
import tslib
ROOT=Path(__file__).resolve().parent

def main():
    (ROOT/'clean').mkdir(exist_ok=True)
    with (ROOT/'partA_audit.txt').open('w') as log, contextlib.redirect_stdout(log):
        process()
    print((ROOT/'partA_audit.txt').read_text())

def process():
    d=pd.read_csv(ROOT/'data/district_grid.csv')
    g=pd.read_csv(ROOT/'data/grid_daily.csv')
    m=pd.read_csv(ROOT/'data/generation_mix.csv')
    geo=json.loads((ROOT/'data/regions.geojson').read_text())
    names={f['properties']['code']:f['properties']['name'] for f in geo['features']}
    decisions=[]
    def decision(what,detect,rule,n): decisions.append([what,detect,rule,str(n)])
    for name,df,keys in [('district',d,['code']),('daily',g,['zone','date']),('generation',m,['month','source','subsource'])]:
        print('\nRAW FILE:',name,'rows:',len(df)); print(df.dtypes.to_string())
        print('Key unique:',not df.duplicated(keys).any(),'duplicate excess:',df.duplicated(keys).sum())
        print('Null counts:',df.isna().sum().to_dict())
        print('Numeric ranges:\n',df.select_dtypes('number').agg(['min','max']).to_string())
        print('Sentinel counts:',{c:int(df[c].isin([-1,999]).sum()) for c in df.select_dtypes('number')})
    print('District calendar gaps: N/A; generation calendar gaps:',len(pd.date_range(m.month.min(),m.month.max(),freq='MS').difference(pd.to_datetime(m.month.unique()))))
    print('Raw duplicate district records:\n',d[d.duplicated('code',keep=False)].to_string(index=False))
    canonical=d.district.eq(d.code.map(names))
    assert (d.loc[canonical].groupby('code').size()==1).all()
    removed=len(d)-canonical.sum(); d=d.loc[canonical].copy()
    decision('District 1/4: conflicting D11 duplicate','Repeated code; GeoJSON names Kotla, not Kotla City','Keep the unique row matching authoritative boundary name; drop conflicting alias; do not add values',removed)
    pph=d.population/d.households; bad=pph.gt(100)
    print('Household anomaly:',d.loc[bad,['code','population','households']].to_dict('records'))
    assert bad.sum()==1 and d.loc[bad,'code'].iloc[0]=='D21'
    d.loc[bad,'households']*=1000
    decision('District 2/4: D21 household scale','182 yields 5939.56 persons/household; peers roughly 6–7','Repair 182 to 182000 as inferred thousand-unit error, consistent with demographic range and published total; explicit assumption, not independent verification',bad.sum())
    pct=d.electrification_pct.astype('string'); percent=pct.str.endswith('%',na=False)
    d['electrification_pct']=pd.to_numeric(pct.str.rstrip('%'),errors='raise')
    decision('District 3/4: mixed percentage strings','Two values end with percent sign; column is text','Strip percent suffix and parse percentage points; preserve three original nulls',percent.sum())
    bad=d.outage_minutes.eq(-1); d.loc[bad,'outage_minutes']=np.nan
    decision('District 4/4: duration sentinel','Two negative interruption durations','Replace -1 by missing; retain districts and counts; duration charts omit these two',bad.sum())
    d['interruptions_per_1000_households']=1000*d.outages/d.households
    d['mean_interruption_minutes']=d.outage_minutes/d.outages
    slash=g.date.str.contains('/'); g['date']=pd.to_datetime(g.date,format='mixed',dayfirst=True,errors='raise')
    decision('Daily 1/6: mixed date formats','Regex finds ISO and day/month/year strings','Parse with dayfirst=True; slash block includes days >12, establishing day-first convention',slash.sum())
    outoforder=sum(not s.is_monotonic_increasing for _,s in g.groupby('zone').date)
    decision('Daily 2/6: shuffled chronology','All six zone timestamp sequences are nonmonotonic','Stable sort by zone and parsed date before differencing or plotting',len(g))
    exact=g.duplicated().sum(); g=g.drop_duplicates()
    conflict=g[g.duplicated(['zone','date'],keep=False)].copy()
    conflict.to_csv(ROOT/'clean/daily_conflict_candidates.csv',index=False)
    print('Exact duplicate excess:',exact,'conflicting candidate rows:',len(conflict));print(conflict.to_string(index=False))
    g=g.groupby(['zone','date'],as_index=False).agg(cumulative_mwh=('cumulative_mwh','max'),peak_load_mw=('peak_load_mw','max'),outage_minutes=('outage_minutes','max'))
    decision('Daily 3/6: repeated zone-day keys','12 exact repeats and 3 conflicting keys (6 candidates); counters agree','Drop 12 exact copies; consolidate 3 conflicting pairs with maximum peak and interruption duration (conservative upper bound, not a claim of true value); retain candidates separately',15)
    dates=pd.date_range(g.date.min(),g.date.max(),freq='D'); zones=sorted(g.zone.unique())
    full=pd.MultiIndex.from_product([zones,dates],names=['zone','date'])
    observed=pd.MultiIndex.from_frame(g[['zone','date']]); absent=full.difference(observed)
    absent.to_frame(index=False).to_csv(ROOT/'clean/unreported_zone_days.csv',index=False)
    decision('Daily 4/6: unreported zone-days','Full calendar anti-join shows 128 missing slots','Keep 3046 reported rows; export 128 absent keys separately; reindex plots so gaps remain missing',len(absent))
    bad=g.peak_load_mw.eq(-1);g.loc[bad,'peak_load_mw']=np.nan
    decision('Daily 5/6: peak-load sentinel','46 readings have peak -1 MW','Set to missing, never zero; preserve row and other valid measures',bad.sum())
    g=g.sort_values(['zone','date']).reset_index(drop=True)
    g['interval_days']=g.groupby('zone').date.diff().dt.days
    g['meter_change_mwh']=g.groupby('zone').cumulative_mwh.diff()
    g['meter_reset']=g.meter_change_mwh.lt(0)
    print('Meter resets:\n',g[g.meter_reset].to_string(index=False))
    g['interval_energy_mwh']=g.meter_change_mwh.mask(g.meter_reset)
    g['daily_energy_mwh']=g.interval_energy_mwh.where(g.interval_days.eq(1))
    decision('Daily 6/6: meter reset','Exactly one negative within-zone counter change: P4 2026-02-17','Retain meter reading; flag reset; mask crossing interval as unknown; resume differencing thereafter; no invented reset-day energy',g.meter_reset.sum())
    decision('Counter semantics','Dictionary defines cumulative reading, not daily flow','Use endpoint changes only across nonreset intervals; gaps give interval energy, never assign it to one day',len(g))
    decision('Partial final daily month','Last observed day September 11, not month end','Keep raw observations; Task B trend stops at August 31; generation September is a separate published complete-month series',g.date.dt.to_period('M').eq('2026-09').sum())
    total=m.subsource.eq('Total') & m.source.eq('All sources')
    totals=m.loc[total].copy();parts=m.loc[~total].copy()
    parts['month']=pd.to_datetime(parts.month,format='%Y-%m');totals['month']=pd.to_datetime(totals.month,format='%Y-%m')
    sums=parts.groupby('month').mwh.sum();published=totals.set_index('month').mwh
    print('Generation parts versus total residual MWh:',(sums-published).to_dict())
    print('All rows / published total:',m.mwh.sum()/totals.mwh.sum())
    decision('Generation 1/1: total mixed with parts','Each month contains eight leaf categories and an All sources / Total row; all rows double-count energy','Separate 18 total rows from 144 mutually exclusive leaves; verify unique month/source/subsource and reconciliation within 2 MWh',total.sum())
    for z,df in g.groupby('zone'):
        print('Calendar audit',z,tslib.audit_index(df.set_index('date'),'D'))
        print('Missing slots',z,int((absent.get_level_values('zone')==z).sum()))
    misses=set(d.code)-set(names); reverse=set(names)-set(d.code)
    print('GeoJSON features:',len(names),'unique codes:',len(names)==len(geo['features']),'join matched:',len(set(d.code)&set(names)),'unmatched district/geometry:',len(misses),len(reverse))
    print('Daily zone join misses:',len(set(g.zone)-set(d.zone)))
    print('Denominator ranges: households',d.households.min(),d.households.max(),'outages',d.outages.min(),d.outages.max(),'monthly total MWh',published.min(),published.max())
    print('Clean district ranges:\n',d.select_dtypes('number').agg(['min','max']).to_string())
    june=g[(g.zone=='P1') & g.date.between('2026-06-01','2026-06-30')]
    prev=g[(g.zone=='P1') & g.date.eq('2026-05-31')].cumulative_mwh.iloc[0]
    energy=june.cumulative_mwh.iloc[-1]-prev
    print('P1 June endpoint energy:',energy,'naive sum:',june.cumulative_mwh.sum(),'inflation:',june.cumulative_mwh.sum()/energy)
    print('r(count, households):',d.outages.corr(d.households),'r(rate, households):',d.interruptions_per_1000_households.corr(d.households))
    print('Pooled rate:',1000*d.outages.sum()/d.households.sum())
    big=d.nlargest(5,'population'); print('Top five population shares land, people:',big.area_km2.sum()/d.area_km2.sum(),big.population.sum()/d.population.sum())
    assert len(d)==24 and d.population.sum()==57857000 and d.households.sum()==8908512
    assert (d.population/d.households).between(5.69,7.37).all()
    assert d.electrification_pct.isna().sum()==3 and d.outage_minutes.notna().sum()==22
    assert d.outages.sum()==388879 and len(g)==3046 and len(absent)==128
    assert len(dates)==529 and g.peak_load_mw.isna().sum()==46 and g.meter_reset.sum()==1
    assert abs(energy-1199206.7)<0.01 and round(june.cumulative_mwh.sum())==574845315
    print('ANCHOR DISCREPANCY: supplied 1,200,239 MWh differs by 1,032.3 MWh from endpoint energy 1,199,206.7; do not force the data to match.')
    assert len(parts)==144 and (sums-published).abs().le(2).all()
    assert not parts.duplicated(['month','source','subsource']).any() and parts.groupby('month').size().eq(8).all()
    assert not misses and not reverse
    assert d.nlargest(3,'outages').code.tolist()==['D17','D13','D24']
    assert d.nlargest(3,'interruptions_per_1000_households').code.tolist()==['D12','D11','D13']
    for name,df in [('district_grid',d),('grid_daily',g),('generation_mix',parts),('generation_totals',totals)]: df.to_csv(ROOT/'clean'/f'{name}.csv',index=False)
    (ROOT/'clean/regions.geojson').write_text(json.dumps(geo))
    header='| What | How detected | Rule applied | Rows affected |\n|---|---|---|---|\n'
    (ROOT/'partA_decisions.md').write_text('# Task A — decisions\n\n'+header+'\n'.join('| '+' | '.join(row)+' |' for row in decisions)+'\n\nThe eleven defect kinds are explicitly numbered 4 + 6 + 1. Extra decisions explain semantics and partial periods. Conflict rules are conservative estimates; D21 is an inferred unit correction supported by the supplied validation anchors.\n')
    print('\nAll reproducible data assertions passed; one published energy anchor discrepancy recorded.')
if __name__=='__main__': main()

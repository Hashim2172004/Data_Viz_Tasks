from common import *
import json
COLS=['age','systolic','diastolic','heart_rate','spo2','bmi','chol_mmol_l','glucose_mmol_l','los_days']
LABELS=['Age','SBP','DBP','HR','SpO2','BMI','Chol','Glucose','LOS']
WARD_MAP={'general medicine':'General Medicine','gen medicine':'General Medicine','cardiology':'Cardiology','cardio':'Cardiology','day surgery':'Day Surgery','day-surgery':'Day Surgery','intensive care':'ICU','icu':'ICU','i.c.u':'ICU'}
def inspect(df):
    df.info()
    print(df.describe().T)
    print(df.ward.value_counts())
    print(df.admit_date.head(20).tolist())
def clean(raw):
    d=raw.copy();log=[]
    def entry(rule,count,before,after):log.append({'rule':rule,'count':int(count),'before':str(before),'after':str(after)})
    d['ward_clean']=d.ward.str.strip().str.lower().map(WARD_MAP);assert d.ward_clean.notna().all() and d.ward_clean.nunique()==4
    entry('Normalize whitespace/case and explicit ward aliases; no rows removed',sum(d.ward!=d.ward_clean),raw.ward.nunique(),d.ward_clean.nunique())
    dt=pd.Series(pd.NaT,index=d.index,dtype='datetime64[ns]')
    for fmt in ['%Y-%m-%d','%d/%m/%Y','%d-%b-%Y']:dt=dt.fillna(pd.to_datetime(d.admit_date,format=fmt,errors='coerce'))
    d['admit_dt']=dt;assert dt.notna().all();entry('Parse ISO, day/month/year and day-abbreviated-month-year explicitly',len(d),'10000 text dates',f'{dt.notna().sum()} valid datetimes; 0 failures')
    bad_bmi=d.bmi.isin([0,999]);before=d.bmi.mean();d.loc[bad_bmi,'bmi']=np.nan
    entry('BMI 0 or 999 are missing-value sentinels; invalidate cells, retain rows',sum(bad_bmi),f'mean {before:.5f} kg/m2',f'mean {d.bmi.mean():.5f} kg/m2')
    bad_hr=(d.heart_rate==0)|(d.heart_rate>250);before=d.heart_rate.mean();d.loc[bad_hr,'heart_rate']=np.nan
    entry('HR >250 device faults (29) or 0 no valid resting reading (8); invalidate cells, retain other measurements',sum(bad_hr),f'mean {before:.5f} bpm',f'mean {d.heart_rate.mean():.5f} bpm')
    entry('Exclude derived MAP from inferential heatmap; no rows removed',0,f'max formula rounding error {np.abs(d.map_mmhg-(d.systolic+2*d.diastolic)/3).max():.4f} mmHg','9 independently recorded numeric measures in heatmap')
    zero=d.los_days==0;entry('Zero-day stays retained as possible same-day stays; omit only from log-LOS box plot',sum(zero),f'mean LOS {d.los_days.mean():.6f}',f'positive-only mean LOS {d.loc[~zero,"los_days"].mean():.6f}')
    entry('Retain long stays; do not hide fliers; do not impose normality',0,f'LOS skewness {d.los_days.skew():.3f}',f'LOS median {d.los_days.median():.3f}; max {d.los_days.max():.2f}')
    entry('SpO2 empirical bounded support; no ordinary unbounded KDE',0,f'max {d.spo2.max()}%',f'{sum(d.spo2>100)} readings above 100%')
    entry('Systolic bimodality inspected with 3,45,400 bins; use 5 mmHg width',0,'range 92-199 mmHg','all 10000 observations retained')
    # Rounded risk_score does not provide exact event numerator; do not invent it.
    approx=(d.risk_score*d.los_days).sum()/d.los_days.sum()
    entry('Risk is a per-row ratio; exclude it from heatmap and do not call its mean an overall event rate',0,f'unweighted mean {d.risk_score.mean():.6f}',f'LOS-weighted approximation {approx:.6f} events/day; exact numerator unavailable')
    entry('Duplicate IDs and missingness checked; no whole rows deleted',0,f'duplicate IDs {d.patient_id.duplicated().sum()}',f'{len(d)} rows retained; BMI invalid {bad_bmi.sum()}, HR invalid {bad_hr.sum()}')
    t=pd.DataFrame(log);t.to_csv(ROOT/'outputs'/'cleaning_log.csv',index=False);print(t.to_string(index=False));return d,t

def build_figure(d,name='partD_figure',sensitivity=False):
    corr=d[COLS].corr(method='pearson',min_periods=3)
    ranked=corr.where(np.tril(np.ones_like(corr,dtype=bool),-1)).stack().abs().sort_values(ascending=False)
    y,x=ranked.index[0];r=corr.loc[x,y]
    fig,axes=plt.subplots(2,2,figsize=(15,11))
    ax=axes[0,0];ax.hist(d.systolic,bins=np.arange(90,206,5),color=C[0],edgecolor='white');ax.set(title='Systolic pressure contains two visible modes',xlabel='Systolic blood pressure (mmHg)',ylabel='Records');ax.text(.03,.93,'Bin width = 5 mmHg; n = 10,000',transform=ax.transAxes,va='top',fontsize=9)
    positive=d[d.los_days>0];order=positive.groupby('ward_clean').los_days.median().sort_values().index.tolist()
    ax=axes[0,1];sns.boxplot(data=positive,x='ward_clean',y='los_days',order=order,color=C[0],showfliers=True,whis=1.5,width=.6,fliersize=2,linewidth=1,ax=ax);ax.set_yscale('log');ax.set(title='ICU stays are longest; long-stay outliers remain visible',xlabel='Ward (ordered by median)',ylabel='Length of stay (days; log scale)');ax.tick_params(axis='x',labelsize=8)
    # One common colour and explicit positions avoid requiring four distinguishable colours.
    for i,w in enumerate(order):ax.text(i,.99,f'median {positive.loc[positive.ward_clean==w,"los_days"].median():.2f}',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
    ax=axes[1,0];pairs=d[[x,y]].dropna();sample=pairs.sample(n=min(2000,len(pairs)),random_state=220)
    ax.scatter(sample[x],sample[y],s=10,alpha=.18,color=C[0],edgecolors='none');units={'systolic':'Systolic blood pressure (mmHg)','diastolic':'Diastolic blood pressure (mmHg)'}
    ax.set(title=f'Independent BP readings track together: r = {r:.2f}',xlabel=units.get(x,x),ylabel=units.get(y,y));ax.text(.03,.95,'2,000 points; seed=220; alpha=.18\nr uses all valid pairs',transform=ax.transAxes,va='top',fontsize=9)
    ax=axes[1,1];mask=np.triu(np.ones_like(corr,dtype=bool),k=0);sns.heatmap(corr,mask=mask,cmap='RdBu_r',vmin=-1,vmax=1,center=0,annot=True,fmt='.2f',xticklabels=LABELS,yticklabels=LABELS,annot_kws={'fontsize':8},linewidths=.3,cbar_kws={'label':'Pearson r','shrink':.8},ax=ax);ax.set_title('BP has the strongest independent pair; age-cholesterol is weaker');ax.tick_params(axis='x',rotation=45);ax.tick_params(axis='y',rotation=0)
    fig.suptitle('Clinical review: pressure subgroups and long stays require separate attention'+(' | no HR/BMI exclusions' if sensitivity else ''),fontsize=14)
    note='10,000 records retained. Primary: 486 BMI sentinel cells and 37 HR fault cells set missing; pairwise-complete correlation.\nLog LOS omits 2 zero-day records only; 9,998 positive stays, fliers shown. No MAP/risk-score correlation. Histogram width=5; scatter n=2,000, seed=220, alpha=.18.\nHeatmap: lower triangle, RdBu_r [-1,1], center=0; Pearson r; 300 dpi. '+('Sensitivity uses original HR/BMI cells.' if sensitivity else 'All other measurements retained.')
    finish(fig,name,note)
    corr.to_csv(ROOT/'outputs'/f'{name}_correlation.csv')
    # Pairwise denominators are explicit, rather than one misleading n for the whole matrix.
    valid=d[COLS].notna().astype(int);(valid.T@valid).to_csv(ROOT/'outputs'/f'{name}_pairwise_n.csv')
    return corr

def main():
    raw=read('vitals_10k');inspect(raw);d,log=clean(raw)
    d.to_csv(ROOT/'outputs'/'vitals_cleaned.csv',index=False)
    wide=read('ward_los_wide');long=wide.melt(var_name='ward',value_name='los_days');padding=long.los_days.isna().sum();long=long.dropna(subset=['los_days']);long['ward']=long.ward.replace({'Icu':'ICU'});long.to_csv(ROOT/'outputs'/'ward_los_long.csv',index=False)
    assert len(long)==10000
    print(f'Wide LOS: {len(wide)*len(wide.columns)} cells, {padding} padding blanks omitted by melt/dropna; {len(long)} observations. No patient observations lost.')
    # Wide export has no IDs; primary ward panel uses the ID-linked vitals source.
    check1=long.groupby('ward').los_days.agg(['count','median']);check2=d.groupby('ward_clean').los_days.agg(['count','median']);assert np.allclose(check1.sort_index(),check2.sort_index())
    check1.to_csv(ROOT/'outputs'/'ward_los_melt_check.csv');corr=build_figure(d)
    sensitivity=d.copy();sensitivity['heart_rate']=raw.heart_rate;sensitivity['bmi']=raw.bmi;build_figure(sensitivity,'partD_without_exclusion',True)
    fig,axes=plt.subplots(1,2,figsize=(10,4));bins=np.arange(0,441,10)
    axes[0].hist(raw.heart_rate,bins=bins,color=C[1]);axes[0].set(title='All readings include device faults',xlabel='Heart rate (bpm)',ylabel='Records');axes[1].hist(d.heart_rate.dropna(),bins=bins,color=C[0]);axes[1].set(title='37 invalid readings excluded explicitly',xlabel='Heart rate (bpm)',ylabel='Records');finish(fig,'partD_HR_exclusion_sensitivity','Before n=10000, mean=78.8331; after n=9963, mean=78.0469. Shared 0..440 edges, width=10 bpm. No hidden fliers.')
    skew=d[COLS].skew();skew.to_csv(ROOT/'outputs'/'skewness.csv');print('Skewness (non-normality screen, not proof):\n',skew)
    print('Strongest non-derived pair: systolic/diastolic',corr.loc['systolic','diastolic'],'; age/cholesterol',corr.loc['age','chol_mmol_l'])
    return d,log
if __name__=='__main__':main()

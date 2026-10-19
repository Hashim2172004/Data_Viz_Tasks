# %%
from common import *
from statsmodels.tsa.seasonal import seasonal_decompose
_,h,daily,_,_=clean_sessions(False)
report=tslib.window_report(daily,(7,28,91));print(report.to_string(index=False));report.to_csv(OUT/'window_report.csv',index=False)
print('Variation removed is reduction in standard deviation, NOT variance. 7 days cancels the weekly cycle; 28 averages four weeks; 91 averages thirteen weeks and attenuates slower seasonal movement. Select 7 days for Monday monitoring.')
print('Toolkit caveat: its min_periods=window//2 allows partial edge windows, so reported periods_lost_each_end is nominal support loss, not actual missing output. Dashboard uses strict full windows.')
for w in (7,28,91):
    strict=daily.rolling(w,center=True,min_periods=w).mean()
    print(w,'strict leading/trailing support losses:',w//2,(w-1)//2,'missing output total incl gaps:',strict.isna().sum())
# %%
t=pd.Timestamp('2024-11-29');means=daily.rolling(14,center=True,min_periods=14).mean();medians=daily.rolling(14,center=True,min_periods=14).median();ewma=daily.ewm(span=14,adjust=False,ignore_na=True).mean()
print('Black Friday raw:',daily.loc[t]);print('14-day centered mean:',means.loc[t],'median:',medians.loc[t],'EWMA span 14:',ewma.loc[t])
print('EWMA is causal, not centered; alpha=2/15, adjust=False, ignore_na=True. Live monitoring: EWMA alongside raw spike. Retrospective typical-day quarterly summary: centered median with raw event retained. Median is not a substitute for a revenue/session total.')
fig,ax=plt.subplots(figsize=(10,4));sel=slice('2024-11-15','2024-12-15')
for s,label,color in [(daily,'Raw daily sum','#b6bcc3'),(means,'14-day centered mean',COL[0]),(medians,'14-day centered median',COL[1]),(ewma,'EWMA span 14 (trailing)',COL[2])]:ax.plot(s.loc[sel],label=label,color=color)
ax.set(title='Black Friday affects the mean more than the median',ylabel='Sessions/day (sum; smoothers as labelled)');ax.legend(fontsize=8);dateaxis(ax);finish(fig,'partB_spike.png','10×4 in. Sentinel-hour interpolation as documented in Part D.')
# %%
# seasonal_decompose forbids NaN. Interpolate on a separate analysis copy, never silently in raw chart.
analysis=daily.interpolate('time',limit_direction='both');imputed=daily.isna()
print('Decomposition-only estimated days:',int(imputed.sum()),'; boundary fill:',int(daily.iloc[[0,-1]].isna().sum()))
dec=seasonal_decompose(analysis,model='additive',period=7)
amp=dec.seasonal.max()-dec.seasonal.min();resdate=dec.resid.abs().idxmax()
print('Weekly peak-to-trough amplitude:',amp,'sessions/day; largest absolute residual:',resdate,'value:',dec.resid.loc[resdate])
try:
    annual=seasonal_decompose(analysis,model='additive',period=365)
except ValueError as e:
    print('Annual decomposition cannot be estimated:',e)
print('Only 518 days are available, below 730 required for two annual cycles; no annual result is fabricated. With sufficient history, repeating annual variation could move from residual into seasonal.')
fig,axs=plt.subplots(3,1,figsize=(11,7),sharex=True)
axs[0].plot(analysis,color='#b6bcc3',label='Daily analysis copy');axs[0].scatter(analysis.index[imputed],analysis[imputed],s=16,marker='x',color=COL[1],label='Decomposition-only estimated day');axs[0].plot(dec.trend,label='7-day decomposition trend');axs[0].legend(fontsize=7);axs[0].set_title('Weekly decomposition isolates the Black Friday residual')
axs[1].plot(dec.seasonal);axs[1].set_ylabel('Weekly seasonal\n(sessions/day)');axs[2].plot(dec.resid);axs[2].set_ylabel('Residual\n(sessions/day)');dateaxis(axs[2]);finish(fig,'partB_decomposition.png','11×7 in. Additive period 7; missing daily totals interpolated only for decomposition.')
# %%
lag=tslib.lag_at_turn(daily,31);print('31-day turning-point lag:',lag)
print('The minimum is compared on the same regular calendar with strict full-window support. A live dashboard must use trailing estimates and say: 31-day trailing mean, historical smoothing delays turns by about 15 days; newest value uses no future data.')
# %%
# Operational definition: 12 consecutive start months beginning April 2024,
# a fixed common end date, and each stated centered rolling window. No choice is hidden.
rows=[]
for start in pd.date_range(daily.index.min(),periods=12,freq='MS'):
    for w in (7,14,28,56,91):
        s=daily.loc[start:].rolling(w,center=True,min_periods=max(2,w//2)).mean().dropna()
        slope=np.polyfit((s.index-s.index[0]).days,s,1)[0]
        rows.append({'start':start.date(),'end':daily.index.max().date(),'window_days':w,'slope_sessions_per_day2':slope,'direction':'rising' if slope>0 else 'falling' if slope<0 else 'flat'})
sensitivity=pd.DataFrame(rows);print(sensitivity.to_string(index=False));print('Direction counts:',sensitivity.direction.value_counts().to_dict());sensitivity.to_csv(OUT/'window_sensitivity_60.csv',index=False)
print('The brief does not specify a year, end date or fit convention; the above definition makes these 60 results reproducible. A cherry-picked interval has no unique reference effect across periods; a scalar Lie Factor would require a defensible common estimand and baseline. Report every window, dates and slopes, alongside full-history data instead.')
valid=daily.dropna();bank=tslib.banked_figsize(valid.to_numpy(),x=(valid.index-valid.index[0]).days.to_numpy());print('Banked figsize:',bank,'width/height:',bank[0]/bank[1],'; clipping in toolkit means not necessarily exactly 45 degrees.')
fig,ax=plt.subplots(figsize=bank);ax.plot(daily,color='#c1c5cb',lw=.6,label='Daily totals');
for w in (7,28):ax.plot(daily.rolling(w,min_periods=max(2,w//2)).mean(),label=f'{w}-day trailing mean (at least {max(2,w//2)} valid days)')
ax.set(title='Seven- and 28-day views expose window sensitivity',ylabel='Sessions/day (sum before smoothing)');ax.legend(fontsize=7);dateaxis(ax);finish(fig,'partB_window_appendix.png',f'Banked canvas {bank[0]:.2f}×{bank[1]:.2f} in; partial rolling support disclosed.')

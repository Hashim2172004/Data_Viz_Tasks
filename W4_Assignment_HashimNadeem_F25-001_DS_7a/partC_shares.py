# %%
from common import *
import time
from IPython.display import display, Image, clear_output
shares=read('shares_eight.csv');touch=read('case08_channel_attrib.csv');flags=touch.filter(like='touch_').columns
check=tslib.exclusivity_check(touch,flags);print('Touch flags:',check)
assert not check['exclusive']
assert shares.slice.is_unique and shares.subcategory.is_unique and (shares.share_pct>=0).all()
assert abs(shares.share_pct.sum()-100)<1e-6
# One-hot membership of the eight documented disjoint subcategories.
print('Eight category membership:',tslib.exclusivity_check(pd.get_dummies(shares.subcategory),shares.subcategory))
p=read('case09_premium_share.csv').query("quarter=='2025Q4'").iloc[0];parts=pd.Series({'Premium':p.premium_revenue_pkr_m,'Other':p.total_revenue_pkr_m-p.premium_revenue_pkr_m});pct=parts/parts.sum()*100
assert (parts>=0).all() and abs(pct.sum()-100)<1e-6
print('2025Q4:',parts.to_dict(),pct.to_dict())
print('VERDICTS: Touches: no pie (overlap); separate reach bars valid; neither chart proves causation. Eight shares: pie legal for mix, sorted bars preferred for exact ranking. Premium/other: pie or bars legal for revenue composition; neither alone answers absolute growth. Exclusivity of revenue partitions follows their definition, not their summing to 100 alone.')
# %%
fig,ax=plt.subplots(figsize=(7,7));ax.pie(shares.share_pct,labels=shares.slice,startangle=90,counterclock=False,colors=plt.get_cmap('tab20').colors[:8]);ax.set_title('Rank the eight category shares, largest first');finish(fig,'partC_pie_stimulus.png','7×7 in. Reader stimulus: labels only, no numeric values.')
ordered=shares.sort_values('share_pct');fig,ax=plt.subplots(figsize=(8,5));ax.barh(ordered.slice,ordered.share_pct,color=COL[0]);ax.set(title='Rank the eight category shares, largest first',xlabel='Share of eight-subcategory total (%)',xlim=(0,27));finish(fig,'partC_bar_stimulus.png','8×5 in. Common zero baseline; exact ranking uses position and length.')
# %%
true_order=shares.sort_values('share_pct',ascending=False).slice.tolist()
def score_order(order):
    answer=[x for x in order.upper() if x in 'ABCDEFGH']
    if len(answer)!=8 or set(answer)!=set('ABCDEFGH'):raise ValueError('Enter each letter A–H exactly once.')
    positions=[i+1 for i,(a,b) in enumerate(zip(answer,true_order)) if a!=b]
    return ''.join(answer),len(positions),positions

def run_reader_experiment():
    reader=input('Anonymous reader ID (do not use a full name): ').strip()
    rows=[]
    for stimulus in ['pie','bar']:
        clear_output(wait=True)
        input('Press Enter when the reader is ready. Do not reveal the true order.')
        clear_output(wait=True)
        display(Image(filename=str(OUT/f'partC_{stimulus}_stimulus.png')))
        start=time.perf_counter();order=input('Largest to smallest (all A–H, once each): ');seconds=time.perf_counter()-start
        normalized,wrong,positions=score_order(order)
        rows.append(dict(reader=reader,stimulus=stimulus,order=normalized,seconds=seconds,wrong_count=wrong,wrong_positions=' '.join(map(str,positions)),status='observed'))
    result=pd.DataFrame(rows);result.to_csv(OUT/'pie_ranking_results.csv',index=False)
    clear_output(wait=True);display(result)
    print('True order:',''.join(true_order))
    for row in rows:print(row['stimulus'],'wrong positions:',row['wrong_positions'] or 'none','; top two and bottom one correct:',not(set(map(int,row['wrong_positions'].split())) & {1,2,8}))
    print('This is one reader, pie first and bars second: practice, typing time and order effects limit inference. It cannot establish a population effect. Compare middle-position errors against the deck prediction; disagreement is a valid observation.')
    return result
# Leave missing empirical results explicitly missing; never overwrite completed observations.
result_path=OUT/'pie_ranking_results.csv'
if not result_path.exists():
    pd.DataFrame([{'reader':'','stimulus':s,'order':'','seconds':np.nan,'wrong_count':np.nan,'wrong_positions':'','status':'pending_real_reader'} for s in ['pie','bar']]).to_csv(result_path,index=False)
print('Real-reader results are pending. Run the final notebook cell interactively to collect and score them.')
print('Rule: I will draw a pie only for a meaningful, exhaustive whole split into exclusive nonnegative parts, when approximate composition is the question and there are few readily distinguishable slices; I will use bars for exact ranking.')

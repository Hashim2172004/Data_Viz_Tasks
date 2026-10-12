from common import *
from vizlib import lie_factor,lie_verdict
EXPLANATION='''Only C is honest: zero-baseline bar lengths encode the 20% data increase exactly.
A encodes only tips above 29.6%: ink grows 500% for a 6.667% tax increase (LF=75).
B scales the coin in both dimensions: area grows 125% for a 50% increase (LF=2.5).
D ink grows 12.5% for a 50% increase (LF=.25), suppressing the apparent pollution increase; an authority or polluter wishing to downplay deterioration could benefit. Intent is not known.
E sets radius proportional to population: area grows 1500% for a 300% increase (LF=5).
B and E require ink_dimension=2. Using 1 reports both as honest (LF=1) by ignoring squared area growth.
F has no single Lie Factor for the alleged crossing: the formula assumes one comparable magnitude encoding and baseline for a data change. F mixes two unrelated affine coordinate mappings; the crossing is a relation between independently scaled series, not one graphic effect. A series-specific length audit would not quantify the false profit implication.
Actual revenue exceeds cost in all months: profit = 8,12,14,17,20,25 PKR million. Profit increased 212.5% from January to June.
'''
def main():
    d=read('case07_lie_factor');rows=[]
    for r in d.itertuples():
        lf,de,ge=lie_factor(r.value_start,r.value_end,r.ink_start,r.ink_end,ink_dimension=r.ink_dimension)
        rows.append({'chart':r.chart_id,'data_effect':de,'graphic_effect':ge,'lie_factor':lf,'verdict':lie_verdict(lf),'ink_dimension':r.ink_dimension})
    t=pd.DataFrame(rows);assert t.loc[t.verdict=='honest','chart'].tolist()==['C'];t.to_csv(ROOT/'outputs'/'partB_results.csv',index=False)
    text=t.to_string(index=False)+'\n\n'+EXPLANATION+SOURCE
    print(text);(ROOT/'outputs'/'partB_output.txt').write_text(text)
    return t
if __name__=='__main__':main()

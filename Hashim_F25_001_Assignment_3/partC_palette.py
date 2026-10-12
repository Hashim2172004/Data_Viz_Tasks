from common import *
from vizlib import simulate_cvd,worst_pair,verdict
MY_PALETTE=['#1F77B4','#FF7F0E','#2CA02C','#D62728']
COURSE=PALETTE['series']+[PALETTE['series_4th']]
KINDS=['normal','deutan','protan','tritan']
EXPLANATION='''Candidate: first four tab10 colours, selected for appearance without assuming safety.
The tab10 candidate fails: deutan S3/S4 DeltaE=4.06, protan S2/S3=.68, tritan S1/S3=6.72. The overall worst is protan S2/S3; normal-vision distance does not establish accessibility.
Course palette: the worst overall is deutan S3 (green)/S4 (purple), DeltaE=7.55. This is the course's 6-8 range: permitted only with a second channel. Protan and tritan minima exceed 8, but that does not cancel the deutan restriction.
For more than three categories, use direct labels, separated positions, distinct markers/line styles or hatches, or small multiples. Never introduce a fourth colour as the only category identifier. Under DeltaE<6, change the palette rather than merely trusting a label.
Simulations are severity-1.0 Machado matrices in linear RGB; distances are OKLab x100. These are the course's heuristic thresholds, not a universal clinical guarantee of readability.
'''
def main():
    fig,axes=plt.subplots(2,4,figsize=(12,4.8));rows=[]
    for row,(label,pal) in enumerate([('Candidate: tab10 first four',MY_PALETTE),('Course: three plus fourth slot',COURSE)]):
        for col,kind in enumerate(KINDS):
            ax=axes[row,col];shown=pal if kind=='normal' else simulate_cvd(pal,kind)
            for i,h in enumerate(shown):
                ax.add_patch(plt.Rectangle((i,0),.9,1,color=h));ax.text(i+.45,-.15,f'S{i+1}',ha='center',fontsize=9)
            ax.set(xlim=(-.1,4),ylim=(-.35,1.25),title=kind);ax.axis('off')
            if col==0:ax.text(0,1.45,label,fontsize=10)
            i,j,a,b,de=worst_pair(pal,kind);rows.append({'palette':label,'vision':kind,'pair':f'S{i}/S{j}','delta_e':de,'verdict':verdict(de)})
    fig.suptitle('The fourth course colour needs a second encoding channel')
    finish(fig,'partC_palette','Machado et al. (2009), severity=1; linear RGB; OKLab distances. Slots are explicitly labelled.')
    t=pd.DataFrame(rows);t.to_csv(ROOT/'outputs'/'partC_results.csv',index=False);text=t.to_string(index=False)+'\n\n'+EXPLANATION
    (ROOT/'outputs'/'partC_output.txt').write_text(text);print(text);return t
if __name__=='__main__':main()

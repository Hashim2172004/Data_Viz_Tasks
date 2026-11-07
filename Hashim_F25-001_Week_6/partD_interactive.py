"""Bonus D1: interactive counterpart of Task B's P1 time trend."""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
ROOT=Path(__file__).resolve().parent

def main():
    g=pd.read_csv(ROOT/'clean/grid_daily.csv',parse_dates=['date'])
    s=g[g.zone=='P1'].set_index('date').peak_load_mw.reindex(pd.date_range('2025-04-01','2026-08-31'))
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=s.index,y=s,mode='lines',line=dict(color='#0072B2',width=1),opacity=.35,name='Daily maximum',connectgaps=False))
    fig.add_trace(go.Scatter(x=s.index,y=s.rolling(7,min_periods=7).mean(),mode='lines',line=dict(color='#0072B2',width=3),name='Trailing 7-day mean',connectgaps=False))
    fig.update_layout(title='P1 demand rises in summer | hover or zoom to inspect',template='plotly_white',height=620,yaxis=dict(title='Peak load (MW)',rangemode='tozero'),xaxis=dict(title='Calendar date',rangeslider=dict(visible=True)),hovermode='x unified',margin=dict(b=170),annotations=[dict(x=0,y=-.33,xref='paper',yref='paper',showarrow=False,align='left',text='Source: synthetic CDB601220 Week 6; P1, Apr 2025–Aug 2026; September omitted as partial.<br>Daily maximum and trailing 7 calendar-day mean (7 valid readings); no imputation; gaps unconnected.<br>Decision: plan capacity around seasonal demand; compare complete seasons before drawing conclusions.')])
    fig.write_html(ROOT/'partD_interactive.html',include_plotlyjs=True,full_html=True)
    (ROOT/'partD_note.md').write_text('# Bonus D1\n\nInteraction lets the reader hover exact dates and values, toggle the raw or smoothed trace, and zoom into a season, which the static overview cannot do.\n\nIt also lets a reader cherry-pick a short interval or hide context to exaggerate a trend, so seasonal claims should use the complete initial date range.\n\nThe HTML embeds Plotly and works offline; missing values remain gaps.\n')
    print('Task D1: standalone offline interactive HTML written.')
if __name__=='__main__':main()

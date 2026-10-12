from pathlib import Path
import json
import pandas as pd
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parent
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=6,textColor=colors.HexColor('#16202E')))
styles.add(ParagraphStyle(name='SmallCustom',fontName='Helvetica',fontSize=8,leading=10,spaceAfter=4))
def para(s,style='BodyCustom'):return Paragraph(escape(s),styles[style])
def pic(path,maxw=6.7*inch,maxh=2.3*inch):
    w,h=PILImage.open(path).size;k=min(maxw/w,maxh/h);return Image(str(path),width=w*k,height=h*k)
def footer(canvas,doc):
    canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#5B6573'));canvas.drawString(35,20,'CDB601220 | Week 3 | All analysed data are synthetic course datasets');canvas.drawRightString(A4[0]-35,20,str(doc.page))
def main():
    diagnoses=json.loads((ROOT/'outputs'/'partA_diagnoses.json').read_text());story=[]
    for row in diagnoses:
        k=row['case'];story.append(para(f"Case {k}: {row['title']}",'Heading2'))
        for field in ['conclusion','decoy','mechanism','redesign']:story.append(para(field.title()+': '+row[field]))
        if k==6:
            story.append(para('Redesign and disclosed influence sensitivity','SmallCustom'));story.append(pic(ROOT/'figures'/f'A{k:02d}_redesign.png',maxh=2.8*inch));story.append(PageBreak());story.append(para('Case 6: required original 20 x 20 matrix','Heading2'));story.append(pic(ROOT/'figures'/f'A{k:02d}_original.png',maxh=8.6*inch))
        else:
            story.append(para('Required reconstruction (or summary table)','SmallCustom'));story.append(pic(ROOT/'figures'/f'A{k:02d}_original.png'));story.append(Spacer(1,5));story.append(para('Honest redesign','SmallCustom'));story.append(pic(ROOT/'figures'/f'A{k:02d}_redesign.png'))
        if k!=9:story.append(PageBreak())
    SimpleDocTemplate(str(ROOT/'partA_diagnosis.pdf'),pagesize=A4,rightMargin=35,leftMargin=35,topMargin=28,bottomMargin=32).build(story,onFirstPage=footer,onLaterPages=footer)
    log=pd.read_csv(ROOT/'outputs'/'cleaning_log.csv');skew=pd.read_csv(ROOT/'outputs'/'skewness.csv',index_col=0)
    text=[
      ('Part E - Clinical figure justification','Heading2'),
      ('Panel 1 asks whether systolic pressure has one population or multiple modes. A 5 mmHg histogram exposes two modes; aligned position and bar length encode quantitative counts on a common zero baseline. I compared 3, 45 and 400 bins first. Bin edges 90-205 cover every value (n=10,000); the two-mode shape is not evidence identifying a specific clinical subgroup.','BodyCustom'),
      ('Panel 2 asks which wards have longer and more variable stays. A box plot compares median, IQR and tails. Ward order is ascending median; all four use the same blue because labelled positions identify category. Log10 y preserves the 273.65-day maximum while separating typical stays (overall median 1.38 days; skewness 22.755). Whiskers=1.5 IQR, width=.6, linewidth=1, fliersize=2; showfliers=True retains unusual observations.','BodyCustom'),
      ('Panel 3 asks how the strongest independently recorded pair behaves. Panel 4 screens all nine measurements: systolic/diastolic is strongest after excluding derived MAP. Scatter uses aligned x/y position, not area, to show association; it is not a novel causal discovery. A uniform sample of 2,000 valid pairs, seed=220, size=10 points squared, alpha=.18 and no point edges controls overlap. Pearson r uses all valid pairs. Age/cholesterol is a weaker additional association.','BodyCustom'),
      ('Panel 4 asks which independently recorded indicators correlate. Pearson correlation uses pairwise-complete data (minimum 3 pairs); sample-size matrix is exported. Lower triangle excludes diagonal and duplication; RdBu_r, vmin=-1, vmax=1 and center=0 preserve sign and comparability. Two-decimal annotations provide exact readings; cell linewidth=.3 and colourbar shrink=.8 improve legibility. MAP is arithmetic, and risk_score is a ratio, so neither enters the matrix.','BodyCustom'),
      ('Cleaning and exclusions: all 10,000 patient rows remain. Normalize 12 ward spellings to 4 (6,533 labels changed); parse three explicit date formats, including day-first slashes (10,000 successful; 0 failures). BMI 0 (84) and 999 (402) are missing sentinels: 486 cells set missing; mean 66.17704 to 27.34627 kg/m2. Heart-rate readings above 250 bpm were excluded as device faults (n=29), plus 8 zero readings invalidated. Mean HR moves from 78.83310 to 78.04687 bpm (n=9,963). The figure was also produced without the HR/BMI exclusions; it and the shared-scale HR sensitivity histogram are in the appendix.','BodyCustom'),
      ('Two zero-day LOS rows are omitted only from the log box plot (10,000 to 9,998; mean 2.309091 to 2.309553 days). Possible same-day stays and every long stay remain in the source and other analyses; no arbitrary upper LOS cutoff is imposed. Wide LOS is melted: 6,072 padding cells, not patient records, are omitted; 10,000 observations match ID-linked ward medians/counts. No other rows are deleted. The Scott SpO2 KDE leaks beyond 100%, so bounded empirical probabilities are used in Part A; vitals normality is not assumed.','BodyCustom'),
      ('Risk-score mean 1.120877 is not an aggregate event rate. Weighting by LOS gives only an approximation (.654373 events/day) because the exact event numerator is absent and the supplied ratio is rounded; no exact rate is claimed. These choices precede outcome interpretation and would remain if they weakened the finding (symmetry test). Figure: 15 x 11 inches, font DejaVu Sans, message titles, labelled units, top/right spines removed, tight layout, white background, 300 dpi and tight bounding box; source and sample rules accompany the export.','BodyCustom'),
      ('Source: supplied DATA_DICTIONARY.md, TASKS.md and vizlib.py; synthetic CDB601220 Week 3 data. No patient-risk prediction or real-world policy conclusion is claimed.','SmallCustom')]
    (ROOT/'outputs'/'partE_justification.txt').write_text('\n\n'.join(s for s,_ in text))
    SimpleDocTemplate(str(ROOT/'partE_justification.pdf'),pagesize=A4,rightMargin=35,leftMargin=35,topMargin=28,bottomMargin=30).build([para(s,st) for s,st in text],onFirstPage=footer,onLaterPages=footer)
if __name__=='__main__':main()

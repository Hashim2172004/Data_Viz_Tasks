from common import *
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape
styles=getSampleStyleSheet();styles['BodyText'].fontSize=10;styles['BodyText'].leading=14
styles['Title'].textColor=colors.HexColor('#16314a');styles['Heading2'].textColor=colors.HexColor('#0072B2')
def ascii_text(t):return t.replace('→',' to ').replace('–','-').replace('×',' x ').replace('…','...')
def para(t,style='BodyText'):return Paragraph(escape(ascii_text(t)),styles[style])
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#5B6573'));canvas.drawString(42,24,'CDB601220 | Week 4 | Synthetic course data');canvas.drawRightString(A4[0]-42,24,str(doc.page))
diagnoses=json.loads((OUT/'partA_diagnoses.json').read_text());story=[]
for i,d in enumerate(diagnoses):
    story += [para(f'Case {d["case"]}: {d["title"]}','Title'),Spacer(1,10),Image(str(OUT/f'partA_case{d["case"]:02}.png'),width=510,height=213),Spacer(1,12)]
    for label in ['conclusion','decoy','mechanism','redesign']:
        story += [para(label.title(),'Heading2'),para(d[label]),Spacer(1,5)]
    if i<len(diagnoses)-1:story.append(PageBreak())
SimpleDocTemplate(str(ROOT/'partA_diagnosis.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=38,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
log=json.loads((OUT/'cleaning_audit.json').read_text());s=log['sessions'];c=log['catalogue']
sections=[
('Questions and visual channels', 'Panel 1 asks how daily traffic evolves after its weekly rhythm is averaged: time uses horizontal position, sessions vertical position; grey retains raw context and blue provides one pop-out. Panel 2 asks when visits recur: a sequential Blues heatmap encodes mean hourly sessions, with no artificial midpoint. Panel 3 asks where revenue mass sits: nested rectangles show category containment and area. Panel 4 asks by how much subcategories differ: common-baseline position and length outrank angle and area. Values and labels supplement all four parent hues, especially the weaker fourth hue; CVD simulations are included.'),
('Time, coverage and window', 'Two loggers require separate exact formats: ISO timestamps and DD/MM/YYYY HH:MM (3,651 slash rows). Pakistan locale, day values above 12, and the documented April 2024 start support day-first parsing; the verified range is 1 April 2024 to 11 September 2025. Sort before resampling; normalize six device spellings to three classes. Sessions are hourly flows, summed to calendar days only when 24 valid or explicitly estimated hours exist. The 312 absent hours remain gaps. Interpolate 286 invalid sentinel hours between observed neighbours; leave the first unbounded sentinel missing. Crosses mark affected daily estimates. Exclude the 264 recorded hours of partial September from the time-series analysis; 518 days remain, 14 without complete totals. The heatmap uses valid observed hours, without imputation.'),
('Window ethics and sensitivity', 'I fixed the seven-day trailing mean before comparing alternative windows because the target is a weekly cycle and Monday monitoring must not use future data. Full seven-day support is required; gaps break the curve. The start remains the first recorded calendar day. Would I keep this choice if it weakened the finding? Yes. The appendix shows a 28-day alternative with disclosed partial support, not an assertion that every conclusion is unchanged. Across 12 declared starts and five windows, 40 fitted trends rise and 20 fall; all 60 are exported. The 17 x 11 inch dashboard aspect is declared. A separate banked appendix reports its computed ratio.'),
('Exclusions, hierarchy and reconciliation',f'Remove 286 matching duplicate-hour rows: 12,670 to 12,384; session sum {s["raw_sessions_sum"]:,} to {s["after_dedup_sum"]:,}. Replace 287 remaining -1 sentinel values with missing: observed valid sum becomes {s["valid_observed_sum"]:,.0f}; these are value exclusions, not deleted rows. The catalogue loses one conflicting-parent duplicate SKU (14.8275 PKR m), 345 to 344 rows; retain its Audio assignment supported by the AUDI name. Separate seven negative SKUs (-1.0693 PKR m) rather than drawing negative areas: positive area 1,712.4508 plus signed adjustment -1.0693 equals net 1,711.3815. Roll 337 nonnegative SKUs to eight subcategories within four parents; cut depth at subcategory. Other contains zero categories and zero value (all eight exceed 1%). Reference-share differences are below 0.3 percentage points. Catalogue coverage is the entire extract; time panels stop at the last complete month, so their periods are not asserted to be identical.')]
(ROOT/'partE_justification.md').write_text('# Part E - Written justification\n\n'+'\n\n'.join('## '+a+'\n'+b for a,b in sections)+'\n\nSource: '+SOURCE)
styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
styles['Heading2'].fontSize=11;styles['Heading2'].spaceAfter=5;styles['Heading2'].spaceBefore=9
story=[para('Part E | Design and data decisions','Title')]
for a,b in sections:story += [para(a,'Heading2'),para(b)]
SimpleDocTemplate(str(ROOT/'partE_justification.pdf'),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=30,bottomMargin=38).build(story,onFirstPage=footer,onLaterPages=footer)
print('PDF reports written.')

from pathlib import Path
import subprocess,sys,shutil
ROOT=Path(__file__).resolve().parent
for name in ['partA_charts.py','partB_lie_factor.py','partC_palette.py','partD_figure.py']:
    result=subprocess.run([sys.executable,str(ROOT/name)],cwd=ROOT,capture_output=True,text=True,check=True)
    (ROOT/'outputs'/name.replace('.py','_run.txt')).write_text(result.stdout)
    if result.stderr:print(result.stderr)
    print('Completed',name)
subprocess.run([sys.executable,str(ROOT/'build_reports.py')],cwd=ROOT,check=True)
for name in ['partC_palette','partD_figure']:
    shutil.copy2(ROOT/'figures'/f'{name}.png',ROOT/f'{name}.png')
print('All required parts regenerated.')

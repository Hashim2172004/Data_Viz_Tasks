"""Regenerate all computational outputs; real-reader collection stays interactive."""
from pathlib import Path
import os,runpy,contextlib
root=Path(__file__).resolve().parent;os.chdir(root)
(root/'outputs').mkdir(exist_ok=True)
for name in ['partD_figure','partA_charts','partB_windows','partC_shares']:
    print('Running',name)
    with (root/'outputs'/f'{name}_console.txt').open('w') as log,contextlib.redirect_stdout(log):
        runpy.run_path(str(root/f'{name}.py'),run_name='__main__')
runpy.run_path(str(root/'build_reports.py'),run_name='__main__')
print('Done. Real-reader responses must be collected using the notebook.')

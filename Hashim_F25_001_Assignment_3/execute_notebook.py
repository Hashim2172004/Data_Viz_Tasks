"""Execute the notebook in a fresh IPython process, without network sockets."""
from pathlib import Path
import os
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
ROOT=Path(__file__).resolve().parent
os.chdir(ROOT)
shell=InteractiveShell.instance()
shell.user_ns['__name__']='__main__'
p=ROOT/'W3_Assignment.ipynb';nb=nbformat.read(p,as_version=4)
count=0
for cell in nb.cells:
    if cell.cell_type!='code':continue
    count+=1
    with capture_output(stdout=True,stderr=True,display=True) as cap:
        result=shell.run_cell(cell.source,store_history=True)
    if result.error_before_exec or result.error_in_exec:
        print(cap.stdout);print(cap.stderr)
        raise RuntimeError(f'Notebook cell {count} failed') from (result.error_before_exec or result.error_in_exec)
    outputs=[]
    if cap.stdout:outputs.append(nbformat.v4.new_output('stream',name='stdout',text=cap.stdout))
    if cap.stderr:outputs.append(nbformat.v4.new_output('stream',name='stderr',text=cap.stderr))
    for item in cap.outputs:
        outputs.append(nbformat.v4.new_output('display_data',data=item.data,metadata=item.metadata))
    cell.outputs=outputs;cell.execution_count=count
    print('Executed cell',count,flush=True)
nbformat.validate(nb);nbformat.write(nb,p)
print('Notebook fully executed with outputs:',p)

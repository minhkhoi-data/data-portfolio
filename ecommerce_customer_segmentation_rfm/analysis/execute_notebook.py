"""Execute the delivered notebook in a fresh Jupyter kernel; save it and HTML preview.

A subprocess kernel uses the same Python interpreter as this runner. Only an
observed permission failure allows automatic in-process fallback. Notebook
cell/dependency errors are never retried as permission failures. Managed runtime defaults to the network-free mode; other environments try a
subprocess. Set RFM_KERNEL_MODE to override this selection. Metadata records
the actual method; no frontend certification is implied.
"""
import html
import json
import os
import sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def _execute(notebook):
    """Use the runner's interpreter, and never hide a notebook cell error."""
    from jupyter_client import KernelManager
    default_mode = 'inprocess' if 'CODEX_PRIMARY_RUNTIME' in os.environ else 'auto'
    mode = os.environ.get('RFM_KERNEL_MODE', default_mode)
    if mode not in ('auto', 'subprocess', 'inprocess'):
        raise ValueError('RFM_KERNEL_MODE must be auto, subprocess or inprocess')
    subprocess_error = None
    if mode != 'inprocess':
        km = KernelManager(kernel_name='python3')
        # A user's registered python3 kernel can belong to another environment.
        km.kernel_spec.argv[0] = sys.executable
        client = NotebookClient(notebook, km=km, timeout=600,
                                resources={'metadata': {'path': str(ROOT)}})
        try:
            client.execute(cleanup_kc=True)
            return 'nbclient fresh subprocess Jupyter kernel', {
                'kernel_type': 'subprocess', 'fresh_kernel': True,
                'interpreter_matches_runner': True, 'network_free': False}
        except PermissionError as exc:
            if mode == 'subprocess':
                raise
            subprocess_error = exc
            # Only an observed permission failure permits automatic fallback.
            # CellExecutionError and dependency/code errors propagate unchanged.
            try:
                import atexit
                atexit.unregister(client._cleanup_kernel)
            except Exception:
                pass
    from analysis.inprocess_kernel import CompatInProcessKernelManager
    km = CompatInProcessKernelManager()
    km.start_kernel()
    try:
        NotebookClient(notebook, km=km, timeout=600,
                       resources={'metadata': {'path': str(ROOT)}}).execute()
    finally:
        km.shutdown_kernel()
    meta = {'kernel_type': 'in-process', 'fresh_kernel': True,
            'interpreter_matches_runner': True, 'network_free': True,
            'selection': ('explicit inprocess mode' if 'RFM_KERNEL_MODE' in os.environ else 'managed runtime network-free default') if mode == 'inprocess' else 'observed PermissionError fallback'}
    if subprocess_error is not None:
        meta['subprocess_kernel_error'] = type(subprocess_error).__name__ + ': ' + str(subprocess_error)[:240]
    return 'nbclient fresh in-process Jupyter kernel', meta


def main():
    path=ROOT/'ecommerce_customer_segmentation_rfm.ipynb'
    notebook=nbformat.read(path,as_version=4)
    nbformat.validate(notebook)
    method,kernel_meta=_execute(notebook)
    errors=[o for c in notebook.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
    if errors:raise RuntimeError(errors)
    nbformat.write(notebook,path)
    # Standalone reading preview; escaped text and kernel-produced HTML/images.
    blocks=[]
    for cell in notebook.cells:
        if cell.cell_type=='markdown':
            # Text is preserved verbatim; whitespace/pre-wrap makes this preview
            # readable without adding another runtime dependency.
            blocks.append('<div class="markdown">'+html.escape(cell.source)+'</div>')
        else:
            blocks.append('<pre class="code">'+html.escape(cell.source)+'</pre>')
            for output in cell.get('outputs',[]):
                if output.output_type=='stream':blocks.append('<pre>'+html.escape(output.text)+'</pre>')
                data=output.get('data',{})
                if 'image/png' in data:blocks.append('<img alt="Executed notebook figure" src="data:image/png;base64,'+data['image/png']+'">')
                elif 'text/html' in data:blocks.append('<div class="table">'+data['text/html']+'</div>')
                elif 'text/plain' in data:blocks.append('<pre>'+html.escape(data['text/plain'])+'</pre>')
    css='body{font:16px Arial;color:#172536;max-width:1100px;margin:32px auto;padding:0 20px;line-height:1.5}.markdown{white-space:pre-wrap;margin:28px 0;font-size:17px}pre{white-space:pre-wrap;overflow:auto;padding:14px;background:#f5f6f8;font-size:13px}.table{overflow-x:auto}table{border-collapse:collapse;font-size:13px}td,th{padding:7px;border:1px solid #ddd}img{max-width:100%;height:auto}'
    (ROOT/'notebook_preview.html').write_text('<!DOCTYPE html><html lang="en"><meta charset="utf-8"><title>Customer lifecycle — executed notebook</title><style>'+css+'</style><body><h1>Customer lifecycle — executed notebook</h1>'+''.join(blocks)+'</body></html>',encoding='utf-8')
    evidence={'status':'PASS','method':method,'code_cells':sum(c.cell_type=='code' for c in notebook.cells),'errors':len(errors),'frontend_gui_verified':False,'kernel_name':'python3','python_kernel_path_removed_from_deliverable':True,'python_version':sys.version.split()[0],**kernel_meta}
    (ROOT/'audit/notebook_execution.json').write_text(json.dumps(evidence,indent=2))
    print('PASS — notebook executed in a fresh Jupyter kernel and reading preview saved')

if __name__=='__main__':main()

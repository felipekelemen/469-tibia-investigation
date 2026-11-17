#!/usr/bin/env python3
"""Compile/run the exact C++ regular-language key search, without shell input."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'native/periodic_dictionary_search.cpp'
FLAGS=['-O3','-std=c++17','-Wall','-Wextra','-pedantic']


def binary():
    compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]
    digest=hashlib.sha256(SOURCE.read_bytes()+(' '.join(FLAGS)+compiler).encode()).hexdigest()[:20]
    target=Path(tempfile.gettempdir())/('469-periodic-'+digest)
    if not target.exists():
        subprocess.run(['g++',*FLAGS,str(SOURCE),'-o',str(target)],check=True)
    return target


def run_native(codes,tasks,progress=False):
    codes=sorted(set(codes))
    text=['R22V1 '+str(len(codes)),*codes,str(len(tasks))]
    for t in tasks:
        text.append(' '.join([t['id'],str(t['period']),str(t['feedback']),str(len(t['groups'])),*t['groups']]))
    results=[]
    with tempfile.TemporaryFile(mode='w+t') as input_file:
        input_file.write('\n'.join(text)+'\n');input_file.seek(0)
        process=subprocess.Popen([str(binary())],stdin=input_file,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            for line in process.stdout:
                row=json.loads(line)
                i=len(results)
                if i>=len(tasks) or row['id']!=tasks[i]['id']:raise ValueError('native task order mismatch')
                if not row['complete'] or row['checked_keys']+row['prefix_pruned_keys']!=10**tasks[i]['period']:
                    raise ValueError('native exhaustive coverage check failed')
                results.append(row)
                if progress and (len(results)%20==0 or len(results)==len(tasks)):
                    print('Native complete',len(results),'/',len(tasks),flush=True)
            stderr=process.stderr.read();status=process.wait()
            if status:raise RuntimeError('native search failed: '+stderr)
            if len(results)!=len(tasks):raise ValueError('missing native tasks')
        except BaseException:
            if process.poll() is None:process.terminate()
            process.wait()
            raise
        finally:
            process.stdout.close();process.stderr.close()
    return results

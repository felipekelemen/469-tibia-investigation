#!/usr/bin/env python3
"""Train-only optimized homophonic solver; no fixture truth or holdout input."""
import ctypes,hashlib,pathlib,subprocess,tempfile,time,os
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
INT=np.ctypeslib.ndpointer(dtype=np.int32,ndim=1,flags='C_CONTIGUOUS')
DOUBLE=np.ctypeslib.ndpointer(dtype=np.float64,ndim=1,flags='C_CONTIGUOUS')
_LIB=None

def library():
    global _LIB
    if _LIB is not None:return _LIB
    source=ROOT/'src/homophonic_solver.cpp'
    compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]
    flags=['-std=c++17','-O3','-shared','-fPIC']
    digest=hashlib.sha256(source.read_bytes()+compiler.encode()+repr(flags).encode()).hexdigest()[:20]
    dest=pathlib.Path(tempfile.gettempdir())/f'tibia469-solver-{digest}.so'
    if not dest.exists():
        temporary=dest.with_suffix(f'.{os.getpid()}.tmp.so')
        subprocess.run(['g++',*flags,str(source),'-o',str(temporary)],check=True,capture_output=True)
        temporary.replace(dest)
    lib=ctypes.CDLL(str(dest))
    lib.fh_solve.argtypes=[INT,INT,ctypes.c_int,ctypes.c_int,DOUBLE,ctypes.c_uint64,ctypes.c_int,ctypes.c_int,ctypes.c_double,ctypes.c_double,INT,DOUBLE];lib.fh_solve.restype=ctypes.c_int
    lib.fh_delta.argtypes=[INT,INT,ctypes.c_int,ctypes.c_int,DOUBLE,INT,ctypes.c_int,ctypes.c_int];lib.fh_delta.restype=ctypes.c_double
    _LIB=lib;return lib

def _inputs(sequences,table,num_codes=None):
    seqs=[]
    for x in sequences:
        raw=np.asarray(x)
        if raw.ndim!=1 or not np.issubdtype(raw.dtype,np.integer) or (len(raw) and (raw.min()<0 or raw.max()>255)):
            raise ValueError('training sequences must be one-dimensional integer codes 0..255')
        seqs.append(np.ascontiguousarray(raw,dtype=np.int32))
    if not seqs or not any(len(x)>=4 for x in seqs):raise ValueError('at least one training sequence of four codes required')
    flat=np.ascontiguousarray(np.concatenate(seqs),dtype=np.int32);lengths=np.ascontiguousarray([len(x) for x in seqs],dtype=np.int32)
    if flat.min()<0:raise ValueError('negative code')
    k=int(flat.max())+1 if num_codes is None else int(num_codes)
    if k<=int(flat.max()) or not 1<=k<=256:raise ValueError('num_codes must cover observed codes and be <=256')
    lm=np.ascontiguousarray(table,dtype=np.float64).reshape(-1)
    if len(lm)!=26**4 or not np.isfinite(lm).all():raise ValueError('finite 26**4 English table required')
    return flat,lengths,k,lm

def solve(train_sequences,table,seed=46920261110,restarts=8,steps=100000,*,num_codes=100,max_temp=12.0,frequency_weight=2.0):
    """Return code-indexed mapping (integers A=0), train-only score and diagnostics.

    Unobserved code slots remain arbitrary; callers must report their coverage.
    Finite search success is not guaranteed. Never pass test sequences for fitting.
    """
    if restarts<1 or steps<1 or max_temp<=0 or frequency_weight<0:raise ValueError('invalid search budget')
    flat,lengths,k,lm=_inputs(train_sequences,table,num_codes);mapping=np.zeros(k,dtype=np.int32);stats=np.zeros(5,dtype=np.float64)
    lib=library();start=time.monotonic()
    result=lib.fh_solve(flat,lengths,len(lengths),k,lm,int(seed),int(restarts),int(steps),float(max_temp),float(frequency_weight),mapping,stats)
    if result:raise RuntimeError(f'C++ solver rejected input: {result}')
    return {'mapping':mapping.tolist(),'train_score':float(stats[0]),'objective':float(stats[1]),'accepted_moves':int(stats[2]),
            'incremental_score_drift':float(stats[3]),'scored_tetragrams':int(stats[4]),'runtime_seconds':time.monotonic()-start,
            'seed':int(seed),'budget':{'restarts':int(restarts),'steps':int(steps),'max_temp':max_temp,'frequency_weight':frequency_weight}}

def delta_score(sequences,table,mapping,code,newletter):
    flat,lengths,k,lm=_inputs(sequences,table,len(mapping));m=np.ascontiguousarray(mapping,dtype=np.int32)
    if not (0<=code<k and 0<=newletter<26 and np.all((0<=m)&(m<26))):raise ValueError('invalid mapping or mutation')
    return library().fh_delta(flat,lengths,len(lengths),k,lm,m,int(code),int(newletter))

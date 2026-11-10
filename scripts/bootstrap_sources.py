#!/usr/bin/env python3
"""Obtain public immutable source snapshots; never execute upstream code."""
import json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    for entry in json.loads((ROOT/'sources/manifest.json').read_text()):
        dest=ROOT/'sources'/entry['name']
        if not dest.exists(): subprocess.run(['git','clone',entry['url'],str(dest)],check=True)
        actual=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
        if actual != entry['commit']:
            subprocess.run(['git','-C',str(dest),'fetch','origin',entry['commit']],check=True)
            subprocess.run(['git','-C',str(dest),'checkout','--detach',entry['commit']],check=True)
        assert subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()==entry['commit']
        print(entry['name'],entry['commit'])
if __name__=='__main__':main()

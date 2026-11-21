#!/usr/bin/env python3
"""Replay identical frozen search with cached lexical-domain filtering."""
import argparse
from round27_cached_model import enable
from round27_experiment import verify_manifest
from run_round27 import check

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    verify_manifest('round27_baseline_manifest.json')
    verify_manifest('round27_execution_manifest.json')
    enable()
    check(args.full)

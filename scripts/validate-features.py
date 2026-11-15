#!/usr/bin/env python3
import argparse
from common import read, validate, run

def main():
 p=argparse.ArgumentParser(description='Validate schema, tree, references and optional source evidence.'); p.add_argument('input'); p.add_argument('--repo'); a=p.parse_args(); d=validate(read(a.input),a.repo); print(f'VALID: {len(d["features"])} nodes')
if __name__=='__main__': run(main)

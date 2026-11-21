"""Fixed isolated-gravity example: explicit input, direct reference and force CSV."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from numart.particle_gravity import direct_acceleration, tree_acceleration

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input',type=Path,default=Path(__file__).with_name('input.json'))
parser.add_argument('--output',type=Path,default=Path('output-barnes-hut'))
args=parser.parse_args()
config=json.loads(args.input.read_text())
if config['boundary']!='isolated' or config['G']!=1:raise ValueError('This example requires isolated boundaries and G=1')
x=np.asarray(config['positions'],dtype=float);m=np.asarray(config['masses'],dtype=float)
exact=direct_acceleration(x,m,softening=config['softening'])
approximate,work=tree_acceleration(x,m,theta=config['theta'],order=config['moment_order'],softening=config['softening'])
opened,_=tree_acceleration(x,m,theta=0,order=config['moment_order'],softening=config['softening'])
error=float(np.linalg.norm(approximate-exact)/np.linalg.norm(exact))
exact_limit=float(np.max(abs(opened-exact)))
checks={'fixed_case_relative_force_error':error<config['acceptance']['max_relative_force_error'],
        'fully_opened_tree_matches_direct_sum':exact_limit<config['acceptance']['max_exact_opening_error']}
if not all(checks.values()):raise AssertionError(checks)
args.output.mkdir(parents=True,exist_ok=True)
with (args.output/'forces.csv').open('w',newline='') as handle:
    writer=csv.writer(handle);writer.writerow(['x','y','z','mass','ax_tree','ay_tree','az_tree','ax_direct','ay_direct','az_direct'])
    writer.writerows(np.column_stack([x,m,approximate,exact]))
result={'case':'isolated softened Barnes-Hut versus direct sum','particles':len(m),'units':config['units'],'boundary':'isolated','G':1,
        'softening':config['softening'],'theta':config['theta'],'moment_order':config['moment_order'],'relative_rms_force_error':error,
        'fully_opened_max_absolute_error':exact_limit,'checks':checks,'interaction_counts':work,
        'input_sha256':hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'source_sha256':hashlib.sha256((ROOT/'numart/particle_gravity.py').read_bytes()).hexdigest(),
        'scope':'Fixed static example only; not a periodic solver, timing comparison, trajectory integration or original-figure reproduction.'}
(args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

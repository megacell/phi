import config
import time
import sys
import json
import csv

from collections import defaultdict
from pdb import set_trace as T
from random import shuffle, randint

sys.path.append('../../Locality-sensitive-hashing')
import set_lsh as lsh

def get_cellpaths():
    # Difference between database IDs and cell ids.
    OFFSET = 72341
    with open(config.CELLPATHS_CACHE) as cellpaths:
        for line in cellpaths:
            yield map(lambda x: int(x) - OFFSET, line.split())

def get_SSTEM_paths():
    reader = csv.DictReader(open(config.SSTEM_DATA))
    for row in reader:
        if row['commute_direction'] == '0':
            yield int(row['agent_id']), map(int, row['cells_ID_string'].split())

def get_SSTEM_raw():
    reader = csv.DictReader(open(config.SSTEM_RAW))
    for row in reader:
        if row['commute_direction'] == '0':
            yield int(row['agent_id']), map(int, row['cells_ID_string'].split())

def get_ground_truth():
    reader = csv.DictReader(open(config.TRAJECTORY_CSV))
    for row in reader:
        if row['commute_direction'] == '0':
            yield row

def f():
    reader = csv.DictReader(open(config.SSTEM_DATA))
    cellpath_flows = defaultdict(int)
    print 'Loading SSTEM...'
    
    for row in reader:
        if row['commute_direction'] == '0':
            cellpath = tuple(sorted(set(map(int, row['cells_ID_string'].split()))))
            cellpath_flows[cellpath] += 1

    print 'Total agents in SSTEM: {}'.format(sum(cellpath_flows.values()))

    f = []
    for path in get_cellpaths():
        a = tuple(sorted(set(path)))
        f.append(cellpath_flows[a])
    print 'Agents used in SSTEM: {}'.format(sum(f))
    return f

def cells_hash_gen():
    table = range(805)
    shuffle(table)
    return table.__getitem__

class Matcher:
    def match(self, cellpath):
        assert NotImplemented

class LSHMatcher(Matcher):
    def __init__(self, cellpaths, b, k, hashgen=None):
        self.s = lsh.SetLSH(7, 5, hashgen=cells_hash_gen)
        n = 0
        for path in cellpaths:
            if n % 100000 == 0:
                print n
            if len(path) > 0:
                self.s.insert(set(path))
            n += 1
            
    def match(self, cellpath):
        return self.s.query(set(cellpath))
        
class BruteMatcher(Matcher):
    def __init__(self, cellpaths):
        self.cellpaths = [set(path) for path in get_cellpaths()]
        
    def match(self, cellpath):
        path = set(cellpath)
        return max(self.cellpaths, key=lambda x: lsh.jaccard(x, path))

def bench():
    s = lsh.SetLSH(7, 5, hashgen=cells_hash_gen)
    n = 0
    s1 = time.clock()
    loops = 100000
    for path in get_cellpaths():
        if n == loops:
            break
        if len(path) > 0:
            s.insert(set(path))
        n += 1
    print 'Time per insert: {}'.format((time.clock()-s1) / loops)
    

def compare():
    p1 = json.load(open('f_patch1.json'))
    p2 = json.load(open('f_patch2.json'))
    diffs = [a2[1] - a1[1] for a1, a2 in zip(p1, p2) if a1 != None and a2 != None]
    T()

def main():
    lshm = LSHMatcher(get_cellpaths(), 7, 5, hashgen=cells_hash_gen)
    n = 0
    results = []
    for _, path in get_SSTEM_paths():
        if n % 1000 == 0:
            print n
        n += 1
        results.append(lshm.match(path))

    json.dump(results, open('f.json', 'w'))

def compare():
    ''' Compare brute-force solution with LSH matching'''
    chosen_set = set(randint(0, 1000000) for _ in range(1000))
    chosen = {}
    for row in get_ground_truth():
        aid = int(row['agent_id'])
        if aid in chosen_set:
            chosen[aid] = map(int, row['route_string'].split())
            
    brutem = BruteMatcher(get_cellpaths())
    lshm = LSHMatcher(get_cellpaths(), 7, 5, hashgen=cells_hash_gen)
    print 'Loaded matchers'
    
    res = {}
    for agent_id, path in get_SSTEM_paths():
        if agent_id not in chosen:
            continue
        if len(res) % 10 == 0:
            print len(res)
        brute_best = list(brutem.match(path))
        lsh_result = lshm.match(path)
        if lsh_result is None: continue            
        lsh_best = list(lsh_result[0])

        res[agent_id] = {'brute'      : brute_best,
                         'lsh'        : lsh_best,
                         'brute_d'    : lsh.jaccard(set(brute_best), set(path)),
                         'lsh_d'      : lsh.jaccard(set(lsh_best), set(path)),
                         'agent_id'   : agent_id,
                         'path'       : list(set(path)),
                         'trajectory' : chosen[agent_id]})

    for aid, path in get_SSTEM_raw():
        if aid in res:
            res[aid]['sstem_path'] = list(path)
        
    json.dump(res.values(), open('compare.json', 'w'))
    
if __name__ == '__main__':
    compare()
        
        
            
        
            
        
    
    
        

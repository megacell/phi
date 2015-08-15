import config
import time
import sys
import json
import csv

from collections import defaultdict
from pdb import set_trace as T
from random import shuffle

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
            yield map(int, row['cells_ID_string'].split())

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
    
def sorted_set_inters(a, b):
    ''' Returns number of items in both a and b
    >>> sorted_set_inters([2, 4, 6], [1, 2, 3, 4, 5])
    2
    >>> sorted_set_inters([2, 4, 6], [1, 3, 5])
    0
    '''
    i, j, n = 0, 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            i += 1
        elif a[i] > b[j]:
            j += 1
        else:
            i += 1
            j += 1
            n += 1
    return n

def argmax(seq, fn):
    seq = iter(seq)
    best_s = next(seq)
    best_fs = fn(best_s)
    for s in seq:
        fs = fn(s)
        if fs > best_fs:
            best_s = s
            best_fs = fs
    return best_s, best_fs

def cells_hash_gen():
    table = range(805)
    shuffle(table)
    return table.__getitem__

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
    s = lsh.SetLSH(7, 5, hashgen=cells_hash_gen)
    n = 0
        
    for path in get_cellpaths():
        if n % 100000 == 0:
            print n
        if len(path) > 0:
            s.insert(set(path))
        n += 1
        
    n = 0
    results = []
    for path in get_SSTEM_paths():
        if n % 1000 == 0:
            print n
        n += 1
        results.append(s.query(set(path), index=True))

    json.dump(results, open('f.json', 'w'))

def brute():
    ''' Brute-force solution for testing '''
    cellpaths = [set(path) for path in get_cellpaths()]
    print 'Loaded cellpaths'
    res = []
    n = 0
    for path in get_SSTEM_paths():
        if n > 1000:
            break
        if n % 10 == 0:
            print n
        path = set(path)
        best = max(cellpaths, key=lambda x: lsh.jaccard(x, path))
        res.append(lsh.jaccard(best, path))
        n += 1
    
    print res
    json.dump(res, open('f_brute.json', 'w'))
    
if __name__ == '__main__':
    brute()
    #main()
     # n = 0
    # d = []
    # for path in get_SSTEM_paths():
    #     p = set(path)
    #     if len(p) == 0: continue
    #     def similarity_fn(cp):
    #         cp = set(cp)
    #         if len(cp) == 0:
    #             return -1000000
    #         return len(cp & p) / float(max(len(p), len(cp)))
    #     d.append(argmax(cellpaths, similarity_fn) + (path,))
    #     n += 1
    #     if n % 20 == 0:
    #         T()
        
        
            
        
            
        
    
    
        

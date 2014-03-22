import sys
import getopt
import argparse
import logging
import time

import csv
import json
import ipdb

import scipy.io as sio
from lib.console_progress import ConsoleProgress

N_TAZ = 321
N_ROUTES = 280691
N_SENSORS = 1033
ACCEPTED_LOG_LEVELS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'WARN']

def od_travel_time(data_prefix, o, d):
    path = data_prefix+"/data/%d_%d.json" % (o, d)
    od_pair = json.load(open(path))
    return route_times_for_od_pair(od_pair)

def route_times_for_od_pair(od_pair):
    return [compute_route_time(route) for route in od_pair['routes']]

def compute_route_time(route):
    travel_time = 0
    for leg in route['legs']:
        travel_time += leg['duration']['value']
    return travel_time

def main():
    parser = argparse.ArgumentParser(description='Solve Tomography problem with radiation model.')
    parser.add_argument('--verbose', dest='verbose',
                       const=True, default=False, action='store_const',
                       help='Show verbose output (default: silent)')
    parser.add_argument('--data-prefix', dest='prefix', nargs='?', const='data',
                       default='.', help='Set prefix for data files (default: .)')
    parser.add_argument('--log', dest='log', nargs='?', const='INFO',
                       default='WARN', help='Set log level (default: WARN)')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    if args.log in ACCEPTED_LOG_LEVELS:
        logging.basicConfig(level=eval('logging.'+args.log))
    if args.prefix[-1] == '/':
        data_prefix = args.prefix[:-1]
    else:
        data_prefix = args.prefix
    script_progress = ConsoleProgress(N_TAZ, args.verbose, message='Processing travel times for routes')
    with open(data_prefix+'/travel_times.csv', 'wb') as csvfile:
        ttwriter = csv.writer(csvfile, delimiter=',')
        ttwriter.writerow(['origin_index','destination_index','route_index','travel_time'])
        for o in xrange(N_TAZ):
            for d in xrange(N_TAZ):
                if o == d:
                    continue
                routes_for_od_pair = od_travel_time(data_prefix, o, d)
                for route_index, travel_time in enumerate(routes_for_od_pair):
                    ttwriter.writerow([o, d, route_index, travel_time])
            script_progress.update_progress(o+1)
    script_progress.finish()

if __name__ == "__main__":
    main()

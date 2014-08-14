import pickle
import csv
import multiprocessing

def printroutes():
    print 'loading routes'
    f = open('data.pkl')
    routes = pickle.load(f)
    with open('grouped_trajectories.csv', 'wb') as csvfile:
        header = routes[0].convert_to_dictionary().keys()
        writer = csv.DictWriter(csvfile, header)
        #pool = multiprocessing.Pool()
        print 'converting to dictionary'
        dictionaryRoutes = map(lambda x: x.convert_to_dictionary(), routes)
        print 'writing routes'
        for route in dictionaryRoutes:
            writer.writerow(route)

    print routes[:5]
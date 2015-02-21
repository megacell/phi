__author__ = 'lei'
import random
from collections import defaultdict
import scipy.sparse as sparse
import matrix_generator
from django.db import connection

class Route:
    def __init__(self, row):
        self.id = (row[0], row[1], row[2])
        self.flow = row[3]
        self.links = row[4]

def get_routes(num_routes):
    sql_query = "select orig_taz, dest_taz, od_route_index, flow_count, links from experiment2_routes where od_route_index < %(num_routes)s;"
    cursor = connection.cursor()
    cursor.execute(sql_query, {'num_routes': num_routes})
    return [Route(row) for row in cursor]

def get_links():
    sql_query = "select link_id from link_geometry;"
    cursor = connection.cursor()
    cursor.execute(sql_query)
    return [link for (link, ) in cursor]

def make_generator(num_routes, inclusion_probability):
    return LinkSequenceMatrixGenerator(get_routes(num_routes), get_links(), inclusion_probability)

class LinkSequenceMatrixGenerator(matrix_generator.MatrixGenerator):
    def __init__(self, routes, links, inclusion_probability):
        self.matrices = None
        self.routes = routes
        self.links = links
        self.inclusion_probability = inclusion_probability
    @staticmethod
    def create_sensed_links(links, inclusion_probability):
        #print inclusion_probability
        sensed_links = set(link for link in links if random.random() < inclusion_probability)
        #print len(sensed_links)
        #print sensed_links
        return sensed_links

    @staticmethod
    def list_sensed_links(route, sensed_links):
        #print len(tuple(link for link in route.links if link in sensed_links))
        return tuple(link for link in route.links if link in sensed_links)

    @staticmethod
    def route_link_table(routes, sensed_links):
        d = defaultdict(list)
        for index, r in enumerate(routes):
            d[LinkSequenceMatrixGenerator.list_sensed_links(r, sensed_links)].append(index)
        return d

    @staticmethod
    def inverse_map(routes, rlt):
        d = defaultdict(list)
        for key in rlt.keys():
            total = sum(routes[route].flow for route in rlt[key])
            for r in rlt[key]:
                d[r] = routes[r].flow/float(total)
        return d

    @staticmethod
    def create_A(rlt, num_routes):
        print len(rlt.keys()), num_routes
        A = sparse.dok_matrix((len(rlt.keys()), num_routes))
        for index, key in enumerate(sorted(rlt.keys())):
            for r in rlt[key]:
                A[index, r] = 1
        return A.tocsr()

    @staticmethod
    def create_x(inverse_rlt):
        x = []
        for i in sorted(inverse_rlt.keys()):
            x.append(inverse_rlt[i])
        return x

    @staticmethod
    def create_matrices(routes, sensed_links):
        rlt = LinkSequenceMatrixGenerator.route_link_table(routes, sensed_links)
        A = LinkSequenceMatrixGenerator.create_A(rlt, len(routes))
        x = LinkSequenceMatrixGenerator.create_x(LinkSequenceMatrixGenerator.inverse_map(routes, rlt))
        b= A*x
        return A, b, x

    def generate_matrices(self):
        A, b, x = LinkSequenceMatrixGenerator.create_matrices(self.routes,LinkSequenceMatrixGenerator.create_sensed_links(self.links, self.inclusion_probability))
        self.matrices = {'A':A, 'b':b, 'x_true':x}
        return self.matrices


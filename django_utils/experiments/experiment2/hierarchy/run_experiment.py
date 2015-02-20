import waypoint_matrix_generator as waypoints
import os
import django_utils.config as config
import generate_phi as gp
import pickle

def ensure_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)

def waypoint_matrix_file_name(routes, waypoint_density):
    path = "{0}/hierarchy/{1}/{2}".format(config.DATA_DIR, config.EXPERIMENT_MATRICES_DIR, waypoint_density)
    ensure_directory(path)
    return "{0}/experiment2_waypoints_matrices_routes_{1}.mat".format(path, routes)

def matrix_generator(phi, routes, waypoint_density):
    return waypoints.WaypointMatrixGenerator(phi, routes, waypoint_density)

def get_phi(regenerate=False):
    path = "{0}/hierarchy".format(config.DATA_DIR, config.EXPERIMENT_MATRICES_DIR)
    ensure_directory(path)
    path = "{0}/hierarchy/{1}".format(config.DATA_DIR, config.EXPERIMENT_MATRICES_DIR)
    ensure_directory(path)
    filename = "{0}/hierarchy/{1}/phi.pkl".format(config.DATA_DIR, config.EXPERIMENT_MATRICES_DIR)
    if os.path.isfile(filename) and not regenerate:
        return pickle.load(open(filename))
    else:
        phi = gp.PhiGenerator(2000).phi_generation_sql()

        pickle.dump(phi, open(filename,'w'))
        return phi

def generate_experiment_matrices():
    phi = get_phi()
    for d in config.WAYPOINT_DENSITIES:
        for r in reversed([50,40,30,20,10,3]):
            print("Generating Matrix Set (waypoints: {0}, routes: {1})".format(d,r))
            generator = matrix_generator(phi, r, d)
            generator.save_matrices(waypoint_matrix_file_name(r, d))
            print_matrix_sizes(generator.matrices)

def print_matrix_sizes(matrices):
    print ("A shape:", matrices['A'].shape)
    print ("U shape:", matrices['U'].shape)
    print ("x shape:", matrices['x'].shape)
    print ("b shape:", matrices['b'].shape)
    print (matrices['b'])


if __name__ == "__main__":
    get_phi(True)
    generate_experiment_matrices()

from orm.models import Sensor, ExperimentSensor, Experiment
import datetime
from database_setup import trajectory_loader as tl, route_loader as rl, link_loader as lgl
import od_matrix_generator as od
import waypoint_od_matrix_generator as waypoints_od
import waypoint_matrix_generator as waypoints
import waypoint_od_separated_matrix_generator as separated
import os
import django_utils.config as config
from orm import load as lw
import all_links_matrix_generator_v2 as sm
import generate_phi as gp
import pickle
import link_sequences as ls

def create_experiment2():
    experiment_name = 'e2'
    Experiment.objects.filter(description=experiment_name).delete()
    e2 = Experiment(description =experiment_name,
    name = experiment_name,
    run_time = datetime.datetime.now())
    e2.save()
    import_experiment2_sensors(experiment_name)

def import_experiment2_sensors(description):
    experiment = Experiment.objects.get(description=description)
    sensors = Sensor.objects.order_by('pems_id')
    ExperimentSensor.objects.filter(experiment=experiment).delete()
    for idx, s in enumerate(sensors):
        es = ExperimentSensor(sensor=s, value=0, experiment=experiment, vector_index=idx)
        es.save()

def setup_db():
    print("creating experiment 2")
    create_experiment2()
    print("loading links")
    lgl.load_LA_links()
    print("creating routes")
    tl.load()
    print("importing routes into the db")
    rl.load()
    print ("load waypoints")
    lw.import_waypoints()
    os.system("psql -U postgres -d geodjango -f waypoints/voronoi_python.sql")
    os.system("psql -U megacell -d geodjango -f waypoints/set_waypoint_voronoi.sql")
    print("create waypoint bins")
    os.system("psql -U megacell -d geodjango -f experiments/experiment2/database_setup/create_od_waypoint_view.sql")

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def waypoint_matrix_file_name(routes, waypoint_density):
    path = "{0}/{1}".format(config.EXPERIMENT_MATRICES_DIR, waypoint_density)
    ensure_directory(path)
    return "{0}/experiment2_waypoints_matrices_routes_{1}.mat".format(path, routes)

def matrix_generator(phi, routes, waypoint_density):
    if waypoint_density == 0:
        return od.ODMatrixGenerator(phi, routes)
    else:
        #return waypoints.WaypointMatrixGenerator(phi, routes, waypoint_density)
        return separated.WaypointMatrixGenerator(phi,routes, waypoint_density)
        #return waypoints_od.WaypointODMatrixGenerator(phi, routes, waypoint_density)

def get_phi(regenerate=False):
    directory = "{0}/{1}".format(config.DATA_DIR, config.EXPERIMENT_MATRICES_DIR)
    ensure_directory(directory)
    filename = directory + "/phi.pkl"
    if os.path.isfile(filename) and not regenerate:
        return pickle.load(open(filename))
    else:
        pickle.dump([], open(filename,'w'))

        phi = gp.PhiGenerator(2000).phi_generation_sql()

        pickle.dump(phi, open(filename,'w'))
        return phi

def generate_experiment_matrices():
    phi = get_phi()
    for d in config.WAYPOINT_DENSITIES:
        for r in [50,40,30,20,10,3]:
            print("Generating Matrix Set (waypoints: {0}, routes: {1})".format(d,r))
            print waypoint_matrix_file_name(r, d)
            generator = matrix_generator(phi, r, d)
            matrices = generator.generate_matrices()
            matrices.save_matrices(waypoint_matrix_file_name(r, d))
            print matrices
            #print_matrix_sizes(generator.matrices)

def all_link_matrix_file_name(routes, waypoint_density):
    path = "{0}/AllLink".format(config.EXPERIMENT_MATRICES_DIR)
    path2 = "{0}/{1}".format(path, waypoint_density)
    ensure_directory(path)
    ensure_directory(path2)
    return "{0}/experiment2_all_link_matrices_routes_{1}.mat".format(path2, routes)

def print_matrix_sizes(matrices):
    print ("A shape:", matrices['A'].shape)
    print ("U shape:", matrices['U'].shape)
    print ("x_true shape:", matrices['x_true'].shape)
    print ("b shape:", matrices['b'].shape)


def sample_link_matrix_file_name(routes, probability):
    path = "{0}/{1}".format(config.EXPERIMENT_MATRICES_DIR, probability)
    ensure_directory(path)
    return "{0}/sampled_links_routes_{1}.mat".format(path, routes)

def generate_sample_link_matrix():
    for r in [50,40,30,20,10,3]:
        for p in [.01,.1,.2,.3,.4,.5,.6,.7,.8, .9]:
            generator = ls.make_generator(r, p)
            generator.save_matrices(sample_link_matrix_file_name(r, p))


def generate_all_link_matrices():
    for d in config.WAYPOINT_DENSITIES:
        if d == 0: continue
        for r in [50,40,30,20,10,3]:
            print("Generating All Link Matrix Set (waypoints: {0}, routes: {1})".format(d,r))
            generator = sm.AllLinksMatrixGenerator(r, d)
            generator.save_matrices(all_link_matrix_file_name(r, d))
            print_matrix_sizes(generator.matrices)


if __name__ == "__main__":
    #setup_db()
    get_phi(True)
    #generate_sample_link_matrix()
    generate_experiment_matrices()
    #generate_all_link_matrices()

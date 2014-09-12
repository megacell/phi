from django_utils.orm.models import Sensor, ExperimentSensor, Experiment
import datetime
from database_setup import trajectory_loader as tl, route_loader as rl
import experiment2_control as e2_control
import experiment2_waypoints as e2_waypoints
import os
import django_utils.config as config
from django_utils.orm import load as lw
import generate_super_matrix as sm
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
    sensors = Sensor.objects.filter(road_type='Freeway').order_by('pems_id')
    ExperimentSensor.objects.filter(experiment=experiment).delete()
    for idx, s in enumerate(sensors):
        es = ExperimentSensor(sensor=s, value=0, experiment=experiment, vector_index=idx)
        es.save()

def setup_db():
    print("creating experiment2")
    create_experiment2()
    print("creating routes")
    tl.load()
    print("importing routes into the db")
    rl.load()
    print ("load waypoints")
    lw.import_waypoints()
    os.system("psql -U megacell -d geodjango -f /home/lei/traffic/phi-estimation/django_utils/waypoints/set_waypoint_voronoi.sql")
    print("create waypoint bins")
    os.system("psql -U megacell -d geodjango -f /home/lei/traffic/phi-estimation/django_utils/experiments/experiment2/database_setup/create_od_waypoint_view.sql")

def generate_experiment_matrices():
    global i, d
    config.EXPERIMENT_MATRICES_DIR = 'experiment_matrices/0'
    config.NUM_ROUTES_PER_OD = 2000
    e2_control.generate_matrices(True)
    for i in [50, 40, 30, 20, 10, 3]:
        config.NUM_ROUTES_PER_OD = i
        e2_control.generate_matrices(False)
    for d in config.WAYPOINT_DENSITIES:
        print ("waypoint density:", d)
        config.WAYPOINT_DENSITY = d
        config.EXPERIMENT_MATRICES_DIR = 'experiment_matrices/{0}'.format(d)
        for i in [50, 40, 30, 20, 10, 3]:
            config.NUM_ROUTES_PER_OD = i
            e2_waypoints.generate_matrices(False)

def generate_total_link_matrices():
    for d in config.WAYPOINT_DENSITIES:
        for r in [2000,50,40,30,20,10,3]:
            matrix_dir = '{0}/{1}/{2}'.format(config.DATA_DIR , config.EXPERIMENT_MATRICES_DIR + '/AllLinks', d)
            gsm = sm.GenerateSuperMatrix(r,d, matrix_dir)
            gsm.generate_matrices()

if __name__ == "__main__":
    #setup_db()
    #generate_experiment_matrices()
    generate_total_link_matrices()
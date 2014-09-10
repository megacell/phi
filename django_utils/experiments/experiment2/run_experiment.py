from orm.models import Sensor, ExperimentSensor, Experiment
import datetime
from database_setup import trajectory_loader as tl, route_loader as rl, link_geometry_loader as lgl
import experiment2_control as e2_control
import experiment2_waypoints as e2_waypoints
import os
import django_utils.config as config
from orm import load as lw

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
    os.system("psql -U megacell -d geodjango -f /home/lei/traffic/phi-estimation/django_utils/waypoints/set_waypoint_voronoi.sql")
    print("create waypoint bins")
    os.system("psql -U megacell -d geodjango -f /home/lei/traffic/phi-estimation/django_utils/experiments/experiment2/database_setup/create_od_waypoint_view.sql")

if __name__ == "__main__":
    #setup_db()
    config.NUM_ROUTES_PER_OD = 2000
    config.EXPERIMENT_MATRICES_DIR ='experiment_matrices'
    e2_control.generate_matrices(False)
    for d in [3800,2850,1900,1425,950,713,475,238]:
        print ("waypoint density:", d)
        config.WAYPOINT_DENSITY = d
        config.EXPERIMENT_MATRICES_DIR ='experiment_matrices/{0}'.format(d)
        for i in [50, 40, 30, 20, 10, 3]:
            config.NUM_ROUTES_PER_OD = i
            e2_waypoints.generate_matrices(False)

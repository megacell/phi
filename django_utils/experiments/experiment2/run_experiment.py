from django_utils.orm.models import Sensor, ExperimentSensor, Experiment
import datetime
from trajectory_processing import loadsyntheticroutes as synroutes, routes_loader as rl
import experiment2_control as e2_control
import experiment2_waypoints as e2_waypoints
import os

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

def load_trajectories():
    print("creating routes")
    synroutes.load()
    print("importing routes into the db")
    rl.import_to_db()
    print("create waypoint bins")
    os.system("psql -U megacell -d geodjango -f /home/lei/traffic/phi-estimation/django_utils/experiments/experiment2/database_setup/create_od_waypoint_view.sql")

if __name__ == "__main__":
    #create_experiment2()
    #load_trajectories()
    e2_control.generate_matrices(False)
    #e2_waypoints.generate_matrices(False)
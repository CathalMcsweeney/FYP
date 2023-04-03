import importlib
import os
import sys
import argparse

import xml.etree.ElementTree as ET
if 'SUMO_HOME' not in os.environ:
    # adapt your "SUMO_HOME" here
    os.environ["SUMO_HOME"] = "/usr/share/sumo"
if 'SUMO_HOME' in os.environ:
    os.environ["SUMO_HOME"] = "/usr/share/sumo"
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")

sys.path.append("../PonyGE2-master/src")
sys.path.append("../src")
import sumolib
import traci
import edgeCost
#import importlib
import numbers
import psutil
import time
# import timeout_decorator

import sys
import threading
from time import sleep
import math
from utils import *
try:
    import thread
except ImportError:
    import _thread as thread



def get_edge_speeds(edge):
    veh_list = traci.edge.getLastStepVehicleIDs(edge.getID())
    edge_max_speed = edge.getSpeed()
    veh_count = len(veh_list)
    if veh_count <= 0:
        maxSpeed = edge_max_speed
        avgSpeed = edge_max_speed
    else:
        veh_speed = []
        for veh in veh_list:
            veh_speed.append(traci.vehicle.getSpeed(veh))
        maxSpeed = max(veh_speed)
        avgSpeed = sum(veh_speed) / len(veh_speed)
    return maxSpeed, avgSpeed


def get_next_edge_occ(edge):
    next_edges = edge.getOutgoing()
    noNextEdgeChoices = len(next_edges)
    next_occ = []
    for e in next_edges:
        next_occ.append(traci.edge.getLastStepOccupancy(e.getID()))
    if noNextEdgeChoices == 0:
        min_occ, avg_occ, max_occ = 0.0, 0.0, 0.0
    elif noNextEdgeChoices == 1:
        min_occ, avg_occ, max_occ = next_occ[0], next_occ[0], next_occ[0]
    else:
        min_occ, avg_occ, max_occ = min(next_occ), sum(next_occ) / len(next_occ), max(next_occ)
    return noNextEdgeChoices, min_occ, avg_occ, max_occ


def set_edge_cost(edges,functionString):
    # import the module here, so that it can be reloaded.
    #importlib.reload(edgeCost)
    # from edgeCost import evalEdgeCost  # or whatever name you want.
    for e in edges:
        junction = e.getToNode()
        edge_id = e.getID()
        if "stop" in junction._type:
            print("found stop")
        length = e.getLength()
        avgTravelTime = traci.edge.getTraveltime(edge_id)
        edgeOccupancy = traci.edge.getLastStepOccupancy(edge_id)
        maxSpeed, avgSpeed = get_edge_speeds(e)
        noNextEdgeChoices, minSubsequentOccupancy, avgSubsequentOccupancy, maxSubsequentOccupancy = get_next_edge_occ(e)
        
        try:
            #edge_cost = float(edgeCost.evalEdgeCost(junction, avgSpeed, maxSpeed, edgeOccupancy, minSubsequentOccupancy, avgSubsequentOccupancy, maxSubsequentOccupancy, length, avgTravelTime, noNextEdgeChoices))
            edge_cost = float(eval(functionString))
            #print("original Version = ",edge_cost)
        except Exception as ex:
            print("Exception from run: ", ex)
            edge_cost = 0.0
            print("Error Calculating Cost. Cost set to 0")
        if (not(isinstance(edge_cost, numbers.Integral) or isinstance(edge_cost, float))):
            print("Evaluation of cost function does not return a number")
            sys.exit(1)
        traci.edge.setEffort(edge_id, edge_cost)

def junctionWht(junction,one,two):
    junctionWeight = edgeCost.functionJunctionType(junction,one,two)
    return junctionWeight

def reroute(veh_list):
    # vehicleRoutes = set()
    for v in veh_list:
        traci.vehicle.rerouteEffort(v)

def get_results(output_path):
    root = ET.parse(output_path).getroot()
    co2, fuel, duration = [], [], []
    for child in root.iter():
        if child.tag == "emissions":
            co2.append(float(child.attrib["CO2_abs"]))
            fuel.append(float(child.attrib["fuel_abs"]))
        if child.tag == "tripinfo":
            duration.append(float(child.attrib["duration"]))
    # print("The average CO2 emission per trip is: %.2f kg." % (pow(10, -6)*sum(co2)/len(co2)))
    # print("The average fuel consumption per trip is: %.2f ml." % (sum(fuel)/len(fuel)))
    # print("The average travel time per trip is: %.2f seconds." % (sum(duration)/len(duration)))
    return sum(duration)/len(duration) # returns the average duration of a simulation

def run(functionString,scenario):
    import time
    step = 0
    net = sumolib.net.readNet("../../inputs/maps/"+scenario+".net.xml")
    edges = net.getEdges()
    
    start_time = time.time()
    threshold = 10 * 60  # 10minutes
    delta_t = 0.0
    veh_num = 0
    #print("start simulation")
    while traci.simulation.getMinExpectedNumber() > 0 and step <= 250 and veh_num < 5000 and delta_t < threshold:
        print("Edge statistic at time step %d, Delta Time: %d, vehicle count: %d" % (step, delta_t, veh_num))
        #print("Sim")
        try:
            traciSimStep(traci, step)
        except:
            for proc in psutil.process_iter():
                if "sumo" in proc.name():
                    print("Killing proc: ",proc.name())
                    proc.kill()
            print("Exception traciSimStep")
            raise Exception
        print("set edge cost")
        set_edge_cost(edges,functionString)
        #print("reroute")
        reroute(traci.vehicle.getIDList())
        #print("====")
        veh_num = traci.simulation.getMinExpectedNumber()
        delta_t = time.time() - start_time
        step += 60
        print("step:",step)
    if traci.simulation.getMinExpectedNumber() >= 0 and step > 2000 and veh_num > 5000 and delta_t >= threshold:
        print("traci.simulation.getMinExpectedNumber()",traci.simulation.getMinExpectedNumber())
        print("step",step)
        print("veh_num", veh_num)
        print("delta_t", delta_t)
        raise Exception

import multiprocessing.pool
import functools

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator

def runSimulation(functionString, individualnumber, scenario):
    try:
        # print("startTraci")
        if scenario=="small_dublin":
            traci.start([sumolib.checkBinary('sumo'), "-W",
                         "-c","../../inputs/small_dublin.sumocfg",
                         "-n","../../inputs/maps/"+scenario+".net.xml",
                         "-r","../../inputs/routes/"+scenario+".rou.xml",
                         "--tripinfo-output","../../outputs/trips/"+scenario+"_trip_"+str(individualnumber)+".xml",
                         "--vehroute-output","../../outputs/vehroute/"+scenario+"_vr_"+str(individualnumber)+".xml",
                         "--no-step-log","true",
                         "--threads","12",
                         #"--iterate", "true"
                         ], label=functionString)
            print("run")
            run(functionString,scenario)
            traci.close()
        elif scenario=="randomGrid":
            traci.start([sumolib.checkBinary('sumo'), "-W",
                         #"-c", "../../inputs/random_norr.sumocfg",
                         "-n", "../../inputs/maps/" + scenario + ".net.xml",
                         "-r", "../../inputs/routes/buses.flows.xml,../../inputs/routes/commercial.rou.xml,../../inputs/routes/passenger.rou.xml,../../inputs/routes/ptw.rou.xml",
                         "-a", "../../inputs/maps/busStops.add.xml,../../inputs/maps/parkingArea.add.xml,../../inputs/maps/basic.vType.xml",
                         "--ignore-route-errors", "true",
                         "--lateral-resolution", "0.3",
                         "--ignore-junction-blocker", "60",
                         "--collision.action", "none",
                         "--time-to-teleport", "60",
                         "--max-depart-delay", "900",
                         "--time-to-impatience", "30",
                         "--pedestrian.model", "striping",
                         "--pedestrian.striping.stripe-width", "0.55",
                         "--pedestrian.striping.jamtime", "30",
                         "--default.emergencydecel", "decel",
                         "--tripinfo-output", "../../outputs/trips/" + scenario + "_trip_" + str(individualnumber) + ".xml",
                         "--summary-output", "../../outputs/trips/" + scenario + "summary" + str(individualnumber) + ".xml",
                         "--vehroute-output", "../../outputs/vehroute/" + scenario + "_vr_" + str(individualnumber) + ".xml",
                         "--no-step-log", "true"
                         ], label=functionString)
            #'''
            # blabla                        
            #'''
            # print("run")
            run(functionString,scenario)
            traci.close()
        else:
            print("ERROR: Unkown scenario")
    except Exception as ex:
        print("Exception from run: ", ex)
        #raise Exception
        return math.inf
    output_path = "../../outputs/trips/"+scenario+"_trip_"+str(individualnumber)+".xml"
    cost = get_results(output_path) #cost is based on the duration average of this simulation
    print("Cost = ",cost)
    return cost

@timeout(10.0)
def traciSimStep(traci, step):
    traci.simulationStep(step)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SUMO Simulation')
    parser.add_argument('--functionString')
    parser.add_argument('--individualnumber')
    parser.add_argument('--scenario')
    parser.add_argument('--iterate')
    args =parser.parse_args()
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = open('trash', 'w')
    sys.stderr = open('trash_err', 'w')
    #print(args.functionString, args.individualnumber, args.scenario)
    cost = runSimulation(args.functionString, args.individualnumber, args.scenario)
    sys.stdout = save_stdout
    sys.stderr = save_stderr
    print("Cost = ",cost)
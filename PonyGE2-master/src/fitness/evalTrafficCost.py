import time
import traceback

import numpy as np
np.seterr(all="raise")

from algorithm.parameters import params
from utilities.fitness.math_functions import *
from utilities.fitness.optimize_constants import optimize_constants

from fitness.base_ff_classes.base_ff import base_ff

import sys, os, subprocess
sys.path.append(os.path.abspath('../../scripts'))
#print(sys.path)
from simulation import *
import math
import re

class evalTrafficCost(base_ff):


    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()


    def evaluate(self, ind, **kwargs):
        tb_str = traceback.format_stack()
        phen = ind.phenotype
        fitness = 0
        # #create function in python to be used by TraCI
        # list_of_parameters = "avgSpeed, maxSpeed, edgeOccupancy, minSubsequentOccupancy, avgSubsequentOccupancy, maxSubsequentOccupancy, length, avgTravelTime, noNextEdgeChoices"

        # f.write("from utils import *\n"
        #         "def evalEdgeCost("+list_of_parameters+"):\n")
        # #f.write("\t return max(0,"+phen+")\n")
        # f.write("\t return max(0,avgTravelTime)\n")
        # f.close()

        #scenario = "test_8x8_400"
        #scenario = "rand_2000"
        scenario = "small_dublin"
        #scenario = "randomGrid"
        #phen="edgeOccupancy"

        functionString="max(0.0000000001,"+phen+")"
        pairPhenoNumber=None
        if 'MAPPING_PHENO_NUMBER' in params:
            params['MAPPING_PHENO_NUMBER']
        else:
            params['MAPPING_PHENO_NUMBER'] = []
        pairPhenoNumber = [functionString, len(params['MAPPING_PHENO_NUMBER'])]
        params['MAPPING_PHENO_NUMBER'].append(pairPhenoNumber)

        print("\n/////////////////////\nStart with : ",phen)
        # print("/////////////////////")
        import sys
        # save_stdout = sys.stdout
        # save_stderr = sys.stderr
        # sys.stdout = open('trash', 'w')
        # sys.stderr = open('trash_err', 'w')

        cost = float("inf")
        emissions=float("inf")
        try:          
            #p = subprocess.Popen("python3 ../../scripts/simulation.py --functionString \'"+functionString+"\' --individualnumber "+str(pairPhenoNumber[1])+" --scenario "+scenario, stdout=subprocess.PIPE, shell=True)
                        
            p = subprocess.Popen("python3 ../../scripts/simulation.py --functionString \'"+functionString+"\' --individualnumber "+str(pairPhenoNumber[1])+" --scenario "+scenario+" --iterate \'true\'", stdout=subprocess.PIPE, shell=True)
            #p = subprocess.Popen("python3 ../../scripts/simulation.py --functionString \'"+functionString+"\' --individualnumber "+str(pairPhenoNumber[1])+" --scenario "+scenario+" --iterate \'true\'")
            print("python3 ../../scripts/simulation.py --functionString \'"+functionString+"\' \n--individualnumber "+str(pairPhenoNumber[1])+"\n--scenario "+scenario+" --iterate \'true\'")
            (output,err) = p.communicate()
            p.wait()
            #print("output",output, "err",err)
            decoded=output.decode('utf-8')
            if 'inf' in decoded:
                cost=math.inf
            else:
                cost= float(re.findall(r'\d+\.\d+',decoded)[0])
        except Exception as ex:
            print("Exception from run Simulation: ", ex)
            print("Sumo internal error")
            # time.sleep(5)
            cost = math.inf
        # sys.exit(1)
        # sys.stdout = save_stdout
        # sys.stderr = save_stderr
        # need to run sumo
        print("/////////////////////\nEND\nFor: ",phen,"\nCost: ", cost,"\n/////////////////////")

        f = open("../../outputs/trips/" + scenario + "_mapping.txt", "a")
        f.write(pairPhenoNumber[0]+"\t"+str(pairPhenoNumber[1])+"\t"+str(cost)+"\n")
        f.close()

        #fitness = [cost, emissions]
        fitness = cost
        return fitness

    @staticmethod
    def value(fitness_vector, objective_index):
        """
        This is a static method required by NSGA-II for sorting populations
        based on a given fitness function, or for returning a given index of a
        population based on a given fitness function.

        :param fitness_vector: A vector/list of fitnesses.
        :param objective_index: The index of the desired fitness.
        :return: The fitness at the objective index of the fitness vecror.
        """

        if not isinstance(fitness_vector, list):
            return float("inf")

        return fitness_vector[objective_index]

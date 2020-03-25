from Pyrolysis import PYRO
from pso_ga import pso_ga
from aspenplus.aspen_link import init_aspen
from hclscrubber import HCL
from dechlorination import DECH
from combustion import COMB
from others import create_excel_file, print_df_to_excel
import openpyxl
import pickle
import pandas as pd
import numpy as np

def optimisepyrolysis(pso_gen, ga):
    aspen = init_aspen()
    pyrolysis = PYRO(aspen)
    b_temp = [350, 520]
    b_residencetime = [2, 4]
    p_store = [b_temp, b_residencetime]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['reactortemp','residencetime']

    def func(individual):
        nonlocal pyrolysis
        inlettemp, residencetime = individual
        pyrolysis.solve_pyro(reactortemp=inlettemp, residencetime=residencetime, )
        return (pyrolysis.pyro_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best

def optimisehclscrubber(pso_gen, ga):
    aspen = init_aspen()
    hclscrubber = HCL(aspen)
    inlettemp = [25, 80]
    NAOHwaterflow = [1, 10]
    NAOHionsflow = [1, 10]
    N2flow = [1, 10]
    p_store = [inlettemp, NAOHwaterflow, NAOHionsflow, N2flow]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['inlettemp','NAOHwaterflow','NAOHionsflow','N2flow']

    def func(individual):
        nonlocal hclscrubber
        inlettemp, NAOHwaterflow, NAOHionsflow, N2flow = individual
        hclscrubber.solve_hcl(inlettemp=inlettemp, NAOHwaterflow=NAOHwaterflow, NAOHionsflow=NAOHionsflow, N2flow=N2flow)
        return (hclscrubber.hcl_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best

def optimisedechlorination(pso_gen, ga):
    aspen = init_aspen()
    dech = DECH(aspen)
    inlettemp = [250, 350]
    p_store = [inlettemp]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['inlettemp']

    def func(individual):
        nonlocal dech
        inlettemp = individual
        dech.solve_dech(inlettemp=inlettemp)
        return (dech.dech_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best


def optimisecombustion(pso_gen, ga):
    aspen = init_aspen()
    comb = COMB(aspen)
    pressure = [10, 30]
    ER = [0.6, 0.8]
    efficiency = [96, 99.99999999999999]

    p_store = [pressure, ER, efficiency]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['pressure', 'ER', 'combustion efficiency']

    def func(individual):
        nonlocal comb
        pressure , ER, efficiency  = individual
        comb.combustionsolve(OP=pressure, OER=ER, eff=efficiency)
        return (comb.comb_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best


#optimisepyrolysis(pso_gen=50, ga=True)
#optimisehclscrubber(pso_gen=1, ga=True)
#optimisedechlorination(pso_gen=1, ga=True)

optimisecombustion(pso_gen=5, ga=True)
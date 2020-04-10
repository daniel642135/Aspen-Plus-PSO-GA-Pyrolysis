from Pyrolysis import PYRO
from pso_ga import pso_ga
from aspenplus.aspen_link import init_aspen
from hclscrubber import HCL
from dechlorination import DECH
from combustion import COMB
from separation import SEPARATE
from others import create_excel_file, print_df_to_excel
import openpyxl
import pickle
import pandas as pd
import numpy as np

def optimisepyrolysis(pso_gen, ga):
    aspen = init_aspen()
    pyrolysis = PYRO(aspen)
    b_temp = [350, 520]
    b_residencetime = [2, 4.8]
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
    inlettemp = [20, 40]
    NAOHwaterflow = [16, 160]
    p_store = [inlettemp, NAOHwaterflow]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['inlettemp','NAOHwaterflow']

    def func(individual):
        nonlocal hclscrubber
        inlettemp, NAOHwaterflow = individual
        hclscrubber.solve_hcl(inlettemp=inlettemp, NAOHwaterflow=NAOHwaterflow)
        return (hclscrubber.hcl_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best

def optimisedechlorination(pso_gen, ga):
    aspen = init_aspen()
    dech = DECH(aspen)
    inlettemp = [310, 340]
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
        dech.solve_dech(reactortemp=inlettemp)
        return (dech.dech_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best


def optimisecombustion(pso_gen, ga):
    aspen = init_aspen()
    comb = COMB(aspen)
    pressure = [11, 13]
    ER = [0.7, 0.8]
    efficiency = [99, 99.99999999999999]

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


def optimiseseparation(pso_gen, ga):
    aspen = init_aspen()
    sep = SEPARATE(aspen)
    lightcom = [0.998, 0.9999]
    refluxmulti = [15, 3]

    p_store = [lightcom, refluxmulti]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['lightcom', 'refluxmulti']

    def func(individual):
        nonlocal sep
        lightcom, refluxmulti = individual
        sep.sep_solve(lightcom=lightcom, refluxmulti=refluxmulti, )
        return (sep.sep_result(),)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best

#optimisepyrolysis(pso_gen=2, ga=True)
#optimisehclscrubber(pso_gen=2, ga=True)
#optimisedechlorination(pso_gen=1, ga=True) #cannot solve for 1 DV, it will become a particle
#optimisecombustion(pso_gen=2, ga=True)
#optimiseseparation(pso_gen=2, ga=True)

def optimiseall(pso_gen, ga):
    aspen = init_aspen()
    dech = DECH(aspen)
    hclscrubber = HCL(aspen)
    pyrolysis = PYRO(aspen)
    sep = SEPARATE(aspen)
    comb = COMB(aspen)

    #DV range
    #Dechlorination
    inlettempdech = [310, 340]

    #Scrubber
    inlettemp = [20, 40]
    NAOHwaterflow = [16, 160]

    #Pryolysis
    b_temp = [350, 520]
    b_residencetime = [2, 4.8]

    #Distillation
    feedtemp = [100, 200]
    refluxmulti = [1.6, 3]

    #Combustion
    pressure = [11, 13]
    ER = [0.7, 0.8]
    efficiency = [99, 99.99999999999999]

    p_store = [inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure, ER, efficiency]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['inlettempdech', 'inlettemp', 'NAOHwaterflow', 'b_temp', 'b_residencetime', 'feedtemp', 'refluxmulti', 'pressure', 'ER', 'efficiency']

    def func(individual):
        nonlocal dech
        nonlocal hclscrubber
        nonlocal pyrolysis
        nonlocal sep
        nonlocal comb

        inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure, ER, efficiency = individual

        dech.solve_dech(reactortemp=inlettempdech, )
        HCLppm = hclscrubber.solve_hcl(inlettemp=inlettemp, NAOHwaterflow=NAOHwaterflow, )
        pyrolysis.solve_pyro(reactortemp=b_temp, residencetime=b_residencetime, )
        ID, L, dieselflow, gasolineflow, Csb = sep.sep_solve(feedtemp=feedtemp, refluxmulti=refluxmulti, )
        Cbm5, utility5, D_int, NOx_ppm, CO_ppm, turbine_power = comb.combustionsolve(OP=pressure, OER=ER, eff=efficiency, )

        Cbm1, utility1 = dech.dech_totalannualcost()
        Cbm2, utility2, rawmaterial1 = hclscrubber.hcl_totalannualcost()
        Cbm3, utility3, rawmaterial2 = pyrolysis.pyro_totalannualcost()
        Cbm4, utility4, W = sep.totalcost()


        TCbm = Cbm1 + Cbm2 + Cbm3 + Cbm4 + Cbm5 + 3000000 #add $3m from capital cost of HX
        Tutility = utility1 + utility2 + utility3 + utility4 + utility5
        Trawmaterial = rawmaterial1 + rawmaterial2

        TCI = 5.03 * TCbm
        annualisedcapcost = TCI * ((0.05)*(1.05)**7 / ((1.05)**7 - 1)) # 5% interest rate for 7 years

        revenue = (dieselflow*0.75 + gasolineflow*0.98)*60*24*330 + (turbine_power * 0.070 * 603.1/381.1 * 24 * 330)
        annualisedprofit = revenue - annualisedcapcost - Tutility - Trawmaterial

        objective = annualisedprofit

        #constraints
        if HCLppm > 85:
            objective = 1e20
        if L/ID > 20:
            objective = 1e20
        if D_int <= 0:
            objective = 1e20
        if CO_ppm > 0.00011:
            objective = 1e20
        if NOx_ppm > 200:
            objective = 1e20
        if W < 4200:
            objective = 1e20
        if Csb == 0.4:
            objective = 1e20

        return (objective,)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best

optimiseall(pso_gen=1, ga=True)
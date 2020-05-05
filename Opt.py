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

#Optimisation of entire plant
def optimiseall(pso_gen, ga):
    data_store = []
    aspen = init_aspen()
    dech = DECH(aspen)
    print("Connected")
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
    pressure = [15, 19]
    ER = [0.7, 0.8]
    efficiency = [99.3, 99.8]

    p_store = [inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure, ER,
               efficiency]

    params = {'c1': 1.5, 'c2': 1.5, 'wmin': 0.4, 'wmax': 0.9,
              'ga_iter_min': 5, 'ga_iter_max': 20, 'iter_gamma': 10,
              'ga_num_min': 10, 'ga_num_max': 20, 'num_beta': 15,
              'tourn_size': 3, 'cxpd': 0.5, 'mutpd': 0.05, 'indpd': 0.5, 'eta': 0.5,
              'pso_iter': pso_gen, 'swarm_size': 50}

    pmin = [x[0] for x in p_store]
    pmax = [x[1] for x in p_store]

    smin = [abs(x - y) * 0.01 for x, y in zip(pmin, pmax)]
    smax = [abs(x - y) * 0.5 for x, y in zip(pmin, pmax)]

    dv = ['inlettempdech', 'inlettemp', 'NAOHwaterflow', 'b_temp', 'b_residencetime', 'feedtemp', 'refluxmulti',
          'pressure', 'ER', 'efficiency']

    def func(individual):
        nonlocal dech
        nonlocal hclscrubber
        nonlocal pyrolysis
        nonlocal sep
        nonlocal comb


        data_store_column = ['inlettempdech', 'inlettemp', 'NAOHwaterflow', 'b_temp', 'b_residencetime', 'feedtemp',
                             'refluxmulti', 'pressure', 'ER', 'efficiency', 'dechcap', 'hclcap', 'pyrocap', 'sepcap',
                             'combcap', 'dechU', 'hclU', 'pyroU', 'sepU', 'combU', 'rawmaterial1', 'rawmaterial2',
                             'revenue', 'annualisedcapcost', 'Tutility', 'dieselflow', 'gasolineflow', 'turbine_power',
                             'annualisedprofit', 'nonconverge', 'HCLppm', 'L', 'ID' , 'L/ID',
                             'D_int', 'CO_ppm', 'NOx_ppm', 'W', 'Csb', 'objective']

        def save_data_store(data):
            with open('data_store.pkl','wb') as handle:
                pickle.dump([data_store_column, data], handle, protocol=pickle.HIGHEST_PROTOCOL)

        inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure, ER,\
        efficiency = individual

        aspen.Engine.Reinit(4)
        # 4 = IAP_REINIT_SIMULATION
        aspen.Engine.Run()

        dech.solve_dech(reactortemp=inlettempdech, )
        HCLppm = hclscrubber.solve_hcl(inlettemp=inlettemp, NAOHwaterflow=NAOHwaterflow, )
        pyrolysis.solve_pyro(reactortemp=b_temp, residencetime=b_residencetime, )
        L, ID, dieselflow, gasolineflow, Csb, nonconverge = sep.sep_solve(feedtemp=feedtemp, refluxmulti=refluxmulti, )

        if nonconverge == True:
            objective = -1e5
            annualisedprofit = -1
            Cbm1 = -1
            Cbm2 = -1
            Cbm3 = -1
            Cbm4 = -1
            Cbm5 = -1
            utility1 = -1
            utility2 = -1
            utility3 = -1
            utility4 = -1
            utility5 = -1
            rawmaterial1 = -1
            rawmaterial2 = -1
            revenue = -1
            annualisedcapcost = -1
            Tutility = -1
            D_int = -1
            CO_ppm = -1
            NOx_ppm = -1
            W = -1
            turbine_power = -1
        else:
            Cbm5, utility5, D_int, NOx_ppm, CO_ppm, turbine_power = comb.combustionsolve(OP=pressure, OER=ER,
                                                                                         eff=efficiency, )

            Cbm1, utility1 = dech.dech_totalannualcost()
            Cbm2, utility2, rawmaterial1 = hclscrubber.hcl_totalannualcost()
            Cbm3, utility3, rawmaterial2 = pyrolysis.pyro_totalannualcost()
            Cbm4, utility4, W, nonconverge = sep.totalcost()


            TCbm = Cbm1 + Cbm2 + Cbm3 + Cbm4 + Cbm5 + 3000000 #add $3m from capital cost of HX
            Tutility = utility1 + utility2 + utility3 + utility4 + utility5
            Trawmaterial = rawmaterial1 + rawmaterial2

            TCI = 5.03 * TCbm
            annualisedcapcost = TCI * ((0.05)*(1.05)**7 / ((1.05)**7 - 1)) # 5% interest rate for 7 years

            revenue = (dieselflow*0.75 + gasolineflow*0.98)*60*24*340 + (abs(turbine_power)
                                                                         * 0.070 * 603.1/381.1 * 24 * 340)
            annualisedprofit = revenue - annualisedcapcost - Tutility - Trawmaterial


            if annualisedprofit < 0:
                objective = -1e5
            else:
                objective = -annualisedprofit #we are minimising it

            #constraints
            if nonconverge == True:
                objective = -1e5
            if HCLppm > 85:
                objective = -1e5
            if L/ID > 20:
                objective = -1e5
            if D_int <= 0:
                objective = -1e5
            if CO_ppm > 0.00011:
                objective = -1e5
            if NOx_ppm > 200:
                objective = -1e5
            if W < 4200:
                objective = -1e5
            if Csb == -1:
                objective = -1e5

        data = [inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure, ER,
                efficiency, Cbm1, Cbm2, Cbm3, Cbm4, Cbm5, utility1, utility2, utility3, utility4, utility5,
                rawmaterial1, rawmaterial2, revenue, annualisedcapcost, Tutility, dieselflow, gasolineflow,
                turbine_power, annualisedprofit, nonconverge, HCLppm, L, ID, L/ID, D_int, CO_ppm, NOx_ppm, W,
                Csb, objective]

        data_store.append(data)
        save_data_store(data_store)

        return (objective,)

    pop, logbook, best = pso_ga(func=func, pmin=pmin, pmax=pmax,
                                smin=smin, smax=smax,
                                int_idx=None, params=params, ga=ga, dv=dv)
    return best



def readfile(name):
    with open('./data_store.pkl', 'rb') as handle:
        data_store = pickle.load(handle)

    write_excel = create_excel_file('./results/{}_results.xlsx'.format(name))
    wb = openpyxl.load_workbook(write_excel)
    ws = wb[wb.sheetnames[-1]]
    print_df_to_excel(df=pd.DataFrame(data=data_store[1], columns=data_store[0]), ws=ws)
    wb.save(write_excel)


optimiseall(pso_gen=50, ga=True)
readfile(name='fullevalresult')
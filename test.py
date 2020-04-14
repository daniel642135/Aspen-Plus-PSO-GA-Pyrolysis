from aspenplus.aspen_link import init_aspen
from hclscrubber import HCL
from dechlorination import DECH
from combustion import COMB
from separation import SEPARATE
from Pyrolysis import PYRO
from iapws import IAPWS95
from others import create_excel_file, print_df_to_excel
import openpyxl
import pickle
import pandas as pd

def test1():
    aspen = init_aspen()
    hclscrubber = HCL(aspen)
    hclscrubber.solve_hcl(inlettemp=30, NAOHwaterflow=20)
    hclscrubber.hcl_result()

#test1()

def test5():
    aspen = init_aspen()
    dec = DECH(aspen)
    dec.solve_dech(reactortemp=340)
    dec.dech_totalannualcost()

#test5()


def test2():
    aspen = init_aspen()
    pyrolysis = PYRO(aspen)
    pyrolysis.solve_pyro(residencetime=4.8, reactortemp=520)
    pyrolysis.pyro_totalannualcost()
#test2()


def test3():
    aspen = init_aspen()
    sep = SEPARATE(aspen)
    sep.sep_solve(113, 2)
    sep.totalcost()

#test3()

def test123():
    aspen = init_aspen()
    density = aspen.Tree.FindNode('\Data\Blocks\B7\Output\RHO_GAS\\' + str(10)).Value
    print(density)

#test123()

def water():
    sat_steam = IAPWS95(T=125 + 273.15, x=1)
    sat_liquid = IAPWS95(T=125 + 273.15, x=0)
    latentheat = sat_steam.h - sat_liquid.h
    print(latentheat)

#water()

def checkresult(inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure,
                   ER, efficiency):
    data_store = []
    aspen = init_aspen()
    dech = DECH(aspen)
    hclscrubber = HCL(aspen)
    pyrolysis = PYRO(aspen)
    sep = SEPARATE(aspen)
    comb = COMB(aspen)

    data_store_column = ['inlettempdech', 'inlettemp', 'NAOHwaterflow', 'b_temp', 'b_residencetime', 'feedtemp',
                         'refluxmulti', 'pressure', 'ER', 'efficiency', 'dechcap', 'hclcap', 'pyrocap', 'sepcap',
                         'combcap', 'dechU', 'hclU', 'pyroU', 'sepU', 'combU', 'rawmaterial1', 'rawmaterial2',
                         'revenue', 'annualisedcapcost', 'Tutility', 'dieselflow', 'gasolineflow', 'turbine_power',
                         'annualisedprofit', 'nonconverge', 'HCLppm', 'L', 'ID', 'L/ID',
                         'D_int', 'CO_ppm', 'NOx_ppm', 'W', 'Csb', 'objective']

    def save_data_store(data):
        with open('data_store.pkl', 'wb') as handle:
            pickle.dump([data_store_column, data], handle, protocol=pickle.HIGHEST_PROTOCOL)


    dech.solve_dech(reactortemp=inlettempdech, )
    HCLppm = hclscrubber.solve_hcl(inlettemp=inlettemp, NAOHwaterflow=NAOHwaterflow, )
    pyrolysis.solve_pyro(reactortemp=b_temp, residencetime=b_residencetime, )
    ID, L, dieselflow, gasolineflow, Csb, nonconverge = sep.sep_solve(feedtemp=feedtemp, refluxmulti=refluxmulti, )

    if nonconverge == True:
        objective = 1e10
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

        TCbm = Cbm1 + Cbm2 + Cbm3 + Cbm4 + Cbm5 + 3000000  # add $3m from capital cost of HX
        Tutility = utility1 + utility2 + utility3 + utility4 + utility5
        Trawmaterial = rawmaterial1 + rawmaterial2

        TCI = 5.03 * TCbm
        annualisedcapcost = TCI * ((0.05) * (1.05) ** 7 / ((1.05) ** 7 - 1))  # 5% interest rate for 7 years

        revenue = (dieselflow * 0.75 + gasolineflow * 0.98) * 60 * 24 * 330 + (abs(turbine_power)
                                                                               * 0.070 * 603.1 / 381.1 * 24 * 330)
        annualisedprofit = revenue - annualisedcapcost - Tutility - Trawmaterial

        if annualisedprofit < 0:
            objective = 1e10
        else:
            objective = -annualisedprofit  # we are minimising it

        # constraints
        if nonconverge == True:
            objective = 1e10
        if HCLppm > 85:
            objective = 1e10
        if L / ID > 20:
            objective = 1e10
        if D_int <= 0:
            objective = 1e10
        if CO_ppm > 0.00011:
            objective = 1e10
        if NOx_ppm > 200:
            objective = 1e10
        if W < 4200:
            objective = 1e10
        if Csb == -1:
            objective = 1e10

    data = [inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure, ER,
            efficiency, Cbm1, Cbm2, Cbm3, Cbm4, Cbm5, utility1, utility2, utility3, utility4, utility5,
            rawmaterial1, rawmaterial2, revenue, annualisedcapcost, Tutility, dieselflow, gasolineflow,
            turbine_power, annualisedprofit, nonconverge, HCLppm, L, ID, L / ID, D_int, CO_ppm, NOx_ppm, W,
            Csb, objective]

    data_store.append(data)
    save_data_store(data_store)

    objective = annualisedprofit


# inlettempdech, inlettemp, NAOHwaterflow, b_temp, b_residencetime, feedtemp, refluxmulti, pressure,
#                    ER, efficiency
checkresult(330, 25, 160, 500, 3, 113, 2, 17, 0.75, 99.7)

def readfile(name):
    with open('./data_store.pkl', 'rb') as handle:
        data_store = pickle.load(handle)

    write_excel = create_excel_file('./results/{}_results.xlsx'.format(name))
    wb = openpyxl.load_workbook(write_excel)
    ws = wb[wb.sheetnames[-1]]
    print_df_to_excel(df=pd.DataFrame(data=data_store[1], columns=data_store[0]), ws=ws)
    wb.save(write_excel)


readfile(name='basecaseresult')
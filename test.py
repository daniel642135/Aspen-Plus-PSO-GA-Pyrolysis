from aspenplus.aspen_link import init_aspen
from hclscrubber import HCL
from Pyrolysis import PYRO
from separation import SEPARATE
from dechlorination import DECH
from iapws import IAPWS95


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
    sep.sep_solve(190, 2.8)
    sep.totalcost()

#test3()

def test123():
    aspen = init_aspen()
    density = aspen.Tree.FindNode('\Data\Blocks\B7\Output\RHO_GAS\\' + str(10)).Value
    print(density)

test123()

def water():
    sat_steam = IAPWS95(T=125 + 273.15, x=1)
    sat_liquid = IAPWS95(T=125 + 273.15, x=0)
    latentheat = sat_steam.h - sat_liquid.h
    print(latentheat)

#water()
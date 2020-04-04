from aspenplus.aspen_link import init_aspen
from hclscrubber import HCL
from Pyrolysis import PYRO
from separation import SEPARATE
from dechlorination import DECH

def test1():
    aspen = init_aspen()
    hclscrubber = HCL(aspen)
    hclscrubber.solve_hcl(inlettemp=25, NAOHwaterflow=500, NAOHionsflow=4, N2flow=10000)
    hclscrubber.hcl_result()

#test1()

def test5():
    aspen = init_aspen()
    dec = DECH(aspen)
    dec.solve_dech(reactortemp = 330)

test5()


def test2():
    aspen = init_aspen()
    pyrolysis = PYRO(aspen)
    pyrolysis.solve_pyro(residencetime=3, reactortemp=500)
    pyrolysis.pyro_result()

#test2()


def test3():
    aspen = init_aspen()
    sep = SEPARATE(aspen)
    sep.totalcost()

#test3()




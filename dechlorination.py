import math

class DECH:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1 #2018 CE index
        self.pwastemassflow = self.aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TOTFLOW\NC").Value
        self.n2massflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2\Input\TOTAL\MIXED").Value
        self.dechtemp = self.aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\TEMP").Value

    def solve_dech(self, reactortemp): #residencetime in min, reactortemp in oC

        #DV
        self.aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\TEMP").Value = reactortemp
        Ea = 136 #kJ/mol
        A = 10**11.48 #min-1
        n = 1.54
        k = A*math.exp(-Ea*(10**3)/(8.314*(self.dechtemp + 273.15))) #temp need to be in K
        X = 0.98  #constrain to ensure limited PVC in plastic waste
        self.residencetime = -((1-X)**(1-n))/((1-n)*k)
        self.aspen.Engine.Run2()

        #to determine vessel sizing
        pwastevolflow = self.aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TOTFLOW\NC").Value / 962.4 #(kg/h to m3/h)

        #duty
        self.duty = self.aspen.Tree.FindNode(r"\Data\Blocks\DECH\Output\QNET").Value #cal/s


    def vesselcost(self):
        Cp = math.exp(0.481996*(math.log(self.duty * 14.28595459)) + 6.19166) #CE index of 320 #cost based on
        # rotary kiln
        Cbm = Cp * 2.2 * self.CEindex/320
        return Cbm

    def dech_totalannualcost(self):
        cost_of_heating = abs(self.duty) * 0.004184 * 0.070 * self.CEindex/381.1 * 24 * 340 # to approximate using the
        # electricity cost given in seider ($0.070/kW-hr) in 1995 price CE index 381.1
        Cbm = self.vesselcost()
        return Cbm, cost_of_heating



import math

class DECH:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1 #2018 CE index
        self.pwastemassflow = self.aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TOTFLOW\NC").Value
        self.n2massflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2\Input\TOTAL\MIXED").Value


    def solve_dech(self, reactortemp): #residencetime in min, reactortemp in oC
        self.aspen.Engine.Reinit()  # reset the simulation
        #DV
        self.reactortemp = reactortemp #oC
        self.aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\TEMP").Value = reactortemp
        self.aspen.Tree.FindNode(r"\Data\Blocks\PREHEAT\Input\TEMP").Value = reactortemp
        self.aspen.Tree.FindNode(r"\Data\Blocks\N2HETER2\Input\TEMP").Value = reactortemp

        Ea = 136 #kJ/mol
        A = 10**11.48 #min-1
        n = 1.54
        k = A*math.exp(-Ea*(10**3)/(8.314*(self.reactortemp)))
        X = 0.98 #constrain to ensure limit PVC in plastic waste
        self.residencetime = -((1-X)**(1-n))/((1-n)*k)

        self.aspen.Engine.Run2()

        #to determine vessel sizing
        N2volflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2\Output\RES_VOLFLOW").Value * 0.06 # (l/min to m3/h)this value should be fixed due to the determination of fluidizing flow based on the fixed input plastic waste
        pwastevolflow = self.aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TOTFLOW\NC").Value / 926.4 #(kg/h to m3/h) #check if suppose to be the same as pyrolysis
        voidfraction = N2volflow / (N2volflow + pwastevolflow)
        reactorvol = N2volflow*(self.residencetime/60)/voidfraction #m3

        #assuming 1:4 reactor size
        self.ID = (reactorvol / (math.pi))**(1/3) *39.3701 #in
        self.L = self.ID*4 #in
        print("L = "+str(self.L))
        print("ID = " + str(self.ID))
        self.n2heaterduty = self.aspen.Tree.FindNode(r"\Data\Blocks\N2HETER2\Output\QNET").Value #cal/s
        self.dechheaterduty = self.aspen.Tree.FindNode(r"\Data\Blocks\PREHEAT\Output\QNET").Value #cal/s


    def vesselcost(self):  #corr is boolean

        Po = 0
        To = self.reactortemp
        corr = True
        L = self.L
        ID = self.ID
        CEindex = self.CEindex

        if Po <= 5:
            Pd = 10
        elif Po <= 1000:
            Pd = math.exp(0.60608 + 0.91615*math.log(Po)+0.0015655*(math.log(Po))**2)
        else:
            Pd = 1.1*Po

        Td = To + 50 # temperature is in oF

        if not corr:
            if Td <= 650:
                S = 13750 #Carbon steel SA-285
                Fm = 1
                density = 0.284
            elif Td <= 750:
                S = 15000 #low alloy carbon steel SA387B
                Fm = 1.2
                density = 0.284
            elif Td <= 800:
                S = 14750
                Fm = 1.2
                density = 0.284
            elif Td <= 850:
                S = 14200
                Fm = 1.2
                density = 0.284
            elif Td <= 900:
                S = 13100
                Fm = 1.2
                density = 0.284
            else:
                S = 20000 #SS316 max temp is 1500 oF
                Fm = 2.1
                density = 0.289
        else:
            S = 16700 #SS316L
            Fm = 2.1
            density = 0.289

        E = 0.85
        tp = Pd*ID/(2*S*E-1.2*Pd)
        if tp > 1.25:
            E = 1
        tp = Pd * ID / (2 * S * E - 1.2 * Pd)

        if ID < 48:
            if tp < 0.25:
                tp = 0.25
        else:
            ID2 = ID - 48
            ID2 = ID2 / 24
            n2 = math.ceil(ID2)
            tpmin = n2 * (1 / 16) + (1 / 4)
            if tp < tpmin:
                tp = tpmin

        Do = ID + 2*1.25
        tw = (0.22*(Do + 18)*L**2)/(S*(Do**2))
        tpbtm = tp + tw
        tv = (tpbtm + tp)/2
        ts = tv + 0.125
        if ts <= 0.5:
            n = ts/0.0625
            n = math.ceil(n)
            ts = n*0.0625
        elif ts <= 2:
            n = ts/0.125
            n = math.ceil(n)
            ts = n*0.125
        elif ts <= 3:
            n = ts/0.25
            n = math.ceil(n)
            ts = n*0.25

        W = math.pi*(ID + ts)*(L + 0.8*ID)*ts*density
        Cv = math.exp(7.1390 + 0.18255*(math.log(W))+0.02297*(math.log(W))**2)   #CE index = 567 (2013)  # 4200< W < 1,000,000 lb
        Cpl = 410 * ((ID/12)**0.7396) * ((L/12)**0.70684)   # 3 < ID < 21 ft and 12 < L < 40 ft
        Cp = Fm*Cv + Cpl
        Cp = Cp/567 * CEindex
        Cbm = Cp * 4.16

        return Cbm

    def dech_totalannualcost(self):
        cost_of_heating = abs(self.n2heaterduty+self.dechheaterduty) * 0.004184 * 3600* 0.070  * 567/381.1 # using the electricity cost given in seider ($0.070/kW-hr) in 1995 price CE index 381.1
        # do I need to consider cost from dech unit
        Cbm = self.vesselcost()
        print("Cbm = " + str(Cbm))
        print("cost_of_heating = " + str(cost_of_heating))
        annualcost = (Cbm/3) + (cost_of_heating*8160) #per year, but this would need to be J cost of the entire plant
        print("annualcost = "+str(annualcost))
        return annualcost

    def dech_result(self):


        annual_cost = self.dech_totalannualcost()
        objective = annual_cost
        # Constraint

        return objective

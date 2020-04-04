import math

class PYRO:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1 #2018 CE index

    def solve_pyro(self, residencetime, reactortemp): #residencetime in min, reactortemp in oC
        #DV
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\TEMP").Value = reactortemp #change the temp of the reactor
        self.reactortemp = reactortemp
        self.residencetime = residencetime

        # To determine the conversion based on DVs (residencetime and reactortemp)
        # [LDPE, HDPE, PP, PET, PS, PA]
        Ea = [340.8, 445.1, 220, 214, 136.4, 217]
        A = [5.73 * (10 ** 23), 7.5536 * (10 ** 30), 1.1482 * (10 ** 15), 1.5849 * (10 ** 15), 9.66 * (10 ** 9),
             7.9433 * (10 ** 14)]
        k = []
        X = []
        for i in range(6):
            k.append(A[i] * math.exp(-Ea[i] * (10 ** 3) / (8.314 * (self.reactortemp + 273.15))))
            X.append(1 - math.exp(-k[i] * self.residencetime))

        totalconversion = 0.253 * X[0] + 0.486 * X[1] + 0.160 * X[2] + 0.010 * X[3] + 0.081 * X[4] + 0.008 * X[5]
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\CONV\1").Value = totalconversion
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\CONV\2").Value = totalconversion
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\CONV\3").Value = totalconversion
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\CONV\4").Value = totalconversion
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\CONV\5").Value = totalconversion
        self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\CONV\6").Value = totalconversion

        self.aspen.Engine.Run2()

        #to determine vessel sizing
        N2volflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2FLUID\Output\RES_VOLFLOW").Value * 0.06 # (l/min to m3/h)this value should be fixed due to the determination of fluidizing flow based on the fixed input plastic waste
        pwastevolflow = self.aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TOTFLOW\NC").Value / 926.4 #(kg/h to m3/h) #check if this is correct
        voidfraction = N2volflow / (N2volflow + pwastevolflow)
        reactorvol = N2volflow*(self.residencetime/60)/voidfraction #m3

        #assuming 1:4 reactor size
        self.ID = (reactorvol / (math.pi))**(1/3) *39.3701 #in
        self.L = self.ID*4 #in
        print("L = "+str(self.L))
        print("ID = " + str(self.ID))

        #energy requirement
        self.duty = self.aspen.Tree.FindNode("\Data\Blocks\PYRO\Output\QNET").Value #cal/s

    def vesselcost(self, L, ID, Po, To, corr, internal, stage):  # corr is boolean
        CEindex = self.CEindex
        To = To * 9 / 5 + 32  # to convert from oC to oF
        if Po <= 5:
            Pd = 10
        elif Po <= 1000:
            Pd = math.exp(0.60608 + 0.91615 * math.log(Po) + 0.0015655 * (math.log(Po)) ** 2)
        else:
            Pd = 1.1 * Po

        Td = To + 50  # temperature is in oF

        if not corr:
            if Td <= -4:
                S = 20000  # SS304 for low temp operation
                Fm = 1.7
                density = 0.289
            elif Td <= 650:
                S = 13750  # Carbon steel SA-285
                Fm = 1
                density = 0.284
            elif Td <= 750:
                S = 15000  # low alloy carbon steel SA387B
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
                S = 20000  # SS316 max temp is 1500 oF
                Fm = 2.1
                density = 0.289
        else:
            S = 16700  # SS316L
            Fm = 2.1
            density = 0.289

        E = 0.85
        tp = Pd * ID / (2 * S * E - 1.2 * Pd)
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

        Do = ID + 2 * 1.25
        tw = (0.22 * (Do + 18) * L ** 2) / (S * (Do ** 2))
        tpbtm = tp + tw
        tv = (tpbtm + tp) / 2
        ts = tv + 0.125
        if ts <= 0.5:
            n = ts / 0.0625
            n = math.ceil(n)
            ts = n * 0.0625
        elif ts <= 2:
            n = ts / 0.125
            n = math.ceil(n)
            ts = n * 0.125
        elif ts <= 3:
            n = ts / 0.25
            n = math.ceil(n)
            ts = n * 0.25

        W = math.pi * (ID + ts) * (L + 0.8 * ID) * ts * density

        Cv = math.exp(7.1390 + 0.18255 * (math.log(W)) + 0.02297 * (
            math.log(W)) ** 2)  # CE index = 567 (2013)  # 4200< W < 1,000,000 lb
        Cpl = 410 * ((ID / 12) ** 0.7396) * ((L / 12) ** 0.70684)  # 3 < ID < 21 ft and 12 < L < 40 ft

        if internal:
            # to consider for cost of trays
            Cbt = 468 * math.exp(0.1482 * (ID / 12))  # ID here needs to be in feet
            if stage < 20:
                Fnt = 2.25 / (1.0414 ** stage)
            else:
                Fnt = 1
            Ftt = 1  # for sieve trays
            Ftm = 1.401 + 0.0724 * (ID / 12)  # ID here needs to be in feet
            Ct = stage * Fnt * Ftt * Ftm * Cbt
        else:
            Ct = 0
        Cp = Fm * Cv + Cpl + Ct
        Cp = Cp / 567 * CEindex
        Cbm = Cp * 4.16

        return Cbm

    def pyro_totalannualcost(self):
        cost_of_heating = abs(self.duty) * 0.004184 * 3600 * 0.070 * 567/381.1 # to approximate using the electricity cost given in seider ($0.070/kW-hr) in 1995 price CE index 381.1
        Cbm = self.vesselcost(self.L, self.ID, Po=0, To=self.reactortemp, corr=False, internal=False, stage=0)
        print("Cbm = " + str(Cbm))
        print("cost_of_heating = " + str(cost_of_heating))
        annualcost = (Cbm/3) + (cost_of_heating*8160) #per year, but this would need to be J cost of the entire plant
        print("annualcost = "+str(annualcost))
        return annualcost

    def pyro_result(self):
        annual_cost = self.pyro_totalannualcost()
        objective = annual_cost/totalproductflow

        # Constraint

        return objective




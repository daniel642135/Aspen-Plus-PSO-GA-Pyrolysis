import math
from scipy.optimize import fsolve

class HCL:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1 #2018 CE index

        #DVs
        self.coolertemp = self.aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Input\TEMP").Value
        self.NAOHwaterin = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\WATER").Value #kmol/hr
        self.NAOHNAin = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\NA+").Value #kmol/hr
        self.NAOHOHin = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\OH-").Value #kmol/hr
        self.numofstage = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\NSTAGE").Value
        self.numofstage2 = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\FEED_STAGE\N2HCLC").Value
        self.n2massflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2\Input\TOTAL\MIXED").Value

        #target
        self.HCLmolfrac = self.aspen.Tree.FindNode(r"\Data\Streams\CLEANGAS\Output\MASSFLOW\MIXED\HCL").Value

        #for sizing
        self.hclscrubbercoolerduty = self.aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Output\QNET").Value
        self.NAOHvolflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\VOLFLMX2").Value
        self.N2HCLCvolflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\VOLFLMX2").Value

        print("temp = " + str(self.coolertemp))
        print("NAOHwaterin = " + str(self.NAOHwaterin))
        print("NAOHOHin = " + str(self.NAOHOHin))
        print("numofstage = " + str(self.numofstage))
        print("n2massflow = " + str(self.n2massflow))
        print("HCLmolfrac = " + str(self.HCLmolfrac))

    def solve_hcl(self, inlettemp, NAOHwaterflow, NAOHionsflow, N2flow):
        # DV
        self.coolertemp = inlettemp #oC
        self.NAOHwaterin = NAOHwaterflow #kmol/hr
        self.NAOHNAin = NAOHionsflow #kmol/hr
        self.NAOHOHin = NAOHionsflow #kmol/hr
        self.aspen.Tree.FindNode(r"\Data\Streams\N2\Input\FLOW\MIXED\NITROGEN").Value = N2flow #kg/hr
        print("n2massflow = "+str(self.aspen.Tree.FindNode(r"\Data\Streams\N2\Input\FLOW\MIXED\NITROGEN").Value))

        #self.aspen.Engine.Reinit()  # reset the simulation
        self.aspen.Engine.Run2()

        # retrieved required info from aspen
        L_volflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\VOLFLMX2").Value  # l/min
        L_molflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MOLEFLMX\MIXED").Value  # kmol/hr
        L_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MASSFLMX\$TOTAL").Value # kg/hr
        V_volflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\VOLFLMX2").Value  # l/min
        V_molflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MOLEFLMX\MIXED").Value  # kmol/hr
        V_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MASSFLMX\$TOTAL").Value # kg/hr
        print("V_massflow = "+str(V_massflow))

        #determine N number of stages

        print("V = "+str(V_molflow))
        molfracofHClinV = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MOLEFRAC\MIXED\HCL").Value

        # need to get the correlation for K in terms of temp and pressure
        K = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Output\B_K\5\HCL").Value  #distribution coefficient (this should be temperature and pressure dependent)
        print("K = " + str(K))

        Liquidmin_molflow = K*V_molflow*(1-molfracofHClinV)   #(1- fiak) fraction of the key component in the feed gas that is to be absorbed
        Liquid_molflow = Liquidmin_molflow * 1.5 #l/min
        print("Liquid = " + str(Liquid_molflow))
        Ae = Liquid_molflow / (K*V_molflow)
        print("Ae = " + str(Ae))
        def function(N):
            return ((Ae-1)/((Ae**(N+1))-1)) - molfracofHClinV

        N = fsolve(function, 5)
        N = math.ceil(N)
        print("N = " + str(N))
        self.numofstage = N
        self.numofstage2 = N

        #run aspen
        #self.aspen.Engine.Reinit()  # reset the simulation
        self.aspen.Engine.Run2()
        # target value
        self.HClmolfractarget = self.HCLmolfrac
        print("new hcl mol frac = " +  str(self.HClmolfractarget))
        # cooling duty
        self.hclscrubbercoolerduty = self.aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Output\QNET").Value
        #determine L
        trayspacing = 24 #in typical value from aspen
        self.L = (self.numofstage-1)*trayspacing + 36 #in +36 to account for feed inlet distributor
        print("L = " + str(self.L))

        #determine ID
        G = V_massflow  #kg/hr
        densityofgas =self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\RHOMX_MASS\MIXED").Value #g/cm3
        densityofliquid =self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\RHOMX_MASS\MIXED").Value #g/cm3
        f = 0.75
        surfacetension = 58.85 #surface tension of water (major component) n dyne/cm
        print("densityofgas = "+str(densityofgas))
        print("densityofliquid = "+str(densityofliquid))
        print("L = "+str(L_massflow))
        print("G = "+str(G))
        Flg = (L_massflow/G)*((densityofgas/densityofliquid)**0.5)
        Csb = -0.0717*math.log(Flg, 10)**2 - 0.273*math.log(Flg, 10) + 0.1299  #ft/s
        Fst = (surfacetension/20)**0.2
        Ff = 1
        Fha = 1 #considering that Ah/Aa > 0.1
        print(str(Flg) + " " + str(Csb) + " " + str(Fst))
        C = Csb*Fst*Ff*Fha
        print("C = "+ str(C))
        Uf = C*((densityofliquid - densityofgas)/densityofgas)**0.5  #ft/s
        print("Uf = " + str(Uf))
        self.ID = ((4*G)/(f*Uf*math.pi*(1-0.1)*densityofgas)*1000*(1/3600)*(1/12)*0.0610237)**0.5 #convert to in
        print("ID = " + str(self.ID))

    def vesselcost(self):  # corr is boolean

        Po = 0
        To = self.coolertemp #need to get the outlet temperature because this is exothermic process
        corr = True
        L = self.L
        ID = self.ID
        CEindex = self.CEindex

        if Po <= 5:
            Pd = 10
        elif Po <= 1000:
            Pd = math.exp(0.60608 + 0.91615 * math.log(Po) + 0.0015655 * (math.log(Po)) ** 2)
        else:
            Pd = 1.1 * Po

        Td = To + 50  # temperature is in oF

        if not corr:
            if Td <= 650:
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
        Cv = math.exp(7.1390 + 0.18255 * (math.log(W)) + 0.02297 * (math.log(W)) ** 2)  # CE index = 567 (2013)  # 4200< W < 1,000,000 lb
        Cpl = 410 * ((ID / 12) ** 0.7396) * ((L / 12) ** 0.70684)  # 3 < ID < 21 ft and 12 < L < 40 ft

        #to consider for cost of trays
        Cbt = 468*math.exp(0.1482*(ID/12))   #ID here needs to be in feet
        if self.numofstage < 20:
            Fnt = 2.25/(1.0414**self.numofstage)
        else:
            Fnt = 1
        Ftt = 1 # for sieve trays
        Ftm = 1.401 + 0.0724*(ID/12)    #ID here needs to be in feet
        Ct = self.numofstage * Fnt * Ftt * Ftm * Cbt
        Cp = Fm * Cv + Cpl + Ct
        Cp = Cp / 567 * CEindex
        Cbm = Cp * 4.16

        return Cbm

    def hcl_totalannualcost(self):
        cost_of_cooling = abs(self.hclscrubbercoolerduty) * 0.004184 * 3600 * 0.070 * 567/381.1 # using the electricity cost given in seider ($0.070/kW-hr) in 1995 price CE index 381.1 # convert from cal/s to kW/h
        Cbm = self.vesselcost()
        print("Cbm = "+str(Cbm))
        print("Cost of cooling = "+str(cost_of_cooling))
        annualcost = (Cbm/3) + (cost_of_cooling*8160) #consider per year #need to add raw material cost
        return annualcost

    def hcl_result(self):
        annualcost = self.hcl_totalannualcost()
        objective = annualcost
        print("totalcost = "+str(objective))
        # Constraint
        if self.HClmolfractarget > 0.001:    #to check on the discharge limit of HCL
            objective = 1e20
        return objective


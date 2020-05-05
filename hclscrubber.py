import math
from scipy.optimize import fsolve

class HCL:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1 #2018 CE index

        #DVs
        self.coolertemp = self.aspen.Tree.FindNode(r"\Data\Blocks\DECHC3\Input\TEMP") #oC
        self.NAOHwaterin = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\WATER").Value #kmol/hr
        self.NAOHNAin = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\NA+").Value #kmol/hr
        self.NAOHOHin = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\OH-").Value #kmol/hr
        self.numofstage = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\NSTAGE").Value
        self.numofstage2 = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\FEED_STAGE\N2HCLC").Value
        self.n2massflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2\Input\TOTAL\MIXED").Value
        #for sizing
        self.NAOHvolflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\VOLFLMX2").Value
        self.N2HCLCvolflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\VOLFLMX2").Value

        # need to get the correlation for K in terms of temp and pressure
        self.K = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Output\B_K\5\HCL").Value
        # distribution coefficient (this should be temperature and pressure dependent)

    def solve_hcl(self, inlettemp, NAOHwaterflow):
        # DV
        self.aspen.Tree.FindNode(r"\Data\Blocks\DECHC3\Input\TEMP").Value = inlettemp #oC
        self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\WATER").Value = NAOHwaterflow #kmol/hr
        self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\NA+").Value = 0.2 * NAOHwaterflow
        #kmol/hr #consider that 20% caustic is used
        self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\OH-").Value = 0.2 * NAOHwaterflow
        #kmol/hr #consider that 20% caustic is used

        self.aspen.Engine.Run2()

        # retrieved required info from aspen
        L_volflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\VOLFLMX2").Value  # l/min
        L_molflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MOLEFLMX\MIXED").Value  # kmol/hr
        L_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MASSFLMX\$TOTAL").Value # kg/hr
        V_volflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\VOLFLMX2").Value  # l/min
        V_molflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MOLEFLMX\MIXED").Value  # kmol/hr
        V_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MASSFLMX\$TOTAL").Value # kg/hr

        #determine N number of stages
        molfracofHClinV = self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MOLEFRAC\MIXED\HCL").Value

        # need to get the correlation for K in terms of temp and pressure
        K = self.K

        Liquidmin_molflow = K*V_molflow*(1-molfracofHClinV)
        #(1- fiak) fraction of the key component in the feed gas that is to be absorbed
        Liquid_molflow = Liquidmin_molflow * 1.5 #l/min
        Ae = Liquid_molflow / (K*V_molflow)

        def function(N):
            return ((Ae-1)/((Ae**(N+1))-1)) - molfracofHClinV

        N = fsolve(function, 5)
        N = math.ceil(N)
        self.numofstage = N
        self.numofstage2 = N
        self.numoftrays = N

        #run aspen
        self.aspen.Engine.Run2()

        # cooling duty
        self.cooler1 = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\DECHC1\Output\QNET").Value)
        self.cooler2 = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\DECHC2\Output\QNET").Value)
        self.cooler3 = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\DECHC3\Output\QNET").Value)
        #print(self.cooler1, self.cooler2, self.cooler3)
        #determine L
        trayspacing = 24 #in typical value from aspen
        self.L = (self.numofstage-1)*trayspacing + 36 #in +36 to account for feed inlet distributor
        #determine ID
        G = V_massflow  #kg/hr
        densityofgas =self.aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\RHOMX_MASS\MIXED").Value #g/cm3
        densityofliquid =self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\RHOMX_MASS\MIXED").Value #g/cm3
        f = 0.75
        surfacetension = 58.85 #surface tension of water (major component) n dyne/cm
        Flg = (L_massflow/G)*((densityofgas/densityofliquid)**0.5)
        Csb = -0.0717*math.log(Flg, 10)**2 - 0.273*math.log(Flg, 10) + 0.1299  #ft/s
        Fst = (surfacetension/20)**0.2
        Ff = 1
        Fha = 1 #considering that Ah/Aa > 0.1
        C = Csb*Fst*Ff*Fha
        Uf = C*((densityofliquid - densityofgas)/densityofgas)**0.5  #ft/s
        self.ID = ((4*G)/(f*Uf*math.pi*(1-0.1)*densityofgas)*1000*(1/3600)*(1/12)*0.0610237)**0.5 #convert to in

        self.scrubbertemp = self.aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Output\BOTTOM_TEMP").Value

        #for determination of raw material cost
        self.N2volflowrate = self.aspen.Tree.FindNode(r"\Data\Streams\N2\Output\VOLFLMX_GAS").Value #l/min
        massofNa = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MASSFLOW\MIXED\NA+").Value #kg/hr
        massofOH = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MASSFLOW\MIXED\OH-").Value #kg/hr
        self.massofNaOH = massofNa + massofOH
        massofwater = self.aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\MASSFLOW\MIXED\WATER").Value #kg/hr
        self.volofwater = massofwater / 997 #convert kg/hr to m3/hr

        #for determination of discharge limit
        cleangasvolflow = self.aspen.Tree.FindNode(r"\Data\Streams\CLEANGAS\Output\VOLFLMX\MIXED").Value * 0.06
        #convert l/min to m3/hr
        HCLmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\CLEANGAS\Output\MASSFLOW\MIXED\HCL").Value #kg/hr
        cleangastemp = self.aspen.Tree.FindNode(r"\Data\Streams\CLEANGAS\Output\TEMP_OUT\MIXED").Value + 273.15
        #convert oC to K
        self.HCLppm = (HCLmassflow * (10**6) * 22.4 * cleangastemp) / (273.15 * cleangasvolflow * 36.46)
        #conversion to ppm
        #print(self.HCLppm, self.ID, self.L)
        return self.HCLppm

    def vesselcost(self, L, ID, Po, To, corr, internal, stage):  # corr is boolean
        if L < 144:
            L = 144
        if ID < 36:
            ID = 36
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
            if Td > 300:
                S = 6200  # Nickel 201
                Fm = 5.4
                density = 0.321
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
        print(W)
        if W < 4200:
            W = 4200
        Cv = math.exp(7.1390 + 0.18255 * (math.log(W)) + 0.02297 * (math.log(W)) ** 2)
        # CE index = 567 (2013)  # 4200< W < 1,000,000 lb
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

    def hcl_totalannualcost(self):
        cost_of_cooling = (self.cooler1 + self.cooler2 + self.cooler3) * 4.184 * 10**-9 * 3600 * 24 * 340 * 0.354
        # using the cooling water given in Turton ($0.354/GJ) # convert from cal/s to GJ/s To consider that that
        # can be considered as current price
        Cbm = self.vesselcost(self.L, self.ID, Po=0, To=self.scrubbertemp, corr=True, internal=True,
                              stage=self.numoftrays)
        #raw material cost
        N2 = self.N2volflowrate * 0.001 * 60 * 24 * 340 * 0.65 #convert l/min to m3/yr, with the price of 0.65 per m3
        NaOH = self.massofNaOH * 24 * 340 * 0.49 #convert to $/year for 0.49/kg
        water = self.volofwater * 24 * 340 * 0.48 #convert to $/year for 0.48/kg
        rawmaterialcost = N2 + NaOH + water

        return Cbm, cost_of_cooling, rawmaterialcost




import math

class SEPARATE:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 600  # Find value

        self.hotgasvolflow = (self.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX\MIXED").Value + self.aspen.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX\CISOLID").Value)*0.0353146667 #convert from l/min to cfm

        #to determine the ID and L of the separatiors
        #separator 1
        self.vapordensity1 = self.aspen.Tree.FindNode(r"\Data\Blocks\B1\Stream Results\Table\Density gm/cc S2").Value*1000 #convert from g/cm3 to kg/m3
        self.liquiddensity1 = self.aspen.Tree.FindNode(r"\Data\Blocks\B1\Stream Results\Table\Density gm/cc S3").Value*1000 #convert from g/cm3 to kg/m3
        self.vaporvolflow1 = self.aspen.Tree.FindNode(r"\Data\Blocks\B1\Stream Results\Table\Total Flow l/min S2").Value*1.66667e-5 #convert from l/min to m3/s
        self.liquidvolflow1 = self.aspen.Tree.FindNode(r"\Data\Blocks\B1\Stream Results\Table\Total Flow l/min S3").Value*1.66667e-5 #convert from l/min to m3/s
        self.temp1 = self.aspen.Tree.FindNode(r"\Data\Blocks\B1\Input\TEMP").Value
        liquiddropletsdiameter1 = 0.000005 #m
        vapourviscosity1 = 0.01 #cP
        Vt1 = (2.94*(9.81**0.7)*(liquiddropletsdiameter1**1.14)*((self.liquiddensity1-self.vapordensity1)**0.71))/((self.vapordensity1**0.29)*((vapourviscosity1/1000)**0.43)) #m/s  #applicable for 2<Re<500
        #check Re
        Re = 1000*liquiddropletsdiameter1*Vt1*self.vapordensity1/(vapourviscosity1/1000)
        if Re < 2:
            Vt1 = (1000*9.81*(liquiddropletsdiameter1**2)*(self.liquiddensity1-self.vapordensity1))/(18*(vapourviscosity1/1000))
        elif Re < 500:
            Vt1 = Vt1
        else:
            Vt1 = 1.74*math.sqrt((9.81*liquiddropletsdiameter1*(self.liquiddensity1-self.vapordensity1))/self.vapordensity1)
        Vg1 = (2/3)*Vt1 #m/s
        Dv1 = math.sqrt((4*self.vaporvolflow1)/(math.pi*Vg1)) #m
        L1 = (4*self.vaporvolflow1)/(math.pi*Vg1*Dv1)
        Ll = (4*self.vaporvolflow1*120)/(math.pi*(Dv1**2))
        minliquidlevel1 = 0.17*L1
        L1 = minliquidlevel1 + L1
        self.L1 = L1*39.3701 #convert from m to inch
        self.ID1 = Dv1*39.3701 #convert from m to inch

        #flash 2
        self.vapordensity2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B4\Stream Results\Table\Density gm/cc VAPOUR").Value*1000 #convert from g/cm3 to kg/m3
        self.liquiddensity2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B4\Stream Results\Table\Density gm/cc S6").Value*1000 #convert from g/cm3 to kg/m3
        self.vaporvolflow2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B4\Stream Results\Table\Total Flow l/min VAPOUR").Value*1.66667e-5 #convert from l/min to m3/s
        self.liquidvolflow2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B4\Stream Results\Table\Total Flow l/min S6").Value*1.66667e-5 #convert from l/min to m3/s
        self.temp2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B4\Input\TEMP").Value
        liquiddropletsdiameter2 = 0.000004 #m
        vapourviscosity2 = 0.01 #cP
        Vt2 = (2.94*(9.81**0.7)*(liquiddropletsdiameter1**1.14)*((self.liquiddensity1-self.vapordensity1)**0.71))/((self.vapordensity1**0.29)*((vapourviscosity1/1000)**0.43)) #m/s  #applicable for 2<Re<500
        #check Re
        Re = 1000*liquiddropletsdiameter1*Vt1*self.vapordensity1/(vapourviscosity1/1000)
        if Re < 2:
            Vt2 = (1000*9.81*(liquiddropletsdiameter1**2)*(self.liquiddensity1-self.vapordensity1))/(18*(vapourviscosity1/1000))
        elif Re < 500:
            Vt2 = Vt1
        else:
            Vt2 = 1.74*math.sqrt((9.81*liquiddropletsdiameter1*(self.liquiddensity1-self.vapordensity1))/self.vapordensity1)
        Vg2 = (2/3)*Vt2 #m/s
        Dv2 = math.sqrt((4*self.vaporvolflow2)/(math.pi*Vg2)) #m
        L2 = (4*self.vaporvolflow2)/(math.pi*Vg2*Dv2)
        L2 = (4*self.vaporvolflow2*120)/(math.pi*(Dv2**2))
        minliquidlevel2 = 0.17*L2
        L2 = minliquidlevel2 + L2
        self.L2 = L2*39.3701 #convert from m to inch
        self.ID2 = Dv2*39.3701 #convert from m to inch

        #tank separator
        #consider minimum tank volume design 2.4 m3 and L:D is 1:4
        self.L3 = 3.6576*39.3701 #convert from m to inch
        self.ID3 = 0.9144*39.3701 #convert from m to inch
        self.temp3 = self.aspen.Tree.FindNode(r"\Data\Blocks\B5\Input\TEMP").Value

        #distillation
        self.numofstage = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Input\NSTAGE").Value
        self.L4 = self.numofstage*0.6*3.28084*1.3*12 #convert from m to inch
        self.temp4 = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\BOTTOM_TEMP").Value #oC
        feedmassflow = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\TOT_MASS_ABS").Value #kg/h
        botmassflow = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\MASS_B").Value #kg/h
        distmassflow = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\MASS_D").Value #kg/h
        refluxratio = 0.15 #to get from short cut column for the reflux ratio

        vapourmassflow = distmassflow*(1+refluxratio)
        liquidmassflow = vapourmassflow - distmassflow
        vapordensity = 0.0062228 #g/cm3 determine from Hysys - would change based on temperature, but the temperature change is small so it can be approximated to be constant
        liquiddesnity = 0.540485191 #g/cm3 determine from Hysys - would change based on temperature, but the temperature change is small so it can be approximated to be constant
        surfacetension = 23.05 #dyne/cm

        Flg = (liquidmassflow / vapourmassflow) * ((vapordensity / liquiddesnity) ** 0.5)
        Csb = -0.0717 * math.log(Flg, 10) ** 2 - 0.273 * math.log(Flg, 10) + 0.1299  # ft/s
        Fst = (surfacetension / 20) ** 0.2
        Ff = 1
        Fha = 1  # considering that Ah/Aa > 0.1
        C = Csb * Fst * Ff * Fha
        f = 0.8
        Uf = C * ((liquiddesnity - vapordensity) / vapordensity) ** 0.5  # ft/s
        A = 0.1 + (Flg-0.1)/9
        self.ID4 = ((4 * vapourmassflow) / (f * Uf * math.pi * (1 - A) * vapordensity) * 1000 * (1 / 3600) * (1 / 12) * 0.0610237) ** 0.5  # convert to in

    def cyclone(self):
        Cp1 = math.exp(9.227-(0.7892*math.log(self.hotgasvolflow)+(0.08487*(math.log(self.hotgasvolflow))**2)))  #applicable for 200-10^5 cfm
        return Cp1

    def pump(self):
        Pout = self.aspen.Tree.FindNode(r"\Data\Blocks\PUMP\Input\PRES").Value / 14.696 #atm
        Pin = 1 #atm
        Pdiff = Pout - Pin
        feeddensity = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\RHOMX_MASS\MIXED").Value * 62.428 #slight diff #lbm/ft3
        pumphead = Pdiff * 14.696 * 144/feeddensity #ft

        feedmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\MASSFLMX_LIQ").Value * 2.204623 #kg/h to lbm/h
        feeddensity*0.133681
        pumpsize = (feedmassflow/(60*feeddensity*0.133681))*(pumphead**0.5)
        Cb = math.exp(9.7171 - 0.6019 * math.log(pumpsize) + 0.0519 * (math.log(pumpsize)) ** 2)
        Ft = 1
        Fm = 1
        Cp = Ft*Fm*Cb*self.CEindex/500
        feedvolflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\VOLFLMX2").Value * 15.8503 #convert l/min to gal/hr
        pumpeff = -0.316 + 0.24015* math.log(pumphead)-0.01199*(math.log(pumphead))**2
        Pb = pumphead*Pout*feedvolflow/(33000*pumpeff)
        motoreff = 0.8 + 0.0319 * math.log(Pb) - 0.00182 * (math.log(Pb)) ** 2
        Pc = math.log(Pb/motoreff)
        motorCb = math.exp(5.8259 + 0.13141 * Pc + 0.053255 * (Pc) ** 2 + 0.028628 * (Pc) ** 3 - 0.0035549 * (Pc) ** 4)
        totalCb = Cb + motorCb
        Cbm = totalCb*3.3
        return Cbm

    def utilitycost(self):
        CEindex = self.CEindex
        Cf = 6 #$/GJ
        pyrovapourcoolercost = self.aspen.Tree.FindNode(r"\Data\Blocks\COOLER\Output\QNET").Value * 0.004184 * 3600 * 0.070 * self.CEindex/381.1 # using the electricity cost given in seider ($0.070/kW-hr) in 1995 price CE index 381.1 # convert from cal/s to kW/h

        #refrigerant cooler
        T = self.aspen.Tree.FindNode(r"\Data\Blocks\B2\Input\TEMP").Value + 273.15 #oC to k
        Q = self.aspen.Tree.FindNode(r"\Data\Blocks\B2\Output\QNET").Value*4.184 #cal/s to kj/s
        a = 0.5*(Q**(-0.9))*(T**(-3))
        b = 1.1*(10**6)*(T**(-5))
        refrigerantcoolercost = a*CEindex + b*Cf


    def vesselcost(self, L, ID, Po, To, corr, internal):  # corr is boolean
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

        if internal:
            #to consider for cost of trays
            Cbt = 468*math.exp(0.1482*(ID/12))   #ID here needs to be in feet
            if self.numofstage < 20:
                Fnt = 2.25/(1.0414**self.numofstage)
            else:
                Fnt = 1
            Ftt = 1 # for sieve trays
            Ftm = 1.401 + 0.0724*(ID/12)    #ID here needs to be in feet
            Ct = self.numofstage * Fnt * Ftt * Ftm * Cbt
        else:
            Ct = 0
        Cp = Fm * Cv + Cpl + Ct
        Cp = Cp / 567 * CEindex
        Cbm = Cp * 4.16

        return Cbm

    def totalcost(self):
        S1capitalcost = self.vesselcost(self.L1, self.ID1, Po=0, To=self.temp1, corr=False, internal=False)
        S2capitalcost = self.vesselcost(self.L2, self.ID2, Po=0, To=self.temp2, corr=False, internal=False)
        S3capitalcost = self.vesselcost(self.L3, self.ID3, Po=0, To=self.temp3, corr=False, internal=False)
        S4capitalcost = self.vesselcost(self.L4, self.ID4, Po=0, To=self.temp4, corr=False, internal=True)
        cyclonecapticalcost = self.cyclone()




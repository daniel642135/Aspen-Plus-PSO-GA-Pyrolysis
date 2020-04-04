import math

class SEPARATE:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1  # Find value

        self.hotgasvolflow = (self.aspen.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX\MIXED").Value + self.aspen.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX\CISOLID").Value)*0.0353146667 #convert from l/min to cfm

        #to determine the ID and L of the separatiors
        #separator 1
        self.vapordensity1 = self.aspen.Tree.FindNode(r"\Data\Streams\S2\Output\RHOMX_MASS\MIXED").Value*1000 #convert from g/cm3 to kg/m3
        self.liquiddensity1 = self.aspen.Tree.FindNode(r"\Data\Streams\S3\Output\RHOMX_MASS\MIXED").Value*1000 #convert from g/cm3 to kg/m3
        self.vaporvolflow1 = self.aspen.Tree.FindNode(r"\Data\Streams\S2\Output\VOLFLMX\MIXED").Value*1.66667e-5 #convert from l/min to m3/s
        self.liquidvolflow1 = self.aspen.Tree.FindNode(r"\Data\Streams\S3\Output\VOLFLMX\MIXED").Value*1.66667e-5 #convert from l/min to m3/s
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
        Ll1 = (4*self.liquidvolflow1*180)/(math.pi*(Dv1**2))
        minliquidlevel1 = 0.17*Dv1
        L1 = minliquidlevel1 + L1 + Ll1
        self.L1 = L1*39.3701 #convert from m to inch
        self.ID1 = Dv1*39.3701 #convert from m to inch

        #flash 2
        self.vapordensity2 = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\RHOMX_MASS\MIXED").Value*1000 #convert from g/cm3 to kg/m3
        self.liquiddensity2 = self.aspen.Tree.FindNode(r"\Data\Streams\S6\Output\RHOMX_MASS\MIXED").Value*1000 #convert from g/cm3 to kg/m3
        self.vaporvolflow2 = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\VOLFLMX\MIXED").Value*1.66667e-5 #convert from l/min to m3/s
        self.liquidvolflow2 = self.aspen.Tree.FindNode(r"\Data\Streams\S6\Output\VOLFLMX\MIXED").Value*1.66667e-5 #convert from l/min to m3/s
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
        Ll2 = (4*self.liquidvolflow2*180)/(math.pi*(Dv2**2))
        minliquidlevel2 = 0.17*Dv2
        L2 = minliquidlevel2 + L2 + Ll2
        self.L2 = L2*39.3701 #convert from m to inch
        self.ID2 = Dv2*39.3701 #convert from m to inch

        #tank separator
        #consider minimum tank volume design 2.4 m3 and L:D is 1:4
        self.L3 = 3.6576*39.3701 #convert from m to inch
        self.ID3 = 0.9144*39.3701 #convert from m to inch
        self.temp3 = self.aspen.Tree.FindNode(r"\Data\Blocks\B5\Input\TEMP").Value

        #distillation
        self.numofstage = self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\NSTAGE").Value
        self.L4 = self.numofstage*0.6*3.28084*1.3*12 #convert from m to inch
        self.temp4 = self.aspen.Tree.FindNode(r"\Data\Streams\HEAVYACT\Output\TEMP_OUT\MIXED").Value #oC
        feedmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIQAFHEA\Output\MASSFLMX\$TOTAL").Value #kg/h
        botmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\HEAVYACT\Output\MASSFLMX\$TOTAL").Value #kg/h
        distmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIGHTACT\Output\MASSFLMX\$TOTAL").Value #kg/h
        refluxratio = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Input\RR").Value #this is the DV

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
        Cp = math.exp(9.227-(0.7892*math.log(self.hotgasvolflow))+(0.08487*(math.log(self.hotgasvolflow))**2)) #applicable for 200-10^5 cfm
        Cp = Cp * self.CEindex/500
        Cbm = Cp*2
        return Cbm

    def pump(self):
        Pout = self.aspen.Tree.FindNode(r"\Data\Blocks\PUMP\Input\PRES").Value / 14.696 #atm
        Pin = 1 #atm
        Pdiff = Pout - Pin
        feeddensity = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\RHOMX_MASS\MIXED").Value * 62.428 #slight diff #lbm/ft3
        pumphead = Pdiff * 14.696 * 144/feeddensity #ft

        feedmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\MASSFLMX_LIQ").Value * 2.204623 #kg/h to lbm/h
        pumpsize = (feedmassflow/(60*feeddensity*0.133681))*(pumphead**0.5)
        Cb = math.exp(9.7171 - 0.6019 * math.log(pumpsize) + 0.0519 * (math.log(pumpsize)) ** 2)
        Ft = 1
        Fm = 1
        Cp = Ft*Fm*Cb*self.CEindex/500
        Pb = self.aspen.Tree.FindNode(r"\Data\Blocks\PUMP\Output\BRAKE_POWER").Value * 13.4102 #kW to BHp
        motoreff = 0.8 + 0.0319 * math.log(Pb) - 0.00182 * (math.log(Pb)) ** 2
        self.Pc = math.log(Pb/motoreff)
        motorCb = math.exp(5.8259 + 0.13141 * self.Pc + 0.053255 * (self.Pc) ** 2 + 0.028628 * (self.Pc) ** 3 - 0.0035549 * (self.Pc) ** 4)
        motorCp = Pdiff*motorCb*self.CEindex/500
        totalCp = Cp + motorCp
        Cbm = totalCp*3.3
        print(Pdiff, feeddensity, pumphead, feedmassflow, pumpsize, self.Pc)
        return Cbm

    def utilitycost(self):
        CEindex = self.CEindex
        Cf = 6 #$/GJ

        #cooling water cooler
        pyrovapourcoolercost = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\COOLER\Output\QNET").Value) *4.184 * 10**-9 * 3600 * 24 * 330 * 0.378  # using the cooling water given in Turton ($0.378/GJ) # convert from cal/s to GJ/s To consider that that can be considered as current price

        #refrigerant cooler
        T = self.aspen.Tree.FindNode(r"\Data\Blocks\B2\Input\TEMP").Value + 273.15 #oC to k
        Q = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\B2\Output\QNET").Value)*4.184/1000 #cal/s to kj/s
        a = 0.5*(Q**(-0.9))*(T**(-3))
        b = 1.1*(10**6)*(T**(-5))
        Cu = a*CEindex + b*Cf #$/kJ
        refrigerantcoolercost = Cu * Q * 3600 * 24 * 330

        #pump utility cost
        #make sure to run capital cost first before utility cost function or the self variable will not be updated
        electricost = 0.00013*CEindex + 0.01*Cf #$/kwh
        pumpcost = self.Pc * 0.7457 * 31.5 * 10**6 * electricost / 3600 /365 * 330 #$/year
        print(self.Pc)
        def reboiler(duty, steamtempin, steamtempout, pressure):
            CEindex = 603.1
            #first law of thermo
            steammolarenthalpy = 33.4*(10**-3)*steamtempin+0.688*(10**-5)/2*steamtempin**2+0.7604*(10**-8)/3*steamtempin**3-3.593*(10**-12)/4*steamtempin**4-(33.4*(10**-3)*steamtempout+0.688*(10**-5)/2*steamtempout**2+0.7604*(10**-8)/3*steamtempout**3-3.593*(10**-12)/4*steamtempout**4) #kJ/mol
            steammassenthalpy = steammolarenthalpy / 18.02 * 1000 #kJ/kg
            steamcapacity = duty / steammassenthalpy /3600 #kg/s
            a = 2.3 * 10 ** -5 * steamcapacity ** -0.9
            b = 0.0034 * pressure ** 0.05
            process_steam = a * CEindex + b * 6 #Cf is $6/GJ
            reboilercost = steamcapacity*31.5*10**6*process_steam/365*330 #check the formula here
            return reboilercost

        #HE heater to distillation using LPS
        Q1 = self.aspen.Tree.FindNode(r"\Data\Blocks\LIQHEAT\Output\QNET").Value * 15.0624  # convert from cal/s to kJ/hr
        Tin1 = 135  # oC fixed based on process stream and heuristics
        Tout1 = 123.89  # oC fixed based on process stream and heuristics
        P1 = 3.082  # barg (based on LPS)
        reboilercost1 = reboiler(Q1, Tin1, Tout1, P1)

        #Distillation column reboiler using (check what steam is here) #the problem here will be no stream can heat up to 300 plus
        Q2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\REB_DUTY").Value * 15.0624  # convert from cal/s to kJ/hr
        Tin2 = 348.67  # oC (need to change to retrieve from aspen plus)
        Tout2 = 329.78  # oC (need to change to retrieve from aspen plus)
        P2 = 34.47  # barg (based on HPS but need to change)
        reboilercost2 = reboiler(Q2, Tin2, Tout2, P2)

        #Distillation column cooler using cooling water
        Q3 = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\COND_DUTY").Value) * 15.0624  # convert from cal/s to kJ/hr
        Tin3 = 25 #oC
        Tout3 = 49 #oC
        CWmolarenthalpy = 75.4*(10**-3)*(Tout3-Tin3)*1000 #kJ/kmol
        CWmassenthalpy = CWmolarenthalpy / 18.02 #kJ/kg
        CWcapacity = Q3 / CWmassenthalpy / 1002 / 3600 #m3/s #at the lower limit of the correlation
        if CWcapacity < 0.01:
            CWcapacity = 0.01
        a2 = 0.00007 + 2.5 * (10 ** -5) * CWcapacity ** -1
        b2 = 0.003
        process_cw = a2 * CEindex + b2 * 6 #Cf is $6/GJ
        condensercost = CWcapacity*31.5*10**6*process_cw/365*330

        #get total cost for utility
        totalseparationutilitycost = pyrovapourcoolercost + refrigerantcoolercost + pumpcost + reboilercost1 + reboilercost2 + condensercost
        print(pyrovapourcoolercost, refrigerantcoolercost, pumpcost, reboilercost1, reboilercost2, condensercost)
        return totalseparationutilitycost

    def vesselcost(self, L, ID, Po, To, corr, internal, stage):  # corr is boolean
        CEindex = self.CEindex
        To = To *9/5 + 32 #to convert from oC to oF
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
        print(tp)
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
        print(W, ID, ts, L, density)
        Cv = math.exp(7.1390 + 0.18255 * (math.log(W)) + 0.02297 * (math.log(W)) ** 2)  # CE index = 567 (2013)  # 4200< W < 1,000,000 lb
        Cpl = 410 * ((ID / 12) ** 0.7396) * ((L / 12) ** 0.70684)  # 3 < ID < 21 ft and 12 < L < 40 ft

        if internal:
            #to consider for cost of trays
            Cbt = 468*math.exp(0.1482*(ID/12))   #ID here needs to be in feet
            if stage < 20:
                Fnt = 2.25/(1.0414**stage)
            else:
                Fnt = 1
            Ftt = 1 # for sieve trays
            Ftm = 1.401 + 0.0724*(ID/12)    #ID here needs to be in feet
            Ct = stage * Fnt * Ftt * Ftm * Cbt
        else:
            Ct = 0
        Cp = Fm * Cv + Cpl + Ct
        Cp = Cp / 567 * CEindex
        Cbm = Cp * 4.16

        return Cbm

    def totalcost(self):
        S1capitalcost = self.vesselcost(self.L1, self.ID1, Po=0, To=self.temp1, corr=False, internal=False, stage=0)
        S2capitalcost = self.vesselcost(self.L2, self.ID2, Po=0, To=self.temp2, corr=False, internal=False, stage=0)
        S3capitalcost = self.vesselcost(self.L3, self.ID3, Po=0, To=self.temp3, corr=False, internal=False, stage=0)
        S4capitalcost = self.vesselcost(self.L4, self.ID4, Po=0, To=self.temp4, corr=False, internal=True, stage=self.numofstage)
        cyclonecapticalcost = self.cyclone()
        pumpcapitalcost = self.pump()

        utilitycost = self.utilitycost()
        totalcost = S1capitalcost + S2capitalcost + S3capitalcost + S4capitalcost + cyclonecapticalcost + pumpcapitalcost + utilitycost
        print(S1capitalcost, S2capitalcost, S3capitalcost, S4capitalcost, cyclonecapticalcost, pumpcapitalcost, utilitycost)
        print(totalcost)



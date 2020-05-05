import math
from iapws import IAPWS95

class SEPARATE:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1  # Find value

        self.hotgasvolflow = (self.aspen.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX\MIXED").Value +
                              self.aspen.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX\CISOLID").Value)\
                             *0.0353146667 #convert from l/min to cfm

        #to determine the ID and L of the separatiors
        #separator 1
        self.vapordensity1 = self.aspen.Tree.FindNode(r"\Data\Streams\S2\Output\RHOMX_MASS\MIXED").Value*1000
        #convert from g/cm3 to kg/m3
        self.liquiddensity1 = self.aspen.Tree.FindNode(r"\Data\Streams\S3\Output\RHOMX_MASS\MIXED").Value*1000
        #convert from g/cm3 to kg/m3
        self.vaporvolflow1 = self.aspen.Tree.FindNode(r"\Data\Streams\S2\Output\VOLFLMX\MIXED").Value*1.66667e-5
        #convert from l/min to m3/s
        self.liquidvolflow1 = self.aspen.Tree.FindNode(r"\Data\Streams\S3\Output\VOLFLMX\MIXED").Value*1.66667e-5
        #convert from l/min to m3/s
        self.temp1 = self.aspen.Tree.FindNode(r"\Data\Blocks\B1\Input\TEMP").Value
        liquiddropletsdiameter1 = 0.000005 #m
        vapourviscosity1 = 0.01 #cP
        Vt1 = (2.94*(9.81**0.7)*(liquiddropletsdiameter1**1.14)*((self.liquiddensity1-self.vapordensity1)**0.71))/\
              ((self.vapordensity1**0.29)*((vapourviscosity1/1000)**0.43)) #m/s  #applicable for 2<Re<500
        #check Re
        Re = 1000*liquiddropletsdiameter1*Vt1*self.vapordensity1/(vapourviscosity1/1000)
        if Re < 2:
            Vt1 = (1000*9.81*(liquiddropletsdiameter1**2)*(self.liquiddensity1-self.vapordensity1))/\
                  (18*(vapourviscosity1/1000))
        elif Re < 500:
            Vt1 = Vt1
        else:
            Vt1 = 1.74*math.sqrt((9.81*liquiddropletsdiameter1*(self.liquiddensity1-self.vapordensity1))/
                                 self.vapordensity1)
        Vg1 = (2/3)*Vt1 #m/s
        Dv1 = math.sqrt((4*self.vaporvolflow1)/(math.pi*Vg1)) #m
        L1 = (4*self.vaporvolflow1)/(math.pi*Vg1*Dv1)
        Ll1 = (4*self.liquidvolflow1*180)/(math.pi*(Dv1**2))
        minliquidlevel1 = 0.17*Dv1
        L1 = minliquidlevel1 + L1 + Ll1
        self.L1 = L1*39.3701 #convert from m to inch
        self.ID1 = Dv1*39.3701 #convert from m to inch

        #flash 2
        self.vapordensity2 = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\RHOMX_MASS\MIXED").Value*1000
        #convert from g/cm3 to kg/m3
        self.liquiddensity2 = self.aspen.Tree.FindNode(r"\Data\Streams\S6\Output\RHOMX_MASS\MIXED").Value*1000
        #convert from g/cm3 to kg/m3
        self.vaporvolflow2 = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\VOLFLMX\MIXED").Value*1.66667e-5
        #convert from l/min to m3/s
        self.liquidvolflow2 = self.aspen.Tree.FindNode(r"\Data\Streams\S6\Output\VOLFLMX\MIXED").Value*1.66667e-5
        #convert from l/min to m3/s
        self.temp2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B4\Input\TEMP").Value
        liquiddropletsdiameter2 = 0.000004 #m
        vapourviscosity2 = 0.01 #cP
        Vt2 = (2.94*(9.81**0.7)*(liquiddropletsdiameter1**1.14)*((self.liquiddensity1-self.vapordensity1)**0.71))/\
              ((self.vapordensity1**0.29)*((vapourviscosity1/1000)**0.43)) #m/s  #applicable for 2<Re<500
        #check Re
        Re = 1000*liquiddropletsdiameter1*Vt1*self.vapordensity1/(vapourviscosity1/1000)
        if Re < 2:
            Vt2 = (1000*9.81*(liquiddropletsdiameter1**2)*(self.liquiddensity1-self.vapordensity1))/\
                  (18*(vapourviscosity1/1000))
        elif Re < 500:
            Vt2 = Vt1
        else:
            Vt2 = 1.74*math.sqrt((9.81*liquiddropletsdiameter1*(self.liquiddensity1-self.vapordensity1))/
                                 self.vapordensity1)
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

    def sep_solve(self, feedtemp, refluxmulti):
        self.aspen.Tree.FindNode(r"\Data\Blocks\LIQHEAT\Input\TEMP").Value = feedtemp
        self.reboilertemp = feedtemp
        self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Input\RR").Value = -refluxmulti

        self.aspen.Engine.Run2()
        # retrieve info from shortcut column as initial guess, then put into distillation column
        Rmin = self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\MIN_REFLUX").Value
        feedtray = math.ceil(self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\FEED_LOCATN").Value)
        stages = math.ceil(self.aspen.Tree.FindNode(r"\Data\Blocks\B6\Output\ACT_STAGES").Value)
        Distflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIGHT\Output\MASSFLMX_LIQ").Value #kg/hr

        self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\BASIS_D").Value = Distflow
        self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\BASIS_RR").Value = \
            self.aspen.Tree.FindNode("\Data\Blocks\B6\Output\ACT_REFLUX").Value
        self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\DP_COL").Value = 5
        self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\FEED_STAGE\LIQAFHE2").Value = feedtray
        self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\NSTAGE").Value = stages
        #number of stages includes condenser and reboiler
        self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Input\PROD_STAGE\HEAVYACT").Value = stages
        self.aspen.Engine.Run2()

        if self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\BU_RATIO").Value == None:
            nonconverge = True
            L4 = -1
            ID4 = -1
            dieselflow = -1
            gasolineflow = -1
            Csb = -1
        elif self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\REB_DUTY").Value == None:
            nonconverge = True
            L4 = -1
            ID4 = -1
            dieselflow = -1
            gasolineflow = -1
            Csb = -1
        else:
            nonconverge = False

            # determine column diameter and height
            # determine L
            trayspacing = 24  # in typical value from aspen
            self.tray = stages - 1
            L4 = (stages - 1) * trayspacing + 36  # in +36 to account for feed inlet distributor,
            # one of the stage is reboiler

            # determine ID
            def diameter(V_massflow, L_massflow, densityofgas, densityofliquid, surfacetension):
                G = V_massflow  # kg/hr
                f = 0.75

                Flg = (L_massflow / G) * ((densityofgas / densityofliquid) ** 0.5)
                if Flg < 0.01:
                    Csb = 0.39
                if Flg < 2:
                    Csb = -0.0717 * math.log(Flg, 10) ** 2 - 0.273 * math.log(Flg, 10) + 0.1299  # ft/s
                else:
                    Csb = 0.04 #use to indicate out of correlation
                Fst = (surfacetension / 20) ** 0.2
                Ff = 1
                Fha = 1  # considering that Ah/Aa > 0.1
                C = Csb * Fst * Ff * Fha
                Uf = C * ((densityofliquid - densityofgas) / densityofgas) ** 0.5  # ft/s
                if Flg <= 0.1:
                    downarea = 0.1
                elif Flg <= 1:
                    downarea = 0.1 + (Flg - 0.1)/9
                else:
                    downarea = 0.2
                ID = ((4 * G) / (f * Uf * math.pi * (1 - downarea) * densityofgas) * 1000 * (1 / 3600) * (1 / 12) *
                      0.0610237) ** 0.5  # convert to in
                return ID, Csb

            TopV = self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\VAP_FLOW\2").Value
            TopL = self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\LIQ_FLOW\2").Value
            BotV = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\VAP_FLOW\\' + str(stages-1)).Value
            BotL = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\LIQ_FLOW\\' + str(stages-1)).Value

            if TopV > BotV:
                V_mw = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\MW_GAS\\' + str(2)).Value
                V_massflow = TopV * V_mw * 1.2 #size 20% more to account for buffer
                V_moldensity = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\RHO_GAS\\' + str(2)).Value
            else:
                V_mw = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\MW_GAS\\' + str(stages-1)).Value
                V_massflow = BotV * V_mw * 1.2
                V_moldensity = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\RHO_GAS\\' + str(stages-1)).Value

            if TopL > BotL:
                L_mw = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\MW_LIQ\\' + str(2)).Value
                L_massflow = TopL * L_mw * 1.2
                L_moldensity = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\RHO_LIQ\\' + str(2)).Value
            else:
                L_mw = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\MW_LIQ\\' + str(stages-1)).Value
                L_massflow = BotL * L_mw * 1.2
                L_moldensity = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\RHO_LIQ\\' + str(stages-1)).Value

            L_massdensity = L_moldensity * L_mw #g/cc
            V_massdensity = V_moldensity * V_mw #g/cc
            surfacetension = 6.27868046594332  # dyne/cm

            ID4, Csb = diameter(V_massflow, L_massflow, V_massdensity, L_massdensity, surfacetension)

            def round_up(n, decimals=0):
                multiplier = 10 ** decimals
                return math.ceil(n * multiplier) / multiplier

            feedpressure = self.aspen.Tree.FindNode('\Data\Blocks\B7\Output\B_PRES\\' + str(feedtray)).Value
            #Feed pressure
            feedpressure = round_up(feedpressure, 2)
            self.temp4 = self.aspen.Tree.FindNode("\Data\Blocks\B7\Output\BOTTOM_TEMP").Value #oC
            pressure = self.aspen.Tree.FindNode(r"\Data\Streams\HEAVYACT\Output\PRES_OUT\MIXED").Value #bar
            self.pressure = (pressure * 14.5038) - 14.6959 #psig

            #retrieve flow rate of products
            dieselflow = self.aspen.Tree.FindNode(r"\Data\Streams\HEAVYACT\Output\VOLFLMX\MIXED").Value #l/min
            gasolineflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIGHTACT\Output\VOLFLMX\MIXED").Value #l/min

        self.L4 = L4
        self.ID4 = ID4
        return L4, ID4, dieselflow, gasolineflow, Csb, nonconverge

    def cyclone(self):
        Cp = math.exp(9.227-(0.7892*math.log(self.hotgasvolflow))+(0.08487*(math.log(self.hotgasvolflow))**2))
        #applicable for 200-10^5 cfm
        Cp = Cp * self.CEindex/500
        Cbm = Cp*2
        return Cbm

    def pump(self):
        Pout = self.aspen.Tree.FindNode(r"\Data\Blocks\PUMP\Input\PRES").Value / 14.696 #atm
        Pin = 1 #atm
        Pdiff = Pout - Pin
        feeddensity = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\RHOMX_MASS\MIXED").Value * 62.428
        #slight diff #lbm/ft3
        pumphead = Pdiff * 14.696 * 144/feeddensity #ft

        feedmassflow = self.aspen.Tree.FindNode(r"\Data\Streams\LIQUID\Output\MASSFLMX_LIQ").Value * 2.204623
        #kg/h to lbm/h
        pumpsize = (feedmassflow/(60*feeddensity*0.133681))*(pumphead**0.5)
        Cb = math.exp(9.7171 - 0.6019 * math.log(pumpsize) + 0.0519 * (math.log(pumpsize)) ** 2)
        Ft = 1
        Fm = 1
        Cp = Ft*Fm*Cb*self.CEindex/500
        Pb = self.aspen.Tree.FindNode(r"\Data\Blocks\PUMP\Output\BRAKE_POWER").Value * 13.4102 #kW to BHp
        motoreff = 0.8 + 0.0319 * math.log(Pb) - 0.00182 * (math.log(Pb)) ** 2
        self.Pc = math.log(Pb/motoreff)
        motorCb = math.exp(5.8259 + 0.13141 * self.Pc + 0.053255 * (self.Pc) ** 2 + 0.028628 * (self.Pc) ** 3
                           - 0.0035549 * (self.Pc) ** 4)
        motorCp = Pdiff*motorCb*self.CEindex/500
        totalCp = Cp + motorCp
        Cbm = totalCp*3.3

        return Cbm

    def utilitycost(self):
        CEindex = self.CEindex
        Cf = 6 #$/GJ

        #cooling water cooler
        totalcoolingduty = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\VAPC1\Output\QNET").Value +
                               self.aspen.Tree.FindNode(r"\Data\Blocks\VAPC2\Output\QNET").Value +
                               self.aspen.Tree.FindNode(r"\Data\Blocks\VAPC3\Output\QNET").Value +
                               self.aspen.Tree.FindNode(r"\Data\Blocks\VAPC4\Output\QNET").Value +
                               self.aspen.Tree.FindNode(r"\Data\Blocks\VAPC5\Output\QNET").Value)
        pyrovapourcoolercost = totalcoolingduty * 4.184 * 10**-9 * 3600 * 24 * 340 * 0.378
        # using the cooling water given in Turton ($0.378/GJ) # convert from cal/s to GJ/s To consider
        # that that can be considered as current price

        #refrigerant cooler
        T = self.aspen.Tree.FindNode(r"\Data\Blocks\B2\Input\TEMP").Value + 273.15 #oC to k
        Q = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\B2\Output\QNET").Value)*4.184/1000 #cal/s to kj/s
        a = 0.5*(Q**(-0.9))*(T**(-3))
        b = 1.1*(10**6)*(T**(-5))
        Cu = a*CEindex + b*Cf #$/kJ
        refrigerantcoolercost = Cu * Q * 3600 * 24 * 340

        #pump utility cost
        #make sure to run capital cost first before utility cost function or the self variable will not be updated
        electricost = 0.00013*CEindex + 0.01*Cf #$/kwh
        pumpcost = self.Pc * 0.7457 * 31.5 * 10**6 * electricost / 3600 /365 * 340 #$/year

        def reboiler(duty, steamtempin, pressure):
            CEindex = 603.1
            #first law of thermo
            sat_steam = IAPWS95(T=steamtempin + 273.15, x=1)
            sat_liquid = IAPWS95(T=steamtempin + 273.15, x=0)
            latentheat = sat_steam.h - sat_liquid.h
            steamcapacity = duty / latentheat / 3600 #kg/s
            a = 2.3 * 10 ** -5 * steamcapacity ** -0.9
            b = 0.0034 * pressure ** 0.05
            process_steam = a * CEindex + b * 6 #Cf is $6/GJ
            reboilercost = steamcapacity*31.5*10**6*process_steam/365*340

            return reboilercost

        P1 = 0
        Tin1 = 0

        #HE heater to distillation using different steam for different temperature
        if self.reboilertemp < 114: #LPS 125-124
            P1 = 1.31 #barg
            Tin1 = 125  # oC
        elif self.reboilertemp < 164: #MPS 175-174
            P1 = 7.91  # barg
            Tin1 = 175  # oC
        elif self.reboilertemp < 239: #HPS 250-249
            P1 = 38.75  # barg
            Tin1 = 250  # oC

        Q1 = self.aspen.Tree.FindNode(r"\Data\Blocks\LIQHEAT\Output\QNET").Value * 15.0624
        # convert from cal/s to kJ/hr
        reboilercost1 = reboiler(Q1, Tin1, P1)

        #Distillation column reboiler (fired heater) utility based on natural gas
        if self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\REB_DUTY").Value == None:
            nonconverge = True
            reboilercost2 = -1
        else:
            nonconverge = False
            Q2 = self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\REB_DUTY").Value * 0.00396567
            # convert from cal/s to Btu/s
            #for 70% efficiency
            natgas = Q2/0.7/1050 * 3600 * 24 * 340 # SCF/yr
            reboilercost2 = natgas * 0.0283168 * 0.71 * 0.51289615 #based on thailand NGV 2019 price

        #Distillation column cooler using cooling water
        if self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\COND_DUTY").Value == None:
            nonconverge = True
            condensercost = -1
        else:
            nonconverge = False
            Q3 = abs(self.aspen.Tree.FindNode(r"\Data\Blocks\B7\Output\COND_DUTY").Value) * 15.0624
            # convert from cal/s to kJ/hr
            condensercost = Q3 * 4.184 * 10**-9 * 3600 * 24 * 340 * 0.378
        # using the cooling water given in Turton ($0.378/GJ) # convert from cal/s to GJ/s To consider
        # that that can be considered as current price

        #get total cost for utility
        totalseparationutilitycost = pyrovapourcoolercost + refrigerantcoolercost + pumpcost + reboilercost1 + \
                                     reboilercost2 + condensercost
        # print(pyrovapourcoolercost, refrigerantcoolercost, pumpcost, reboilercost1, reboilercost2, condensercost)
        return totalseparationutilitycost, nonconverge

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

    def towercost(self, L, ID, Po, To, corr, internal, stage):  # corr is boolean
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
        self.W = W
        Cv = math.exp(10.5449 - 0.4672 * (math.log(W)) + 0.05482 * (math.log(W)) ** 2)
        # CE index = 567 (2013)  # 9,000 < W < 2,500,000 lb
        Cpl = 341 * ((ID / 12) ** 0.63316) * ((L / 12) ** 0.80161)  # 3 < ID < 21 ft and 27 < L < 170 ft
        #print("W = " + str(W), "Cpl = " + str(Cpl))
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

        return Cbm, W

    def totalcost(self):
        S1capitalcost = self.vesselcost(self.L1, self.ID1, Po=0, To=self.temp1, corr=False, internal=False, stage=0)
        S2capitalcost = self.vesselcost(self.L2, self.ID2, Po=0, To=self.temp2, corr=False, internal=False, stage=0)
        S3capitalcost = self.vesselcost(self.L3, self.ID3, Po=0, To=self.temp3, corr=False, internal=False, stage=0)
        S4capitalcost, W = self.towercost(self.L4, self.ID4, Po=self.pressure, To=self.temp4, corr=False, internal=True,
                                          stage=self.tray)
        cyclonecapticalcost = self.cyclone()
        pumpcapitalcost = self.pump()
        utilitycost, nonconverge = self.utilitycost()
        Cbm = S1capitalcost + S2capitalcost + S3capitalcost + S4capitalcost + cyclonecapticalcost + pumpcapitalcost
        return Cbm, utilitycost, W, nonconverge

import pandas as pd

class COMB:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 600 # Find value
    #calculating mass flow rate of air
    def stoic_air(self):
        methane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\METHANE").Value
        ethane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\ETHANE").Value
        ethene_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\ETHENE").Value
        propane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\PROPANE").Value
        propene_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\PROPENE").Value
        butane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\BUTANE").Value
        CO_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\CO").Value

        methane_stoic = methane_feed_massflow * 17.262
        ethane_stoic = ethane_feed_massflow * 16.111
        ethene_stoic = ethene_feed_massflow * 14.796
        propane_stoic = propane_feed_massflow * 15.693
        propene_stoic = propene_feed_massflow * 14.796
        butane_stoic = butane_feed_massflow * 15.476
        CO_stoic = CO_feed_massflow * 2.466
        stoic_air = methane_stoic+ ethane_stoic+ ethene_stoic+ propane_stoic+ propene_stoic+ butane_stoic+ CO_stoic
        return stoic_air

    #properties to be retrieved from Aspen Plus
    def process_parameters (self):
        m3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\MASSFLMX\MIXED").Value/3600,1) #in kg/s
        P3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\PRES_OUT\MIXED").Value * 100000,1) #in Pa
        T3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value +273.15,1) #in K
        T4 = round(self.aspen.Tree.FindNode(r"\Data\Streams\FLUE\Output\TEMP_OUT\MIXED").Value +273.15,1) #in K
        return [m3,P3,T3,T4]


    def dimensions(self):
        R = 286.9
        Tmax = 2000
        b = 300
        P34_qref = 20
        P34_P3 = 0.06
        P3_P34 = 1 / P34_P3
        theta = 80000000

        aspen_outputs = self.process_parameters()
        m3 = aspen_outputs[0]
        P3 = aspen_outputs[1]
        T3 = aspen_outputs[2]
        T4 = aspen_outputs[3]

        A_ref = ((R / 2) * ((m3 * T3 ** 0.5 / P3) ** 2) * P34_qref * P3_P34) ** 0.5
        A_L = 0.66 * A_ref
        A_an = A_ref - A_L
        PF = (Tmax - T4) / (T4 - T3)
        D_ref = ((m3 * theta) / (P3 ** 1.75 * A_ref * math.exp(T3 / b))) ** (4 / 3)
        D_L = D_ref * 0.66
        L_L = (-1 * D_L) / (0.05 * P34_qref * math.log(1 - PF))
        L_PZ = 0.75 * D_L
        L_SZ = 0.5 * D_L
        L_DZ = D_L * (3.83 - 11.83 * PF + 13.4 * PF ** 2)
        D_int = A_L / (math.pi * D_L) - D_ref
        CSTR_V = (L_PZ + L_SZ) * A_L
        PFR_L = L_DZ
        PFR_D = (4 * A_L / 3.14) ** 0.5

        Dimensions = {}
        Dimensions['A_ref'] = A_ref
        Dimensions['A_L'] = A_L
        Dimensions['A_an'] = A_an
        Dimensions['PF'] = PF
        Dimensions['D_ref'] = D_ref
        Dimensions['D_L'] = D_L
        Dimensions['L_L'] = L_L
        Dimensions['L_PZ'] = L_PZ
        Dimensions['L_SZ'] = L_SZ
        Dimensions['L_DZ'] = L_DZ
        Dimensions['D_int'] = D_int
        Dimensions['CSTR_V'] = CSTR_V
        Dimensions['PFR_L'] = PFR_L
        Dimensions['PFR_D'] = PFR_D
        Dimensions['air entering combustor'] = m3
        Dimensions['pressure'] = P3
        Dimensions['temperature pre'] = T3
        Dimensions['temperature posst'] = T4

        df = pd.DataFrame(Dimensions, index=[0])
        return df


    def combustor_volumes(self):
        R = 286.9
        Tmax = 2000
        b = 300
        P34_qref = 20
        P34_P3 = 0.06
        P3_P34 = 1 / P34_P3
        theta = 80000000

        aspen_outputs = self.process_parameters()
        m3 = aspen_outputs[0]
        P3 = aspen_outputs[1]
        T3 = aspen_outputs[2]
        T4 = aspen_outputs[3]

        A_ref = ((R / 2) * ((m3 * T3 ** 0.5 / P3) ** 2) * P34_qref * P3_P34) ** 0.5
        A_L = 0.66 * A_ref
        A_an = A_ref - A_L
        PF = (Tmax - T4) / (T4 - T3)
        D_ref = ((m3 * theta) / (P3 ** 1.75 * A_ref * math.exp(T3 / b))) ** (4 / 3)
        D_L = D_ref * 0.66
        L_L = (-1 * D_L) / (0.05 * P34_qref * math.log(1 - PF))
        L_PZ = 0.75 * D_L
        L_SZ = 0.5 * D_L
        L_DZ = D_L * (3.83 - 11.83 * PF + 13.4 * PF ** 2)
        D_int = A_L / (math.pi * D_L) - D_ref
        CSTR_V = (L_PZ + L_SZ) * A_L * 1000  # in Litres
        PFR_L = L_DZ  # in metres
        PFR_D = (4 * A_L / 3.14) ** 0.5  # in metres
        return [CSTR_V, PFR_L, PFR_D, T4]

    # note to self: only the length of the PFR(dilution zone) keeps on changing due to T4

    # iterative process:
    def iterative_solution(self):
        CSTR_vol = self.combustor_volumes()[0]
        DZ_Length = self.combustor_volumes()[1]
        DZ_Diameter = self.combustor_volumes()[2]
        guess_post_combustion_temperature = round(self.combustor_volumes()[3], 0)

        self.aspen.Tree.FindNode(r"\Data\Blocks\ANNULAR\Input\VOL").Value = CSTR_vol
        self.aspen.Tree.FindNode(r"\Data\Blocks\DILUTION\Input\DIAM").Value = DZ_Diameter
        self.aspen.Tree.FindNode(r"\Data\Blocks\DILUTION\Input\LENGTH").Value = DZ_Length
        self.aspen.Engine.run2()

        Post_combustion_temperature = round(self.aspen.Tree.FindNode(r"\Data\Streams\FLUE\Output\TEMP_OUT\MIXED").Value + 273.15,
                                            1)

        error = abs(Post_combustion_temperature - guess_post_combustion_temperature)

        if error <= 1:
            return self.dimensions()
        else:
            return self.iterative_solution()

    # def comb_result(self):
    #     annualcost = self.hcl_totalannualcost() #J cost
    #     objective = annualcost
    #     # Constraint
    #     if self.HClmolfractarget > 0.001:  # to check on the discharge limit of HCL
    #         objective = 1e20
    #     return objective


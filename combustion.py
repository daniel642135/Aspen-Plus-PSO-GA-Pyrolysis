import pandas as pd
import numpy as np
import math

class COMB:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1  # 2018 CE index
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

    def combustor_volumes(self, eff, m3, P3, T3, T4):

        self.R = 286.9
        self.Tmax = 2200
        self.b = 300
        self.P34_qref = 20
        self.P34_P3 = 0.06
        self.P3_P34 = 1 / self.P34_P3


        A_ref = ((self.R/2)*((m3*T3**0.5/P3)**2)*self.P34_qref*self.P3_P34)**0.5
        A_L = 0.66 * A_ref
        A_an = A_ref - A_L
        PF = (self.Tmax - T4)/(T4 - T3)
        D_ref = ((m3*self.theta) / (P3**1.75*A_ref*math.exp(T3/self.b)))**(4/3)
        D_L = D_ref * 0.66
        L_L= (-1*D_L)/(0.05*self.P34_qref*math.log(1-PF))
        L_PZ = 0.75 * D_L
        L_SZ = 0.5 * D_L
        L_DZ = D_L * (3.83 - 11.83*PF + 13.4*PF**2)
        D_int = A_L/(math.pi*D_L) - D_ref
        CSTR_V= L_PZ * A_L * 1000
        PFR_L = L_DZ + L_SZ
        PFR_D = (4* A_L/3.14)**0.5
        return [CSTR_V,PFR_L,PFR_D]

    def iterative_solution(self, eff, m3, P3, T3, T4):
        CSTR_vol = self.combustor_volumes(eff, m3, P3, T3, T4)[0]
        DZ_Length = self.combustor_volumes(eff, m3, P3, T3, T4)[1]
        DZ_Diameter = self.combustor_volumes(eff, m3, P3, T3, T4)[2]

        self.aspen.Tree.FindNode(r"\Data\Blocks\ANNULAR\Input\VOL").Value = CSTR_vol
        self.aspen.Tree.FindNode(r"\Data\Blocks\DILUTION\Input\DIAM").Value = DZ_Diameter
        self.aspen.Tree.FindNode(r"\Data\Blocks\DILUTION\Input\LENGTH").Value = DZ_Length
        self.aspen.Engine.run2()

        combustor_inlet_mass_flow = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\MASSFLMX\MIXED").Value/3600,1) #in kg/s
        operating_pressure = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\PRES_OUT\MIXED").Value * 100000,1) #in Pa
        inlet_temperature = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value +273.15,1) #in K
        outlet_temperature = round(self.aspen.Tree.FindNode(r"\Data\Streams\FLUE\Output\TEMP_OUT\MIXED").Value +273.15,1) #in K
        self.CO_ppm =  self.aspen.Tree.FindNode(r"\Data\Streams\FLUESTAC\Output\MASSFRAC\MIXED\CO").Value # mass_frac
        turbine_power = self.aspen.Tree.FindNode(r"\Data\Blocks\TURBINE\Output\WNET").Value #in kW
        fuel_comp_power = self.aspen.Tree.FindNode(r"\Data\Blocks\FUELCOMP\Output\WNET").Value #in kW
        air_comp_power = self.aspen.Tree.FindNode(r"\Data\Blocks\AIRCOMP\Output\WNET").Value #in kW
        net_power = (turbine_power + fuel_comp_power + air_comp_power)*(-1)

        A_ref = ((self.R/2)*((m3*T3**0.5/P3)**2)*self.P34_qref*self.P3_P34)**0.5
        A_L = 0.66 * A_ref
        A_an = A_ref - A_L
        PF = (self.Tmax - T4)/(T4 - T3)
        D_ref = ((m3*self.theta) / (P3**1.75*A_ref*math.exp(T3/self.b)))**(4/3)
        D_L = D_ref * 0.66
        L_L= (-1*D_L)/(0.05*self.P34_qref*math.log(1-PF))
        L_PZ = 0.75 * D_L
        L_SZ = 0.5 * D_L
        L_DZ = D_L * (3.83 - 11.83*PF + 13.4*PF**2)
        self.D_int = A_L/(math.pi*D_L) - D_ref
        CSTR_V= L_PZ * A_L * 1000
        PFR_L = L_DZ + L_SZ
        PFR_D = (4* A_L/3.14)**0.5


        Dimensions = {}
        Dimensions['A_ref']=A_ref
        Dimensions['A_L']=A_L
        Dimensions['A_an']=A_an
        Dimensions['PF']=PF
        Dimensions['D_ref']=D_ref
        Dimensions['D_L']=D_L
        Dimensions['L_L']=L_L
        Dimensions['L_PZ']=L_PZ
        Dimensions['L_SZ']=L_SZ
        Dimensions['L_DZ']=L_DZ
        Dimensions['D_int']=self.D_int
        Dimensions['CSTR_V']=CSTR_V
        Dimensions['PFR_L']=PFR_L
        Dimensions['PFR_D']=PFR_D
        Dimensions['combustor_inlet_mass_flow'] = combustor_inlet_mass_flow
        Dimensions['operating_pressure'] = operating_pressure
        Dimensions['inlet_temperature'] = inlet_temperature
        Dimensions['outlet_temperature'] = outlet_temperature
        Dimensions['CO_ppm'] = self.CO_ppm
        Dimensions['turbine_power'] = turbine_power
        Dimensions['fuel_comp_power'] = fuel_comp_power
        Dimensions['air_comp_power'] = air_comp_power
        Dimensions['net_power'] = net_power

        return Dimensions


#
# OPressure = [24] #gives list of pressures to test
# ER=[0.8]
# combustion_efficiency = [0.998]
# col_names = ['A_ref','A_L', 'A_an', 'PF', 'D_ref', 'D_L', 'L_L', 'L_PZ', 'L_SZ','L_DZ', 'D_int', 'CSTR_V', 'PFR_L', 'PFR_D', 'combustor_inlet_mass_flow', 'operating_pressure', 'inlet_temperature', 'outlet_temperature', 'CO_ppm', 'turbine_power', 'fuel_comp_power', 'air_comp_power', 'net_power', 'Base cost for air comp', 'Base cost for fuel comp', 'Base cost for turbine', 'BM cost for air comp', 'BM cost for fuel comp', 'BM cost for turbine', 'adjusted BM cost for air comp', 'adjusted BM cost for fuel comp', 'adjusted BM cost for turbine', 'utilities cost in USD/year', 'capital cost in USD', 'capital cost in USD per year','J cost']
#all_results_list = []

    def combustionsolve(self, OP, OER, eff):

        self.theta = ((-0.413 * math.log(1 - (eff / 100))) ** 2.146) * 100000000  # function has to take in eff somewhere...

        stoichiometric_air = self.stoic_air()
        actual_mass_flow_rate_of_air = stoichiometric_air / OER

        self.aspen.Tree.FindNode(r"\Data\Blocks\AIRCOMP\Input\PRATIO").Value = OP
        self.aspen.Tree.FindNode(r"\Data\Blocks\FUELCOMP\Input\PRATIO").Value = OP
        self.aspen.Tree.FindNode(r"\Data\Blocks\ANNULAR\Input\PRES").Value = OP
        #print(OP)
        self.aspen.Engine.run2()
        T_inlet = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value + 273.15, 1)
        #print(T_inlet)
        cooling_air_percentage = ((0.1 * T_inlet - 30) + 100) / 100
        compressed_air_needed = actual_mass_flow_rate_of_air * cooling_air_percentage
        self.aspen.Tree.FindNode(r"\Data\Streams\ATMAIR\Input\TOTFLOW\MIXED").Value = compressed_air_needed
        self.aspen.Tree.FindNode(r"\Data\Blocks\COMPSPLI\Input\BASIS_FLOW\TOPREMIX").Value = actual_mass_flow_rate_of_air

        self.aspen.Engine.run2()
        m3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\MASSFLMX\MIXED").Value / 3600, 1)  # in kg/s
        P3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\PRES_OUT\MIXED").Value * 100000, 1)  # in Pa
        T3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value + 273.15, 1)  # in K

        methane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\METHANE").Value
        ethane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\ETHANE").Value
        ethene_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\ETHENE").Value
        propane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\PROPANE").Value
        propene_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\PROPENE").Value
        butane_feed_massflow = self.aspen.Tree.FindNode(r"\Data\Streams\VAPOUR\Output\MASSFLOW\MIXED\BUTANE").Value

        C1_heat = methane_feed_massflow * 55.5
        C2_heat = (ethane_feed_massflow * 51.9) + (ethene_feed_massflow * 47.2)
        C3_heat = (propane_feed_massflow * 50.4) + (propene_feed_massflow * 49)
        C4_heat = butane_feed_massflow * 49.5

        total_heat = C1_heat + C2_heat + C3_heat + C4_heat  # in MJ/hr
        mass_out = self.aspen.Tree.FindNode(r"\Data\Streams\FLUE\Output\MASSFLMX\MIXED").Value  # in kG/hr
        #print(C1_heat, C2_heat, C3_heat, C4_heat)
        actual_heat = (eff * total_heat) / 100
        delta_T = (actual_heat / mass_out) / 0.0013
        T4 = delta_T + T3
        #PF = (self.Tmax - T4) / (T4 - T3)
        #print(m3, P3, T3, T4)

        aspen_results_dict = self.iterative_solution(eff, m3, P3, T3, T4)
        #print('ok!!')
        hp_air_comp = aspen_results_dict['air_comp_power'] * 1.34102
        hp_fuel_comp = aspen_results_dict['fuel_comp_power'] * 1.34102
        hp_turbine_comp = aspen_results_dict['turbine_power'] * -1.34102

        aspen_results_dict['Base cost for air comp'] = math.exp(9.1553 + 0.63 * math.log(hp_air_comp))
        aspen_results_dict['Base cost for fuel comp'] = math.exp(9.1553 + 0.63 * math.log(hp_fuel_comp))
        aspen_results_dict['Base cost for turbine'] = 1618.8 * ((hp_turbine_comp) ** 0.7951)

        MOC_air_comp = 2
        MOC_fuel_comp = 2
        MOC_turbine = 2

        BM_coefficient = 2.15

        aspen_results_dict['BM cost for air comp'] = aspen_results_dict['Base cost for air comp'] * (MOC_air_comp + BM_coefficient - 1)
        aspen_results_dict['BM cost for fuel comp'] = aspen_results_dict['Base cost for fuel comp'] * (MOC_fuel_comp + BM_coefficient - 1)
        aspen_results_dict['BM cost for turbine'] = aspen_results_dict['Base cost for turbine'] * (MOC_turbine + BM_coefficient - 1)

        CE_air_comp = 567
        CE_fuel_comp = 567
        CE_turbine = 390

        CE_current = 603.1 #2018

        aspen_results_dict['adjusted BM cost for air comp'] = (CE_current / CE_air_comp) * aspen_results_dict['BM cost for air comp']
        aspen_results_dict['adjusted BM cost for fuel comp'] = (CE_current / CE_fuel_comp) * aspen_results_dict['BM cost for fuel comp']
        aspen_results_dict['adjusted BM cost for turbine'] = (CE_current / CE_turbine) * aspen_results_dict['BM cost for turbine']

        aspen_results_dict['utilities cost in USD/year'] = (aspen_results_dict['fuel_comp_power'] + aspen_results_dict['air_comp_power']) * 0.12 * 8760  # USD/year
        aspen_results_dict['capital cost in USD'] = aspen_results_dict['adjusted BM cost for air comp'] + aspen_results_dict['adjusted BM cost for fuel comp'] + aspen_results_dict['adjusted BM cost for turbine']
        aspen_results_dict['capital cost in USD per year'] = aspen_results_dict['capital cost in USD'] / 3
        aspen_results_dict['J cost'] = aspen_results_dict['capital cost in USD per year'] + aspen_results_dict['utilities cost in USD/year']
        aspen_results_dict['OP from python'] = OP
        aspen_results_dict['OER from python'] = OER
        aspen_results_dict['combustion efficiency'] = eff
        aspen_results_dict['T3'] = T3
        aspen_results_dict['P3'] = P3
        aspen_results_dict['T4 (estimated)'] = T4

        # NOx emissions
        ma = self.aspen.Tree.FindNode(r"\Data\Streams\COMPAIR\Output\MASSFLMX\$TOTAL").Value / 3600
        fuel_mass_flow = (methane_feed_massflow + ethane_feed_massflow + ethene_feed_massflow + propane_feed_massflow + propene_feed_massflow + butane_feed_massflow) / 3600
        q = fuel_mass_flow / ma
        NOx_ppmv = 18.1 * (OP ** 1.42) * (ma ** 0.3) * (q ** 0.72)  # ppmv
        # ppm = ppmv * density of mixture / density of species
        self.NOx_ppm = NOx_ppmv * 0.64035
        aspen_results_dict['NOx ppm'] = self.NOx_ppm
        #all_results_list.append(aspen_results_dict)
        #print('next!', NOx_ppm)
        self.Jcost = aspen_results_dict['J cost']

    def comb_result(self):
        objective = self.Jcost
        #constraints
        if self.D_int <= 0:
            objective = 1e20
        if self.CO_ppm > 0.00011:
            objective = 1e20
        if self.NOx_ppm > 200:
            objective = 1e20
        return objective


#all_results_df = pd.DataFrame(all_results_list)
#all_results_df.to_csv('all_results_25March.csv')
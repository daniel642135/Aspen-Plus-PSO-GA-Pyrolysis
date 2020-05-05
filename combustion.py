import pandas as pd
import numpy as np
import math
from aspenplus.aspen_link import init_aspen

class COMB:
    def __init__(self, aspen):
        self.aspen = aspen
        self.CEindex = 603.1  # 2018 CE index
    def combustionsolve(self, OP, OER, eff):
        R = 286.9
        Tmax = 2200
        b = 300
        P34_qref = 20
        P34_P3 = 0.06
        P3_P34 = 1 / P34_P3
        theta = ((-0.413 * math.log(1 - (eff / 100))) ** 2.146) * 100000000  # function has to take in eff somewhere...

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
        stoichiometric_air = methane_stoic + ethane_stoic + ethene_stoic + propane_stoic + propene_stoic + butane_stoic\
                             + CO_stoic

        actual_mass_flow_rate_of_air = stoichiometric_air / OER

        self.aspen.Tree.FindNode(r"\Data\Blocks\AIRCOMP\Input\PRATIO").Value = OP
        self.aspen.Tree.FindNode(r"\Data\Blocks\FUELCOMP\Input\PRATIO").Value = OP
        self.aspen.Tree.FindNode(r"\Data\Blocks\ANNULAR\Input\PRES").Value = OP

        self.aspen.Engine.run2()

        T_inlet = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value + 273.15, 1)



        cooling_air_percentage = ((0.1 * T_inlet - 30) + 100) / 100
        compressed_air_needed = actual_mass_flow_rate_of_air * cooling_air_percentage
        self.aspen.Tree.FindNode(r"\Data\Streams\ATMAIR\Input\TOTFLOW\MIXED").Value = compressed_air_needed
        self.aspen.Tree.FindNode(r"\Data\Blocks\COMPSPLI\Input\BASIS_FLOW\TOPREMIX").Value = \
            actual_mass_flow_rate_of_air
        # print(compressed_air_needed, actual_mass_flow_rate_of_air)

        self.aspen.Engine.run2()
        m3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\MASSFLMX\MIXED").Value / 3600, 1)  # in kg/s
        P3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\PRES_OUT\MIXED").Value * 100000, 1)  # in Pa
        T3 = round(self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value + 273.15, 1)  # in K

        C1_heat = methane_feed_massflow * 55.5
        C2_heat = (ethane_feed_massflow * 51.9) + (ethene_feed_massflow * 47.2)
        C3_heat = (propane_feed_massflow * 50.4) + (propene_feed_massflow * 49)
        C4_heat = butane_feed_massflow * 49.5
        #print(C1_heat,C2_heat,C3_heat,C4_heat)
        total_heat = C1_heat + C2_heat + C3_heat + C4_heat  # in MJ/hr
        mass_out = self.aspen.Tree.FindNode(r"\Data\Streams\FLUE\Output\MASSFLMX\MIXED").Value  # in kG/hr
        #print(total_heat, mass_out)
        actual_heat = (eff * total_heat) / 100
        delta_T = (actual_heat / mass_out) / 0.0013
        T4 = delta_T + T3

        A_ref = ((R / 2) * ((m3 * T3 ** 0.5 / P3) ** 2) * P34_qref * P3_P34) ** 0.5
        A_L = 0.66 * A_ref
        A_an = A_ref - A_L
        PF = (Tmax - T4) / (T4 - T3)
        D_ref = ((m3 * theta) / (P3 ** 1.75 * A_ref * np.exp(T3 / b))) ** (4 / 3)
        D_L = D_ref * 0.66
        L_L = (-1 * D_L) / (0.05 * P34_qref * np.log(1 - PF))
        L_PZ = 0.75 * D_L
        L_SZ = 0.5 * D_L
        L_DZ = D_L * (3.83 - 11.83 * PF + 13.4 * PF ** 2)
        D_int = A_L / (math.pi * D_L) - D_ref
        CSTR_V = L_PZ * A_L * 1000
        PFR_L = L_DZ + L_SZ
        PFR_D = (4 * A_L / 3.14) ** 0.5

        self.aspen.Tree.FindNode(r"\Data\Blocks\ANNULAR\Input\VOL").Value = CSTR_V
        self.aspen.Tree.FindNode(r"\Data\Blocks\DILUTION\Input\DIAM").Value = PFR_D
        self.aspen.Tree.FindNode(r"\Data\Blocks\DILUTION\Input\LENGTH").Value = PFR_L
        self.aspen.Engine.run2()

        combustor_inlet_mass_flow = round(
            self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\MASSFLMX\MIXED").Value / 3600, 1)  # in kg/s
        operating_pressure = round(
            self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\PRES_OUT\MIXED").Value * 100000, 1)  # in Pa
        inlet_temperature = round(
            self.aspen.Tree.FindNode(r"\Data\Streams\PREMIXED\Output\TEMP_OUT\MIXED").Value + 273.15, 1)  # in K
        outlet_temperature = round(
            self.aspen.Tree.FindNode(r"\Data\Streams\FLUE\Output\TEMP_OUT\MIXED").Value + 273.15, 1)  # in K
        CO_ppm = self.aspen.Tree.FindNode(r"\Data\Streams\FLUESTAC\Output\MASSFRAC\MIXED\CO").Value  # mass_frac
        turbine_power = self.aspen.Tree.FindNode(r"\Data\Blocks\TURBINE\Output\WNET").Value  # in kW
        fuel_comp_power = self.aspen.Tree.FindNode(r"\Data\Blocks\FUELCOMP\Output\WNET").Value  # in kW
        air_comp_power = self.aspen.Tree.FindNode(r"\Data\Blocks\AIRCOMP\Output\WNET").Value  # in kW
        net_power = (turbine_power + fuel_comp_power + air_comp_power) * (-1)

        hp_air_comp = air_comp_power * 1.34102
        hp_fuel_comp = fuel_comp_power * 1.34102
        hp_turbine_comp = turbine_power * -1.34102
        air_comp_base_cost = math.exp(9.1553 + 0.63 * math.log(hp_air_comp))
        fuel_comp_base_cost = math.exp(9.1553 + 0.63 * math.log(hp_fuel_comp))
        turbine_base_cost = 1618.8 * ((hp_turbine_comp) ** 0.7951)

        MOC_air_comp = 1
        MOC_fuel_comp = 1
        MOC_turbine = 1

        BM_coefficient = 2.15

        BMC_air_comp = air_comp_base_cost * (MOC_air_comp + BM_coefficient - 1)
        BMC_fuel_comp = fuel_comp_base_cost * (MOC_fuel_comp + BM_coefficient - 1)
        BMC_turbine = turbine_base_cost * (MOC_turbine + BM_coefficient - 1)

        CE_air_comp = 567
        CE_fuel_comp = 567
        CE_turbine = 390
        CE_current = 603.1

        adj_BMC_air_comp = BMC_air_comp * (CE_current / CE_air_comp)
        adj_BMC_fuel_comp = BMC_fuel_comp * (CE_current / CE_fuel_comp)
        adj_BMC_turbine = BMC_turbine * (CE_current / CE_turbine)

        comb_utilities_cost = (fuel_comp_power + air_comp_power) * 0.12 * 8760  # USD/year
        comb_capital_cost = adj_BMC_air_comp + adj_BMC_fuel_comp + adj_BMC_turbine
        comb_j_cost = (comb_capital_cost / 3) + comb_utilities_cost
        #print(adj_BMC_air_comp, adj_BMC_fuel_comp, adj_BMC_turbine)
        # NOx emissions
        ma = compressed_air_needed / 3600
        fuel_mass_flow = (methane_feed_massflow + ethane_feed_massflow + ethene_feed_massflow + propane_feed_massflow
                          + propene_feed_massflow + butane_feed_massflow) / 3600
        q = fuel_mass_flow / ma
        NOx_ppmv = 18.1 * (OP ** 1.42) * (ma ** 0.3) * (q ** 0.72)  # ppmv
        # ppm = ppmv * density of mixture / density of species
        NOx_ppm = NOx_ppmv * 0.64035

        aspen_results_dict = {}
        aspen_results_dict['A_ref'] = A_ref
        aspen_results_dict['A_L'] = A_L
        aspen_results_dict['A_an'] = A_an
        aspen_results_dict['PF'] = PF
        aspen_results_dict['D_ref'] = D_ref
        aspen_results_dict['D_L'] = D_L
        aspen_results_dict['L_L'] = L_L
        aspen_results_dict['L_PZ'] = L_PZ
        aspen_results_dict['L_SZ'] = L_SZ
        aspen_results_dict['L_DZ'] = L_DZ
        aspen_results_dict['D_int'] = D_int
        aspen_results_dict['CSTR_V'] = CSTR_V
        aspen_results_dict['PFR_L'] = PFR_L
        aspen_results_dict['PFR_D'] = PFR_D
        aspen_results_dict['combustor_inlet_mass_flow'] = combustor_inlet_mass_flow
        aspen_results_dict['operating_pressure'] = operating_pressure
        aspen_results_dict['inlet_temperature'] = inlet_temperature
        aspen_results_dict['outlet_temperature'] = outlet_temperature
        aspen_results_dict['CO_ppm'] = CO_ppm
        aspen_results_dict['turbine_power'] = turbine_power
        aspen_results_dict['fuel_comp_power'] = fuel_comp_power
        aspen_results_dict['air_comp_power'] = air_comp_power
        aspen_results_dict['net_power'] = net_power
        aspen_results_dict['Base cost for air comp'] = air_comp_base_cost
        aspen_results_dict['Base cost for fuel comp'] = fuel_comp_base_cost
        aspen_results_dict['Base cost for turbine'] = turbine_base_cost
        aspen_results_dict['BM cost for air comp'] = BMC_air_comp
        aspen_results_dict['BM cost for fuel comp'] = BMC_fuel_comp
        aspen_results_dict['BM cost for turbine'] = BMC_turbine
        aspen_results_dict['adjusted BM cost for air comp'] = adj_BMC_air_comp
        aspen_results_dict['adjusted BM cost for fuel comp'] = adj_BMC_fuel_comp
        aspen_results_dict['adjusted BM cost for turbine'] = adj_BMC_turbine
        aspen_results_dict['utilities cost in USD/year'] = comb_utilities_cost
        aspen_results_dict['capital cost in USD'] = comb_capital_cost
        aspen_results_dict['capital cost in USD per year'] = comb_capital_cost / 3
        aspen_results_dict['J cost'] = comb_j_cost
        aspen_results_dict['OP from python'] = OP
        aspen_results_dict['OER from python'] = OER
        aspen_results_dict['combustion efficiency'] = eff
        aspen_results_dict['T3'] = T3
        aspen_results_dict['P3'] = P3
        aspen_results_dict['T4 (estimated)'] = T4
        aspen_results_dict['NOx ppm'] = NOx_ppm
        all_results_list = []
        all_results_list.append(aspen_results_dict)
        self.comb_j_cost = comb_j_cost
        self.D_int = D_int
        self.NOx_ppm = NOx_ppm
        self.CO_ppm = CO_ppm
        return comb_capital_cost, comb_utilities_cost, D_int, NOx_ppm, CO_ppm, turbine_power

    def comb_result(self):
        objective = self.comb_j_cost
        #constraints
        if self.D_int <= 0:
            objective = 1e20
        if self.CO_ppm > 0.00011:
            objective = 1e20
        if self.NOx_ppm > 200:
            objective = 1e20
        return objective

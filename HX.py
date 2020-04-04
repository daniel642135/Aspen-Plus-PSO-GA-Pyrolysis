import math
import ht
import thermo
from thermo import *
import fluids

def heat_exchanger_sizing(Thi,Tho,Tci,Tco,Q,dext,dint,hsf,htf,REs,Prs,ks,REt,Prt,kt,k,tubes_length):
    R = (Thi - Tho) / (Tco - Tci)
    P = (Tco - Tci) / (Thi - Tci)
    Xp = 0.9
    W = (R + 1 + (((R ** 2) + 1) ** 0.5) - (2 * R * Xp)) / (R + 1 + (((R ** 2) + 1) ** 0.5) - (2 * Xp))
    num_shell = (math.log((1 - (R * P)) / (1 - P))) / (math.log(W))
    num_shell2 = math.ceil(num_shell)

    N = num_shell2

    Ft = ht.F_LMTD_Fakheri(Tci, Tco, Thi, Tho, shells=N)
    LMTempDiff = ht.LMTD(Thi=Thi, Tho=Tho, Tci=Tci, Tco=Tco)
    UA = Q/(Ft*LMTempDiff)
    shell_Nu = ht.conv_external.Nu_cylinder_Sanitjai_Goldstein(Re=REs, Pr=Prs)
    hshell = (shell_Nu * ks)/dext
    friction_factor_darcy = (1.82 * math.log10(REt)-1.64)**(-2)
    tube_nu = ht.conv_internal.turbulent_Gnielinski(Re=REt, Pr=Prt, fd=friction_factor_darcy)
    htube = (tube_nu * kt)/dint
    invU = (1/hshell)+ (1/hsf) + (dext/(2*k))*(math.log(dext/dint)) + ((dext/dint)/htf) + ((dext/dint)/htube)
    U = 1/invU
    A = UA/U
    number_of_tubes = A/(tubes_length*3.14*dint)
    return {'UA':UA,'U':U, 'A':A, 'Ft' : Ft, 'LMTD': LMTempDiff, 'Shell number': N,'Number of tubes': number_of_tubes, 'tubes_length':tubes_length}

def heat_exchanger_sizing2(Thi,Tho,Tci,Tco,Q,dint,N_tubes,U):
    R = (Thi - Tho) / (Tco - Tci)
    P = (Tco - Tci) / (Thi - Tci)
    Xp = 0.9
    W = (R + 1 + (((R ** 2) + 1) ** 0.5) - (2 * R * Xp)) / (R + 1 + (((R ** 2) + 1) ** 0.5) - (2 * Xp))
    num_shell = (math.log((1 - (R * P)) / (1 - P))) / (math.log(W))
    num_shell2 = math.ceil(num_shell)

    N = num_shell2

    Ft = ht.F_LMTD_Fakheri(Tci=Tci, Tco=Tco, Thi=Thi, Tho=Tho, shells=N)
    LMTempDiff = ht.LMTD(Thi=Thi, Tho=Tho, Tci=Tci, Tco=Tco)
    UA = Q/(Ft*LMTempDiff)
    A = UA/U
    tubes_length = A/(N_tubes*3.14*dint)
    return {'UA':UA, 'U':U, 'A':A, 'Ft' : Ft, 'LMTD': LMTempDiff, 'Shell number': N,'Number of tubes': N_tubes, 'tubes_length':tubes_length}

def heat_exchanger_costs(resultsdict, shell_side_pressure, MOC_factor_a, MOC_factor_b, hX_type):
    area_in_ft2 = resultsdict['A']
    tube_length = resultsdict['tubes_length']
    if hX_type == 'Floating head':
        base_cost = math.exp(12.0310 - (0.8709 * math.log(area_in_ft2)) + (0.09005 * ((math.log(area_in_ft2)) ** 2)))
    elif hX_type == 'Fixed head':
        base_cost = math.exp(11.4185 - (0.9228 * math.log(area_in_ft2)) + (0.09861 * ((math.log(area_in_ft2)) ** 2)))
    elif hX_type == 'U-tube':
        base_cost = math.exp(11.5510 - (0.9186 * math.log(area_in_ft2)) + (0.09790 * ((math.log(area_in_ft2)) ** 2)))
    elif hX_type == 'Kettle vap':
        base_cost = math.exp(12.3310 - (0.8709 * math.log(area_in_ft2)) + (0.09005 * ((math.log(area_in_ft2)) ** 2)))
    else:
        return 'type error'

    if tube_length <= 8:
        tube_length_correction = 1.25
    elif tube_length <= 12:
        tube_length_correction = 1.12
    elif tube_length <= 16:
        tube_length_correction = 1.05
    elif tube_length <= 20:
        tube_length_correction = 1
    else:
        return 'length error'

    MOC_factor = MOC_factor_a + ((area_in_ft2 / 100) ** (MOC_factor_b))
    pressure_correction_factor = 0.9803 + 0.018 * (shell_side_pressure / 100) + 0.0017 * (
                ((shell_side_pressure / 100)) ** 2)

    fob_cost = MOC_factor * pressure_correction_factor * tube_length_correction * base_cost
    BM_HX = 3.17
    BM_cost = fob_cost * BM_HX
    inflation_adjusted_cost = BM_cost * 603.1 / 567

    new_results_dict = resultsdict
    new_results_dict['inflation adjusted costs'] = inflation_adjusted_cost
    new_results_dict['MOC factor'] = MOC_factor
    new_results_dict['Pressure correction factor'] = pressure_correction_factor
    new_results_dict['fob_cost'] = fob_cost
    new_results_dict['BM_cost'] = BM_cost
    return new_results_dict
#sample sizing. shell side is cooling water and tube side is hydrocarbon gases

#please read the following temperatures from Aspen.
#It does not matter the units, as long as you are consistent throughout the codes
#in cases where units are implied, I have indicated them as comments

Thi = 932 #F
Tho = 120.2 #F
Tci = 77 #F
Tco = 118.4 #F
shell_mat_velocity = 2 #m/s value by heuristics
tube_mat_velocity = 30 #m/s value by heuristics #initial appropriate guess

shell_average_temp_F = (Tci + Tco) /2
shell_average_temp_K = (shell_average_temp_F +459.67)*(5/9)
shell_mat_density = thermo.chemical.Chemical('water', T=shell_average_temp_K, P=101325).rho #kg/m3
dext_m = 0.01905 # m by heuristics where dext = 3/4 inch pipe
shell_mat_viscosity = thermo.chemical.Chemical('water', T=shell_average_temp_K, P=101325).mu #Pa/s
REs = shell_mat_density * shell_mat_velocity * dext_m / shell_mat_viscosity #water

Prs = thermo.chemical.Chemical('water', T=shell_average_temp_K, P=101325).Pr
ks = (thermo.chemical.Chemical('water', T=shell_average_temp_K, P=101325).k)*0.578175
# from W/m-K to Btu/h-ft-F

tube_average_temp_F = (Thi+Tho)/2
tube_average_temp_K = (tube_average_temp_F +459.67)*(5/9)
tube_mat_density = (0.774943 + 2.604311)/2 #kg/m3 from aspen. average between inlet and outlet
dint_m = 0.0157 # m by heuristics where dext = 3/4 inch pipe and material standard is BWG 16
tube_mat_viscosity = thermo.chemical.Chemical('styrene', T=tube_average_temp_K, P=101325).mu #Pa/s
#based on average temperature to estimate property of most abundant species in stream

REt = tube_mat_density * tube_mat_velocity * dint_m / tube_mat_viscosity #hydrocarbon gases
kt = (thermo.chemical.Chemical('styrene', T=tube_average_temp_K, P=101325).k)*0.578175
# from W/m/K to Btu/h-ft-F
#based on average temperature to estimate property of most abundant species in stream
Prt = 0.71 #common for gases

dint_ft = dint_m *3.28
dext_ft = dext_m *3.28

average_volumetric_flow_rate = ((65275.49098+219368.0787)/2 )*1.67*(10**(-5))   #should get from Aspen
tube_cross_sectional_area_total = average_volumetric_flow_rate/tube_mat_velocity
tubes_number = tube_cross_sectional_area_total/((dint_m**2)*(3.14/4))
length_of_tubes = 20

results1 = heat_exchanger_sizing(Thi = Thi,# F
                      Tho= Tho,# F
                      Tci = Tci,# F
                      Tco= Tco, # F
                      Q=10639718, #Btu/hr
                      dext=dext_ft, #ft
                      dint=dint_ft,#ft
                      hsf=1938, #Btu/ft2-hr-F
                      htf=880,#Btu/ft2-hr-F
                      REs=REs,#
                      Prs=Prs,
                      ks=ks, #Btu/h-ft-F
                      REt=REt,
                      Prt = Prt,
                      kt= kt, #Btu/h-ft-F
                      k= 9.251,#Btu/h-ft-F
                        tubes_length = length_of_tubes)  #ft

results2 = heat_exchanger_costs (resultsdict=results1,shell_side_pressure= 14.7 ,MOC_factor_a = 0,MOC_factor_b=0,hX_type='Floating head')
results3 = results2
if results3['Number of tubes'] <= 20:
    results3['Number of tubes'] = 20
elif results3['Number of tubes'] <= 68:
    results3['Number of tubes'] = 68
elif results3['Number of tubes'] <= 116:
    results3['Number of tubes'] = 116
elif results3['Number of tubes'] <= 246:
    results3['Number of tubes'] = 246
elif results3['Number of tubes'] <= 370:
    results3['Number of tubes'] = 370
elif results3['Number of tubes'] <= 600:
    results3['Number of tubes'] = 600
elif results3['Number of tubes'] <= 886:
    results3['Number of tubes'] = 886
else:
    print('error!!!')
results3['A'] = length_of_tubes * results2['Number of tubes'] *3.14 * dint_ft
results3['U'] = results2['UA']/results2['A']
results4 = heat_exchanger_sizing2(Thi =Thi, Tho=Tho, Tci=Tci, Tco=Tco, Q=10639718, dint=dint_ft, N_tubes=results3['Number of tubes'], U=results3['U'])
results5 = heat_exchanger_costs(resultsdict=results4,shell_side_pressure= 14.7 ,MOC_factor_a = 0,MOC_factor_b=0,hX_type='Floating head')
results5['tube velocity'] = average_volumetric_flow_rate/(results5['Number of tubes']*((dint_m**2)*(3.14/4)))
# print(results5)

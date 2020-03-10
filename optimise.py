from aspenplus.aspen_link import init_aspen
import math
# def test():
#     aspen = init_aspen()
#     temp = aspen.Tree.FindNode(r"\Data\Blocks\PREHEAT\Input\TEMP").Value
#     print('Initial  = ' + str(temp))
#     tempS1 = aspen.Tree.FindNode(r"\Data\Streams\S1\Output\TEMP_OUT\NC").Value
#     print('Input S1  = ' + str(temp))
#     temp = 350
#     aspen.Tree.FindNode(r"\Data\Blocks\PREHEAT\Input\TEMP").Value = temp
#     aspen.Engine.Run2()
#     tempS1 = aspen.Tree.FindNode(r"\Data\Streams\S1\Output\TEMP_OUT\NC").Value
#     print('Input S1  = ' + str(tempS1))
#     aspen.AutoSave()
#     return
#
# test()
#
#
# def test2():
#     aspen = init_aspen()
#     tempS1 = aspen.Tree.FindNode(r"\Data\Streams\S1\Output\TEMP_OUT\NC").Value
#     print('Input S1  = ' + str(tempS1))
#
#     return
#
# test2()


# def test():
#     aspen = init_aspen()
#     plastictemp = aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TEMP\NC").Value
#     print('Input plastic waste  = ' + str(plastictemp))
#     plastictemp = 20
#     aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TEMP\NC").Value = plastictemp
#     aspen.Engine.Run2()
#     print('Input plastic waste  = ' + str(plastictemp))
#     return


#corr is boolean
def vesselcost(L, ID, density, Po, To, corr):

    if Po <= 5:
        Pd = 10
    elif Po <= 1000:
        Pd = math.exp(0.60608 + 0.91615*math.log(Po)+0.0015655*(math.log(Po))**2)
    else:
        Pd = 1.1*Po

    Td = To + 50 # temperature is in oF

    if corr == False:
        if Td <= 650:
            S = 13750 #Carbon steel SA-285
            Fm = 1
        elif Td <= 750:
            S = 15000 #low alloy carbon steel SA387B
            Fm = 1.2
        elif Td <= 800:
            S = 14750
            Fm = 1.2
        elif Td <= 850:
            S = 14200
            Fm = 1.2
        elif Td <= 900:
            S = 13100
            Fm = 1.2
        else:
            S = 20000 #SS316 max temp is 1500 oF
            Fm = 2.1
    else:
        S = 16700 #SS316L
        Fm = 2.1

    E = 0.85
    tp = Pd*ID/(2*S*E-1.2*Pd)
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

    Do = ID + 2*1.25
    tw = (0.22*(Do + 18)*L**2)/(S*(Do**2))
    tpbtm = tp + tw
    tv = (tpbtm + tp)/2
    ts = tv + 0.125
    if ts <= 0.5:
        n = ts/0.0625
        n = math.ceil(n)
        ts = n*0.0625
    elif ts <= 2:
        n = ts/0.125
        n = math.ceil(n)
        ts = n*0.125
    elif ts <= 3:
        n = ts/0.25
        n = math.ceil(n)
        ts = n*0.25

    W = math.pi*(ID + ts)*(L + 0.8*ID)*ts*density
    Cv = math.exp(7.1390 + 0.18255*(math.log(W))+0.02297*(math.log(W))**2)   #CE index = 567 (2013)  # 4200< W < 1,000,000 lb
    Cpl = 410 * ((ID/12)**0.7396) * ((L/12)**0.70684)   # 3 < ID < 21 ft and 12 < L < 40 ft
    Cp = Fm*Cv + Cpl
    print(Cp)
    return

vesselcost(L = 409, ID = 136, density = 0.284, Po = 0, To = 932, corr = False)



from aspenplus.aspen_link import init_aspen

def test():
    aspen = init_aspen()
    print("n2massflow = "+str(aspen.Tree.FindNode(r"\Data\Streams\N2\Input\FLOW\MIXED\NITROGEN").Value))
    print("duty = "+str(aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Output\QNET").Value))
    print("flow = "+str(aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MASSFLMX\$TOTAL").Value))
    aspen.Tree.FindNode(r"\Data\Streams\N2\Input\FLOW\MIXED\NITROGEN").Value = 4000
    aspen.Engine.Run2()
    print("n2massflow = " + str(aspen.Tree.FindNode(r"\Data\Streams\N2\Input\TOTAL\MIXED").Value))
    print("duty = " + str(aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Output\QNET").Value))
    print("flow = " + str(aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\MASSFLMX\$TOTAL").Value))

test()

def test2():
    aspen = init_aspen()
    print("temp = "+str(aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Input\TEMP").Value))
    print("duty = "+str(aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Output\QNET").Value))
    aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Input\TEMP").Value = 1000
    aspen.Engine.Run2()
    print("temp = " + str(aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Input\TEMP").Value))
    print("duty = " + str(aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Output\QNET").Value))

#test2()

def test3():
    aspen = init_aspen()
    print("n2flow = "+str(aspen.Tree.FindNode(r"\Data\Streams\N2FLUID\Input\TOTAL\MIXED").Value))
    print("massflow = "+str(aspen.Tree.FindNode(r"\Data\Streams\N2AFHEAT\Output\MASSFLMX_GAS").Value))
    print("duty = " + str(aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Output\QNET").Value))
    aspen.Tree.FindNode(r"\Data\Streams\N2FLUID\Input\TOTAL\MIXED").Value = 2000
    aspen.Engine.Run2()
    print("n2flow = " + str(aspen.Tree.FindNode(r"\Data\Streams\N2FLUID\Input\TOTAL\MIXED").Value))
    print("massflow = " + str(aspen.Tree.FindNode(r"\Data\Streams\N2AFHEAT\Output\MASSFLMX_GAS").Value))
    print("duty = " + str(aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Output\QNET").Value))

#test3()
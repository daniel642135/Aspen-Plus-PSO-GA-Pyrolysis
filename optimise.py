from aspenplus.aspen_link import init_aspen

def test():
    aspen = init_aspen()
    plastictemp = aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TEMP\NC").Value
    print('Input plastic waste  = ' + str(plastictemp))
    return plastictemp

test()



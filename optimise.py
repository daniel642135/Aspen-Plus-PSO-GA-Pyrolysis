from aspenplus.aspen_link import init_aspen

def test():
    aspen = init_aspen()
    plastictemp = aspen.Tree.FindNode('\Data\Streams\PWASTEW\Input\TEMP\NC').Value
    print 'Input plastic waste  = {0}'.format(plastictemp)





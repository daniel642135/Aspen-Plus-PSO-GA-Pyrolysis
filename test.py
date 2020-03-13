from aspenplus.aspen_link import init_aspen
aspen = init_aspen()
reactortemp = self.aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\TEMP").Value

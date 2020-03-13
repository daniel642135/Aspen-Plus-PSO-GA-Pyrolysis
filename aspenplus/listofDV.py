




# dechlorination reactor
# input stream values
pwastemassflow = aspen.Tree.FindNode(r"\Data\Streams\PWASTE\Input\TOTFLOW\NC").Value
n2massflow = aspen.Tree.FindNode(r"\Data\Streams\N2\Input\TOTAL\MIXED")
# reaction kinetics
coefpvc = aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\COEF\1\PVC NC")
coefhcl = aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\COEF1\1\HCL MIXED")
coefpa = aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\COEF1\1\PA NC")
dechtime = 3
#important to change 3 temp
dechtemp = aspen.Tree.FindNode(r"\Data\Blocks\DECH\Input\TEMP")
dechheatertemp = aspen.Tree.FindNode(r"\Data\Blocks\PREHEAT\Input\TEMP")
n2heatertemp = aspen.Tree.FindNode(r"\Data\Blocks\N2HETER2\Input\TEMP")
# energy and sizing calculation
dechheaterduty = aspen.Tree.FindNode(r"\Data\Blocks\PREHEAT\Output\QNET")
n2heaterduty = aspen.Tree.FindNode(r"\Data\Blocks\N2HETER2\Output\QNET")
dechduty = aspen.Tree.FindNode(r"\Data\Blocks\DECH\Output\QNET") #the result shows that it is exothermic, need to check

# HCl scrubber
# input stream values
hclscrubbertemp = aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Input\TEMP")
NAOHwaterin = aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\WATER")
NAOHNAin = aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\NA+")
NAOHCLin = aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Input\FLOW\MIXED\OH-")
# optimization
numofstage = aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\NSTAGE")
numofstage2 = aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\FEED_STAGE\N2HCLC") #need to change in conjuction
# (optional) for converge
stage1tempest = aspen.Tree.FindNode(r"\Data\Blocks\SCRUB\Input\TEMP_EST\1")
# target
HCLmolfrac = aspen.Tree.FindNode(r"\Data\Streams\CLEANGAS\Output\MASSFLOW\MIXED\HCL")
# energy and sizing calculation
hclscrubbercoolerduty = aspen.Tree.FindNode(r"\Data\Blocks\COOLER1\Output\QNET")
NAOHvolflow = aspen.Tree.FindNode(r"\Data\Streams\NAOHIN\Output\VOLFLMX2")
N2HCLCvolflow = aspen.Tree.FindNode(r"\Data\Streams\N2HCLC\Output\VOLFLMX2")

# pyrolysis reactor
# input stream
N2fluidizingflow = aspen.Tree.FindNode(r"\Data\Streams\N2FLUID\Input\FLOW\MIXED\NITROGEN")
# optimising
n2fluidheatertemp = aspen.Tree.FindNode(r"\Data\Blocks\N2HETER\Input\TEMP")
pyrotemp = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\TEMP")
pyrotime = 180
# reactant stoichio
coefhdpe1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF\1\HDPE NC")
coefldpe2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF\2\LDPE NC")
coefpp3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF\3\PP NC")
coefps4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF\4\PS NC")
coefpet5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF\5\PET NC")
coefpa6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF\6\PA NC")
# product stoichio
co1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\CO MIXED")
co21 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\CO2 MIXED")
methane1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\METHANE MIXED")
ethane1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\ETHANE MIXED")
ethene1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\ETHENE MIXED")
propane1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\PROPANE MIXED")
propene1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\PROPENE MIXED")
butane1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\BUTANE MIXED")
toulene1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\TOLUENE MIXED")
styrene1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\STYRENE MIXED")
ethylbe1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\ETHYL-BE MIXED")
c14h301 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\C14H30 MIXED")
c18h381 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\C18H38 MIXED")
c25h521 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\C25H52 MIXED")
char1 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\1\CHAR CISOLID")

co2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\CO MIXED")
co22 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\CO2 MIXED")
methane2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\METHANE MIXED")
ethane2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\ETHANE MIXED")
ethene2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\ETHENE MIXED")
propane2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\PROPANE MIXED")
propene2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\PROPENE MIXED")
butane2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\BUTANE MIXED")
toulene2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\TOLUENE MIXED")
styrene2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\STYRENE MIXED")
ethylbe2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\ETHYL-BE MIXED")
c14h302 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\C14H30 MIXED")
c18h382 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\C18H38 MIXED")
c25h522 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\C25H52 MIXED")
char2 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\2\CHAR CISOLID")

co3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\CO MIXED")
co23 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\CO2 MIXED")
methane3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\METHANE MIXED")
ethane3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\ETHANE MIXED")
ethene3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\ETHENE MIXED")
propane3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\PROPANE MIXED")
propene3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\PROPENE MIXED")
butane3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\BUTANE MIXED")
toulene3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\TOLUENE MIXED")
styrene3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\STYRENE MIXED")
ethylbe3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\ETHYL-BE MIXED")
c14h303 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\C14H30 MIXED")
c18h383 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\C18H38 MIXED")
c25h523 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\C25H52 MIXED")
char3 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\3\CHAR CISOLID")


co4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\CO MIXED")
co24 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\CO2 MIXED")
methane4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\METHANE MIXED")
ethane4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\ETHANE MIXED")
ethene4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\ETHENE MIXED")
propane4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\PROPANE MIXED")
propene4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\PROPENE MIXED")
butane4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\BUTANE MIXED")
toulene4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\TOLUENE MIXED")
styrene4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\STYRENE MIXED")
ethylbe4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\ETHYL-BE MIXED")
c14h304 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\C14H30 MIXED")
c18h384 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\C18H38 MIXED")
c25h524 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\C25H52 MIXED")
char4 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\4\CHAR CISOLID")

co5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\CO MIXED")
co25 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\CO2 MIXED")
methane5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\METHANE MIXED")
ethane5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\ETHANE MIXED")
ethene5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\ETHENE MIXED")
propane5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\PROPANE MIXED")
propene5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\PROPENE MIXED")
butane5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\BUTANE MIXED")
toulene5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\TOLUENE MIXED")
styrene5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\STYRENE MIXED")
ethylbe5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\ETHYL-BE MIXED")
c14h305 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\C14H30 MIXED")
c18h385 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\C18H38 MIXED")
c25h525 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\C25H52 MIXED")
char5 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\5\CHAR CISOLID")


co6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\CO MIXED")
co26 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\CO2 MIXED")
methane6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\METHANE MIXED")
ethane6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\ETHANE MIXED")
ethene6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\ETHENE MIXED")
propane6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\PROPANE MIXED")
propene6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\PROPENE MIXED")
butane6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\BUTANE MIXED")
toulene6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\TOLUENE MIXED")
styrene6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\STYRENE MIXED")
ethylbe6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\ETHYL-BE MIXED")
c14h306 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\C14H30 MIXED")
c18h386 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\C18H38 MIXED")
c25h526 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\C25H52 MIXED")
char6 = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Input\COEF1\6\CHAR CISOLID")
# target
# the target for the pyrolysis output should be the fixed since we would have 100% conversion (it is always the case?), hence just want to balance between cap and ops cost
# unless we can get the kinetics information of 3 k for each polymer
# energy and sizing calculation
pyroduty = aspen.Tree.FindNode(r"\Data\Blocks\PYRO\Output\QNET")
n2fluidheaterduty = aspen.Tree.FindNode(r"\Data\Blocks\N2HEATER\Output\QNET")
n2fluidvolflow = aspen.Tree.FindNode(r"\Data\Streams\N2AFHEAT\Output\VOLFLMX2")
# do we need to preheat the solids? if not just dump it into the fludizing reactor, same thing should apply to dechlorination
# cannot seems to get the volume flow of the solids entering pyro reactor

#cyclone
hotgasvolflow = aspen.Tree.FindNode(r"\Data\Streams\HOTGAS\Output\VOLFLMX2")

#distillation optimisation
# optimisation
# no of tray, inlet temp (feed tray)

# sizing and energy
vapcoolerduty = aspen.Tree.FindNode(r"\Data\Blocks\COOLER\Output\QNET")
# liquid and vapour volumetric flow rate to determine sizing of the column
# retrieve the heating and cooling duty


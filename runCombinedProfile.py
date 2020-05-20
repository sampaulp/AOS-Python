'''
Testing environment for the CombinedProfile class
'''

workDir = "D:\\sma\\99-others\\01-AOS\\Sampaul\\final\\Project-2\\" # set the working directory here

# set workdirectory
import os
os.chdir(workDir)

#>>>> for developing
import InputData
reload(InputData)

import ResultData
reload(ResultData)

import CombinedProfile
reload(CombinedProfile)

#<<<<

# show work directory
from Base import Base

# create HGirder object
from CombinedProfile import CombinedProfile
sys = CombinedProfile()

# create system
sys.createSystem()

# create step for a linear static analysis
sys.createStep(sys.LINEAR)

# create and run the job
sys.createAndRunJob()

# open database
sys.openDatabase(sys.LINEAR)

# do analysis
sys.analyzeResults()
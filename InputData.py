# ==============================================================================
# a class to handle the input parameters
# for the Combined profile
# ==============================================================================

from Base import Base
from math import sin
from math import cos
from math import radians as rad

class InputData(Base):
    # constructor
    def __init__(self):
        # uncomment the required combined profile(CP) here.
        #                                                  prjName, dh1, dw1, dt1, ds1, dh2, dw2, dt2, ds2, l
        prjName, dh1, dw1, dt1, ds1, dh2, dw2, dt2, ds2, l = "CP3", 120,  64, 6.3, 4.4,  80,  80, 9, 9, 3700
        #prjName, dh1, dw1, dt1, ds1, dh2, dw2, dt2, ds2, l = "CP2", 120, 64, 6.3, 4.4, 70, 70, 8, 8, 3700
        #prjName, dh1, dw1, dt1, ds1, dh2, dw2, dt2, ds2, l = "CP1", 120, 64, 6.3, 4.4, 60, 60, 7, 7, 3700

        # call the Base constructor
        Base.__init__(self)

        # geometry parameters
        self.prjName = prjName  			# name of the profile
        self.dh1     = dh1  				# Height of I-Profile
        self.dw1     = dw1  				# Breadth of I-Profile
        self.dt1     = dt1  				# Flange thickness of I-Profile
        self.ds1     = ds1  				# Web thickness of I-Profile
        self.dh2     = dh2  				# Height of T-Profile
        self.dw2     = dw2  				# Breadth of T-Profile
        self.dt2     = dt2  				# Flange thickness of T-Profile
        self.ds2     = ds2  				# Web thickness of T-Profile
        self.l       = l    				# length of the profile

        # material parameters
        self.matName = "Steel"				# Material name
        self.EMod    = 210000.  			# Young's modulus [N/mm^2]
        self.nue     = 0.3  				# Poisson ratio
        self.rho     = 7.8e-5  			    # density [N/mm^3]
        self.load    = 43.0  				# load in [kN]

        # model parameters
        # set mesh seed
        self.maxElement = int(1000)		    # maximum allowed elements in Abaqus student version
        self.iFSeed     = int(1)			# no of seeds on I-Flange
        self.iWSeed     = int(2)			# no of seeds on I-Web
        self.tFSeed     = int(1)			# no of seeds on I-Flange
        self.tWSeed     = int(2)            # no of seeds on I-Web
        self.cFSeed     = int(4)			# no of seeds on Connecting flange

        # no of seed along the length  
        self.lengthSeed = self.maxElement/(8*self.iFSeed+2*self.iWSeed+2*self.tFSeed+2*self.tWSeed+2*self.cFSeed)

        # step parameters
        self.LINEAR   = 0   # linear static calculation
        self.BUCKLING = 1   # stability analysis
        self.stepName = ("Linear", "Buckling")
        self.jobnames = (self.prjName + "-Linear", self.prjName + "-Buckling")
        self.stepType = self.LINEAR

        self.Check()        # check for possible geometrical errors
        self.calcHelpers()  # calculate helper variables

    # load the input data from a file
    def Load(self, filename):
        # calculate helper variables
        self.calcHelpers()

    # check the input data
    def Check(self):
        dmin = 0.1  # minimum length
        if self.dh2 < dmin:
            raise Exception("error: Invalid flange length for T section", self.dh2)
        elif self.ds2 < dmin:
            raise Exception("error: Invalid web length for T section", self.ds2)
        elif self.dw2 < dmin:
            raise Exception("error: Invalid flange breath for T section", self.dw2)
        elif (self.dt2 < dmin):
            raise Exception("error: Geometric parameters must be non-negative - invalid T section thickness : %8.4f",
                            self.dt2)
        elif (self.dt2 > self.dh2):
            raise Exception("error: Flange length must be greater than T section thickness", self.dt2, self.dh2)
        elif (self.dt2 > self.ds2):
            raise Exception("error: Web length must be greater than T section thickness", self.dt2, self.ds2)
        else:
            print"--------------error check on T-section successful:::::no errors found-----------------"
        if self.dh1 < dmin:
            raise Exception("error: Invalid flange length for I section", self.dh1)
        elif self.ds1 < dmin:
            raise Exception("error: Invalid web length for I section", self.ds1)
        elif self.dw1 < dmin:
            raise Exception("error: Invalid flange breath for I section", self.dw1)
        elif (self.dt1 < dmin):
            raise Exception("error: Geometric parameters must be non-negative - invalid I section thickness : %8.4f",
                            self.dt1)
        elif (self.dh1 < 2*self.dt1):
            raise Exception("error: Flange length must be greater than I section thickness", self.dt1, self.dh1)
        elif (self.ds1 > self.dt1):
            raise Exception("error: Web length must be greater than I section thickness", self.dt1, self.ds1)
        else:
            print"--------------error check on I-section successful:::::no errors found-----------------"

    # calculate helper variables
    def calcHelpers(self):
        # helper variables to locate the nodes
        self.x1_I = self.dh2 + self.dw1
        self.x2_I = self.dh2 + (self.dw1 / 2.)
        self.x3_I = self.dh2
        self.y1_I = self.dh1 - self.dt1
        self.x1_T = 0.
        self.y1_T = self.dh1 - self.dt1 + (self.dw2 / 2.)
        self.y2_T = self.dh1 - self.dt1
        self.y3_T = self.dh1 - self.dt1 - (self.dw2 / 2.)

        # helper variables to locate the midpoints between nodes
        self.ix1 =  (self.x1_I+self.x2_I)/2.
        self.ix2 =  (self.x2_I+self.x3_I)/2.
        self.ix3 =   self.x2_I
        self.iy1 =   self.y1_I
        self.iy2 =   self.y1_I/2.
        self.tx1 =  (self.x3_I+self.x1_T)/2.
        self.tx2 =   self.x1_T
        self.ty1 =  (self.y1_T+self.y2_T)/2.
        self.ty2 =   self.y2_T
        self.ty3 =  (self.y2_T+self.y3_T)/2.
        self.mz1 =   self.l/2.
        
        # helper variables to calculate the load
        self.p1   = self.load * 1.e3 / (self.l * (2 * (self.dw1 + self.dh2)))  # pressure

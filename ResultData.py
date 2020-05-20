# result class for CombinedProfile
# container for fiber nodes and reaction forces
# calculates maximum vertical displacements

from math import fabs
from Base import Base

class ResultData(Base):

    # initialize the attributes
    def __init__(self):
        Base.__init__(self)
        self.nodePos    = {}           # selected fiber nodes
        self.sumRFo     = [0.,0.,0.]   # sum of reaction forces
        self.nodeRFo    = {}           # reaction force on nodes
        self.nodeDisp   = {}           # displacements along the fiber
        self.maxU2Disp  = None         # maximum displacment for the SLS proof
        self.maxStress  = None         # maximum stress for the ULS proof
        self.elementX   = 0            # most critical element
        self.minBuckleEV= None         # minimal positive buckling value
                                       
        self.myOdb      = None         # reference to result odb
        self.myViewport = None         # viewport to show results

    # calculate the maximum vertical displacement along the fiber
    def getMaxDisp(self):
        max = 0.
        for label in self.nodePos:
            disp = self.nodeDis[label]
            # y
            if (fabs(disp[1]) > fabs(max)): max = disp[1]
        return max
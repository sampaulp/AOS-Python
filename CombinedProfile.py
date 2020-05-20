#=============================================================================
# Script to create the FE model and solve the Combined profile
#=============================================================================

from abaqus import *                # from the main library
from caeModules import *            # import the modules
from abaqusConstants import *       # constants we need
from math import fabs

# setup the logger
from Base import Base
from ResultData import ResultData

# forced reload for the developer step
import InputData                    # bind module to the symbol
reload(InputData)                   # reload in any case
from InputData import InputData     # standard import

class CombinedProfile(InputData, ResultData):
    # constructor
    def __init__(self):

        # call base Constructor
        InputData.__init__(self)
        ResultData.__init__(self)

        # create attributes
        self.myModel    = None
        self.mySketch   = None
        self.myPart     = None

    # create the system (geometry, material, properties,...)
    # except loads and BCs
    def createSystem(self):
        self.createModel()
        self.createSketch()
        self.createPart()
        self.createMaterials()
        self.createSections()
        self.assignSections()
        self.createMesh()
        self.createInstance()
        self.getFiberNodes()

    # create model
    def createModel(self):
        self.appendLog("> create model '%s'..." % self.prjName)
        try:
            del mdb[self.prjName]
        except:
            pass
        
        self.myModel = mdb.Model(name=self.prjName)

    # create a sketch
    def createSketch(self):
        self.appendLog("> create sketch '%s'..." % self.prjName)
        self.mySketch = self.myModel.ConstrainedSketch(name = self.prjName, sheetSize = 2*self.dh1)

        xyPoints = [ (-self.x1_I, self.y1_I), # node 1
                     (-self.x2_I, self.y1_I), # node 2
                     (-self.x3_I, self.y1_I), # node 3
                     (-self.x1_I,0),          # node 4  
                     (-self.x2_I,0),          # node 5
                     (-self.x3_I,0),          # node 6
                     (0,self.y1_T),           # node 7
                     (0,self.y2_T),           # node 8
                     (0,self.y3_T),           # node 9
                     (0,self.y1_T),           # node 10
                     (0,self.y2_T),           # node 11
                     (0,self.y3_T),           # node 12
                     ( self.x3_I,self.y1_I),  # node 13
                     ( self.x2_I,self.y1_I),  # node 14
                     ( self.x1_I,self.y1_I),  # node 15
                     ( self.x3_I,0),          # node 16
                     ( self.x2_I,0),          # node 17
                     ( self.x1_I,0)]          # node 18

        #create the lines
        self.mySketch.Line(point1=xyPoints[0] , point2=xyPoints[1]) 
        self.mySketch.Line(point1=xyPoints[2] , point2=xyPoints[1]) 
        self.mySketch.Line(point1=xyPoints[7] , point2=xyPoints[2]) 
        self.mySketch.Line(point1=xyPoints[7], point2=xyPoints[12]) 
        self.mySketch.Line(point1=xyPoints[12], point2=xyPoints[13])
        self.mySketch.Line(point1=xyPoints[13], point2=xyPoints[14])
        self.mySketch.Line(point1=xyPoints[1] , point2=xyPoints[4]) 
        self.mySketch.Line(point1=xyPoints[6] , point2=xyPoints[7]) 
        self.mySketch.Line(point1=xyPoints[7] , point2=xyPoints[8])
        self.mySketch.Line(point1=xyPoints[13], point2=xyPoints[16])
        self.mySketch.Line(point1=xyPoints[17], point2=xyPoints[16])
        self.mySketch.Line(point1=xyPoints[16], point2=xyPoints[15])
        self.mySketch.Line(point1=xyPoints[15], point2=xyPoints[5])
        self.mySketch.Line(point1=xyPoints[5] , point2=xyPoints[4])
        self.mySketch.Line(point1=xyPoints[4] , point2=xyPoints[3]) 

    # create the part
    def createPart(self):
        self.appendLog("> create part '%s'..." % self.prjName)
        self.myPart = self.myModel.Part(name = self.prjName)
        self.myPart.BaseShellExtrude(sketch = self.mySketch,
                                     depth = self.l)

    # create the materials
    def createMaterials(self):
        self.appendLog("> create material '%s'..." % self.matName)
        myMaterial = self.myModel.Material(name = self.matName)
        myMaterial.Elastic(table=( (self.EMod,self.nue) ,))
        myMaterial.Density(table=((self.rho,),))

    # create section
    def createSections(self):
        self.appendLog("> create sections...")
        self.myModel.HomogeneousShellSection(name= self.prjName+"-I-Section-Flange",
                                             material=self.matName,
                                             thickness=self.dt1)
        self.myModel.HomogeneousShellSection(name= self.prjName+"-I-Section-Web",
                                             material=self.matName,
                                             thickness=self.ds1)
        self.myModel.HomogeneousShellSection(name= self.prjName+"-T-Section",
                                             material=self.matName,
                                             thickness=self.dt2)

    # assign sections
    def assignSections(self):
        self.appendLog("> assign sections...")

        # I-Section flange assignment
        self.flangeFacesI = self.myPart.faces.findAt(
            ( (-self.ix1, self.iy1, self.mz1),),   # node  1 -  2
            ( (-self.ix2, self.iy1, self.mz1),),   # node  2 -  3
            ( (-self.ix1,        0, self.mz1),),   # node  4 -  5
            ( (-self.ix2,        0, self.mz1),),   # node  5 -  6
            ( ( self.ix1, self.iy1, self.mz1),),   # node  14 -  15
            ( ( self.ix2, self.iy1, self.mz1),),   # node  13 -  14
            ( ( self.ix1,        0, self.mz1),),   # node  17 -  18
            ( ( self.ix2,        0, self.mz1),),   # node  16 -  17
            ( (        0,        0, self.mz1),),)  # connecting flange

        region = regionToolset.Region(faces=self.flangeFacesI)
        self.myPart.SectionAssignment(region=region,
                                      sectionName= self.prjName + "-I-Section-Flange")

        # I-Section web assignment
        self.webFacesI = self.myPart.faces.findAt(
            ( (-self.ix3, self.iy2, self.mz1),),    # node  2 -  5
            ( ( self.ix3, self.iy2, self.mz1),), )  # node 14 - 17

        region = regionToolset.Region(faces=self.webFacesI)
        self.myPart.SectionAssignment(region=region,
                                      sectionName= self.prjName + "-I-Section-Web")

        # T-Section assignment
        self.facesT = self.myPart.faces.findAt(
            ( (-self.tx1, self.ty2, self.mz1),),    # nodes 3 to 8
            ( (-self.tx2, self.ty1, self.mz1),),    # node  7 to 8
            ( (-self.tx2, self.ty3, self.mz1),),    # node  8 to 9
            ( ( self.tx2, self.ty1, self.mz1),),    # node  10 to 
            ( ( self.tx2, self.ty3, self.mz1),),    # node  11 to 
            ( ( self.tx1, self.ty2, self.mz1),), )  # nodes 13 to 
        
        region = regionToolset.Region(faces=self.facesT)
        self.myPart.SectionAssignment(region=region,
                                      sectionName= self.prjName + "-T-Section")

    # create the mesh on the part
    def createMesh(self):
        self.appendLog("> create mesh on part...")

        # Element type selection
        elemType1 = mesh.ElemType(elemCode=S4R)
        elemType2 = mesh.ElemType(elemCode=S3)
        # assign the element types
        regions   = (self.flangeFacesI, self.webFacesI, self.facesT)
        self.myPart.setElementType(regions=regions,
                                   elemTypes=(elemType1, elemType2))

        # assign the seeds
        # I-flange
        select = self.myPart.edges.findAt(
            ((-self.ix1, self.iy1,      0),),
            ((-self.ix2, self.iy1,      0),),
            ((-self.ix1,        0,      0),),
            ((-self.ix2,        0,      0),),
            (( self.ix1, self.iy1,      0),),
            (( self.ix2, self.iy1,      0),),
            (( self.ix1,        0,      0),),
            (( self.ix2,        0,      0),),
            ((-self.ix1, self.iy1, self.l),),
            ((-self.ix2, self.iy1, self.l),),
            ((-self.ix1,        0, self.l),),
            ((-self.ix2,        0, self.l),),
            (( self.ix1, self.iy1, self.l),),
            (( self.ix2, self.iy1, self.l),),
            (( self.ix1,        0, self.l),),
            (( self.ix2,        0, self.l),),
        )
        
        self.myPart.seedEdgeByNumber(edges=select,
                                number=self.iFSeed)

        # I-Web
        select = self.myPart.edges.findAt(
            ((-self.ix3, self.iy2,      0),),
            (( self.ix3, self.iy2,      0),),
            ((        0,        0,      0),),
            ((-self.ix3, self.iy2, self.l),),
            (( self.ix3, self.iy2, self.l),),
            ((        0,        0, self.l),),
        )

        self.myPart.seedEdgeByNumber(edges=select,
                                number=self.iWSeed)

        # T-Web
        select = self.myPart.edges.findAt(
            ((-self.tx1, self.ty2,      0),),
            ((-self.tx1, self.ty2, self.l),),
            (( self.tx1, self.ty2,      0),),
            (( self.tx1, self.ty2, self.l),),
        )
        
        self.myPart.seedEdgeByNumber(edges=select,
                                number=self.tWSeed)

        # T-Flange
        select = self.myPart.edges.findAt(
            ((-self.tx2, self.ty1,      0),),
            ((-self.tx2, self.ty3,      0),),
            ((-self.tx2, self.ty1, self.l),),
            ((-self.tx2, self.ty3, self.l),),
            (( self.tx2, self.ty1,      0),),
            (( self.tx2, self.ty3,      0),),
            (( self.tx2, self.ty1, self.l),),
            (( self.tx2, self.ty3, self.l),),
        )
        
        self.myPart.seedEdgeByNumber(edges=select,
                                number=self.tFSeed)
        
        # Connecting-Flange
        select = self.myPart.edges.findAt(
            (( 0, 0,      0),),
            (( 0, 0, self.l),),
        )
        
        self.myPart.seedEdgeByNumber(edges=select,
                                number=self.cFSeed)

        # Length seed
        select = self.myPart.edges.findAt(
            ((-self.x1_I, self.y1_I, self.l/2.),),
            ((-self.x2_I, self.y1_I, self.l/2.),),
            ((-self.x1_I,         0, self.l/2.),),
            ((-self.x2_I,         0, self.l/2.),),
            ((-self.x1_T, self.y1_T, self.l/2.),),
            ((-self.x1_T, self.y2_T, self.l/2.),),
            ((-self.x1_T, self.y3_T, self.l/2.),),
            (( self.x1_T, self.y1_T, self.l/2.),),
            (( self.x1_T, self.y2_T, self.l/2.),),
            (( self.x1_T, self.y3_T, self.l/2.),),
            (( self.x2_I, self.y1_I, self.l/2.),),
            (( self.x1_I, self.y1_I, self.l/2.),),
            (( self.x2_I,         0, self.l/2.),),
            (( self.x1_I,         0, self.l/2.),),
        )      
                                        
        self.myPart.seedEdgeByNumber(edges=select,
                                number=self.lengthSeed)
        
        self.appendLog("> No of seeds...")
        self.appendLog("  I-flange seed........: %d" % self.iFSeed)
        self.appendLog("  I-web seed...........: %d" % self.iWSeed)
        self.appendLog("  T-flange seed........: %d" % self.tFSeed)
        self.appendLog("  T-web seed...........: %d" % self.tWSeed)
        self.appendLog("  Length seed..........: %d" % self.lengthSeed)

        # create mesh
        self.myPart.generateMesh()

        # print summary
        self.appendLog(">  %4d elements created." % len(self.myPart.elements))
        self.appendLog(">  %4d nodes created." % len(self.myPart.nodes))

    # create instance
    def createInstance(self):
        self.appendLog("> create instance...")
        
        self.myInstance = self.myModel.rootAssembly.Instance(
            name=self.prjName,
            part=self.myPart,
            dependent=ON)

    # select fiber nodes, nodes for deformation analysis
    def getFiberNodes(self):
        self.appendLog("> select fiber nodes...")

        # over all nodes
        for node in self.myPart.nodes:

            # calculate distance from fiber line
            dist = sqrt((node.coordinates[0] + self.x1_I)**2
                      + (node.coordinates[1] +         0)**2)
            if dist > 1.: continue

            self.nodePos[node.label] = node.coordinates

        # print fiber nodes
        self.appendLog("> %d fiber nodes:" % len(self.nodePos))
        self.appendLog("--no ---------x ---------y ---------z")
        for label in self.nodePos:
            node = self.nodePos[label]
            self.appendLog("%4d %10.2f %10.2f %10.2f" %
                           (label,node[0],node[1],node[2]))

    def createStep(self,stepType):
        self.stepType = stepType
        self.appendLog("> create step '%s'..." % self.stepName[self.stepType])

        # delete old step from step container
        try:
            del self.myModel.steps[self.stepName[self.stepType]]
        except:
            pass

        # create data for the linear step
        if self.stepType == self.LINEAR:
            self.myModel.StaticStep(name=self.stepName[self.stepType],
                                    previous='Initial')
            self.createBCs()
            self.createLoads()

    # create BCs
    def createBCs(self):
        self.appendLog("> create BCs...")

        # physical BCs
        edges = self.myInstance.edges.findAt(
            ((-self.ix1, self.iy1,      0),),
            ((-self.ix2, self.iy1,      0),),
            ((-self.tx1, self.iy1,      0),),
            ((-self.ix1, self.iy1, self.l),),
            ((-self.ix2, self.iy1, self.l),),
            ((-self.tx1, self.iy1, self.l),),
            (( self.ix1, self.iy1,      0),),
            (( self.ix2, self.iy1,      0),),
            (( self.tx1, self.iy1,      0),),
            (( self.ix1, self.iy1, self.l),),
            (( self.ix2, self.iy1, self.l),),
            (( self.tx1, self.iy1, self.l),),
        )
        region = regionToolset.Region(edges=edges)
        self.myModel.DisplacementBC(
            name='vertical supported lines',
            createStepName=self.stepName[self.stepType],
            region=region,
            u1=0.0, u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0)

        # rigid body modes
        vertices = self.myInstance.vertices.findAt(((-self.x1_I, self.iy1, self.l),),)
        region = regionToolset.Region(vertices=vertices)
        self.myModel.DisplacementBC(
            name='rigid body modes',
            createStepName=self.stepName[self.stepType],
            region = region,
            u1=0.0, u3=0.0, ur2=0.0)

    # create pressure load
    def createLoads(self):
        self.appendLog("> create Loads...")

        faces = self.myInstance.faces.findAt(
            ((-self.ix1, self.iy1, self.mz1),),
            (( self.ix1, self.iy1, self.mz1),),
        )

        region = regionToolset.Region(side2Faces=faces)
        self.myModel.Pressure(name='Pressure-1',
                              createStepName=self.stepName[self.stepType],
                              region=region,
                              magnitude=self.p1)

        faces = self.myInstance.faces.findAt(
            ((-self.ix2, self.iy1, self.mz1),),
            (( self.ix2, self.iy1, self.mz1),),
        )

        region = regionToolset.Region(side1Faces=faces)
        self.myModel.Pressure(name='Pressure-2',
                              createStepName=self.stepName[self.stepType],
                              region=region,
                              magnitude=self.p1)

    # create and run the job
    def createAndRunJob(self):
        self.jobName = self.prjName + "-" + self.stepName[self.stepType]
        self.appendLog("> create job '%s' and run it..." % self.jobName)

        job = mdb.Job(name=self.jobName,
                      model=self.prjName)

        self.closeDatabase()
        job.submit()
        job.waitForCompletion()

    # set font size of all components
    def setFontSize(self,size):
        fsize = int(size*10 +0.5)
        self.myViewport.viewportAnnotationOptions.setValues(
            triadFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize,
            legendFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize,
            titleFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize,
            stateFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize)

    # close the database
    def closeDatabase(self):
        self.odbName = self.prjName + "-" + self.stepName[self.stepType] + ".odb"
        self.appendLog("> close database '%s'..." % self.odbName)
        try:
            session.odbs[self.odbName].close()
        except:
            pass

    # open the result database and set a default viewport configuration
    def openDatabase(self, stepType):
        self.odbName = self.prjName + "-" + self.stepName[self.stepType] + ".odb"
        self.appendLog("> open database '%s'..." % self.odbName)

        self.myViewport = session.viewports['Viewport: 1']
        self.myOdb = session.openOdb(name=self.odbName)

        # assign database to viewport
        self.myViewport.setValues(displayedObject=self.myOdb)

        # set standard view: U/U2 vertical displacements
        self.myViewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)
        self.myViewport.odbDisplay.setPrimaryVariable(
                variableLabel='U',
                outputPosition=NODAL,
                refinement=(COMPONENT, 'U2'))

        # set standard font size
        self.setFontSize(10)

        # auto scale it
        self.myViewport.view.fitView()

    # main routine for the analysis
    def analyzeResults(self):
        self.jobName = self.prjName + "-" + self.stepName[self.stepType]
        self.appendLog("> analysis of step '%s'..." %
                       (self.stepName[self.stepType]))

        # analyse static calculation
        if self.stepType == self.LINEAR:
            self.analyseLinearStep()
        else:
            pass

    # analyses of the linear static calculation
    def analyseLinearStep(self,state="SLS"):
        # get frame
        frame = self.myOdb.steps[self.stepName[self.stepType]].frames[-1]

        # get reaction forces
        rfo   = frame.fieldOutputs['RF']

        # sum of reaction forces
        self.sumRFo = [0.,0.,0.]

        # table header
        self.appendLog("  --no ------Fx ------Fy ------Fz")

        # over all nodes
        for value in rfo.values:
            if sqrt(value.data[0]**2
                   +value.data[1]**2
                   +value.data[2]**2) < 1.e-3: continue

            self.appendLog("  %4d %8.2f %8.2f %8.2f" %
                           (value.nodeLabel,
                            value.data[0],value.data[1],value.data[2]))

            # sum up components
            for i in range(3): self.sumRFo[i] += value.data[i]

        self.appendLog("sum of reaction forces: %8.3f %8.3f %8.3f kN" %
                       (self.sumRFo[0]/1.e3,
                        self.sumRFo[1]/1.e3,
                        self.sumRFo[2]/1.e3))

        # maximum vertical displacement
        if 2 > 1:

            # get displacements
            disp = frame.fieldOutputs['U']

            self.maxU2Disp = None
            for value in disp.values:

                if self.maxU2Disp is None: self.maxU2Disp = -value.data[1]
                else:
                    if self.maxU2Disp < -value.data[1]:
                        self.maxU2Disp = -value.data[1]

                # save node displacement vectors
                self.nodeDisp[value.nodeLabel] = value.data

            self.appendLog("Maximum vertical displacements:")
            self.appendLog("  total............: %8.3f mm" % self.maxU2Disp)

            # maximum vertical displacement on support fiber
            maxU2FiberDisp = None
            # over all fiber nodes
            for label in self.nodePos:
                #                                            - vector ----------
                #                                                                 |y-component
                if maxU2FiberDisp is None: maxU2FiberDisp = -self.nodeDisp[label][1]
                else:
                    if maxU2FiberDisp < -self.nodeDisp[label][1]:
                        maxU2FiberDisp = -self.nodeDisp[label][1]

            self.appendLog("  on supported line: %8.3f mm" % maxU2FiberDisp)

        # calculate maximum stress
        else:

            # get displacements
            self.elementX  = 0
            self.maxStress = 0.
            for value in frame.fieldOutputs['S'].values:
                if self.maxStress < value.mises:
                    self.maxStress = value.mises
                    self.elementX  = value.elementLabel

            self.appendLog("> max. Mises stress:")
            self.appendLog(">   Element %d, %8.1f N/mm^2" % (self.elementX,self.maxStress))

        # set standard font size
        self.setFontSize(10)

        # print figures
        # displacement figures for SLS
        if 2 > 1:
            varList = ["U1","U3","U2"]
            for var in varList:
                self.myViewport.odbDisplay.setPrimaryVariable(
                        variableLabel='U',
                        outputPosition=NODAL,
                        refinement=(COMPONENT, var))

                # auto scale it
                self.myViewport.view.fitView()

                # print figure into a file
                self.printPngFile(self.jobName + "-" + var)

        # stress plot for ULS
        else:
            self.myViewport.odbDisplay.setPrimaryVariable(
                    variableLabel='S',
                    outputPosition=INTEGRATION_POINT,
                    refinement=(INVARIANT, 'Mises'), )

            # auto scale it
            self.myViewport.view.fitView()

            # print figure into a file
            self.printPngFile(self.jobName + "-S")

    # print a png file from a viewport
    def printPngFile(self,name):
        session.printOptions.setValues(vpBackground=ON)
        session.printToFile(fileName = name,
                            format=PNG,
                            canvasObjects=(self.myViewport,))      
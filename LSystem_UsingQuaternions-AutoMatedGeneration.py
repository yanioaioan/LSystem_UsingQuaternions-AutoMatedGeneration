import math,copy
import maya.cmds as mc
import time

#tree like structure
rules = {'A': 'Fv[F]F',  'F': 'FA'}
axiom = 'A'
iterations = 1

'''
Alphabet : A, B
Constants : F + −
Axiom : A
Production rules:

        A → − B F + A F A + F B −
        B → + A F − B F B − F A +

Here, "F" means "draw forward", "−" means "turn left 90°", "+" means "turn right 90°" (see turtle graphics), and "A" and "B" are ignored during drawing.
'''

#Hilbert space-filling curve 2D - maya specific implementation
rules = {'A': 'BF^AFA^FBv',  'B': 'AFvBFBvFA^'}
axiom = 'A'
iterations = 1


rules = {'F': 'F[vFF]FF[<F]',  'B': 'AFvBFBvFA^'}
axiom = 'F'
iterations = 1


genericLSysAngle=25

cmds.select(all=True)
cmds.delete()

m_string = axiom
for i in range(iterations):
    tempStr = ''
    for c in m_string:
        tempStr += rules.get(c, c)
    m_string = tempStr
    
print m_string

for c in m_string:
    cmds.delete(ch=True)#delete construction history
    if c == 'F':        
        createABranch(rotAxis,genericLSysAngle)               
    if c == 'v':        
	    #rotateX
	    setRotAxis(1)
	    setAngle(genericLSysAngle)
    if c == '^':
	    #rotateX
	    setRotAxis(1)
	    setAngle(-genericLSysAngle)
    if c == '+':
        #rotateY
        setRotAxis(2)
        setAngle(genericLSysAngle)
    if c == '-':
        #rotateY
        setRotAxis(2)
        setAngle(-genericLSysAngle)
    if c == '<':
        #rotateZ
        setRotAxis(3)
        setAngle(genericLSysAngle)
    if c == '>':
        #rotateZ
        setRotAxis(3)
        setAngle(-genericLSysAngle)
    if c == '[':
        push()        
    if c == ']':
        pop()
        setAngle(0)
        
        




curpos=[0,0,0]
branchLength=1 
genericLSysAngle=0
prevRot=[0,0,0]#initial rotation
prevPos=[0,-0.5,0]#initial position


genericLSysAngle=0
rotAxis=[0,0,0]

pushFlag=False
popFlag=False

#rotate about x or y or z axis using an angle (could be used for 3d L-System without matrices)
def toDegrees(radangle):
    return radangle*180/math.pi
    
def rotateAbout(rotAboutAxis, genericLSysAngle):
    
    #rotAboutAxis = [1,0,0]#we know what axis we want to rotate about
    myangle=genericLSysAngle * math.pi/180 ##we know our angle and transform it to radians
    '''Quaternion built'''
    qx = rotAboutAxis[0] * math.sin(myangle/2)
    qy = rotAboutAxis[1] * math.sin(myangle/2)
    qz = rotAboutAxis[2] * math.sin(myangle/2)
    qw = math.cos(angle/2)
    Q=[qx,qy,qz,qw]
    return  Q

def EulerAnglesFromAxisQuat(rotAboutAxis, genericLSysAngle):
    qx,qy,qz,qw = rotateAbout(rotAboutAxis, genericLSysAngle)
    
    '''Yaw Pitch Roll calculation from quaternion'''
    heading = math.atan2(2*qy*qw-2*qx*qz , 1 - 2*qy*qy - 2*qz*qz)#z
    attitude = math.asin(2*qx*qy+2*qz*qw)#y
    bank = math.atan2(2*qx*qw-2*qy*qz , 1 - 2*qx*qx - 2*qz*qz)# Attention this is euler angle X ..not z
    
    angles=[bank,heading,attitude]
    
    #print "angles=%s"%(angles)
    
    return angles



branchStackPos=[]
branchStackRot=[]

def createABranch(rotAxis, genericLSysAngle):
    global prevRot,prevPos
    '''Extract Euler angles from constructed quaternion'''
    euAngles=EulerAnglesFromAxisQuat(rotAxis, genericLSysAngle)
    
    #print toDegrees(euAngles[0])#x
    #print toDegrees(euAngles[1])#y 
    #print toDegrees(euAngles[2])#z
            
    '''Create Cylinder'''
    branch = mc.polyCylinder(n='cy1',  r=0.1, height=branchLength)#axis=(dirx[0],diry[0],dirz[0]),
    
    #time.sleep(1)
    
    '''Set pivot to botton so as to rotate properly'''
    bbox = mc.exactWorldBoundingBox(branch)
    bottom = [(bbox[0]+bbox[3])/2, bbox[1], (bbox[2]+bbox[5])/2] #(xmin,xmax)/2 , (zmin,zmax)/2
    #now set pivot to the bottom of the cylinder
    mc.xform(branch[0], piv=bottom, ws=True, r=True)
    cmds.refresh()
    #time.sleep(1)
    
    global pushFlag,popFlag
    if pushFlag==True:
        branchStackPos.append(prevPos)
        branchStackRot.append(prevRot)
        pushFlag=False
        
        
    if popFlag==True:
        prevPos=branchStackPos.pop()
        prevRot=branchStackRot.pop()
        popFlag=False
        
        
    mypos=prevPos
    myrot=prevRot
    
    #mypos=branchStackPos.pop()
    #myrot=branchStackRot.pop()
        
    
    
    '''Move cylinder to the current position & the current rotation'''
    mc.xform( rotation=myrot, translation=mypos)    
    cmds.refresh()
    #time.sleep(1)
    
    
    cylHeight=mc.polyCylinder(branch[0], height=True, query=True)

    
    '''move towards direction- push it up on the local y Axis'''
    mc.move( 0,cylHeight,0, r=True, os=True)#step forward - move up in local Y
    
    '''Store this new branch position'''    
    prevPos=mc.xform( query=True, translation=True, worldSpace=True)#keeps the previous position
            
    cmds.refresh()
    #time.sleep(1)
    
    '''Rotate and Store rotation'''
    mc.rotate( toDegrees(euAngles[0]), toDegrees(euAngles[1]), toDegrees(euAngles[2]), branch[0], r=True ) #perform relative rotation       
    prevRot=mc.xform( query=True, rotation=True, worldSpace=True)#keeps the previous rotated degree angles
    
    cmds.refresh()
    #time.sleep(1)
    
    
    
def push( *pArgs):
	global pushFlag
	pushFlag=True

def pop( *pArgs):
	global popFlag
	popFlag=True
	
	
	

'''Choose rot axis'''
def setRotAxis(axis, *pArgs):
	global rotAxis
	if axis==1:
	    rotAxis=[1,0,0]#world rotation axis
	elif axis==2:
	    rotAxis=[0,1,0]#world rotation axis
	elif axis==3:
	    rotAxis=[0,0,1]#world rotation axis
	#print rotAxis
	

	
'''Choose rot angle'''
def setAngle(angl,*pArgs):
    global genericLSysAngle
    genericLSysAngle=angl
    print angl
	

def createUI():
    
    #cmds.select(all=True)
    #cmds.delete()
    
    prevRot=[0,0,0]
    prevPos=[0,0,0]

    if cmds.window('LSys', exists=True):
        cmds.deleteUI("LSys")
        print 'deleted window'
    
    cmds.window("LSys")    
    
    #    Create a window with two separate radio button groups.        
    cmds.columnLayout()
    axesRadio = cmds.radioButtonGrp( label='Rotation About Axis', labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3, onCommand = lambda *args: setRotAxis(cmds.radioButtonGrp(axesRadio, query=True, sl=True)) )    
    
    angleSlider = mc.intSliderGrp('angle',field=True, label='Angle of rotation', minValue=-180, maxValue=180,value=0, changeCommand = lambda *args: setAngle(cmds.intSliderGrp(angleSlider, query=True, value=True)) )
    #print 'generic angle'+str(genericLSysAngle)
    cmds.button(label = "Create Branch", command = lambda *args: createABranch(rotAxis, genericLSysAngle) )
    
    cmds.button(label = "Push-Store branch's Root position and rotation ", command = lambda *args: push() )
    cmds.button(label = "Pop-Use and remove branch's Root position and rotation ", command = lambda *args: pop() )
    
    cmds.showWindow()
    

#createUI()
    
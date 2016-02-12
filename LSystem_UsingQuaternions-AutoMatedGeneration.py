import math,copy
import maya.cmds as mc
import time


'''
Alphabet : A, B
Constants : F + ?
Axiom : A
Production rules:

        A ? ? B F + A F A + F B ?
        B ? + A F ? B F B ? F A +

Here, "F" means "draw forward", "?" means "turn left 90°", "+" means "turn right 90°" (see turtle graphics), and "A" and "B" are ignored during drawing.
'''




#Quadratic Koch curve
#F -> F+F-F-F+F
rules = {'F': 'F<F>F>F<F'}
axiom = 'F'
iterations = 3


#Tree like Structure
#'F':'FFFA[F[vFF<FF][F[FF^FAvFA]>F+FF-AF[-FvAF]<FA]<F]', 'A':'FAF'
#rules = {'F':'FFFA[F[vFF<FF][F[FF^FAvFA]>F+FF-AF[-FvAF]<FA]<F]', 'A':'FAF'}
#axiom = 'F'
#iterations = 2

'''
#Peano curve curve
#F ? F+F-F-F-F+F+F+F-F
rules = {'F': 'F^FvFvFvF^F^F^FvF'}
axiom = 'F'
iterations = 2
'''


'''
#Hilbert curve
#L ? +RF-LFL-FR+ , R ? -LF+RFR+FL
rules = {'L': 'vRF^LFL^FRv', 'R': '^LFvRFRvFL'}
axiom = 'L'
iterations = 2
'''

'''
#Sierpinski sieve
#n = 6
#axiom = FXF++FF++FF
#rule = F ? FF , X ? ++FXF--FXF--FXF++
#ä = 60°
rules = {'F' : 'FF' , 'X' : '^^FXFvvFXFvvFXF^^'}
axiom = 'FXF^^FF^^FF'
iterations = 4
'''

fixedAngle=90
genericLSysAngle=90


curpos=[0,0,0]
branchLength=1 
prevRot=[0,0,0]#initial rotation
prevPos=[0,-0.5,0]#initial position


rotAxis=[0,0,0]

pushFlag=False
popFlag=False

cmds.select(all=True)
cmds.delete()

m_string = axiom
for i in range(iterations):
    tempStr = ''
    for c in m_string:
        tempStr += rules.get(c, c)
    m_string = tempStr
    
print m_string



branchStackPos=[]
branchStackRot=[]

def createABranch(rotAxis, angle):
    global prevRot,prevPos
    '''Extract Euler angles from constructed quaternion'''
    euAngles=EulerAnglesFromAxisQuat(rotAxis, angle)
    
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
    
    
    print "branchStackPos=%s"%(branchStackPos)    
    
    #print "myposUsed=%s"%(prevPos)    
        
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
    
    setAngle(0)
    
    
    
def push( *pArgs):
	global pushFlag,prevPos,prevRot
	pushFlag=True
	
	if pushFlag==True:
	    branchStackPos.append(prevPos)
	    branchStackRot.append(prevRot)
	    pushFlag=False
	    


def pop( *pArgs):
    global popFlag,prevPos,prevRot
    popFlag=True
    
    if popFlag==True:
        prevPos=branchStackPos.pop()
        prevRot=branchStackRot.pop()
        popFlag=False
        
    	
	

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
    #print angl





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
    qw = math.cos(myangle/2)
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
    

for c in m_string:
    cmds.delete(ch=True)#delete construction history
    if c == 'F':
        #print "genericLSysAngle=%s"%(genericLSysAngle)        
        createABranch(rotAxis,genericLSysAngle)               
    if c == 'v':        
	    #rotateX
	    setRotAxis(1)
	    setAngle(fixedAngle)
    if c == '^':
	    #rotateX
	    setRotAxis(1)
	    setAngle(-fixedAngle)
    if c == '+':
        #rotateY
        setRotAxis(2)
        setAngle(fixedAngle)
    if c == '-':
        #rotateY
        setRotAxis(2)
        setAngle(-fixedAngle)
    if c == '<':
        #rotateZ
        setRotAxis(3)
        setAngle(fixedAngle)
    if c == '>':
        #rotateZ
        setRotAxis(3)
        setAngle(-fixedAngle)
    if c == '[':
        push()
        print "mypos_PUSHED=%s"%(prevPos)        
    if c == ']':
        pop()
        print "mypos_POPPED=%s"%(prevPos)
        setAngle(0)
        
        


#createUI()
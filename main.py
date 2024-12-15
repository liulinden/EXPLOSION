#screams
print("AAAAAAAAAAAAAAA")

#imports
import random
import pygame
import math
#import polygenerator 
pygame.init()
#random.seed(200)

#get magnitude of vector
def magnitude(cx,cy):
    return math.sqrt(cx**2+cy**2)

def toPolar(x,y):
    if x>0:
        return math.atan(y/x), magnitude(x,y)
    elif x<0:
        return math.pi+math.atan(y/x), magnitude(x,y)
    elif y>0:
        return math.pi/2, y
    elif y<0:
        return -math.pi/2, -y
    else:
        return 0,0

def toComponents(angle,r):
    return r*math.cos(angle), r*math.sin(angle)

def getIntersection(seg1,seg2, segment=True):
    a1,a2=seg1
    b1,b2=seg2
    #verticle line
    if a1[0]==a2[0] or b1[0]==b2[0]:
        if a1[0]==a2[0] and b1[0]==b2[0] and a1[0]==b1[0]:
            if not (max(a1[1],a2[1])<min(b1[1],b2[1]) or max(b1[1],b2[1])<min(a1[1],a2[1])):
                return ["inf"]
        return ["none"]

    ma= (a2[1]-a1[1])/(a2[0]-a1[0])
    mb=(b2[1]-b1[1])/(b2[0]-b1[0])

    #equal slope
    #TODO edit to be if theyre close enough
    if ma ==mb:
        if a1[1]+(-a1[0])*ma==b1[1]+(-b1[0])*mb:
            if not (max(a1[0],a2[0])<min(b1[0],b2[0]) or max(b1[0],b2[0])<min(a1[0],a2[0])):
                return ["inf"]
        return ["none"]

    #get intersection x
    x=(b1[0]*(mb)-a1[0]*(ma)-b1[1]+a1[1])/(mb-ma)
    if segment:
        if (a1[0]<=x and x<=a2[0]) or ((a1[0]>=x and x>=a2[0])):
            if (b1[0]<=x and x<=b2[0]) or ((b1[0]>=x and x>=b2[0])):
                return ["one", [x,a1[1]+(x-a1[0])*ma]]
            
    return ["none"]

#get positional velocities at angle
def angVelToPos(radius, angle, aVel):
    mag=radius*aVel
    dx=mag*(-math.sin(angle))
    dy=mag*(math.cos(angle))
    return dx,dy

#ground class
class Ground:
    def __init__(self, color, y):
        global id
        self.id=id
        id+=1
        self.type = "ground"
        self.color= color
        self.y = y
        self.x = 0
        self.xVel=0
        self.yVel=0
        self.aVel=0
        self.mass=-1
    
    def draw(self, w):
        pygame.draw.rect(w, self.color, pygame.Rect(0,self.y,w.get_width(),w.get_height()-self.y))

#polygon class
class Polygon:
    def __init__(self, color, shape, x=0, y=0):
        global id
        
        self.type = "polygon"
        self.id = id
        id+=1

        self.color = color

        #relative position from initial position
        self.x=x
        self.y=y
        self.angle=0


        #should be calculated, currently not used
        self.mass=1
        self.inertia=2500

        #find center of mass and set self.x and self.y accordingly
        ...
        
        #
        self.axVel=0
        self.ayVel=0

        #coordinates of vertices on window
        self.vertices = []
        for vertex in shape:
            self.vertices.append([vertex[0]+x,vertex[1]+y])

        #velocities (x,y,angle)
        self.xVel = 0#random.randint(-10,10) #4
        self.yVel = -10
        self.aVel = 0

        self.forces= []

        #temporary
        self.rotate(2)

        #rect
        self.rect=pygame.Rect(0,0,10,10)
        self.updateRect()

        #biggest radius
        self.radius=0
        for vertex in self.vertices:
            self.radius=max(self.radius,magnitude(vertex[0]-self.x,vertex[1]-self.y))
    
    #get velocities at point on shape
    def getPointVel(self,x,y):
        ax,ay = angVelToPos(magnitude(y-self.x,x-self.x),math.atan2(y-self.y,x-self.x),self.aVel)
        return ax+self.xVel,ay+self.yVel

    def updateRect(self):
        minx, maxx,miny,maxy=self.vertices[0][0],self.vertices[0][0],self.vertices[0][1],self.vertices[0][1]
        for vertex in self.vertices:
            minx=min(minx,vertex[0])
            miny=min(miny,vertex[1])
            maxx=max(maxx,vertex[0])
            maxy=max(maxy,vertex[1])
        self.rect=pygame.Rect(minx,miny,maxx-minx,maxy-miny)

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.vertices)

    def drawForces(self,surface):
        for force in self.forces:
            pygame.draw.line(surface,(0,0,0),(self.x+force[3],self.y+force[4]),(self.x+force[3]+10*force[1],self.y+force[4]+10*force[2]))

    #return list of collisions, with collisions given as [collider object, point of contact, normal angle at contact]
    def checkCollisions(self, colliders):
        self.updateRect()
        collisions = []
        for collider in colliders:

            #should not check with self
            if collider != self:

                #ground collision case
                if collider.type == "ground":
                    collided=False
                    for vertex in self.vertices:
                        if vertex[1] >= collider.y:
                            collided = True
                            break
                    if collided:
                        nContacts = 0
                        xContactsSum=0
                        for vertex in self.vertices:
                            if vertex[1] >= collider.y-1:
                                xContactsSum+=vertex[0]
                                nContacts+=1
                        if nContacts>0:
                            collisions.append([collider,[xContactsSum/nContacts,collider.y],-math.pi/2])
                
                #polygon collision case
                elif collider.type == "polygon":
                    if self.rect.colliderect(collider.rect):
                        for i in range(len(self.vertices)):
                            if i==0:
                                segment1=[self.vertices[len(self.vertices)-1],self.vertices[0]]
                            else:
                                segment1=[self.vertices[i-1],self.vertices[i]]
                            for j in range(len(collider.vertices)):
                                if j==0:
                                    segment2=[collider.vertices[len(collider.vertices)-1],collider.vertices[0]]
                                else:
                                    segment2=[collider.vertices[j-1],collider.vertices[j]]
                                intersect=getIntersection(segment1,segment2)

        return collisions
    
    #move by dx dy and rotate by da, ignoring physics
    def transform(self, dx,dy,da):
        self.move(dx,dy)
        self.rotate(da)
    
    #move by dx dy, ignoring physics and stuff
    def move(self, dx, dy):
        self.x+=dx
        self.y+=dy
        for vertex in self.vertices:
            vertex[0]+=dx
            vertex[1]+=dy
    
    #rotate by da, ignoring physics
    def rotate(self, da):
        self.angle+=da
        for vertex in self.vertices:
            x=vertex[0]-self.x
            y=vertex[1]-self.y
            a,r=toPolar(x,y)
            x,y=toComponents(a+da,r)
            vertex[0]=x+self.x
            vertex[1]=y+self.y

    #applyForces
    def applyForces(self):
        xAcc=0
        yAcc=0
        aAcc=0
        axAcc=0
        ayAcc=0
        for force in self.forces:
            if force[3]==0 and force[4]==0:
                xAcc+=force[1]/self.mass
                yAcc+=force[2]/self.mass
                axAcc+=force[1]/self.mass
                ayAcc+=force[2]/self.mass
            else:
                refAngle,lever=toPolar(force[3],force[4])
                a,r=toPolar(force[1],force[2])
                dirComp,tanComp = toComponents(a-refAngle,r)
                dx,dy=toComponents(refAngle,dirComp)
                xAcc+=dx/self.mass
                yAcc+=dy/self.mass
                aAcc+=tanComp*lever/self.inertia
                axAcc+=force[1]/self.mass
                ayAcc+=force[2]/self.mass
        self.xVel+=xAcc
        self.yVel+=yAcc
        self.aVel+=aAcc
        self.axVel+=axAcc
        self.ayVel+=ayAcc


    #apply force
    def addForce(self, id, xForce, yForce, xLoc, yLoc):
        for i in range(len(self.forces)):
            if self.forces[i][0]==id:
                self.forces[i]=[id,xForce,yForce,xLoc,yLoc]
                return
        self.forces.append([id,xForce, yForce, xLoc, yLoc])

    #setup for tick
    def tickStart(self):
        self.forces = [(0,0,GRAVITY*self.mass,0,0)]

    #move one frame
    def tickMove(self):
        
        maxStepSize=1

        #break down movement
        maxDistance = self.radius+magnitude(self.xVel,self.yVel)
        steps=math.ceil(maxDistance/maxStepSize)

        if steps==0:
            return

        xStep=self.xVel/steps
        yStep=self.yVel/steps
        aStep=self.aVel/steps
        axStep=self.axVel/steps
        ayStep=self.ayVel/steps
        initX=self.x
        initY=self.y
        initA=self.angle
        #take steps
        while steps > 0:
            steps-=1

            self.transform(xStep,yStep,aStep)

            #check for collisions
            collisions=self.checkCollisions(shapes+ground)
            if len(collisions) > 0:
                #self.transform(-xStep,-yStep,-aStep)
                #self.transform(axStep,ayStep,0)
                #collisions=self.checkCollisions(shapes+ground)
                if len(collisions) > 0:
                    for i in range(10):
                        self.transform(-xStep/10,-yStep/10,-aStep/10)
                        collisions=self.checkCollisions(shapes+ground)
                        if len(collisions)==0:
                            break
                        if i==9:
                            print("stuck")
                        
                    self.transform(xStep/10,yStep/10,aStep/10)
                    collisions=self.checkCollisions(shapes+ground)
                    self.transform(-xStep/10,-yStep/10,-aStep/10)
                    
                    #update forces
                    for collision in collisions:
                        collider, contact, angle = collision

                        #get net velocities at point of contact
                        colliderXVel, colliderYVel = 0, 0
                        if collider.type=="polygon":
                            colliderXVel, colliderYVel = collider.getPointVel(contact[0],contact[1])
                        netXVel, netYVel = self.getPointVel(contact[0],contact[1])
                        #netYVel+=2
                        #isolate relevant velocities
                        a,r=toPolar(netXVel, netYVel)
                        netVel, trash = toComponents(a-angle,r)
                        a,r=toPolar(colliderXVel, colliderYVel)
                        colliderVel, trash = toComponents(a-angle,r)

                        #calculate force\
                        # inelastic collision
                        if collider.mass==-1:
                            force = self.mass*(netVel-colliderVel)
                        else:
                            force = self.mass*collider.mass*(netVel-colliderVel)/(self.mass+collider.mass)
                        forceX, forceY = toComponents(angle,force)
                        print(self.yVel,self.aVel,forceY)
                        #add forces
                        self.addForce(str(collider.id)+'N',-forceX,(-forceY)*self.mass,contact[0]-self.x,contact[1]-self.y)
                        if collider.type=="polygon":
                            collider.addForce(str(self.id)+'N',forceX,forceY,contact[0]-collider.x,contact[1]-collider.y)
                    break
                else:
                    ...
        self.xVel=self.x-initX
        self.yVel=self.y-initY
        self.aVel=self.angle-initA            
                    



                    


                

                
                


            

    """
    #frame actions
    def tick(self):
        
        initX = self.x
        initY = self.y
        initA = self.angle

        #get net acceleration
        xAcc=0
        yAcc=0
        aAcc=0
        for force in self.forces:
            if force[2]==0 and force[3]==0:
                xAcc+=force[0]
                yAcc+=force[1]
            else:
                refAngle,lever=toPolar(force[2],force[3])
                a,r=toPolar(force[0],force[1])
                dirComp,tanComp = toComponents(a-refAngle,r)
                dx,dy=toComponents(refAngle,dirComp)
                xAcc+=dx
                yAcc+=dy
                #print(dirComp, tanComp)

                aAcc+=tanComp*lever/2000
        #print(xAcc,yAcc, aAcc)
        
        #print(self.yVel)

        #apply net force
        self.xVel+=xAcc
        self.yVel+=yAcc
        self.aVel+=aAcc
        #reset forces
        self.forces = [GRAVITY]

        #move 
        #TODO redefine steps for angles based on change in position of points, not change in angle
        steps = (magnitude(self.xVel, self.yVel)+self.radius*(abs(self.aVel)+1))/20
        if steps > 0:
            stepSize = magnitude(self.xVel, self.yVel)/steps
            #be wary of getting stuck between stuff,
            #print("steps", steps)
            xStep = self.xVel/steps
            yStep = self.yVel/steps
            aStep = self.aVel/steps
            print(self.aVel*180/math.pi)
            collisions = []
            finalCollisions=[]
            while steps > 1:
                steps-=1
                self.move(xStep,yStep)
                self.rotate(aStep)
                collisions=self.checkCollisions(shapes+ground)
                if len(collisions) > 0:
                    finalCollisions=collisions
                    tolerance=math.ceil(stepSize+self.radius)
                    for i in range(tolerance):
                        dx,dy=toComponents(collisions[0][2],1)
                        self.move(dx,dy)
                        collisions=self.checkCollisions(shapes+ground)
                        if len(collisions)==0:
                            break
                    if len(collisions)>0:
                        print(collisions,"womp1")
                        self.move(-tolerance*dx-xStep,-tolerance*dy-yStep)
                        self.rotate(-aStep)
                        steps=1
                        break
            while steps > 0:
                steps -= 0.1
                self.move(xStep/10,yStep/10)
                self.rotate(aStep/10)
                collisions=self.checkCollisions(shapes+ground)
                
                if len(collisions) > 0:
                    print("boom2")
                    finalCollisions=collisions
                    tolerance=math.ceil(stepSize/10+self.radius)
                    stuck=True
                    for i in range(tolerance):
                        dx,dy=toComponents(collisions[0][2],1)
                        self.move(dx,dy)
                        collisions=self.checkCollisions(shapes+ground)
                        if len(collisions)==0:
                            stuck=False
                            break
                        else:
                            #TODO edit for multiple collisions
                            finalCollisions=collisions
                    
                    if stuck:
                        print("womp2")
                        self.move(-tolerance*dx-xStep/10,-tolerance*dy-yStep/10)
                        self.rotate(-aStep/10)
                        break
            if len(finalCollisions) >0:
                for collision in finalCollisions:
                    speed,contact,angle=collision

                    #temporary
                    a,r=toPolar(xAcc,yAcc)
                    normalMag=math.cos(a-angle)*r
                    x,y=toComponents(-angle,normalMag)
                    #print(x,y)
                    self.forces.append((x,y,contact[0]-self.x,contact[1]-self.y))

                    #friction skip
                    

                    staticFriction=1
                    kineticFriction=1/2

                    a,r=toPolar(self.xVel-speed[0],self.yVel-speed[1])
                    x,y=toComponents(a-angle,r)
                    a,r=toPolar(0,y)
                    x,y=toComponents(a+angle,normalMag)
                    #if r>2:
                        #self.forces.append((x*kineticFriction,y*kineticFriction,contact[0]-self.x,contact[1]-self.y))

        #self.rotate(10*math.pi/180)
        self.xVel=self.x-initX
        self.yVel=self.y-initY
        self.aVel=self.angle-initA

        self.updateRect()
        """
            


    def split(self):
        ...

def createRegularShape(color, sides, radius=1, x=0,y=0):
    #make function that creates a list of points according to parameters
    
    shape=[]
    for i in range(sides):
        arg= math.pi*2*(1/4+1/2/sides+i/sides)
        shape.append((math.cos(arg)*radius,math.sin(arg)*radius))
    return Polygon(color, shape,x,y)



def randomColor():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

#setup
SCREENWIDTH = 1000
SCREENHEIGHT = 700
w = pygame.display.set_mode([SCREENWIDTH,SCREENHEIGHT])
c = pygame.time.Clock()
w.fill((255,255,255))
id=1

#constants
GRAVITY = 2

lines=[]
ground = [Ground((50,50,50), 600)]
#Polygon((200,50,50),[[-70,10],[10,10],[10,50],[50,50],[50,-30],[-70,-30]],SCREENWIDTH/2,SCREENHEIGHT/2), 
shapes = [createRegularShape(randomColor(),random.randint(3,7),50,SCREENWIDTH/2,SCREENHEIGHT/2)]#,createRegularShape(randomColor(),4,50,SCREENWIDTH/2,100)]
running = True
 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    if running:
        w.fill((255,255,255))

        for shape in shapes:
            shape.tickStart()
        
        
        

        for shape in shapes:
            shape.tickMove()
        
        for shape in shapes:
            shape.applyForces()
        
        for shape in shapes:
            shape.draw(w)
            shape.drawForces(w)
        ground[0].draw(w)
        
        pygame.display.flip()
        c.tick(30)
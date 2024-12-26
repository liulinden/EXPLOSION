#screams
print("AAAAAAAAAAAAAAA")

#imports
import random
import pygame
import math
import copy
#import polygenerator 
pygame.init()
#random.seed(200)

#get magnitude of vector
def magnitude(cx,cy):
    return math.sqrt(cx**2+cy**2)

def randomColor():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

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
        #global id
        #elf.id=id
        #id+=1
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
        #id+=1

        self.color = color

        #relative position from initial position
        self.x=x
        self.y=y
        self.angle=0


        #should be calculated, currently not used
        self.mass=1
        self.inertia=50000

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
        self.rotate(0)

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
                                intersects=getIntersection(segment1,segment2)
                                if intersects[0]=="one":
                                    #may need to be flipped sometimes
                                    collisions.append([collider,[intersects[1][0],intersects[1][1]],math.pi/2+math.atan2(segment2[1][1]-segment2[0][1],segment2[1][0]-segment2[0][0])])

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
    def applyForce(self, force):
        physics.forces.append([force[3]+self.x,force[4]+self.y,force[1]*10/force[5],force[2]*10/force[5]])
        #print(physics.forces)
        self.xVel+=force[1]/self.mass
        self.yVel+=force[2]/self.mass
        if (force[3]!=0 or force[4]!=0):
            refAngle,lever=toPolar(force[3],force[4])
            a,r=toPolar(force[1],force[2])
            dirComp,tanComp = toComponents(a-refAngle,r)
            self.aVel+=tanComp*lever/self.inertia   
                    
    #simulate physics for ms milliseconds
    def simulate(self, physics, ms):

        #convert to seconds
        s=ms/1000

        #apply gravity
        self.applyForce(['gravity',0,physics.g*s,0,0,ms])

        #move shape
        self.transform(self.xVel*s,self.yVel*s,self.aVel*s)

        #check collisions
        colliders=physics.shapes+physics.staticColliders
        collisions = self.checkCollisions(colliders)

        #collision
        if len(collisions) > 0:
            self.transform(-self.xVel*s,-self.yVel*s,-self.aVel*s)
            #TODO UNREVISED apply forces
            for collision in collisions:
                collider, contact, angle = collision

                #get net velocities at point of contact
                colliderXVel, colliderYVel = 0, 0
                if collider.type=="polygon":
                    colliderXVel, colliderYVel = collider.getPointVel(contact[0],contact[1])
                netXVel, netYVel = self.getPointVel(contact[0],contact[1])
                
                #isolate relevant velocities
                a,r=toPolar(netXVel, netYVel)
                netVel, trash = toComponents(a-angle,r)
                a,r=toPolar(colliderXVel, colliderYVel)
                colliderVel, trash = toComponents(a-angle,r)

                #calculate force
                # inelastic collision
                if collider.mass==-1:
                    force = self.mass*(netVel-colliderVel)
                else:
                    force = self.mass*collider.mass*(netVel-colliderVel)/(self.mass+collider.mass)

                #elastic collision
                if collider.mass==-1:
                    force = 2*self.mass*(netVel-colliderVel)
                else:
                    force=-2*self.mass*collider.mass*(colliderVel-netVel)/(self.mass+collider.mass)
                    #force = self.mass*collider.mass*(netVel-colliderVel)/(self.mass+collider.mass)

                

                forceX, forceY = toComponents(angle,force)
                #print(forceX,forceY)
                #print(self.yVel,netVel,self.yVel*self.mass,forceY,"\n")
                #add forces
                self.applyForce(['N',-forceX,-forceY,contact[0]-self.x,contact[1]-self.y,ms])
                if collider.type=="polygon":
                    collider.applyForce(['N',forceX,forceY,contact[0]-collider.x,contact[1]-collider.y,ms])
        #print(ms,"xvel", self.xVel,"yvel", self.yVel,"avel",self.aVel)
        if self.maxMovement() > 2000:
            physics.shapes.remove(self)

    def maxMovement(self):
        return magnitude(self.xVel,self.yVel)+abs(self.aVel)*self.radius

    def split(self):
        ...

def createRegularShape(color, sides, radius=1, x=0,y=0):
    #make function that creates a list of points according to parameters
    
    shape=[]
    for i in range(sides):
        arg= math.pi*2*(1/4+1/2/sides+i/sides)
        shape.append((math.cos(arg)*radius,math.sin(arg)*radius))
    return Polygon(color, shape,x,y)



#overarching class
class Physics:

    #setup
    def __init__(self, GRAVITY=2000, startShapes=[Ground((0,0,0),600)]):
        self.shapes = []
        self.time = 0
        self.g = GRAVITY
        self.staticColliders = startShapes
        self.forces = []
    
    #do physics for frame
    def tick(self, fps):
            
        #kill forces
        self.forces = []

        #set time tracking variables
        frameTime = 0
        finishTime = 1000/fps

        #simulate frame
        while frameTime < finishTime:

            #choose time per step based on shape movement - number of milliseconds to simulate
            stepTime= finishTime-frameTime
            for shape in self.shapes:
                #can be adjusted depending on performance goals; currently simulates a max step size of 3
                stepTime = min(stepTime,1*1000/max(1,shape.maxMovement()))
            
            #update time
            frameTime += stepTime

            

            #simulate shapes for stepTime milliseconds
            for shape in self.shapes:
                shape.simulate(self, stepTime)
        
        #update physics time
        self.time += finishTime
    
    #draw shapes and colliders
    def draw(self,w):
        for shape in self.shapes:
            shape.draw(w)
        for collider in self.staticColliders:
            collider.draw(w)
    
    #draw forces
    def drawForces(self,w):
        for force in self.forces:
            pygame.draw.line(w,(0,0,0),(force[0],force[1]),(force[2]+force[0],force[1]+force[3]))

    def addRegularShape(self, sides, radius):
        ...


    def addShape(self, vertices):
        ...
    


#setup
SCREENWIDTH = 1000
SCREENHEIGHT = 700
w = pygame.display.set_mode([SCREENWIDTH,SCREENHEIGHT])
c = pygame.time.Clock()
w.fill((255,255,255))
fps=30
running = True

#constants
physics = Physics()
physics.shapes.append(createRegularShape(randomColor(),5,50,SCREENWIDTH/2,SCREENHEIGHT/2))


#main loop
while running:

    #check for closing window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x,y=pygame.mouse.get_pos()
            physics.shapes.append(createRegularShape(randomColor(),random.randint(3,7),50,x,y))
    
    #frame stuff
    if running:

        #simulate physics
        physics.tick(fps)

        #render screen
        w.fill((255,255,255))
        physics.draw(w)
        #physics.drawForces(w)

        #update screen and tick
        pygame.display.flip()
        c.tick(fps)
        
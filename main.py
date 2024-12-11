#screams
print("AAAAAAAAAAAAAAA")

#imports
import random
import pygame
import math
#import polygenerator 
pygame.init()

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

def getIntersection(seg1,seg2):
    ...

#ground class
class Ground:
    def __init__(self, color, y):
        self.type = "ground"
        self.color= color
        self.y = y
    
    def draw(self, w):
        pygame.draw.rect(w, self.color, pygame.Rect(0,self.y,w.get_width(),w.get_height()-self.y))

#polygon class
class Polygon:
    def __init__(self, color, shape, x=0, y=0):
        
        self.type = "polygon"

        self.color = color

        #relative position from initial position
        self.x=x
        self.y=y
        self.angle=0
        self.mass=1000

        #find center of mass and set self.x and self.y accordingly


        #coordinates of vertices on window
        self.vertices = []
        for vertex in shape:
            self.vertices.append([vertex[0]+x,vertex[1]+y])

        #velocities (x,y,angle)
        self.xVel = 5+-1*len(shape) #4
        self.yVel = -10
        self.aVel = -8*math.pi/180

        self.forces= []

        #temporary
        self.rotate(2)

        self.rect=pygame.Rect(0,0,10,10)
        self.updateRect()
    
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
            pygame.draw.line(surface,(0,0,0),(self.x+force[2],self.y+force[3]),(self.x+force[2]+10*force[0],self.y+force[3]+10*force[1]))

    #return list of collisions, with collisions given as [vector of collider speed, point of contact, angle at contact]
    def checkCollisions(self, colliders):
        self.updateRect()
        collisions = []
        for collider in colliders:

            #should not check with self
            if collider != self:

                #ground collision case
                if collider.type == "ground":
                    nContacts = 0
                    xContactsSum=0
                    for vertex in self.vertices:
                        if vertex[1] >= collider.y:
                            xContactsSum+=vertex[0]
                            nContacts+=1
                    if nContacts>0:
                        collisions.append([[0,0],[xContactsSum/nContacts,collider.y],-math.pi/2])
                
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
    
    #move by dx dy, ignoring physics and stuff
    def move(self, dx, dy):
        self.x+=dx
        self.y+=dy
        for vertex in self.vertices:
            vertex[0]+=dx
            vertex[1]+=dy
    
    #rotate by da degrees, ignoring physics
    def rotate(self, da):
        self.angle+=da
        for vertex in self.vertices:
            x=vertex[0]-self.x
            y=vertex[1]-self.y
            a,r=toPolar(x,y)
            x,y=toComponents(a+da,r)
            vertex[0]=x+self.x
            vertex[1]=y+self.y

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

                aAcc+=tanComp*lever/1500
                if len(self.vertices)==3:
                    print(tanComp)
        #print(xAcc,yAcc, aAcc)
        
        #apply net force
        self.xVel+=xAcc
        self.yVel+=yAcc
        self.aVel+=aAcc

        #reset forces
        self.forces = [GRAVITY]

        #move
        steps = max(magnitude(self.xVel, self.yVel)/10,abs(self.aVel)/0.01)
        if len(self.vertices)==3:
            print(steps,self.aVel)
        stepSize = magnitude(self.xVel, self.yVel)/steps
        if steps > 0:
            #be wary of getting stuck between stuff,
            xStep = self.xVel/steps
            yStep = self.yVel/steps
            aStep = self.aVel/steps
            collisions = []
            while steps >= 1:
                steps-=1
                self.move(xStep,yStep)
                self.rotate(aStep)
                collisions=self.checkCollisions(shapes+ground)
                if len(collisions) > 0:
                    for i in range(20):
                        dx,dy=toComponents(collisions[0][2],stepSize/10)
                        self.move(dx,dy)
                        collisions=self.checkCollisions(shapes+ground)
                        if len(collisions)==0:
                            break
                    if len(collisions)>0:
                        print("womp")
                        self.move(-20*dx-xStep,-20*dy-yStep)
                        self.rotate(-aStep)
                        steps=0.9
                        break
            while steps > 0:
                steps -= 0.1
                self.move(xStep/10,yStep/10)
                self.rotate(aStep/10)
                collisions=self.checkCollisions(shapes+ground)
                if len(collisions) > 0:
                    self.move(-xStep/10,-yStep/10)
                    self.rotate(-aStep/10)

            if len(collisions) >0:
                for collision in collisions:
                    speed,contact,angle=collision

                    #temporary
                    a,r=toPolar(xAcc,yAcc)
                    normalMag=math.cos(a-angle)*r
                    x,y=toComponents(-angle,normalMag)
                    #print(x,y)
                    self.forces.append((x,y,contact[0]-self.x,contact[1]-self.y))

        """
        stepSize = 10
        steps = max(math.floor(magnitude(self.xVel, self.yVel)/stepSize),math.floor(self.aVel/0.1))
        if steps==0:
            stepSize=1
            steps = max(math.floor(magnitude(self.xVel, self.yVel)),math.floor(self.aVel/0.01))
        if steps>0:
            xStep = self.xVel/steps
            yStep = self.yVel/steps
            aStep = self.aVel/steps
            collisions = []

            #redo part, include friction
            for i in range(steps):
                self.move(xStep,yStep)
                self.rotate(aStep)
                collisions=self.checkCollisions(shapes+ground)
                if len(collisions) > 0:
                    self.move(-xStep,-yStep)
                    self.rotate(-aStep)
                    if stepSize==1:
                        break
                    else:
                        for i in range(10):
                            self.move(xStep/10,yStep/10)
                            self.rotate(aStep/10)
                            collisions=self.checkCollisions(shapes+ground)
                            if len(collisions) > 0:
                                self.move(-xStep/10,-yStep/10)
                                self.rotate(-aStep/10)
                                break

            if len(collisions) >0:
                for collision in collisions:
                    speed,contact=collision

                    #temporary
                    self.forces.append((0,-2,contact[0]-self.x,contact[1]-self.y))
                    """

        #self.rotate(10*math.pi/180)
        print("avel,1", self.aVel)
        self.xVel=self.x-initX
        self.yVel=self.y-initY
        self.aVel=self.angle-initA
        print(self.aVel)

        self.updateRect()

            


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

#constants
GRAVITY = (0,2,0,0)



def createRandomPolygon(color, minSides, maxSides):

    center_x = SCREENWIDTH/2
    center_y = SCREENHEIGHT/2

    radius = random.randint(50, 100)
    sides = random.randint(minSides, maxSides)

    points = []

    for i in range(sides):
        #generate random angle 
        angle = random.uniform(0, 6.28319)
        distance = random.uniform(radius/2, radius)

        x = center_x + distance * math.cos(angle)
        y = center_y + distance * math.sin(angle)
        
        points.append((x, y))

    points.sort()
    print(points)

    shape=points

    return Polygon(color, shape)


lines=[]
ground = [Ground((50,50,50), 600)]
shapes = [createRegularShape(randomColor(),3,50,SCREENWIDTH/2,SCREENHEIGHT/2),createRegularShape(randomColor(),10,50,SCREENWIDTH/2,100), createRandomPolygon(randomColor(), 3, 10)]
running = True
 
def findArea():
    pass

def centerOfMass():
    #find center of mass of a shape
    pass

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    if running:
        w.fill((255,255,255))
        lines = []
        for shape in shapes:
            shape.tick()
            shape.draw(w)
            #shape.drawForces(w)
        ground[0].draw(w)
        
        pygame.display.flip()
        c.tick(60)


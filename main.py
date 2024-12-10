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

        #find center of mass and set self.x and self.y accordingly
        ...

        #coordinates of vertices on window
        self.vertices = []
        for vertex in shape:
            self.vertices.append([vertex[0]+x,vertex[1]+y])
        
        #velocities (x,y,angle)
        self.xVel = 0
        self.yVel = -30
        self.aVel = 0

        #temporary
        self.rotate(1)
    
    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.vertices)

    #return list of collisions, with collisions given as [vector of collider speed, point of contact]
    def checkCollisions(self, colliders):
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
                        collisions.append([[0,0],[xContactsSum/nContacts,collider.y]])
                
                #polygon collision case
                elif collider.type == "polygon":
                    ...
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
        for vertex in self.vertices:
            x=vertex[0]-self.x
            y=vertex[1]-self.y
            a,r=toPolar(x,y)
            x,y=toComponents(a+da,r)
            vertex[0]=x+self.x
            vertex[1]=y+self.y

    #frame actions
    def tick(self):

        #apply forces
        self.yVel += GRAVITY

        #move
        stepSize = 10
        steps = math.floor(magnitude(self.xVel, self.yVel)/stepSize)
        if steps==0:
            stepSize=1
            steps = math.floor(magnitude(self.xVel, self.yVel))
        if steps>0:
            xStep = self.xVel/steps
            yStep = self.yVel/steps
            collisions = []
            for i in range(steps):
                self.move(xStep,yStep)
                collisions=self.checkCollisions(shapes+ground)
                if len(collisions) > 0:
                    self.move(-xStep,-yStep)
                    if stepSize==1:
                        break
                    else:
                        for i in range(10):
                            self.move(xStep/10,yStep/10)
                            collisions=self.checkCollisions(shapes+ground)
                            if len(collisions) > 0:
                                self.move(-xStep/10,-yStep/10)
                                break

            if len(collisions) >0:
                for collision in collisions:
                    speed,contact=collision
                    refAngle,lever=toPolar(contact[0]-self.x,contact[1]-self.y)
                    a,r=toPolar(speed[0]-self.xVel,speed[1]-self.yVel)
                    dirComp,tanComp = toComponents(a-refAngle,r)
                    dx,dy=toComponents(refAngle,dirComp)
                    self.xVel+=dx
                    self.yVel+=dy
                    self.aVel+=tanComp*lever
                    print(self.yVel)

                #apply forces based on collision information
                ...
        #self.rotate(10*math.pi/180)
        

            


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
screenWidth = 1000
screenHeight = 700
w = pygame.display.set_mode([screenWidth,screenHeight])
c = pygame.time.Clock()
w.fill((255,255,255))

#constants
GRAVITY = 2

ground = [Ground((0,0,0), 600)]
shapes = [createRegularShape(randomColor(),7,50,screenWidth/2,screenHeight/2)]
running = True
 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
    if running:
        w.fill((255,255,255))
        for shape in shapes:
            shape.tick()
            shape.draw(w)
        ground[0].draw(w)
        
        pygame.display.flip()
        c.tick(60)
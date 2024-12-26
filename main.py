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

#get area
def getArea(vertices):
    area = 0
    for i in range(len(vertices)):
        shoe = abs((vertices[i][0]*vertices[(i+1) % len(vertices)][1])-(vertices[(i+1) % len(vertices)][0]*vertices[i][1]))/2
        area += shoe
    print(int(area))
    return area

#get area
def getArea(vertices):
    area = 0
    for i in range(len(vertices)):
        shoe = abs((vertices[i][0]*vertices[(i+1) % len(vertices)][1])-(vertices[(i+1) % len(vertices)][0]*vertices[i][1]))/2
        area += shoe
    print(int(area))
    return area

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
        self.inertia=10000

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
        self.rotate(1)

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
                    #print(tanComp)
                    pass
                    #print(tanComp)
                    pass
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
            #print(steps,self.aVel)
            pass
        # if len(self.vertices)==3:
        #     print(steps,self.aVel)
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
                        #print("womp")
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
        #print("avel,1", self.aVel)
        # print("avel,1", self.aVel)
        self.xVel=self.x-initX
        self.yVel=self.y-initY
        self.aVel=self.angle-initA
        #print(self.aVel)
        # print(self.aVel)

        self.updateRect()

    def drawShadow(self, surface, light_source):
        shadow_color = (200, 200, 200)
        shadow_length = 10
        lx, ly = light_source  # Light source position

        # List to hold the extended shadow points
        shadow_vertices = []

        # Loop through each edge of the polygon
        for i in range(len(self.vertices)):
            # Get the current vertex and the next vertex
            current_vertex = self.vertices[i]
            next_vertex = self.vertices[(i + 1) % len(self.vertices)]

            # Calculate the direction of the shadow for each vertex
            dx1, dy1 = current_vertex[0] - lx, current_vertex[1] - ly
            dx2, dy2 = next_vertex[0] - lx, next_vertex[1] - ly

            # Project the vertices far away to simulate the shadow
            shadow_v1 = (current_vertex[0] + dx1 * shadow_length, current_vertex[1] + dy1 * shadow_length)
            shadow_v2 = (next_vertex[0] + dx2 * shadow_length, next_vertex[1] + dy2 * shadow_length)

            # Add the original and projected shadow points
            shadow_vertices.append(current_vertex)
            shadow_vertices.append(next_vertex)
            shadow_vertices.append(shadow_v2)
            shadow_vertices.append(shadow_v1)

            # Close and fill the shadow polygon
            pygame.draw.polygon(surface, shadow_color, [current_vertex, next_vertex, shadow_v2, shadow_v1])

        
        


    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.vertices)

    


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
    def draw(self,w,forces=False,shadows=False,shadowPos=(0,0)):
        if shadows:
            for shape in self.shapes:
                shape.drawShadow(w,shadowPos)
        for shape in self.shapes:
            shape.draw(w)
        for collider in self.staticColliders:
            collider.draw(w)
        if forces:
            self.drawForces(w)
    
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

#constants
GRAVITY = (0,2,0,0)

def centerOfMass(vertices):
    area = getArea(vertices)
    vertices = list(vertices)
    x = []
    y = []
    xCenter = []
    yCenter = []
    #split the tuple into a list of x and list of y
    for i in range(len(vertices)):
        xVertex, yVertex = vertices[i]
        x.append(xVertex)
        y.append(yVertex)

    #complete the summations for x and y coordinates
    for i in range (len(x) - 1):
        point = (x[i] + x[i+1]) * (x[i] * y[i+1] - x[i+1] * y[i])
        xCenter.append(point)
    for i in range(len(y) - 1):
        point = (y[i] + y[i+1]) * (x[i] * y[i+1] - x[i+1] * y[i])
        yCenter.append(point)
    yCenter = sum(yCenter)
    xCenter = sum(xCenter)

    #multiply by 1 over 6 * the Area
    xCenter = xCenter * (1 / (6 * getArea(vertices)))
    yCenter = yCenter * (1 / (6 * getArea(vertices)))

    print(xCenter, yCenter)


def createRandomPolygon(color, minSides, maxSides):

    center_x = 0
    center_y = 0

    radius = random.randint(50, 100)
    sides = random.randint(minSides, maxSides)

    points = []

    angles = sorted([random.uniform(0, 6.28319) for i in range(sides)])

    # angle = random.uniform(0, 6.28319)

    for angle in angles:
        
        distance = random.uniform(radius/2, radius)

        x = center_x + distance * math.cos(angle)
        y = center_y + distance * math.sin(angle)
        
        points.append((x, y))

    shape=points
    centerOfMass(shape)
    return Polygon(color, shape, SCREENWIDTH/2, SCREENHEIGHT/2)


lines=[]
ground = [Ground((50,50,50), 600)]
shapes = [createRegularShape(randomColor(),3,50,SCREENWIDTH/2,SCREENHEIGHT/2),createRegularShape(randomColor(),10,50,SCREENWIDTH/2,100), createRandomPolygon(randomColor(),3,10)]
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
        physics.draw(w, shadows=True, shadowPos=(0,0))

        #update screen and tick
        pygame.display.flip()
        c.tick(fps)
        
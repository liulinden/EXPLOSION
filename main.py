#Screams
print("AAAAAAAAAAAAAAA")

#Imports
import random
import pygame
import math
import time
pygame.init()

# Basic Functions

exp = False

#
def magnitude(cx,cy):
    return math.sqrt(cx**2+cy**2)

def randomColor():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Convert regular to polar coordinates
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

# Convert polar to regular coordinates
def toComponents(angle,r):
    return r*math.cos(angle), r*math.sin(angle)

#get area
def getArea(vertices):
    area = 0
    for i in range(len(vertices)):
        shoe = abs((vertices[i][0]*vertices[(i+1) % len(vertices)][1])-(vertices[(i+1) % len(vertices)][0]*vertices[i][1]))/2
        area += shoe
    print(int(area))
    return area

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
    
    def getEssentialMass(self, a,b,c,maxDepth=0):
        return -1

#wall class
class Wall:
    def __init__(self, color, x, facingRight=True):
        self.type = "wall"
        if facingRight:
            self.type+="Left"
        else:
            self.type+="Right"        
        self.color= color
        self.x = x
        self.y = 0
        self.xVel=0
        self.yVel=0
        self.aVel=0
        self.mass=-1
    
    def draw(self, w):
        if self.type=="wallRight":
            pygame.draw.rect(w, self.color, pygame.Rect(self.x,0,w.get_width()-self.x,w.get_height()))
        else:
            pygame.draw.rect(w, self.color, pygame.Rect(0,0,self.x,w.get_height()))
    
    def getEssentialMass(self, a,b,c,maxDepth=0):
        return -1


#polygon class
class Polygon:
    def __init__(self, color, shape, x=0, y=0):
        global id
        
        self.type = "polygon"
        self.id = id

        self.color = color

        #relative position from initial position
        self.x=x
        self.y=y
        self.angle=0

        #particleness
        self.tater = 150

        #inertia is fakely calculated
        self.mass=getArea(shape)
        self.inertia=math.pow(self.mass,2)*5
        print(self.mass)

        #find center of mass and set self.x and self.y accordingly
        offsetX,offsetY=centerOfMass(shape)

        #offset vertex coordinates
        self.vertices = []
        for vertex in shape:
            self.vertices.append([vertex[0]+x-offsetX,vertex[1]+y-offsetY])

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
    
    def rotationalForce(self,x,y):
        return toComponents(self.angle+math.pi/2,self.inertia*self.aVel/magnitude(x,y)/self.mass)

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

    #def drawForces(self,surface):
    #    for force in self.forces:
    #        pygame.draw.line(surface,(255,0,0),(self.x+force[3],self.y+force[4]),(self.x+force[3]+10*force[1],self.y+force[4]+10*force[2]))

    #return list of collisions, with collisions given as [collider object, point of contact, normal angle at contact]

    def checkCollisions(self, colliders):
        global tater
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
                elif collider.type in ["wallRight", "wallLeft"]:
                    dir=-1
                    if collider.type=="wallRight":
                        dir=1
                    collided=False
                    for vertex in self.vertices:
                        if vertex[0]*dir >= collider.x*dir:
                            collided = True
                            break
                    if collided:
                        nContacts = 0
                        yContactsSum=0
                        for vertex in self.vertices:
                            if vertex[0]*dir >= collider.x*dir - 1:
                                yContactsSum+=vertex[1]
                                nContacts+=1
                        if nContacts>0:
                            collisions.append([collider,[collider.x,yContactsSum/nContacts],math.pi/2*(1+dir)])
                        

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
       
        current_time = pygame.time.get_ticks()
        cooldown = 100
        if len(collisions) > 0 and current_time - self.tater > cooldown:
            for collision in collisions:
                particles.extend(createParticles(collision[1][0], collision[1][1], num_particles = 3))
            self.tater = current_time


                
                

        return collisions
    
    #move by dx dy and rotate by da, ignoring physics
    def transform(self, dx,dy,da):
        self.move(dx,dy)
        self.rotate(da)
        self.updateRect()
    
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
        physics.forces.append([force[3]+self.x,force[4]+self.y,force[1]/force[5]/300,force[2]/force[5]/300])
    
        #print(physics.forces)
        #self.xVel+=force[1]/self.mass
        #self.yVel+=force[2]/self.mass
        if (force[3]!=0 or force[4]!=0):
            #print(physics.forces)
            refAngle,lever=toPolar(force[3],force[4])
            a,r=toPolar(force[1],force[2])
            dirComp,tanComp = toComponents(a-refAngle,r)

            #probably should be +=
            #self.aVel+=tanComp*lever/self.inertia
            da=tanComp*lever/self.inertia
            self.aVel+=da
            #if da*self.aVel<0:
            #    self.aVel+=da
            #else:
            #    self.aVel=max(self.aVel,da)
            
            dx,dy=toComponents(math.pi+refAngle,r)
            self.xVel+=dx/self.mass
            self.yVel+=dy/self.mass
        else:
            self.xVel+=force[1]/self.mass
            self.yVel+=force[2]/self.mass

    def getEssentialMass(self, colliders, dx,dy,maxDepth=5):
        if maxDepth==0:
            return self.mass
        essentialMass=self.mass
        self.transform(dx,dy,0)
        collisions=self.checkCollisions(colliders)
        for collision in collisions:
            eMass2=collision[0].getEssentialMass(colliders, dx, dy, maxDepth-1)
            if eMass2==-1:
                essentialMass=-1
                break
            else:
                essentialMass+=eMass2
        self.transform(-dx,-dy,0)
        return essentialMass


    #simulate physics for ms milliseconds
    def simulate(self, physics, ms):

        #convert to seconds
        s=ms/1000

        #apply gravity
        self.applyForce(['gravity',0,physics.g*self.mass*s,0,0,ms])

        #simulate linear motion
        self.simulateLinearMotion(physics,ms)
        self.simulateRotationalMotion(physics,ms)

        #safeguard
        if self.maxMovement() > 10000:
            print(self.xVel,self.yVel,self.aVel, physics.forces)
            physics.shapes.remove(self)

    #linear motion
    def simulateLinearMotion(self,physics,ms):

        #convert to seconds
        s=ms/1000

        #move shape
        self.transform(self.xVel*s,self.yVel*s,0)

        #check collisions
        colliders=physics.shapes+physics.staticColliders
        collisions = self.checkCollisions(colliders)

        #collision
        if len(collisions) > 0:
            self.transform(-self.xVel*s,-self.yVel*s,0)
            #TODO UNREVISED apply forces
            for collision in collisions:
                collider, contact, angle = collision

                #get net velocities at point of contact
                colliderXVel, colliderYVel = 0, 0
                if collider.type=="polygon":
                    colliderXVel, colliderYVel = collider.getPointVel(contact[0],contact[1])
                netXVel, netYVel = self.getPointVel(contact[0],contact[1])

                #get rid of net
                netXVel,netYVel = self.xVel,self.yVel
                if collider.type=="polygon":
                    colliderXVel, colliderYVel = collider.xVel, collider.yVel

                
                #isolate relevant velocities
                a,r=toPolar(netXVel, netYVel)
                netVel, trash = toComponents(a-angle,r)
                a,r=toPolar(colliderXVel, colliderYVel)
                colliderVel, trash = toComponents(a-angle,r)
                
                dx,dy=math.cos(angle),math.sin(angle)
                mass1,mass2=self.getEssentialMass(colliders,dx,dy),collider.getEssentialMass(colliders,dx,dy)
                
               

                #calculate force
                if mass1==-1:
                    if mass2==-1:
                        #stop speed cuz stuck
                        #dx,dy=toComponents(angle,netVel)
                        #self.xVel-=dx/self.mass
                        #self.yVel-=dy/self.mass
                        force=0
                    else:
                        force=-(1+physics.elasticity)*mass2*(colliderVel-netVel)
                else:
                    if mass2==-1:
                        force = (1+physics.elasticity)*mass1*(netV el-colliderVel)
                    else:
                        force=-(1+physics.elasticity)*mass1*mass2*(colliderVel-netVel)/(mass1+mass2)

                forceX, forceY = toComponents(angle,force)
                #print(forceX,forceY)
                #print(self.yVel,netVel,self.yVel*self.mass,forceY,"\n")
                #add forces
                if mass1!=-1:
                    self.applyForce(['N',-forceX,-forceY,contact[0]-self.x,contact[1]-self.y,ms])
                if mass2!=-1:
                    collider.applyForce(['N',forceX,forceY,contact[0]-collider.x,contact[1]-collider.y,ms])
                elif mass1==-1:
                    print(angle, "both unmoveables??? what the heck????")
    
    #linear motion
    def simulateRotationalMotion(self,physics,ms):
        #return
        #convert to seconds
        s=ms/1000
        print(self.aVel*s)
        #move shape
        self.transform(0,0,self.aVel*s)

        #check collisions
        colliders=physics.shapes+physics.staticColliders
        collisions = self.checkCollisions(colliders)

        #collision
        if len(collisions) > 0:
            self.transform(0,0,-self.aVel*s)
            #TODO UNREVISED apply forces
            for collision in collisions:
                collider, contact, angle = collision
                
                #break
                #get net velocities at point of contact
                colliderXVel, colliderYVel = 0, 0
                if collider.type=="polygon":
                    colliderXVel, colliderYVel = collider.rotationalForce(contact[0]-collider.x,contact[1]-collider.y)
                netXVel, netYVel = self.rotationalForce(contact[0]-collider.x,contact[1]-collider.y)
                print(netXVel,netYVel)
                
                if netYVel>0:
                    #isolate relevant velocities
                    a,r=toPolar(netXVel, netYVel)
                    netVel, trash = toComponents(a-angle,r)
                    a,r=toPolar(colliderXVel, colliderYVel)
                    colliderVel, trash = toComponents(a-angle,r)

                    dx,dy=math.cos(angle),math.sin(angle)
                    mass1,mass2=self.getEssentialMass(colliders,dx,dy),collider.getEssentialMass(colliders,dx,dy)
                    

                    #calculate force
                    if mass1==-1:
                        if mass2==-1:
                            force=0
                        else:
                            force=-(1+physics.elasticity)*mass2*(colliderVel-netVel)
                    else:
                        if mass2==-1:
                            force = (1+physics.elasticity)*mass1*(netVel-colliderVel)
                        else:
                            force=-(1+physics.elasticity)*mass1*mass2*(colliderVel-netVel)/(mass1+mass2)

                    forceX, forceY = toComponents(angle,force)
                    
                    print(forceX,forceY)
                    print()
                    if mass1!=-1:
                        self.applyForce(['N',-forceX,-forceY,contact[0]-self.x,contact[1]-self.y,ms])
                    if mass2!=-1:
                        collider.applyForce(['N',forceX,forceY,contact[0]-collider.x,contact[1]-collider.y,ms])
                    elif mass1==-1:
                        print(angle, "both unmoveables??? what the heck????")
                
                
    def maxMovement(self):
        return magnitude(self.xVel,self.yVel)+abs(self.aVel)*self.radius

    def drawShadow(self, surface, light_source,color=(200,200,200)):
        shadow_length = 10
        lx, ly = light_source  # Light source position

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

            # Close and fill the shadow polygon
            pygame.draw.polygon(surface, color, [current_vertex, next_vertex, shadow_v2, shadow_v1])

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.vertices)

    def split(self):
        ...

#overarching class
class Physics:

    #setup
    def __init__(self, GRAVITY=2000, startShapes=[Ground((0,0,0),650),Wall((0,0,0),40),Wall((0,0,0),960,False)]):
        self.shapes = []
        self.time = 0
        self.g = GRAVITY
        self.staticColliders = startShapes
        self.elasticity = 0
    
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
                maxStepSize=3
                stepTime = min(stepTime,maxStepSize*1000/max(1,shape.maxMovement()))
            
            #update time
            frameTime += stepTime

            #simulate shapes for stepTime milliseconds
            for shape in self.shapes:
                shape.simulate(self, stepTime)
        
        #update physics time
        self.time += finishTime
    
    #draw shapes and colliders
    def draw(self,w,forces=False,shadows=False,particles=False,lightPos=(0,0),light=False,shadowColor=(200,200,200)):
        if shadows:
            if light:
                w.fill((0,0,0))
                x,y=lightPos
                offsetX,offsetY=light.get_width()/2,light.get_height()/2
                w.blit(light,(x-offsetX,y-offsetY))
            for shape in self.shapes:
                shape.drawShadow(w,lightPos,color=shadowColor)
        for shape in self.shapes:
            shape.draw(w)
        if particles:
            for particle in particles:
                particle.draw(w)
        for collider in self.staticColliders:
            collider.draw(w)
        if forces:
            self.drawForces(w)
    
    #draw forces
    def drawForces(self,w):
        for force in self.forces:
            pygame.draw.line(w,(255,0,0),(force[0],force[1]),(force[0]+force[2],force[1]+force[3]))

    def addRegularShape(self, sides, radius):
        ...


    def addShape(self, vertices):
        ...

class Particle:



    def __init__(self, x, y, exp, color = (255, 255, 255)):
        self.exp = exp
        if exp == False:
        # Regular particle attributes
            self.x = x
            self.y = y
            self.color = color
            self.size = random.randint(3, 9)
            self.xVel = random.choice(range(-15, 0)) + random.choice(range(1, 16))
            self.yVel = random.choice(range(-15, 0)) + random.choice(range(1, 16))
            self.creation_time = time.time()
            # def draw(self, surface):
                # Draw the regular particle as a circle


        else:
            # Explosion particle attributes
            self.x = x
            self.y = y
            self.color = random.choice([(255, 255, 0), (255, 0, 0), (255, 165, 0)]) 
            self.size = random.randint(10, 20)
            self.xVel = random.choice(range(-6, 0)) + random.choice(range(1, 7))
            self.yVel = random.choice(range(-6, 0)) + random.choice(range(1, 7))
            self.creation_time = time.time()
            # def draw(self, surface):


    def draw(self, surface):
        if self.exp:
           # Calculate angle based on velocity for explosion particles
            angle = math.atan2(self.yVel, self.xVel)
            # Triangle vertices
            point1 = (self.x + self.size * math.cos(angle), self.y + self.size * math.sin(angle))
            point2 = (self.x + self.size * math.cos(angle + math.radians(120)),
                    self.y + self.size * math.sin(angle + math.radians(120)))
            point3 = (self.x + self.size * math.cos(angle - math.radians(120)),
                    self.y + self.size * math.sin(angle - math.radians(120)))
            # Draw the triangle
            pygame.draw.polygon(surface, self.color, [point1, point2, point3])
        else: 
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
            


    def move(self):
        # Update position for regular particles
        self.x += self.xVel
        self.y += self.yVel




    def is_expired(self):
        # Check if the particle has exceeded its lifespan
        return time.time() - self.creation_time > 0.3


# Function to create particles originating from the center of the screen
def createParticles(center_x, center_y, num_particles=3):
    return [Particle(center_x, center_y,False) for i in range(num_particles)]

def expcreateParticles(center_x, center_y, num_particles=13):
    out=[]
    for i in range(num_particles):
        out+=[Particle(center_x, center_y,True),Particle(center_x, center_y,False)]
    return out

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
    xCenter = xCenter * (1 / (6 * area))
    yCenter = yCenter * (1 / (6 * area))

    return xCenter, yCenter


#create random polygon
def createRandomPolygon(color, minSides, maxSides,shapeX,shapeY):

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

    return Polygon(color, points, shapeX,shapeY)

def createRegularShape(color, sides, radius=1, x=0,y=0):
    #make function that creates a list of points according to parameters
    
    shape=[]
    for i in range(sides):
        arg= math.pi*2*(1/4+1/2/sides+i/sides)
        shape.append((math.cos(arg)*radius,math.sin(arg)*radius))
    return Polygon(color, shape,x,y)

#setup
SCREENWIDTH = 1000
SCREENHEIGHT = 700
w = pygame.display.set_mode((SCREENWIDTH,SCREENHEIGHT))
center_x, center_y = SCREENWIDTH // 2, SCREENHEIGHT // 2
c = pygame.time.Clock()
w.fill((255,255,255))
FPS=80
physics = Physics()
physics.shapes.append(createRegularShape(randomColor(),5,50,SCREENWIDTH/2,SCREENHEIGHT/2))
image = pygame.image.load('circlegradient.png')
image = pygame.transform.scale(image, (image.get_width() * 2.5, image.get_height() * 2.5))
#particles = createParticles(center_x, center_y, False, 5)
particles=[]
#setup vars
lines=[]
running = True



#main loop
while running:

    #check for closing window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False

        #new shape
        if event.type == pygame.MOUSEBUTTONDOWN:
            x,y=pygame.mouse.get_pos()
            physics.shapes.append(createRegularShape(randomColor(),random.randint(3,7),50,x,y))
            #physics.shapes.append(createRandomPolygon(randomColor(),3,10,x,y))
            particles.extend(expcreateParticles(x, y, num_particles = 8))

            


    # Update particles
    particles = [particle for particle in particles if not particle.is_expired()]
    for particle in particles:
        particle.move()
        
    #frame stuff
    if running:

        #
        # 
        #  physics, increase argument here for slow mo
        physics.tick(FPS)
        #render screen
        w.fill((255,255,255))

        
        physics.draw(w, shadows=True,particles=False,light=image,shadowColor=(0,0,0),lightPos=(SCREENWIDTH/2,-100),forces=True)
        
        
        

        #update screen and tick
        pygame.display.flip()
        c.tick(FPS)
        
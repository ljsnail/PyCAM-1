from Point import *
from Plane import *
from utils import *
from Line import *

ORIENTATION_CCW = 2
ORIENTATION_CW  = 3

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except:
    pass

class Triangle:
    id = 0
    # points are expected to be in ClockWise order
    def __init__(self, p1=None, p2=None, p3=None, e1=None, e2=None, e3=None):
        self.id = Triangle.id
        Triangle.id += 1
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        if (not e1) and p1 and p2:
            self.e1 = Line(p1,p2)
        else:
            self.e1 = e1
        if (not e2) and p2 and p3:
            self.e2 = Line(p2,p3)
        else:
            self.e2 = e2
        if (not e3) and p3 and p1:
            self.e3 = Line(p3,p1)
        else:
            self.e3 = e3

    def __repr__(self):
        return "Triangle%d<%s,%s,%s>" % (self.id,self.p1,self.p2,self.p3)

    def name(self):
        return "triangle%d" % self.id

    def to_OpenGL(self):
        glBegin(GL_TRIANGLES)
        glVertex3f(self.p1.x, self.p1.y, self.p1.z)
        glVertex3f(self.p2.x, self.p2.y, self.p2.z)
        glVertex3f(self.p3.x, self.p3.y, self.p3.z)
        glEnd()
        if False: # display surface normals
            n = self.normal()
            c = self.center()
            d = 0.5
            glBegin(GL_LINES)
            glVertex3f(c.x, c.y, c.z)
            glVertex3f(c.x+n.x*d, c.y+n.y*d, c.z+n.z*d)
            glEnd()
        if False and hasattr(self, "_middle"): # display bounding sphere
            glPushMatrix()
            glTranslate(self._middle.x, self._middle.y, self._middle.z)
            if not hasattr(self,"_sphere"):
                self._sphere = gluNewQuadric()
            gluSphere(self._sphere, self._radius, 10, 10)
            glPopMatrix()
        if True: # draw triangle id on triangle face
            glPushMatrix()
            cc = glGetFloatv(GL_CURRENT_COLOR)
            c = self.center()
            glTranslate(c.x,c.y,c.z)
            p12=self.p1.add(self.p2).mul(0.5)
            p3_12=self.p3.sub(p12).normalize()
            p2_1=self.p1.sub(self.p2).normalize()
            pn=p2_1.cross(p3_12)
            glMultMatrixf((p2_1.x, p2_1.y, p2_1.z, 0, p3_12.x, p3_12.y, p3_12.z, 0, pn.x, pn.y, pn.z, 0, 0,0,0,1))
            n = self.normal().mul(0.01)
            glTranslatef(n.x,n.y,n.z)
            glScalef(0.003,0.003,0.003)
            w = 0
            for ch in str(self.id):
                w += glutStrokeWidth(GLUT_STROKE_ROMAN, ord(ch))
            glTranslate(-w/2,0,0)
            glColor4f(1,1,1,0)
            for ch in str(self.id):
                glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
            glPopMatrix()
            glColor4f(cc[0],cc[1],cc[2],cc[3])

        if False: # draw point id on triangle face
            cc = glGetFloatv(GL_CURRENT_COLOR)
            c = self.center()
            p12=self.p1.add(self.p2).mul(0.5)
            p3_12=self.p3.sub(p12).normalize()
            p2_1=self.p1.sub(self.p2).normalize()
            pn=p2_1.cross(p3_12)
            n = self.normal().mul(0.01)
            for p in (self.p1,self.p2,self.p3):
                glPushMatrix()
                pp = p.sub(p.sub(c).mul(0.3))
                glTranslate(pp.x,pp.y,pp.z)
                glMultMatrixf((p2_1.x, p2_1.y, p2_1.z, 0, p3_12.x, p3_12.y, p3_12.z, 0, pn.x, pn.y, pn.z, 0, 0,0,0,1))
                glTranslatef(n.x,n.y,n.z)
                glScalef(0.001,0.001,0.001)
                w = 0
                for ch in str(p.id):
                    w += glutStrokeWidth(GLUT_STROKE_ROMAN, ord(ch))
                    glTranslate(-w/2,0,0)
                glColor4f(0.5,1,0.5,0)
                for ch in str(p.id):
                    glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
                glPopMatrix()
            glColor4f(cc[0],cc[1],cc[2],cc[3])

    def normal(self):
        if not hasattr(self, '_normal'):
            # calculate normal, if p1-p2-pe are in clockwise order
            self._normal = self.p3.sub(self.p1).cross(self.p2.sub(self.p1))
            denom = self._normal.norm()
            self._normal = self._normal.div(denom)
        return self._normal

    def plane(self):
        if not hasattr(self, '_plane'):
            self._plane=Plane(self.center(), self.normal())
        return self._plane

    def point_inside(self, p):
        # http://www.blackpawn.com/texts/pointinpoly/default.html

        # Compute vectors
        v0 = self.p3.sub(self.p1)
        v1 = self.p2.sub(self.p1)
        v2 = p.sub(self.p1)

        # Compute dot products
        dot00 = v0.dot(v0)
        dot01 = v0.dot(v1)
        dot02 = v0.dot(v2)
        dot11 = v1.dot(v1)
        dot12 = v1.dot(v2)

        # Compute barycentric coordinates
        denom = dot00 * dot11 - dot01 * dot01
        # originally, "u" and "v" are multiplied with "1/denom"
        # we don't do this, to avoid division by zero (for triangles that are "almost" invalid)
        u = dot11 * dot02 - dot01 * dot12
        v = dot00 * dot12 - dot01 * dot02

        # Check if point is in triangle
        return ((u * denom) > 0) and ((v * denom) > 0) and (u + v < denom)

    def minx(self):
        if not hasattr(self, "_minx"):
            self._minx = min3(self.p1.x, self.p2.x, self.p3.x)
        return self._minx

    def miny(self):
        if not hasattr(self, "_miny"):
            self._miny = min3(self.p1.y, self.p2.y, self.p3.y)
        return self._miny

    def minz(self):
        if not hasattr(self, "_minz"):
            self._minz = min3(self.p1.z, self.p2.z, self.p3.z)
        return self._minz

    def maxx(self):
        if not hasattr(self, "_maxx"):
            self._maxx = max3(self.p1.x, self.p2.x, self.p3.x)
        return self._maxx

    def maxy(self):
        if not hasattr(self, "_maxy"):
            self._maxy = max3(self.p1.y, self.p2.y, self.p3.y)
        return self._maxy

    def maxz(self):
        if not hasattr(self, "_maxz"):
            self._maxz = max3(self.p1.z, self.p2.z, self.p3.z)
        return self._maxz

    def center(self):
        if not hasattr(self, "_center"):
            self._center = self.p1.add(self.p2).add(self.p3).mul(1.0/3)
        return self._center

    def middle(self):
        if not hasattr(self, "_middle"):
            self.calc_circumcircle()
        return self._middle

    def radius(self):
        if not hasattr(self, "_radius"):
            self.calc_circumcircle()
        return self._radius

    def radiussq(self):
        if not hasattr(self, "_radiussq"):
            self.calc_circumcircle()
        return self._radiussq

    def calc_circumcircle(self):
        normal = self.p2.sub(self.p1).cross(self.p3.sub(self.p2))
        denom = normal.norm()
        self._radius = (self.p2.sub(self.p1).norm()*self.p3.sub(self.p2).norm()*self.p3.sub(self.p1).norm())/(2*denom)
        self._radiussq = self._radius*self._radius
        denom2 = 2*denom*denom;
        alpha = self.p3.sub(self.p2).normsq()*(self.p1.sub(self.p2).dot(self.p1.sub(self.p3))) / (denom2)
        beta  = self.p1.sub(self.p3).normsq()*(self.p2.sub(self.p1).dot(self.p2.sub(self.p3))) / (denom2)
        gamma = self.p1.sub(self.p2).normsq()*(self.p3.sub(self.p1).dot(self.p3.sub(self.p2))) / (denom2)
        self._middle = Point(self.p1.x*alpha+self.p2.x*beta+self.p3.x*gamma,
                             self.p1.y*alpha+self.p2.y*beta+self.p3.y*gamma,
                             self.p1.z*alpha+self.p2.z*beta+self.p3.z*gamma)

    def subdivide(self, depth):
        sub = []
        if depth == 0:
            sub.append(self)
        else:
            p4 = self.p1.add(self.p2).div(2)
            p5 = self.p2.add(self.p3).div(2)
            p6 = self.p3.add(self.p1).div(2)
            sub += Triangle(self.p1,p4,p6).subdivide(depth-1)
            sub += Triangle(p6,p5,self.p3).subdivide(depth-1)
            sub += Triangle(p6,p4,p5).subdivide(depth-1)
            sub += Triangle(p4,self.p2,p5).subdivide(depth-1)
        return sub


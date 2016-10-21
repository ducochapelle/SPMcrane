# square and cubic symbols require UTF-8-BOM encoding???
# is this my final push to python 3?
from math import sin, cos, pi
import xml.etree.ElementTree as ET
import subprocess, csv, sqlite3
elemnumbers = [0]
nodenumbers = [0]
mecway = r"C:\Program Files (x86)\Mecway\Mecway5\x64\mecway.exe"
def nodes(children, unit):
    if unit == "um": unit = 1000000.
    if unit == "mm": unit = 1000.
    if unit == "m":  unit = 1.
    for nodes in children:
        a,b,c,d = nodes
        nodenumbers.append(a)
        b,c,d = map(lambda x: x/float(unit), [b,c,d])
        a,b,c,d = map(str,[a,b,c,d])
        ET.SubElement(liml,"node", nid=a,x=b,y=c,z=d)
    for n in range(min(nodenumbers),max(nodenumbers)):
        if n in nodenumbers:
            continue
        else:
            ET.SubElement(liml,"node",nid=str(n),x="0",y="0",z="0")        
def elems(mother,children,shape="line2"):
    for elems in children:
        if len(elems)==1:
            a = max(elemnumbers)+1
            b = shape
            c = elems[0]
        elif len(elems)==2:
            a = max(elemnumbers)+1
            b,c = elems
        elif len(elems)==3:
            a,b,c = elems
        elemnumbers.append(a)    
        ET.SubElement(mother,"elem",eid=str(a),shape=b,nodes=c)
def modify(dof,a,nodes):
    new_nodes = []
    for node in nodes:
        n,x,y,z = node
        if dof == "rotz":
            x, y = x*cos(a)-y*sin(a), x*sin(a)+y*cos(a)
        elif dof == "rotx":
            y, z = y*cos(a)-z*sin(a), y*sin(a)+z*cos(a)
        elif dof == "roty":
            z, x = z*cos(a)-x*sin(a), z*sin(a)+x*cos(a)
        elif dof == "ux":
            x += a
        elif dof == "uy":
            y += a
        elif dof == "uz":
            z += a
        else:
            print "Unknown DOF in modify:", dof
            raise
        new_nodes.append([n,x,y,z])
    return new_nodes
def nodeselection(name1, nodes):
    sele =  ET.SubElement(liml,"nodeselection",
                      name=name1,
                      direct="true")
    for n in nodes.split():
        node =  ET.SubElement(sele,"node",nid=n)
def force(name,x,y,z):
    s = ET.SubElement(liml,"force",selection=name)
    ET.SubElement(s,"x").text = x
    ET.SubElement(s,"y").text = y
    ET.SubElement(s,"z").text = z
def gravity(x,y,z):
    s = ET.SubElement(liml,"gravity")
    ET.SubElement(s,"x").text = x
    ET.SubElement(s,"y").text = y
    ET.SubElement(s,"z").text = z
def displacement(name,value,x,y,z):
    s = ET.SubElement(liml,"displacement",selection=name)
    ET.SubElement(s,"value").text = value
    ET.SubElement(s,"x").text = str(x)
    ET.SubElement(s,"y").text = str(y)
    ET.SubElement(s,"z").text = str(z)
def coupling(dof1,node1,node2):
    ce = ET.SubElement(liml,"constraintequation")
    term = ET.SubElement(ce,"term",coefficient="1 1/m",
                     nid=str(node1),dof=dof1)
    term = ET.SubElement(ce,"term",coefficient="-1 1/m",
                     nid=str(node2),dof=dof1)
def table(mother,filename1, elem=False):
    a = ["m","m","m","m",u"°",u"°",u"°","kN","N","N","N.m","N.m","N.m","MPa","MPa","MPa","MPa","MPa",u"°","N","N","N","N","N.m","N.m","N.m","N.m"]
    b = ["displmag","displx","disply","displz","rotx","roty","rotz","tensileforce","sheary","shearz","torsion","bendingmomy","bendingmomz","stresspt1","stresspt2","stresspt3","stresspt4","stressptu","twistangle","reactionforcemag","reactionforcex","reactionforcey","reactionforcez","reactionmommag","reactionmomx","reactionmomy","reactionmomz"]
    table = ET.SubElement(mother,"table")
    component = ET.SubElement(table, "component").text = "Default"
    for n in zip(a,b):
        ET.SubElement(table, "fieldvalue", unit=n[0]).text = n[1]
    if elem:
        ET.SubElement(table, "materials")
        ET.SubElement(table, "elementvalues")
    ET.SubElement(table, "coordinates")
    ET.SubElement(table, "saveonsolve", filename=filename1)
    
#------------#
# PARAMETERS #
#------------#

#
alfa = pi/3.
beta = pi*2./3.

# NODE NUMBERS
#          4    5   
#          14 15  
#       3         6                             
#        13     16                
#    2              7             
#     12             8          
# 1                         
#11                          
#   19                       
#   (21,22,23,24,25,26,29) equivalent on other side where applicable               


# Members: lenghts sort of arbitrary
blfp = 3*5800+500-112+1000  # boom tip from pivot
jrtt = 3*5800+500-3500+112  # jib rotationpoint to tip
jahw = 760                  # jib actuator half width (the length between the two)
jphw = 650                  # jib pivot half width
bahw = 1202                 # boom actuator half width
bphw = 1202                 # boom pivot half width

# Actuators will take up equal force though#
jahw = 1e-12
bahw = 1e-12

# Mechanism: Following parameters taken from CAD drawing
btta = 6199 # boom tip to actuator
bctr = 730 # boom centerlinte to rotatejib
bcta = 730+537 # boom centerline to actuator
jrax = 2046.489*cos(37.152/180*pi) # Jib Rotationpoint to Actuator dX
jray = 2046.489*sin(37.152/180*pi) # Jib Rotationpoint to Actuator dY


# Actuators: Choosen out of CAD drawing and excel
# Original, estimated from drawing
brod = 160 # boom actuator rod diametert
bpush = -1000e3 # push and pull capacities
bpull =   500e3 # push and pull capacities
brod = 220
bpush = -1689e3
bpull = 891e3
jrod = 250 # jib actuator rod diameter
jpush = -2138e3 # push and pull capacities
jpull =  1107e3 # push and pull capacities


def INITIALIZATION():
    global liml
    liml =  ET.Element("liml", version="5")
    anal =  ET.SubElement(liml, "analysis", type="S30")

def MATERIALS():
    global elset
    mat =   ET.SubElement(liml,"mat",name="Material")
    geo =   ET.SubElement(mat,"geometric",
                type="RectTube",
                recta="1.5 m", 
                rectb="0.8 m", 
                rectthickness="0.01 m")
    mech =  ET.SubElement(mat,"mechanical",
                type="Isotropic", 
                youngsmodulus="210 GPa", 
                poissonratio="0.3", 
                density=u"7860 kg/m³")
    elset = ET.SubElement(liml,"elset",
                name="Default", 
                color="-6710887", 
                material="Material")

def MESH(alfa,beta):
    boom = [[1,0,0,0],
            [11,0, bphw,0],
            [21,0,-bphw,0],
            [ 2,750+5730,0,0],
            [12,5800, bahw,-1450],
            [22,5800,-bahw,-1450],
            [ 3,blfp-btta,0,0],
            [13,blfp-btta, jahw,-bcta],
            [23,blfp-btta,-jahw,-bcta],
            [ 4,blfp,0,0],
            [14,blfp, jphw,-bctr],
            [24,blfp,-jphw,-bctr]]
    jib =  [[ 5,0,0,0],
            [15,0, jphw,-bctr],
            [25,0,-jphw,-bctr],
            [ 6,jrax,   0,    0],
            [16,jrax, jahw,-bctr+jray],
            [26,jrax,-jahw,-bctr+jray],
            [ 7,jrtt,0,0],
            [ 8,jrtt+1000,0,500]]
    ground=[[19,1300, bahw,-2500],
            [29,1300,-bahw,-2500]]

    boom = modify("roty",-alfa,boom)
    jib  = modify(  "uz", bctr, jib)
    jib  = modify("roty",pi-beta,  jib)
    jib  = modify(  "uz",-bctr, jib)
    jib  = modify(  "ux", blfp, jib)
    jib  = modify("roty",-alfa, jib)

    nodes(boom+jib+ground, "mm")      
    elems(elset,[["1 2"],
                 ["2 3"],
                 ["3 4"],
                 ["1 11"],
                 ["1 21"],
                 ["2 12"],
                 ["2 22"],
                 ["3 13"],
                 ["3 23"],
                 ["4 14"],
                 ["4 24"],
                 ["5 6"],
                 ["6 7"],
                 ["7 8"],
                 ["6 16"],
                 ["6 26"],
                 ["5 15"],
                 ["5 25"],
                 ["19 12"],
                 ["29 22"],
                 ["13 16"],
                 ["23 26"]])

def RELATIONS():
    nodeselection("dxyz","19 21 29")
    nodeselection("dxz","11")
    displacement("dxyz","0",1,0,0)
    displacement("dxyz","0",0,1,0)
    displacement("dxyz","0",0,0,1)
    displacement("dxz","0",1,0,0)
    displacement("dxz","0",0,0,1)
    coupling("ux",14,15)
    coupling("uz",14,15)
    coupling("ux",24,25)
    coupling("uy",24,25)
    coupling("uz",24,25)
    gravity(u"0 m/s²",u"0 m/s²",u"9.806 m/s²")

def SOLUTION():
    solu =  ET.SubElement(liml,"solution")
    anal =  ET.SubElement(solu, "analysis", type="S30")
    elset = ET.SubElement(solu,"elset",
                name="Default", 
                color="-6710887")
    table(solu,"nodes.csv")
    table(solu,"elems.csv",elem=True)

def OUTPUT(filename):
    from xml.dom import minidom
    xmlstr = minidom.parseString(ET.tostring(liml)).toprettyxml(indent="   ")
    with open(filename, "w") as f:
        f.write(xmlstr.encode('utf8'))

def POST(parameters):
    global db
    if not db:
        headers = parameters.keys()+["Material","Element","Local node","Node","X","Y","Z","Displacement Magnitude","Displacement in X","Displacement in Y","Displacement in Z","Rotation about X","Rotation about Y","Rotation about Z","Tensile Force","Shear Force V","Shear Force W","Torsion Moment","Bending Moment about V","Bending Moment about W","Longitudinal Stress Point 1","Longitudinal Stress Point 2","Longitudinal Stress Point 3","Longitudinal Stress Point 4","Longitudinal Stress User Defined Point","Twist Angle","Reaction Force Magnitude","Reaction Force X","Reaction Force Y","Reaction Force Z","Reaction Moment Magnitude","Reaction Moment X","Reaction Moment Y","Reaction Moment Z"]
        h = ','.join(map(lambda x: ''.join(x.split()),headers))
        s = "CREATE TABLE t ("+h+");"
        print s
        cur.execute(s)
        db = True
    for filename in ['nodes.csv','elems.csv']:
        with open(filename,'r') as fin:
            dr = csv.DictReader(fin)
            row = dr.next()
            row.update(parameters)
            headers = row.keys()
            h = ','.join(map(lambda x: ''.join(x.split()),headers))
            v = ','.join(len(headers)*['?'])
            to_db = [[row[c] for c in headers]]
            s = "INSERT INTO t ("+h+") VALUES ("+v+");"
            print s
            cur.executemany(s, to_db)
    con.commit()
                
db = False
con = sqlite3.connect(":memory:")
cur = con.cursor()
for alfa in range(0,81,40):
    alfa *= pi/180
    for beta in range(0,121,40):
        beta *= pi/180
        INITIALIZATION()
        MATERIALS()
        MESH(alfa,beta)
        RELATIONS()
        SOLUTION()
        OUTPUT("file.liml")
        subprocess.call([mecway,"file.liml","solve"])
        POST({"alfa":alfa,"beta":beta})
        

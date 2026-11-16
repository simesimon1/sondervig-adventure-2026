"""Original stylized avatar meshes, authored in Blender from design notes.
Run: blender --background --factory-startup --python tools/build-characters.py
No photographs/reference images are loaded, baked, embedded or exported.
Blender 4.3+, metres, +Y up after glTF export, character faces +Z.
"""
import bpy, bmesh, math, json, random
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from math import sin, cos, pi
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'characters'
OUT.mkdir(parents=True, exist_ok=True)
random.seed(2026)


def material(name, color, roughness=.7, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=roughness;bs.inputs['Metallic'].default_value=metal
    return m


def weave_map():
    image=bpy.data.images.new('Original woven cloth normal',128,128)
    pixels=[]
    for y in range(128):
        for x in range(128):
            nx=.11*sin(x*pi/2)*(.65+.35*cos(y*pi/2));ny=.11*sin(y*pi/2)*(.65+.35*cos(x*pi/2))
            pixels.extend((.5+nx,.5+ny,1,1))
    image.pixels=pixels;image.colorspace_settings.name='Non-Color';image.pack()
    return image


class Avatar:
    def __init__(self,name,height,kind):
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        for a in list(bpy.data.actions):bpy.data.actions.remove(a)
        self.name=name;self.height=height;self.kind=kind;self.objects=[]
        self.mats={
            'skin':material('warm skin',(.64,.39,.25),.68),
            'hair':material('brown hair' if kind!='child' else 'golden blonde hair',(.085,.042,.021) if kind!='child' else (.49,.31,.095),.8),
            'lips':material('natural lip color',(.45,.21,.15),.82),
            'stubble':material('short brown beard',(.20,.105,.058),.95),
            'hairlight':material('hair highlights',(.19,.09,.039) if kind!='child' else (.72,.5,.20),.8),
            'eyes':material('ivory / sneaker rubber',(.88,.85,.77),.65),
            'iris':material('green brown eyes',(.075,.095,.055),.34),
            'dark':material('dark trims',(.018,.023,.025),.74),
            'shirt':material('yellow jersey' if kind=='male' else 'rose hoodie' if kind=='child' else 'cream fleece',(.93,.65,.028) if kind=='male' else (.49,.19,.24) if kind=='child' else (.77,.70,.58),.87),
            'coat':material('brown suede' if kind=='male' else 'cream fleece',(.25,.115,.055) if kind=='male' else (.77,.70,.58),.96),
            'lining':material('shearling / cream lining',(.72,.63,.48),.99),
            'pants':material('washed denim' if kind=='male' else 'navy leggings' if kind=='child' else 'cream trousers',(.24,.33,.40) if kind=='male' else (.044,.055,.09) if kind=='child' else (.62,.56,.46),.9),
            'shoe':material('sneaker upper',(.67,.25,.31) if kind=='child' else (.78,.76,.69),.7),
        }
        tex=weave_map()
        for key in ['coat','shirt','pants','lining']:
            m=self.mats[key];ns=m.node_tree.nodes;ts=ns.new('ShaderNodeTexImage');ts.image=tex
            norm=ns.new('ShaderNodeNormalMap');norm.inputs['Strength'].default_value=.17 if key=='pants' else .25
            m.node_tree.links.new(ts.outputs['Color'],norm.inputs['Color']);m.node_tree.links.new(norm.outputs['Normal'],ns.get('Principled BSDF').inputs['Normal'])
        self.mats['skin'].node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.07
    def point(self,p,head=False):
        x,y,z=p
        if self.kind=='child':
            if z<=.91:zz=z*.46/.91
            elif z<=1.50:zz=.46+(z-.91)*.34/.59
            else:zz=.80+(z-1.50)*.25/.38
            s=.82 if head else .63
            return (x*s,y*s,zz)
        s=self.height/1.88
        return (x*s*(.94 if self.kind=='female' and not head else 1),y*s,z*s)
    def mesh(self,name,verts,faces,mat,bone='chest',head=False,uv=None):
        mapped=[self.point(v,head) for v in verts]
        data=bpy.data.meshes.new(name);data.from_pydata(mapped,[],faces);data.update()
        obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.data.materials.append(self.mats[mat])
        for p in data.polygons:p.use_smooth=True
        layer=data.uv_layers.new(name='UVMap')
        for poly in data.polygons:
            for li in poly.loop_indices:
                vi=data.loops[li].vertex_index;p=verts[vi]
                layer.data[li].uv=uv[vi] if uv else ((p[0]+p[1])*5,p[2]*5)
        groups={}
        for i,p in enumerate(verts):
            weights=bone(p) if callable(bone) else {bone:1}
            for b,w in weights.items():
                if w<=0:continue
                if b not in groups:groups[b]=obj.vertex_groups.new(name=b)
                groups[b].add([i],w,'REPLACE')
        # Weld UV-seam duplicates for continuous vertex normals, then round the
        # authored silhouette while preserving interpolated bone weights.
        bm=bmesh.new();bm.from_mesh(data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
        if name in ['sculpted head','sculpted hair cap','short shaped beard','jersey','hooded fleece','open suede jacket','tailored trouser leg','jacket sleeve','fleece sleeve']:
            bpy.context.view_layer.objects.active=obj
            modifier=obj.modifiers.new('Smooth silhouette','SUBSURF');modifier.levels=1
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        for poly in obj.data.polygons:poly.use_smooth=True
        self.objects.append(obj);return obj
    def ellipsoid(self,name,center,radii,mat,bone='head',head=False,segments=16,rings=10):
        verts=[];uv=[]
        for j in range(rings+1):
            a=pi*j/rings
            for i in range(segments+1):
                t=2*pi*i/segments
                verts.append((center[0]+radii[0]*sin(a)*sin(t),center[1]-radii[1]*sin(a)*cos(t),center[2]+radii[2]*cos(a)));uv.append((i/segments,j/rings))
        faces=[]
        for j in range(rings):
            for i in range(segments):
                k=j*(segments+1)+i;faces.append((k,k+segments+1,k+segments+2,k+1))
        return self.mesh(name,verts,faces,mat,bone,head,uv)
    def tube(self,name,points,radii,mat,bone='chest',head=False,sides=8):
        pts=[Vector(p) for p in points];verts=[];uv=[]
        for j,p in enumerate(pts):
            d=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
            axis=d.cross(Vector((0,1,0)))
            if axis.length<.001:axis=d.cross(Vector((1,0,0)))
            axis.normalize();second=d.cross(axis).normalized()
            r=radii[j] if isinstance(radii,list) else radii
            rx,ry=r if isinstance(r,tuple) else (r,r)
            for i in range(sides+1):
                angle=i/sides*2*pi;q=p+axis*(cos(angle)*rx)+second*(sin(angle)*ry)
                verts.append(tuple(q));uv.append((i/sides,j/(len(pts)-1)))
        faces=[]
        for j in range(len(pts)-1):
            for i in range(sides):
                k=j*(sides+1)+i;faces.append((k,k+1,k+sides+2,k+sides+1))
        faces.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*(sides+1)+i for i in range(sides))])
        return self.mesh(name,verts,faces,mat,bone,head,uv)
    def torso(self,name,rings,mat,bone=None,start=0,end=2*pi,sides=32):
        verts=[];uv=[]
        for j,(z,rx,ry,cy) in enumerate(rings):
            for i in range(sides+1):
                a=start+(end-start)*i/sides
                wrinkle=1+.008*sin(i*2.7+j*2.1)
                verts.append((sin(a)*rx*wrinkle,cy-cos(a)*ry*wrinkle,z));uv.append((i/sides*3,z*3))
        faces=[]
        for j in range(len(rings)-1):
            for i in range(sides):
                k=j*(sides+1)+i;faces.append((k,k+1,k+sides+2,k+sides+1))
        if abs(end-start-2*pi)<.001:
            faces.extend([tuple(reversed(range(sides))),tuple((len(rings)-1)*(sides+1)+i for i in range(sides))])
        return self.mesh(name,verts,faces,mat,bone or self.torso_weights,uv=uv)
    @staticmethod
    def torso_weights(p):
        t=max(0,min(1,(p[2]-.96)/.42));return {'hips':max(0,1-t*2),'spine':max(0,1-abs(t-.5)*2),'chest':max(0,(t-.5)*2)}
    def body(self):
        male=self.kind=='male';child=self.kind=='child'
        self.torso('trouser waistband',[(.90,.177,.116,0),(.94,.182,.12,.004),(.98,.172,.11,0)],'pants',bone='hips')
        self.ellipsoid('rounded pelvis',(0,.005,.895),(.175,.116,.085),'pants',bone='hips',segments=24,rings=12)
        shirt_rings=[(.95,.165,.12,-.003),(1.02,.173,.122,-.005),(1.15,.176,.12,0),(1.31,.212,.127,0),(1.40,.231,.114,0),(1.455,.125,.083,0),(1.478,.064,.058,0)]
        self.torso('jersey' if male else 'hooded fleece',shirt_rings,'shirt')
        # Neck is independent of clothing and narrows into the jaw.
        self.torso('neck',[(1.435,.063,.058,.0),(1.51,.058,.054,0),(1.555,.067,.061,-.002)],'skin',bone='neck',sides=20)
        if male:
            coat_rings=[(.94,.186,.14,.012),(1.01,.191,.142,.01),(1.12,.19,.14,.012),(1.29,.225,.146,.012),(1.39,.247,.137,.012),(1.445,.197,.11,.017),(1.468,.126,.09,.017),(1.48,.097,.077,.015)]
            self.torso('open suede jacket',coat_rings,'coat',start=.58,end=2*pi-.58)
            for side in [-1,1]:
                points=[(side*sin(.58)*rx,cy-cos(.58)*ry-.006,z) for z,rx,ry,cy in coat_rings]
                self.tube('zipper tape',points,.006,'dark',bone=self.torso_weights,sides=5)
                self.tube('jacket front seam',[(side*.145,-.113,.98),(side*.157,-.12,1.12),(side*.18,-.115,1.28),(side*.20,-.105,1.36)],.0023,'lining',bone=self.torso_weights,sides=5)
                self.tube('welt pocket',[(side*.135,-.13,1.015),(side*.177,-.11,1.105)],.006,'coat',bone=self.torso_weights)
            collar=[]
            for i in range(25):
                a=.51+(2*pi-1.02)*i/24;collar.append((sin(a)*.108,.018-cos(a)*.105,1.46+.017*cos(a)))
            self.tube('shearling collar',collar,.025,'lining',sides=10)
            self.tube('black V neck',[(-.098,-.066,1.445),(0,-.132,1.376),(.098,-.066,1.445)],.011,'dark',sides=6)
            # Subtle vertical jersey stripes visible through the open jacket.
            for side in [-1,1]:self.tube('jersey stripe',[(side*.04,-.13,.97),(side*.04,-.129,1.12),(side*.04,-.132,1.32)],.005,'dark',bone=self.torso_weights,sides=4)
            self.ellipsoid('sponsor patch',(0,-.131,1.235),(.07,.006,.044),'dark',bone='spine',segments=12,rings=6)
            self.text('1&1',(0,-.14,1.21),.042,'eyes','spine')
        else:
            self.ellipsoid('folded hood',(0,.104,1.398),(.133,.076,.113),'shirt',bone='chest')
            self.tube('hood opening',[(-.086,-.06,1.447),(-.083,.07,1.48),(0,.122,1.49),(.083,.07,1.48),(.086,-.06,1.447)],.019,'lining' if not child else 'shirt',sides=8)
            self.tube('fleece zipper',[(0,-.132,.97),(0,-.13,1.16),(0,-.131,1.32),(0,-.085,1.44)],.004,'lining' if child else 'dark',bone=self.torso_weights,sides=5)
            for side in [-1,1]:
                self.tube('hood drawstring',[(side*.06,-.095,1.445),(side*.056,-.136,1.35),(side*.054,-.14,1.30)],.003,'lining',sides=5)
                self.tube('kangaroo pocket seam',[(side*.03,-.127,1.08),(side*.09,-.132,1.10),(side*.146,-.10,1.055)],.003,'lining' if not child else 'shirt',bone=self.torso_weights,sides=5)
        # Two-segment limbs with smooth skinning across knees/elbows.
        for side,label in [(-1,'L'),(1,'R')]:
            hip=(side*.103,0,.90);knee=(side*.105,-.005,.50);ankle=(side*.105,0,.13)
            def leg_weights(p,l=label):
                w=max(0,min(1,(p[2]-.45)/.14));return {l+'Thigh':w,l+'Shin':1-w}
            if self.kind=='female':pants_r=[.102,.111,.103,.105,.11,.116,.113]
            elif child:pants_r=[.081,.083,.073,.066,.061,.056,.055]
            else:pants_r=[.108,.108,.099,.091,.081,.077,.074]
            centers=[(side*.103,0,.91),(side*.103,.005,.82),(side*.104,-.002,.67),(side*.105,-.007,.52),(side*.105,-.001,.39),(side*.105,0,.24),(side*.105,0,.145)]
            self.tube('tailored trouser leg',centers,[(r,r*.86)for r in pants_r],'pants',bone=leg_weights,sides=16)
            # The cuffs and side seam help separate fabric from a featureless cylinder.
            self.tube('outer trouser seam',[(side*(.103+r),.007,z) for (x,y,z),r in zip(centers,pants_r)],.0021,'pants',bone=leg_weights,sides=5)
            self.torso('sneaker sole',[(0,.068,.14,-.057),(.008,.078,.153,-.057),(.032,.078,.153,-.057),(.043,.069,.14,-.057)],'eyes',bone=label+'Foot',sides=24)
            sole=self.objects[-1]
            for v in sole.data.vertices:v.co.x+=self.point((side*.105,0,0))[0]
            self.ellipsoid('sneaker upper',(side*.105,-.048,.073),(.074,.137,.053),'shoe',bone=label+'Foot',segments=20,rings=10)
            self.ellipsoid('shoe tongue',(side*.105,-.032,.114),(.042,.068,.012),'eyes',bone=label+'Foot',segments=12,rings=6)
            for j in range(4):
                yy=-.006-j*.019
                self.tube('lace',[(side*.105-.029,yy,.123),(side*.105+.029,yy-.006,.123)],.002,'eyes',bone=label+'Foot',sides=4)
            shoulder=(side*.232,.005,1.383);elbow=(side*.278,-.002,1.115);wrist=(side*.286,-.04,.881)
            def arm_weights(p,l=label):
                w=max(0,min(1,(p[2]-1.06)/.12));return {l+'UpperArm':w,l+'Forearm':1-w}
            arm_points=[shoulder,(side*.262,.006,1.32),(side*.273,.004,1.21),elbow,(side*.283,-.018,1.02),(side*.286,-.034,.927),wrist]
            radii=[(.079,.086),(.088,.085),(.078,.074),(.07,.069),(.067,.062),(.059,.052),(.053,.047)]
            self.tube('jacket sleeve' if male else 'fleece sleeve',arm_points,radii,'coat' if male else 'shirt',bone=arm_weights,sides=16)
            self.tube('ribbed cuff',[(side*.286,-.037,.911),(side*.286,-.04,.874)],[.054,.048],'coat' if male else 'shirt',bone=label+'Forearm',sides=16)
            self.ellipsoid('rounded shoulder',(side*.228,.006,1.37),(.091,.086,.092),'coat' if male else 'shirt',bone=label+'UpperArm',segments=20,rings=12)
            self.ellipsoid('palm',(side*.287,-.041,.834),(.036,.026,.055),'skin',bone=label+'Hand',segments=12,rings=8)
            for j in range(4):
                xx=side*.287+(j-1.5)*.015
                self.tube('finger',[(xx,-.045,.812),(xx,-.057,.786+(abs(j-1.5))*.006),(xx,-.053,.778+(abs(j-1.5))*.006)],[.009,.008,.0045],'skin',bone=label+'Hand',sides=6)
            self.tube('thumb',[(side*.264,-.05,.85),(side*.25,-.07,.823),(side*.25,-.075,.804)],[.014,.012,.007],'skin',bone=label+'Hand',sides=8)
    def text(self,words,location,size,mat,bone):
        curve=bpy.data.curves.new('jersey lettering','FONT');curve.body=words;curve.align_x='CENTER';curve.size=size;curve.extrude=.0004
        obj=bpy.data.objects.new('original lettering',curve);bpy.context.collection.objects.link(obj);obj.location=location;obj.rotation_euler[0]=pi/2
        bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH')
        verts=[tuple(obj.matrix_world@v.co)for v in obj.data.vertices];faces=[tuple(p.vertices)for p in obj.data.polygons]
        bpy.data.objects.remove(obj,do_unlink=True);self.mesh('jersey lettering',verts,faces,mat,bone)
    def face(self):
        male=self.kind=='male';child=self.kind=='child'
        # Sculpted ring profile: defined chin, cheekbones and temples.
        rings=[(1.526,.029,.051,-.012),(1.54,.060,.074,-.008),(1.565,.081,.088,-.001),(1.60,.101,.095,0),(1.65,.116,.104,0),(1.70,.115,.102,.003),(1.745,.108,.101,.004),(1.785,.091,.086,.006),(1.81,.06,.058,.006),(1.825,.008,.009,.007)]
        verts=[];uv=[];sides=32
        for j,(z,rx,ry,cy)in enumerate(rings):
            for i in range(sides+1):
                a=2*pi*i/sides;front=max(0,cos(a));x=sin(a)*rx;y=cy-cos(a)*ry
                if 1.61<z<1.72:y-=.006*front*abs(sin(a))*2
                verts.append((x,y,z));uv.append((i/sides,j/(len(rings)-1)))
        faces=[]
        for j in range(len(rings)-1):
            for i in range(sides):k=j*(sides+1)+i;faces.append((k,k+1,k+sides+2,k+sides+1))
        self.mesh('sculpted head',verts,faces,'skin','head',True,uv)
        for side in [-1,1]:
            self.ellipsoid('ear',(side*.117,.004,1.67),(.018,.025,.037),'skin','head',True)
            self.ellipsoid('ear concha',(side*.126,-.012,1.67),(.006,.011,.019),'skin','head',True,segments=10,rings=6)
            # Sclera remains mostly in the sockets; iris and catchlight are small.
            self.ellipsoid('eye white',(side*.045,-.099,1.699),(.022,.012,.012),'eyes','head',True,segments=16,rings=8)
            self.ellipsoid('iris',(side*.045,-.111,1.699),(.008,.0024,.008),'iris','head',True,segments=12,rings=8)
            self.ellipsoid('pupil',(side*.045,-.1134,1.699),(.0034,.0013,.0041),'dark','head',True,segments=10,rings=6)
            self.ellipsoid('eye highlight',(side*.043,-.1147,1.702),(.0019,.0008,.0019),'eyes','head',True,segments=8,rings=4)
            self.tube('upper lid',[(side*.024,-.109,1.70),(side*.044,-.112,1.710),(side*.066,-.102,1.701)],[.002,.003,.002],'skin','head',True,sides=6)
            self.tube('eyebrow',[(side*.023,-.102,1.728),(side*.043,-.108,1.734),(side*.065,-.099,1.729),(side*.073,-.091,1.723)],[.002,.0045 if male else .0035,.004,.0015],'hair','head',True,sides=6)
        self.ellipsoid('nose bridge',(0,-.108,1.675),(.013 if child else .016,.012 if child else .019,.025 if child else .035),'skin','head',True,segments=16,rings=10)
        self.ellipsoid('nose tip',(0,-.124 if child else -.132,1.651),(.016 if child else .021,.012 if child else .017,.012 if child else .015),'skin','head',True)
        for side in [-1,1]:self.ellipsoid('nose wing',(side*.018,-.117,1.646),(.011,.012,.01),'skin','head',True,segments=12,rings=8)
        self.tube('mouth line',[(-.034,-.094,1.600),(-.015,-.106,1.597),(0,-.108,1.597),(.016,-.105,1.598),(.034,-.093,1.602)],[.0016,.002,.002,.002,.0016],'stubble' if male else 'lips','head',True,sides=5)
        self.tube('lower lip',[(-.026,-.102,1.593),(0,-.111,1.589),(.026,-.101,1.595)],[.0015,.003,.0015],'lips','head',True,sides=6)
        if male:
            # Surface patch conforming to the lower face, not a sphere over the mouth.
            vs=[];fs=[];rows=[(1.542,.064,.074),(1.558,.079,.085),(1.58,.09,.092),(1.605,.104,.096),(1.63,.113,.10)]
            for j,(z,rx,ry)in enumerate(rows):
                for i in range(25):
                    a=-1.80+i/24*3.6;top=abs(sin(a))
                    zz=z if j<4 else 1.609+.035*top
                    vs.append((sin(a)*rx*1.018,-cos(a)*ry*1.025-.002,zz))
            for j in range(4):
                for i in range(24):k=j*25+i;fs.append((k,k+1,k+26,k+25))
            self.mesh('short shaped beard',vs,fs,'stubble','head',True)
            self.tube('moustache',[(-.032,-.099,1.616),(-.015,-.111,1.623),(0,-.113,1.621),(.015,-.111,1.623),(.032,-.099,1.616)],[.002,.0045,.0035,.0045,.002],'stubble','head',True,sides=8)
        self.hair()
    def hair(self):
        male=self.kind=='male';child=self.kind=='child';vs=[];fs=[];sides=32;rows=10
        for j in range(rows+1):
            t=j/rows
            for i in range(sides+1):
                a=i/sides*2*pi;limit=1.40-.24*cos(a)
                phi=t*limit
                vs.append((.128*sin(phi)*sin(a),.007-.125*sin(phi)*cos(a),1.702+.138*cos(phi)))
        for j in range(rows):
            for i in range(sides):k=j*(sides+1)+i;fs.append((k,k+1,k+sides+2,k+sides+1))
        self.mesh('sculpted hair cap',vs,fs,'hair','head',True)
        if male:
            for i in range(63):
                a=i*2.399;rr=.022+.07*math.sqrt((i+.5)/63);x=cos(a)*rr;y=sin(a)*rr
                z=1.705+.125*math.sqrt(max(.1,1-(x/.124)**2-(y/.119)**2))
                points=[(x,y,z-.012),(x+.013,y+.005,z+.012),(x+.023,y+.018,z+.026),(x+.028,y+.025,z+.014)]
                self.tube('swept hair clump',points,[.012,.010,.007,.0008],'hairlight' if i%5==0 else 'hair','head',True,sides=7)
        elif child:
            self.tube('ponytail',[(0,.098,1.77),(.013,.164,1.756),(.025,.205,1.66),(.04,.196,1.57),(.046,.18,1.53)],[(.045,.04),(.05,.04),(.042,.034),(.026,.025),(.004,.005)],'hair','head',True,sides=16)
            self.ellipsoid('rose hair tie',(.007,.128,1.762),(.046,.016,.032),'shirt','head',True)
            for i in range(7):
                x=(i-3)*.012
                self.tube('ponytail strand',[(x,.098,1.78),(x+.013,.166,1.75),(x+.024,.216,1.65),(x+.04,.202,1.57)],.0018,'hairlight','head',True,sides=5)
        else:
            for side in [-1,1]:
                for j in range(6):
                    shift=j*.013;xx=side*(.073+shift*.5)
                    self.tube('long layered hair',[(xx,.025+shift*.35,1.78),(side*(.11+shift*.3),.043+shift*.4,1.65),(side*(.114+shift*.3),.074+shift*.45,1.49),(side*(.12+shift*.4),.087+shift*.5,1.33),(side*(.137+shift*.3),.08+shift*.5,1.25)],[(.024,.016),(.025,.021),(.026,.02),(.018,.016),(.001,.002)],'hairlight' if j==2 else 'hair','head',True,sides=9)
            self.tube('half up hair loop',[(-.078,.084,1.75),(0,.123,1.735),(.078,.084,1.75)],.021,'hair','head',True,sides=10)
    def smooth_clothing(self):
        # Union overlapping garment volumes so shoulders, hips and sleeves form
        # one continuous silhouette. Preserve skin weights with nearest samples.
        for names,target,label in [
            (['open suede jacket','jacket sleeve','ribbed cuff','rounded shoulder'] if self.kind=='male' else ['hooded fleece','fleece sleeve','ribbed cuff','rounded shoulder','folded hood'],9000,'continuous outer garment'),
            (['trouser waistband','rounded pelvis','tailored trouser leg'],6000,'continuous trousers')]:
            chosen=[o for o in self.objects if o.name.split('.')[0] in names]
            if not chosen:continue
            bpy.ops.object.select_all(action='DESELECT')
            for o in chosen:
                o.select_set(True)
                if o.name.split('.')[0]=='open suede jacket':
                    bpy.context.view_layer.objects.active=o
                    modifier=o.modifiers.new('Jacket thickness','SOLIDIFY');modifier.thickness=.014;modifier.use_even_offset=True
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.context.view_layer.objects.active=chosen[0];bpy.ops.object.join();obj=bpy.context.object
            for o in chosen:self.objects.remove(o)
            names_by_group={g.index:g.name for g in obj.vertex_groups}
            samples=[{names_by_group[g.group]:g.weight for g in v.groups}for v in obj.data.vertices]
            tree=KDTree(len(samples))
            for v in obj.data.vertices:tree.insert(v.co,v.index)
            tree.balance()
            material=obj.data.materials[0]
            obj.data.remesh_voxel_size=.006 if self.kind!='child' else .0045
            obj.data.remesh_voxel_adaptivity=0
            bpy.ops.object.voxel_remesh()
            smooth=obj.modifiers.new('Soft garment transitions','SMOOTH');smooth.factor=.7;smooth.iterations=7;bpy.ops.object.modifier_apply(modifier=smooth.name)
            tris=sum(len(p.vertices)-2 for p in obj.data.polygons)
            if tris>target:
                mod=obj.modifiers.new('Mobile triangle budget','DECIMATE');mod.ratio=target/tris;bpy.ops.object.modifier_apply(modifier=mod.name)
            obj.data.materials.clear();obj.data.materials.append(material)
            for p in obj.data.polygons:p.use_smooth=True;p.material_index=0
            obj.vertex_groups.clear();groups={}
            for v in obj.data.vertices:
                _,index,_=tree.find(v.co)
                for name,w in samples[index].items():
                    if name not in groups:groups[name]=obj.vertex_groups.new(name=name)
                    groups[name].add([v.index],w,'REPLACE')
            uv=obj.data.uv_layers.new(name='UVMap')
            for poly in obj.data.polygons:
                for li in poly.loop_indices:
                    co=obj.data.vertices[obj.data.loops[li].vertex_index].co
                    uv.data[li].uv=(math.atan2(co.x,-co.y)/pi*2,co.z*4)
            obj.name=label;self.objects.append(obj)
    def rig_and_export(self):
        # One skinned mesh with material primitives; no per-finger draw calls.
        bpy.ops.object.select_all(action='DESELECT')
        for o in self.objects:o.select_set(True)
        bpy.context.view_layer.objects.active=self.objects[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name=self.name+'Mesh'
        bottom=min(v.co.z for v in mesh.data.vertices);top=max(v.co.z for v in mesh.data.vertices)
        scale=self.height/(top-bottom)
        for v in mesh.data.vertices:v.co.z-=bottom;v.co*=scale
        def pt(p):
            q=Vector(self.point(p));q.z-=bottom;return q*scale
        arm=bpy.data.armatures.new(self.name+'Skeleton');rig=bpy.data.objects.new(self.name+'Rig',arm);bpy.context.collection.objects.link(rig)
        bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
        defs=[('root',(0,0,0),(0,0,.12),None),('hips',(0,0,.90),(0,0,1.03),'root'),('spine',(0,0,1.03),(0,0,1.26),'hips'),('chest',(0,0,1.26),(0,0,1.455),'spine'),('neck',(0,0,1.455),(0,0,1.54),'chest'),('head',(0,0,1.54),(0,0,1.82),'neck')]
        for side,l in [(-1,'L'),(1,'R')]:
            defs.extend([(l+'Thigh',(side*.103,0,.90),(side*.105,-.005,.50),'hips'),(l+'Shin',(side*.105,-.005,.50),(side*.105,0,.13),l+'Thigh'),(l+'Foot',(side*.105,0,.13),(side*.105,-.19,.06),l+'Shin'),(l+'UpperArm',(side*.232,.005,1.383),(side*.278,-.002,1.115),'chest'),(l+'Forearm',(side*.278,-.002,1.115),(side*.286,-.04,.881),l+'UpperArm'),(l+'Hand',(side*.286,-.04,.881),(side*.287,-.052,.78),l+'Forearm')])
        for name,h,t,parent in defs:
            b=arm.edit_bones.new(name);b.head=pt(h);b.tail=pt(t)
            if parent:b.parent=arm.edit_bones[parent]
        bpy.ops.object.mode_set(mode='OBJECT');mesh.parent=rig
        modifier=mesh.modifiers.new('Armature deformation','ARMATURE');modifier.object=rig
        # Rest values are reset before every action, preventing animation leakage.
        rig.animation_data_create();scene=bpy.context.scene;scene.render.fps=30
        for clip,frames in [('Idle',120),('Walk',24)]:
            rig.animation_data.action=bpy.data.actions.new(clip)
            for frame in range(1,frames+2,3):
                t=(frame-1)/frames;phase=t*2*pi
                for b in rig.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0)
                if clip=='Idle':
                    rig.pose.bones['chest'].rotation_euler[0]=.012*sin(phase)
                    rig.pose.bones['head'].rotation_euler[1]=.025*sin(phase)
                    for l in ['L','R']:rig.pose.bones[l+'Forearm'].rotation_euler[0]=.04
                else:
                    rig.pose.bones['root'].location[2]=.014*(1-cos(phase*2))
                    rig.pose.bones['hips'].rotation_euler[2]=.035*sin(phase)
                    for i,l in enumerate(['L','R']):
                        a=phase+i*pi
                        rig.pose.bones[l+'Thigh'].rotation_euler[0]=.54*sin(a)
                        rig.pose.bones[l+'Shin'].rotation_euler[0]=max(0,-sin(a))*.82
                        rig.pose.bones[l+'Foot'].rotation_euler[0]=-.10*sin(a)-max(0,-sin(a))*.18
                        rig.pose.bones[l+'UpperArm'].rotation_euler[0]=-.38*sin(a)
                        rig.pose.bones[l+'Forearm'].rotation_euler[0]=.10+max(0,sin(a))*.12
                for b in rig.pose.bones:
                    b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name)
                    if b.name=='root':b.keyframe_insert(data_path='location',frame=frame,group=b.name)
            action=rig.animation_data.action;rig.animation_data.action=None
            track=rig.animation_data.nla_tracks.new();track.name=clip;track.strips.new(clip,1,action)
        for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
        bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
        bpy.context.scene.frame_set(1)
        rig['character']=self.name;rig['height_m']=self.height;rig['provenance']='Original parametric mesh authored from design notes. No reference images embedded.'
        dest=OUT/(self.name.lower()+'.glb')
        bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_skins=True,export_morph=False,export_cameras=False,export_lights=False,export_extras=True,export_copyright='Sondervig Adventure 2026; original avatar geometry',export_yup=True)
        triangles=sum(len(p.vertices)-2 for p in mesh.data.polygons)
        return {'name':self.name,'file':dest.name,'height_m':self.height,'triangles':triangles,'vertices':len(mesh.data.vertices),'bones':len(arm.bones),'bytes':dest.stat().st_size,'animations':['Idle','Walk']}


if __name__=='__main__':
    result=[]
    for name,height,kind in [('Simon',1.88,'male'),('Swantje',1.87,'female'),('Ida',1.05,'child')]:
        avatar=Avatar(name,height,kind);avatar.body();avatar.face();avatar.smooth_clothing();result.append(avatar.rig_and_export())
    (OUT/'manifest.json').write_text(json.dumps({'version':'0.16','format':'glTF 2.0 / GLB','characters':result,'source':'Original meshes and animation, generated by tools/build-characters.py. User reference cards are not included.'},indent=2)+'\n')
    print('CHARACTER_BUILD',json.dumps(result))

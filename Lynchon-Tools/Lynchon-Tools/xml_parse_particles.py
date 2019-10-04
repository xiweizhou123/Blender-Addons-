import bpy
import os
import bmesh
import math
import mathutils
from mathutils import Vector
import sys
import numpy as np



from xml.etree import ElementTree as ET
from xml.dom import minidom

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator



def createLowPolyVenue(tree, filename):

    for estadio in tree:
        #Create Venue parent
        O = bpy.data.collections.new(filename)
        
        bpy.context.scene.collection.children.link(O)
        O = bpy.data.collections[filename]

        for Sector in estadio.findall('Sector'):

            # Create Tiers
            tier = str(Sector.get('tier'))
            tier = tier.replace('T_0', '_TIER')
            tier = "00_LODs-" +filename.split("_")[1].split("-")[3]+ tier
            

            if bpy.data.collections.get(tier) is None:
                """ global tier_O """
                tier_O =  bpy.data.collections.new(tier)
                bpy.data.collections[O.name].children.link(bpy.data.collections[tier_O.name])         

            else:
                tier_O = bpy.data.collections[tier]
                

            #Create Sector
            mesh = bpy.data.meshes.new('mesh')
            sector = bpy.data.objects.new(Sector.get('id'), mesh)
            
            bpy.context.view_layer.objects.active = sector
            bm = bmesh.new()

            total_seats = 0


            # Parent sector to venue empty
            bpy.data.collections[tier_O.name].objects.link(sector)

            for Seat in Sector:

                # Get Position Data
                posX, posY, posZ = float(Seat.get('px')), float(Seat.get('py')), float(Seat.get('pz'))
                rotX, rotY, rotZ = float(Seat.get('rx')), float(Seat.get('ry')), float(Seat.get('rz'))

                #Total number of seats for each sector
                total_seats = total_seats + 1
                #Create vertex and face for each position and orient it
                v1 = bm.verts.new((-posX-0.01, -posZ, posY-0.01))
                v2 = bm.verts.new((-posX+0.01, -posZ, posY-0.01))
                v3 = bm.verts.new((-posX, -posZ, posY+0.01))
                f1 = bm.faces.new([v1,v2,v3])

                vert_list = [v1,v2,v3]
                mat_rot = mathutils.Matrix.Rotation(math.radians(-rotY+180), 3, 'Z')
                bmesh.ops.rotate(bm, cent= (-posX, -posZ, posY), matrix = mat_rot, verts= vert_list)



                #Detect seat and change name to convention while adding description from the seat model

                seat_type_lower = str(Seat.get('prefab')[2:9])
                seat_type = seat_type_lower.upper()
                seat_type = seat_type.replace('-','_')

                for obj in bpy.data.collections['seats_lp'].objects:

                    if obj.name[0:7] == seat_type:
                        seat_type = seat_type + obj.name[7:]

                #Create vertex group and assign vertices to vertex group

                dl = bm.verts.layers.deform.verify()
                seatID = str(Seat.get('name'))

                
                for v in f1.verts:
                    if sector.vertex_groups.get(seat_type) is None:
                        group = sector.vertex_groups.new(name=seat_type)
                        v[dl][group.index] = 1.0    

                    else:
                        group = sector.vertex_groups.find(seat_type)
                        v[dl][group] = 1.0
                        
                    
                    if sector.vertex_groups.get(seatID) is None:
                        group_seatID = sector.vertex_groups.new(name = seatID)
                        v[dl][group_seatID.index] = 1.0
                    
                    else:
                        group_seatID = sector.vertex_groups.find(seatID)
                        v[dl][group_seatID] = 1.0

            bm.to_mesh(mesh)
            bm.free()

            bpy.context.view_layer.objects.active = sector

            for vg in range(len(sector.vertex_groups)):


                bpy.context.view_layer.objects.active = sector
                sector_name = bpy.context.active_object.name
                vg_name =bpy.data.objects[sector_name].vertex_groups[vg].name

                if "SEAT" in vg_name:           

                    #Create particle system

                    sector.modifiers.new(name=seat_type, type = 'PARTICLE_SYSTEM')

                    part = sector.particle_systems[vg]

                    part.settings.emit_from = 'FACE'
                    part.settings.userjit = 1
                    part.settings.physics_type = 'NO'
                    part.settings.frame_start = 1.0
                    part.settings.frame_end = 1.0
                    part.settings.render_type = 'OBJECT'
                    part.settings.particle_size = 1
                    part.settings.use_emit_random = False

                    #Count number of vertices in each vertex group
                    o = bpy.context.object
                    vs = [v for v in o.data.vertices if vg in [vg.group for vg in v.groups]]
                    part.settings.count = len(vs) / 3 

                    part.settings.use_rotations = True
                    part.settings.rotation_mode = 'VEL'
                    part.settings.phase_factor = 0
                    part.settings.use_even_distribution = False

                    #Assign vertex group(seat type) to particle system
                    part.vertex_group_density = vg_name
                    #Assign seat model to particle system
                    part.settings.instance_object = bpy.data.collections['seats_lp'].objects[vg_name]

selection = []           

def getChildren():

    # x = bpy.ops.object.select_grouped(type='COLLECTION')
    x = bpy.context.collection

    # print (x.objects)
    
    sel_obj = bpy.context.selected_objects
    
    for obj in x.objects:
        selection.append(obj)
    

    # print(selection, sep="\n")
    return sel_obj
def indent(elem, level=0, more_sibs=False):
    i = "\n"
    if level:
        i += (level-1) * '  '
    num_kids = len(elem)
    if num_kids:
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
            if level:
                elem.text += '  '
        count = 0
        for kid in elem:
            indent(kid, level+1, count < num_kids - 1)
            count += 1
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
            if more_sibs:
                elem.tail += '  '
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            if more_sibs:
                elem.tail += '  ' 
def convert_to_mesh():        
        # bpy.ops.object.select_all(action='TOGGLE')
    for ob in selection:
        ob.select_set(state=True)
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=False)
        bpy.context.view_layer.objects.active = ob
        x = bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        print (x, 'hola')
        ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.join()
        ob.modifiers.clear()
        ob.select_set(state=False)
    del selection[:]
def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def writexml(tree, file_root):

    sectorSelection = []

    for objSectors in bpy.context.collection.all_objects:
        
        sectorSelection.append(objSectors)

    

    xml = ET.Element("xml")
    Sectors = ET.SubElement(xml, "Sectors")
    

    for obj in sectorSelection:
        
        # Get the active mesh
        newtree = ET.ElementTree(xml)
        Sector = ET.SubElement(Sectors, "Sector", id=obj.name, lodValue="", rampValue="", tier=bpy.data.objects[obj.name].users_collection[0].name)
        # print (obj.name, "sector")
        obj.select_set(state=True)
        bpy.context.view_layer.objects.active
        
        bpy.ops.object.mode_set(mode = 'EDIT')
        me = obj.data
        # print (me)
        bm = bmesh.from_edit_mesh(me)

        #Identificación de los vertex groups a los que pertenece cada cara, aquí es donde detecto el id de la silla.

        for f in bm.faces:

            f_pos = f.calc_center_median() 
            f_pos_x = str("%.3f"%f_pos[0])
            f_pos_y = str("%.3f"%f_pos[1]) 
            f_pos_z = str("%.3f"%f_pos[2])
            f_nor = f.normal
            # print (f_nor[0], f_nor[1] , "face normal")
            v1 = Vector((f_nor[0], f_nor[1]))
            v2 = Vector ((0,-1))
            f_rot_y= angle_between(v1,v2)* (180/math.pi)
            
            print (f_rot_y)



            
            layer_deform = bm.verts.layers.deform.active
            assert layer_deform is not None

            bmv = f.verts[0]
            
            names = tuple(vertex_group.name for vertex_group in obj.vertex_groups)

            for vertex_group_index, weight in bmv[layer_deform].items():
                name = names[vertex_group_index]
                print("Name: %s, Weight: %f" % (name, weight))

            root = tree.getroot()
            for seatID in root.iter('Seat'):
                
                
                if seatID.attrib['name'] == name:
                    seat = seatID.attrib['name']
                
            ET.SubElement(Sector, "Seat", name=seat, prefab="", px=f_pos_x, py=f_pos_z, pz=f_pos_y, rx="", ry=str(f_rot_y), rz="" )


        bm.free()
        obj.select_set(state=False)
        bpy.ops.object.mode_set(mode = 'OBJECT')   
    
    
    indent(xml)
    # ET.dump(xml)
    newtree = ET.ElementTree(xml)
    newtree.write(file_root + '.xml', encoding='utf-8', xml_declaration=True, method="xml")
        
         
        

class XML_OT_lowPolyGeneratorParticles(Operator, ImportHelper):
    bl_idname = "xml.lowpolygeneratorparticles"
    bl_label = "Low poly venue Particles"

    filter_glob : StringProperty(
        default='*.xml',
        options={'HIDDEN'}
    )

    some_boolean : BoolProperty(
        name='Do a thing',
        description='Do a thing with the file you\'ve selected',
        default=True,
    )

    def execute(self, context):
        """Do something with the selected file(s)."""

        file_root, extension = os.path.splitext(self.filepath)
        print(self.filepath)
        tree = ET.parse(self.filepath).getroot()
        filename = os.path.basename(file_root)
        createLowPolyVenue(tree, filename)

        print('Selected file:', self.filepath)
        print('File root:', file_root)
        print('File name:', filename)
        print('File extension:', extension)
        print('Some Boolean:', self.some_boolean)

        return {'FINISHED'}

class XML_OT_conformLpVenue(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "xml.conform_lp_venue"
    bl_label = "Collapse lp venue"

    def execute(self, context):
        getChildren()
        convert_to_mesh()
        return {'FINISHED'}

class XML_OT_writexml(bpy.types.Operator, ImportHelper):
    """Tooltip"""
    bl_idname = "xml.write_xml"
    bl_label = "Write XML"

    def execute(self, context):
        
        """Do something with the selected file(s)."""

        file_root, extension = os.path.splitext(self.filepath)
        tree = ET.parse(self.filepath)
        print(self.filepath)
        writexml(tree, file_root)
        
        return {'FINISHED'}



classes = (XML_OT_lowPolyGeneratorParticles, XML_OT_conformLpVenue, XML_OT_writexml,)

register, unregister = bpy.utils.register_classes_factory(classes)
 


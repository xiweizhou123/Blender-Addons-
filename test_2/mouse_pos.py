import bgl, bpy, bmesh, mathutils from mathutils import Vector


"""Functions for the mouse_coords_to_3D_view"""
def get_viewport():
    view = bgl.Buffer(bgl.GL_INT, 4)
    bgl.glGetIntegerv(bgl.GL_VIEWPORT, view)
    return view


def get_modelview_matrix():
    model_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4, 4])
    bgl.glGetDoublev(bgl.GL_MODELVIEW_MATRIX, model_matrix)
    return model_matrix


def get_projection_matrix():
    proj_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4, 4])
    bgl.glGetDoublev(bgl.GL_PROJECTION_MATRIX, proj_matrix)
    return proj_matrix


def get_depth(x, y):
    depth = bgl.Buffer(bgl.GL_FLOAT, [0.0])
    bgl.glReadPixels(x, y, 1, 1, bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, depth)
    return depth


"""Function mouse_coords_to_3D_view"""


def mouse_coords_to_3D_view(x, y):    
    depth = get_depth(x, y)
    #if (depth[0] != 1.0):
    world_x = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_y = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_z = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    view1 = get_viewport()
    model = get_modelview_matrix()
    proj = get_projection_matrix ()   
    bgl.gluUnProject(x, y, depth[0], 
                     model, proj,
                     view1,
                     world_x, world_y, world_z)
    return (world_x[0], world_y[0], world_z[0])


def coords_3D_to_2D(x, y, z):
    world_x = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_y = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_z = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    view3 = get_viewport()
    model1 = get_modelview_matrix()
    proj1 = get_projection_matrix () 
    bgl.gluProject(x, y, z, model1, proj1, view3, world_x, world_y, world_z)
    return (world_x[0], world_y[0], world_z[0])


def close_point_range(location, range):
    obj = bpy.context.active_object
    bm = bmesh.from_edit_mesh(obj.data)
    vertices = bm.verts
        
    # Global coordinates ( Transform Matrix * local_coordinates )
    verts = [obj.matrix_world * vert.co for vert in vertices]
    verts2d = [coords_3D_to_2D(*coord) for coord in verts]
    #print(verts2d[1])
    #for vert in vertices:
        #verts = obj.matrix_world * vert.co
        #verts2d = coords_3D_to_2D(*verts)
    ## coordinates as tuples
    ## plain_verts = [vert.to_tuple() for vert in verts]


    # create a kd-tree from a mesh
    # 3d cursor relative to the object data    
    co_find = location * obj.matrix_world.inverted()
    #print(co_find)
    size = len(verts2d)
    kd = mathutils.kdtree.KDTree(size)
    for i, v in enumerate(verts2d):
        kd.insert(v, i)


    kd.balance()
    # Find points within a radius of the location
    for (co, index, dist) in kd.find_range(co_find, range):
        #print(co)
        return co
            
    return location   


"""drawing point OpenGL in mouse_coords_to_3D_view"""
def draw_callback_px(self, context):
    # mouse coordinates relative to 3d view
    x, y = self.mouse_path
    
    # mouse coordinates relative to Blender interface    
    view2 = get_viewport()
    gmx = view2[0] + x
    gmy = view2[1] + y
    
    # draw 3d mouse OpenGL point in the 3D View
    depth1 = get_depth(gmx, gmy)
    snap3d = close_point_range(Vector((gmx, gmy, 1.0)), 20)
    mouse3d = mouse_coords_to_3D_view(int(snap3d[0]), int(snap3d[1]))
    
    #print(snap3d)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 0.8, 0.0, 1.0)
    bgl.glPointSize(30)    
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex3f(*(mouse3d))
    bgl.glEnd()
    
    # restore opengl defaults
    bgl.glPointSize(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    
    context.area.header_text_set("hit: %.2f %.2f %.2f" % (mouse3d))
    
class ModalDrawOperator(bpy.types.Operator):
    """Draw a point with the mouse"""
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"   
    
    def modal(self, context, event):
        context.area.tag_redraw()


        if event.type == 'MOUSEMOVE':
            self.mouse_path = (event.mouse_region_x, event.mouse_region_y)            
                        
        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.area.header_text_set()
            return {'FINISHED'}


        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.area.header_text_set()
            return {'CANCELLED'}


        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        # the arguments we pass the the callback
        args = (self, context)
        # Add the region OpenGL drawing callback
        # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_VIEW')
        self.mouse_path = []
        #self.wx = bpy.context.window.width
        #self.wy = bpy.context.window.height
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(ModalDrawOperator)


def unregister():
    bpy.utils.unregister_class(ModalDrawOperator)


if __name__ == "__main__":
    register()
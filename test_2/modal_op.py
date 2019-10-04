import bpy, bgl

class ModalOperator(bpy.types.Operator):
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"
    
    def __init__(self):
        print("Start")
 
    def __del__(self):
        print("End")

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    
    def execute(self, context):
        context.object.location.x = self.x / 100.0
        context.object.location.y = self.y / 100.0
        print(self.x,self.y)
        return {'FINISHED'}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':  # Apply
            self.x = event.mouse_x
            self.y = event.mouse_y 
            self.execute(context)
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        elif event.type in {'RIGHTMOUSE', 'ESC'}:  # Cancel
            context.object.location.x = self.init_loc_x
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        
        self.x = event.mouse_x
        self.y = event.mouse_y
        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}





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


"""Function mouse_coords_to_3D_view"""
def mouse_coords_to_3D_view(x, y):    
    depth = bgl.Buffer(bgl.GL_FLOAT, [0.0])
    bgl.glReadPixels(x, y, 1, 1, bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, depth)
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
    return world_x[0], world_y[0], world_z[0]


"""drawing point OpenGL in mouse_coords_to_3D_view"""
def draw_callback_px(self, context):
    # mouse coordinates relative to 3d view
    x, y = self.mouse_path
    
    # mouse coordinates relative to Blender interface
    view = get_viewport()
    gmx = view[0] + x
    gmy = view[1] + y
    
    # draw 3d mouse OpenGL point in the 3D View
    mouse3d = mouse_coords_to_3D_view(gmx, gmy)        
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 0.8, 0.0, 1.0)
    bgl.glPointSize(30)    
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex3f(*(mouse3d))
    bgl.glEnd()
    
    context.area.header_text_set("hit: %.2f %.2f %.2f" % mouse3d)
    
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


from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Add Sphere on Click"

    _timer = None

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # left click

            if context.area.type == 'VIEW_3D':
                region = context.region
                r3d = context.space_data.region_3d
                x, y = event.mouse_region_x, event.mouse_region_y
                view = region_2d_to_vector_3d(region, r3d, (x, y))
                loc = region_2d_to_location_3d(region, r3d, (x, y), view)
                bpy.ops.mesh.primitive_uv_sphere_add(location=loc)

        if event.type == 'TIMER':
            #print("timer")
            pass


        return {'PASS_THROUGH'}

    def execute(self, context):
        if context.area.type != 'VIEW_3D':
            print("Must use in a 3d region")
            return {'CANCELLED'}

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window = context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
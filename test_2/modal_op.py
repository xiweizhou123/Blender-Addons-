import bpy


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


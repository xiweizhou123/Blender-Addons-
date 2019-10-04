import bpy


class View3DPanel:
    bl_space_type = 'VIEW_3D'
    @classmethod
    def poll(cls, context):
        return (context.object is not None)


class View3DPanelUI(View3DPanel):
    bl_region_type = 'UI'

class View3DPanelTools(View3DPanel):
    bl_region_type = 'TOOLS'


class PanelTwo(View3DPanelUI, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_2"
    bl_label = "Panel Two"
    bl_category = "my thing"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="Also Small Class")
        row = layout.row()
        row.operator("object.modal_operator", text= "move")



class PanelOne(View3DPanelUI, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "Panel One"
    bl_category = "my thing"

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        layout.label(text="Small Class")
        row = layout.row()
        row.operator("mesh.add_cube_sample")


import bpy

class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)


class View3DPanelUI(View3DPanel):
    bl_region_type = 'UI'

class View3DPanelTools(View3DPanel):
    bl_region_type = 'TOOLS'


class PanelOne(View3DPanelUI, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "Panel One"

    def draw(self, context):
        self.layout.label(text="Small Class")


class PanelTwo(View3DPanelUI, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_2"
    bl_label = "Panel Two"

    def draw(self, context):
        self.layout.label(text="Also Small Class")

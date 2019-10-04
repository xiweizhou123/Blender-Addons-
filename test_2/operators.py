import bpy
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_location_3d

class addCubeSample(bpy.types.Operator):
    bl_idname = 'mesh.add_cube_sample'
    bl_label = 'Add Cube'
    bl_options = {"REGISTER", "UNDO"}

    x = bpy.props.IntProperty(default=0)
    y = bpy.props.IntProperty(default=0)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        region = context.region
        r3d = context.space_data.region_3d
        view = region_2d_to_vector_3d(region, r3d, (self.x, self.y))
        loc = region_2d_to_location_3d(region, r3d, (self.x, self.y), view)
        
        bpy.ops.mesh.primitive_cube_add(location=loc)
        return {"FINISHED"}

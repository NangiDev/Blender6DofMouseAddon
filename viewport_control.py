
bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}
import bpy
from bpy.props import EnumProperty, IntProperty

class SIX_DOF_PT_settings_panel(bpy.types.Panel):
    bl_label = "USB Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '6DOF'

    def port_callback(self, context):
        return (
               ('1', 'COM1', ''),
               ('2', 'COM2', ''),
               ('3', 'COM3', ''),
            )

    bpy.types.Scene.port_dropdown_list = EnumProperty(
        name="Port",
        items=port_callback,
        )
        
    def baudrate_callback(self, context):
        return (
               ('1', '115200', ''),
               ('2', '94000', ''),
               ('3', '12300', ''),
            )

    bpy.types.Scene.baudrate_dropdown_list = EnumProperty(
        name="Baudrate",
        items=baudrate_callback,
    )
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(context.scene, "port_dropdown_list")

        row = layout.row()
        row.prop(context.scene, "baudrate_dropdown_list")
        
        

class SIX_DOF_PT_axis_panel(bpy.types.Panel):
    bl_label = "Axis"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '6DOF'

    bpy.types.Scene.JoyX1 = bpy.props.IntProperty(
        name = "x",
        description = "Joystick 1 X-axis",
        default = 512,
        min = 0,
        max = 1023
    )

    bpy.types.Scene.JoyY1 = IntProperty(
        name = "y",
        description = "Joystick 1 Y-axis",
        default = 512,
        min = 0,
        max = 1023
    )

    bpy.types.Scene.JoyX2 = IntProperty(
        name = "x",
        description = "Joystick 2 X-axis",
        default = 512,
        min = 0,
        max = 1023
    )

    bpy.types.Scene.JoyY2 = IntProperty(
        name = "y",
        description = "Joystick 2 Y-axis",
        default = 512,
        min = 0,
        max = 1023
    )

    bpy.types.Scene.JoyX3 = IntProperty(
        name = "x",
        description = "Joystick 3 X-axis",
        default = 512,
        min = 0,
        max = 1023
    )

    bpy.types.Scene.JoyY3 = IntProperty(
        name = "y",
        description = "Joystick 3 Y-axis",
        default = 512,
        min = 0,
        max = 1023
    )

    bpy.context.scene.JoyX1 = 25
    bpy.context.scene.JoyY1 = 65
    bpy.context.scene.JoyX2 = 123
    bpy.context.scene.JoyY2 = 765
    bpy.context.scene.JoyX3 = 342
    bpy.context.scene.JoyY3 = 797

    def draw(self, context):
        layout = self.layout
                
        row = layout.row()
        row.label(text= "")
        row.label(text= "X")
        row.label(text= "Y")
        row.enabled = False

        row = layout.row()
        row.label(text= "Joystick 1")
        row.prop(context.scene, "JoyX1")
        row.prop(context.scene, "JoyY1")
        row.enabled = False

        row = layout.row()
        row.label(text= "Joystick 2")
        row.prop(context.scene, "JoyX2")
        row.prop(context.scene, "JoyY2")
        row.enabled = False

        row = layout.row()
        row.label(text= "Joystick 3")
        row.prop(context.scene, "JoyX3")
        row.prop(context.scene, "JoyY3")
        row.enabled = False
    
classes = [SIX_DOF_PT_settings_panel, SIX_DOF_PT_axis_panel]
        

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
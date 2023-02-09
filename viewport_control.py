bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}

import bpy
import random
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
from bpy.types import Operator, Panel

class BASE_panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '6DOF'

class SIX_DOF_PT_main_panel(BASE_panel, Panel):
    bl_label = "6 DOF Mouse"
    
    def draw(self, context):
        layout = self.layout

class SIX_DOF_PT_settings_panel(BASE_panel, Panel):
    bl_parent_id = "SIX_DOF_PT_main_panel"
    bl_label = "USB Settings"

    def port_callback(self, context):
        return (
               ('COM1', 'COM1', ''),
               ('COM2', 'COM2', ''),
               ('COM3', 'COM3', ''),
            )

    bpy.types.Scene.port_dropdown_list = EnumProperty(
        name="Port",
        items=port_callback,
        )
        
    def baudrate_callback(self, context):
        return (
               ('115200', '115200', ''),
               ('9600', '9600', ''),
            )

    bpy.types.Scene.baudrate_dropdown_list = EnumProperty(
        name="Baudrate",
        items=baudrate_callback,
    )
    
    bpy.types.Object.delay_prop = FloatProperty(
        name = "Delay",
        description = "Delay of serial read",
        default = 1.0,
        min = 0.01,
        max = 1.0,
    )

    def update_connect(self, context):
        # print()
        # if bpy.context.window_manager.is_running == True:
        #     print("Connect to:")
        # else:
        #     print("Disconnect from:")
        # print(context.scene.port_dropdown_list)
        # print(context.scene.baudrate_dropdown_list)
        # print()
        pass # Just an empty function to force update of BoolProperties

    bpy.types.WindowManager.is_running = BoolProperty(update = update_connect)

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        wm = context.window_manager
        label = "Disconnect" if wm.is_running else "Connect"
        layout.prop(wm, 'is_running', text=label, toggle=True)
        
        row = layout.row()
        row.prop(context.scene, "port_dropdown_list")
        row.enabled = not bpy.context.window_manager.is_running

        row = layout.row()
        row.prop(context.scene, "baudrate_dropdown_list")
        row.enabled = not bpy.context.window_manager.is_running

        row = layout.row()
        row.prop(context.object, 'delay_prop', slider=True)


def update_redraw(self, context):
    pass # Just an empty function to force update of IntProperties


class SIX_DOF_PT_axis_panel(BASE_panel, Panel):
    bl_parent_id = "SIX_DOF_PT_main_panel"
    bl_label = "Axis"

    def create_axis(num, axis):
        DEF = 512
        MIN = 0
        MAX = 1023
        return IntProperty(
            name = "",
            description = "Joystick {} {}-axis".format(num, axis),
            default = DEF,
            min = MIN,
            max = MAX,
            update = update_redraw
        )

    bpy.types.Scene.JoyX1 = create_axis(1, 'X')
    bpy.types.Scene.JoyY1 = create_axis(1, 'Y')
    bpy.types.Scene.JoyX2 = create_axis(2, 'X')
    bpy.types.Scene.JoyY2 = create_axis(2, 'Y')
    bpy.types.Scene.JoyX3 = create_axis(3, 'X')
    bpy.types.Scene.JoyY3 = create_axis(3, 'Y')

    def draw(self, context):
        layout = self.layout
                
        row = layout.row()
        row.label(text= "")
        row.label(text= "X")
        row.label(text= "Y")
        row.enabled = False

        for num in range(1, 4):
            row = layout.row()
            row.label(text= "Joystick {}".format(num))
            row.prop(context.scene, "JoyX{}".format(num))
            row.prop(context.scene, "JoyY{}".format(num))
            row.enabled = False


class OT_fetch_data_operator(Operator):
    bl_label = "Fetch USB data"
    bl_idname = "object.fetch_usb_data"
    
    def execute(self, context):
        if bpy.context.window_manager.is_running == False:
            return {'FINISHED'}    

        bpy.context.scene.JoyX1 = random.randint(0,1023)
        bpy.context.scene.JoyY1 = random.randint(0,1023)
        bpy.context.scene.JoyX2 = random.randint(0,1023)
        bpy.context.scene.JoyY2 = random.randint(0,1023)
        bpy.context.scene.JoyX3 = random.randint(0,1023)
        bpy.context.scene.JoyY3 = random.randint(0,1023)
        return {'FINISHED'}    


def timer_call_fnc():
    bpy.ops.object.fetch_usb_data()
    return bpy.context.object.delay_prop


classes = [SIX_DOF_PT_main_panel, SIX_DOF_PT_settings_panel, SIX_DOF_PT_axis_panel, OT_fetch_data_operator]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.timers.register( timer_call_fnc )
    bpy.context.window_manager.is_running = False
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.timers.unregister( timer_call_fnc )

if __name__ == "__main__":
    register()
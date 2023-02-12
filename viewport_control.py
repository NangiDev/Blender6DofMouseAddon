from bpy.types import Operator, Panel
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
import serial.tools.list_ports
import random
import bpy
bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}


DEBUG = False
ser = serial.Serial(bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0.01)


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
        ports = [(str(item).split(" ")[0], str(item), '')
                 for item in list(serial.tools.list_ports.comports())]
        return ports if ports else (('-1', 'No device found', ''),)

    bpy.types.Scene.port_dropdown_list = EnumProperty(
        name="Port",
        items=port_callback,
    )

    def baudrate_callback(self, context):
        baudrates = [(str(item), str(item), '')
                     for item in serial.Serial.BAUDRATES]
        baudrates.reverse()
        return baudrates if baudrates else (('-1', 'No valid baudrates', ''),)

    bpy.types.Scene.baudrate_dropdown_list = EnumProperty(
        name="Baudrate",
        items=baudrate_callback,
    )

    bpy.types.Object.delay_prop = FloatProperty(
        name="Delay",
        description="Delay of serial read",
        default=1.0,
        min=0.000001,
        max=1.0,
    )

    def update_connect(self, context):
        pass  # Just an empty function to force update of BoolProperties

    bpy.types.WindowManager.is_running = BoolProperty(update=update_connect)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        wm = context.window_manager
        label = "Disconnect" if wm.is_running else "Connect"
        row.prop(wm, 'is_running', text=label, toggle=True)
        row.enabled = context.scene.port_dropdown_list != '-1' or DEBUG

        if bpy.context.window_manager.is_running and context.scene.port_dropdown_list == '-1':
            bpy.context.window_manager.is_running = False

        row = layout.row()
        row.prop(context.scene, "port_dropdown_list")
        row.enabled = not bpy.context.window_manager.is_running and context.scene.port_dropdown_list != '-1' or DEBUG

        row = layout.row()
        row.prop(context.scene, "baudrate_dropdown_list")
        row.enabled = not bpy.context.window_manager.is_running and context.scene.baudrate_dropdown_list != '-1' and context.scene.port_dropdown_list != '-1' or DEBUG

        row = layout.row()
        row.prop(context.object, 'delay_prop', slider=True)
        row.enabled = context.scene.port_dropdown_list != '-1' or DEBUG


def update_redraw(self, context):
    pass  # Just an empty function to force update of IntProperties


class SIX_DOF_PT_axis_panel(BASE_panel, Panel):
    bl_parent_id = "SIX_DOF_PT_main_panel"
    bl_label = "Axis"

    def create_axis(num, axis):
        DEF = 512
        MIN = 0
        MAX = 1023
        return IntProperty(
            name="",
            description="Joystick {} {}-axis".format(num, axis),
            default=DEF,
            min=MIN,
            max=MAX,
            update=update_redraw
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
        row.label(text="")
        row.label(text="X")
        row.label(text="Y")
        row.enabled = False

        for num in range(1, 4):
            row = layout.row()
            row.label(text="Joystick {}".format(num))
            row.prop(context.scene, "JoyX{}".format(num))
            row.prop(context.scene, "JoyY{}".format(num))
            row.enabled = False


class OT_fetch_data_operator(Operator):
    bl_label = "Fetch USB data"
    bl_idname = "object.fetch_usb_data"

    def execute(self, context):
        if bpy.context.window_manager.is_running:
            if not ser.is_open:
                ser.port = context.scene.port_dropdown_list
                ser.baudrate = context.scene.baudrate_dropdown_list
                ser.open()

            if ser.is_open:
                ints = []
                for i in range(6):
                    high_byte = ord(ser.read(1))
                    low_byte = ord(ser.read(1))
                    ints.append(high_byte << 8 | low_byte)

                bpy.context.scene.JoyX1 = ints[0]
                bpy.context.scene.JoyY1 = ints[1]
                bpy.context.scene.JoyX2 = ints[2]
                bpy.context.scene.JoyY2 = ints[3]
                bpy.context.scene.JoyX3 = ints[4]
                bpy.context.scene.JoyY3 = ints[5]
        else:
            if ser.is_open:
                ser.close()
        return {'FINISHED'}


classes = [SIX_DOF_PT_main_panel, SIX_DOF_PT_settings_panel,
           SIX_DOF_PT_axis_panel, OT_fetch_data_operator]


def timer_call_fnc():
    bpy.ops.object.fetch_usb_data()
    return bpy.context.object.delay_prop


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.app.timers.register(timer_call_fnc)
    bpy.context.window_manager.is_running = False


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.timers.unregister(timer_call_fnc)


if __name__ == "__main__":
    register()

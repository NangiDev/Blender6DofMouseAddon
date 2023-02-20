from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty, PointerProperty
import bpy
import mathutils
import math
import random

import serial.tools.list_ports

bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}


class MyAddonProperties(PropertyGroup):

    def update_is_running(self, context):
        pass

    def port_callback_list(self, context):
        ports = [(str(item).split(" ")[0], str(item), '')
                 for item in list(serial.tools.list_ports.comports())]
        return ports if ports else (('-1', 'No device found', ''),)

    def create_axis(num, axis):
        def update_redraw(self, context):
            pass
        DEF = 0.5
        MIN = 0
        MAX = 1
        return FloatProperty(
            name="",
            description="Joystick {} {}-axis".format(num, axis),
            default=DEF,
            min=MIN,
            max=MAX,
            update=update_redraw
        )

    joyX1: create_axis(1, 'X')
    joyY1: create_axis(1, 'Y')
    joyX2: create_axis(2, 'X')
    joyY2: create_axis(2, 'Y')
    joyX3: create_axis(3, 'X')
    joyY3: create_axis(3, 'Y')

    ser: serial.Serial = serial.Serial(baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                       stopbits=serial.STOPBITS_ONE, timeout=0.01)

    is_running: BoolProperty(default=False, update=update_is_running)

    joy_speed: FloatProperty(
        name="Speed",
        description="Speed",
        precision=2,
        default=100.0,
        min=1.0,
        max=200.0)

    joy_threshold: FloatProperty(
        name="Threshold",
        description="Threshold",
        step=0.1,
        precision=2,
        default=0.0,
        min=0.0,
        max=1.0)

    port_dropdown_list: EnumProperty(
        name="Port",
        items=port_callback_list,
    )


class SIX_DOF_PT_main_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '6DOF'
    bl_label = "6 DOF Mouse"

    def draw(self, context):
        layout = self.layout
        properties = context.scene.my_addon

        row = layout.row()
        row.label(text="USB Settings")

        row = layout.row()
        label = "Disconnect" if properties.is_running else "Connect"
        row.prop(properties, 'is_running', text=label, toggle=True)

        row = layout.row()
        row.prop(properties, "port_dropdown_list")
        row.enabled = not properties.is_running and properties.port_dropdown_list != '-1'

        row = layout.row()
        row.prop(properties, 'joy_speed', slider=True)

        row = layout.row()
        row.prop(properties, 'joy_threshold', slider=True)

        row = layout.row()
        row.label(text="Axis")
        row.label(text="X")
        row.label(text="Y")
        row.enabled = False

        for num in range(1, 4):
            row = layout.row()
            row.label(text="Joystick {}".format(num))
            row.prop(properties, "joyX{}".format(num))
            row.prop(properties, "joyY{}".format(num))
            row.enabled = False


class OT_fetch_data_operator(Operator):
    bl_label = "Fetch USB data"
    bl_idname = "object.fetch_usb_data"

    def read_one_int(self, ser):
        data = ser.read(2)
        return int.from_bytes(data, byteorder='little') / 1023

    def execute(self, context):
        properties = context.scene.my_addon
        if properties.is_running:
            try:
                if not properties.ser.is_open:
                    properties.ser.port = properties.port_dropdown_list
                    properties.ser.open()

                properties.ser.write(1)
                if properties.ser.in_waiting >= 12:
                    properties.joyX1 = self.read_one_int(properties.ser)
                    properties.joyY1 = self.read_one_int(properties.ser)
                    properties.joyX2 = self.read_one_int(properties.ser)
                    properties.joyY2 = self.read_one_int(properties.ser)
                    properties.joyX3 = self.read_one_int(properties.ser)
                    properties.joyY3 = self.read_one_int(properties.ser)
                    properties.ser.flush()
            except:
                properties.is_running = False
        else:
            if properties.ser.is_open:
                properties.ser.close()
        return {'FINISHED'}


classes = [MyAddonProperties,
           SIX_DOF_PT_main_panel, OT_fetch_data_operator]


def timer_call_fnc():
    bpy.ops.object.fetch_usb_data()
    return 0.01


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon = PointerProperty(
        type=MyAddonProperties)
    bpy.app.timers.register(timer_call_fnc)


def unregister():
    del bpy.types.Scene.my_addon
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.app.timers.unregister(timer_call_fnc)


if __name__ == "__main__":
    register()

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
        DEF = 0.0
        MIN = -1.0
        MAX = 1.0
        return FloatProperty(
            name="",
            description="Joystick {} {}-axis".format(num, axis),
            default=DEF,
            min=MIN,
            max=MAX,
            update=update_redraw
        )

    joyX1: create_axis(1, 'X')  # Right
    joyY1: create_axis(1, 'Y')
    joyX2: create_axis(2, 'X')  # Mid
    joyY2: create_axis(2, 'Y')
    joyX3: create_axis(3, 'X')  # Left
    joyY3: create_axis(3, 'Y')

    ser: serial.Serial = serial.Serial(baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                       stopbits=serial.STOPBITS_ONE, timeout=0.01)

    is_running: BoolProperty(default=False, update=update_is_running)

    joy_speed: FloatProperty(
        name="",
        description="Speed",
        precision=2,
        default=100.0,
        min=1.0,
        max=200.0)

    joy_threshold: FloatProperty(
        name="",
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
        row.separator()
        row = layout.row()
        row.label(text="Joystick Settings")

        row = layout.row()
        row.label(text="Speed")
        row.prop(properties, 'joy_speed', slider=True)

        row = layout.row()
        row.label(text="Threshold")
        row.prop(properties, 'joy_threshold', slider=True)

        row = layout.row()
        row.separator()
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

    origo = mathutils.Vector((0, 0, 0))
    up = mathutils.Vector((0, 0, 1))  # Shared up vector

    # Origo acts as normal to the plane the joysticks move on
    planeOrigo1 = origo + mathutils.Vector((math.sin(0), -math.cos(0), 0))
    planeOrigo2 = origo + \
        mathutils.Vector(
            (math.sin(2*math.pi / 3), -math.cos(2*math.pi / 3), 0))
    planeOrigo3 = origo + \
        mathutils.Vector((math.sin(2*2*math.pi / 3), -
                          math.cos(2*2*math.pi / 3), 0))
    # Side Axis is the third joystick axis. Up, PlaneOrigo and PlaneSide makes up 3 axis
    planeSideAxis1 = up.cross(planeOrigo1)
    planeSideAxis2 = up.cross(planeOrigo2)
    planeSideAxis3 = up.cross(planeOrigo3)

    def move(self, context):
        properties = context.scene.my_addon
        joystick1 = mathutils.Vector((properties.joyX1, properties.joyY1, 0))
        joystick2 = mathutils.Vector((properties.joyX2, properties.joyY2, 0))
        joystick3 = mathutils.Vector((properties.joyX3, properties.joyY3, 0))

        point1 = self.planeOrigo1 + self.planeSideAxis1 * \
            joystick1.x + self.up * joystick1.y
        point2 = self.planeOrigo2 + self.planeSideAxis2 * \
            joystick2.x + self.up * joystick2.y
        point3 = self.planeOrigo3 + self.planeSideAxis3 * \
            joystick3.x + self.up * joystick3.y

        v1 = point2 - point1
        v2 = point3 - point1
        normal = v1.cross(v2)
        normal.normalize()

        # Om denna funkar så multiplicera denna matris på kamerans rotationsmatris
        rotation = normal.rotation_difference(self.up).to_matrix()
        centroid = (point1 + point2 + point3) / 3

        camera = bpy.context.scene.camera
        camera_rotation_matrix = camera.matrix_world.to_3x3()
        translation = centroid @ camera_rotation_matrix
        camera.location += translation

        # Print the results
        # print("Position:", centroid)
        # print("Normal:", normal)
        # print("Rot:", rotation)
        # print("Up:", self.up)

    def read_one_int(self, context, ser):
        threshold = context.scene.my_addon.joy_threshold
        data = ser.read(2)
        value = int.from_bytes(data, byteorder='little') / 512 - 1
        if (abs(value) - threshold < 0.0):
            return 0.0
        return value

    def execute(self, context):
        properties = context.scene.my_addon
        if properties.is_running:
            try:
                if not properties.ser.is_open:
                    properties.ser.port = properties.port_dropdown_list
                    properties.ser.open()

                properties.ser.write(1)
                if properties.ser.in_waiting >= 12:
                    properties.joyY1 = self.read_one_int(
                        context, properties.ser)
                    properties.joyX1 = self.read_one_int(
                        context, properties.ser)
                    properties.joyY2 = self.read_one_int(
                        context, properties.ser)
                    properties.joyX2 = self.read_one_int(
                        context, properties.ser)
                    properties.joyY3 = self.read_one_int(
                        context, properties.ser)
                    properties.joyX3 = self.read_one_int(
                        context, properties.ser)
                    properties.ser.flush()

            except Exception as e:
                print(e)
                properties.is_running = False
        else:
            properties.joyY1 = 0
            properties.joyX1 = 0
            properties.joyY2 = 0
            properties.joyX2 = 0
            properties.joyY3 = 0
            properties.joyX3 = 0
            if properties.ser.is_open:
                properties.ser.close()
        self.move(context)
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

import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty, PointerProperty
import math
import mathutils
from mathutils import Matrix, Vector, Euler
import serial.tools.list_ports

bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}


# Class containing the properties for the 6DOF Mouse Add-on
class MyAddonProperties(PropertyGroup):
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

    def update_is_running(self, context):
        pass

    is_running: BoolProperty(default=False, update=update_is_running)

    def port_callback_list(self, context):
        ports = [(str(item).split(" ")[0], str(item), '')
                 for item in list(serial.tools.list_ports.comports())]
        return ports if ports else (('-1', 'No device found', ''),)

    port_dropdown_list: EnumProperty(
        name="Port",
        items=port_callback_list,
    )

    joy_speed: FloatProperty(
        name="",
        description="Speed",
        precision=4,
        default=1.0,
        min=0.0,
        max=2.0)

    joy_threshold: FloatProperty(
        name="",
        description="Threshold",
        step=0.1,
        precision=2,
        default=0.0,
        min=0.0,
        max=1.0)


class SIX_DOF_PT_main_panel(Panel):  # Main Panel class
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


# Operator for fetching data from the serial port
class OT_fetch_data_operator(Operator):

    # TODO Extract math to a separate function that can take object you want to control as parameter

    bl_label = "Fetch USB data"
    bl_idname = "object.fetch_usb_data"

    # Common up vector
    up = Vector((0, 0, 1))
    right = Vector((1, 0, 0))
    forward = Vector((0, 1, 0))

    # Origo acts as normal in joystick space
    planeOrigo1 = \
        Vector((math.sin(2*math.pi / 3),
                -math.cos(2*math.pi / 3), 0))
    planeOrigo2 = \
        Vector((math.sin(2*math.pi),
                -math.cos(2*math.pi), 0))
    planeOrigo3 = \
        Vector((math.sin(2*2*math.pi / 3),
                -math.cos(2*2*math.pi / 3), 0))

    # Side Axis is the third joystick axis. Up, PlaneOrigo and PlaneSide makes up 3 axis
    planeSideAxis1 = up.cross(planeOrigo1)
    planeSideAxis2 = up.cross(planeOrigo2)
    planeSideAxis3 = up.cross(planeOrigo3)

    def move(self, context):
        properties = context.scene.my_addon
        joystick1 = Vector((properties.joyX1, 0, properties.joyY1))
        joystick2 = Vector((properties.joyX2, 0, properties.joyY2))
        joystick3 = Vector((properties.joyX3, 0, properties.joyY3))

        # Joystick Y is axis Z in Blender
        point1 = self.planeOrigo1 + \
            self.planeSideAxis1 * joystick1.x + \
            self.up * joystick1.z
        point2 = self.planeOrigo2 + \
            self.planeSideAxis2 * joystick2.x + \
            self.up * joystick2.z
        point3 = self.planeOrigo3 + \
            self.planeSideAxis3 * joystick3.x + \
            self.up * joystick3.z
        centroid = (point1 + point2 + point3) / 3

        camera = bpy.context.scene.camera
        blender_translation = Vector((centroid.x, centroid.z, -centroid.y))
        world_translation = camera.matrix_world.to_3x3() @ blender_translation
        camera.location += world_translation * properties.joy_speed

        v1 = point1 - point2
        v2 = point3 - point2
        normal = v1.cross(v2)
        normal.normalize()

        xAxis = (point1 - point3)
        yAxis = ((point1 + point3) / 2 - point2)
        xAxis.normalize()
        yAxis.normalize()

        speed_multiplier = 0.1
        yaw = yAxis.x * speed_multiplier * properties.joy_speed
        pitch = yAxis.z * speed_multiplier * properties.joy_speed
        roll = xAxis.z * speed_multiplier * properties.joy_speed

        euler_angles = Euler((pitch, -yaw, roll), 'XYZ').to_matrix().to_4x4()
        camera.matrix_basis @= euler_angles

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

                # The mouse is sending coordinates in the wrong order
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

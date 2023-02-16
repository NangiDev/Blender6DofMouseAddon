from bpy.types import Operator, Panel
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
import serial.tools.list_ports
import threading
import bpy


bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}


ser = serial.Serial(bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0.01)
ser.close()


def your_function_to_run_in_background():
    while True:
        print("lol1")


# the_thread = threading.Thread(
    daemon=True, target=your_function_to_run_in_background, args=())


class SIX_DOF_PT_main_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '6DOF'
    bl_label = "6 DOF Mouse"

    the_thread.start()

    def draw(self, context):
        layout = self.layout


classes = [SIX_DOF_PT_main_panel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

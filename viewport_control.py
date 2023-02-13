from bpy.types import Operator, Panel
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
import bpy

import serial.tools.list_ports
import threading

bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}


class SIX_DOF_PT_main_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '6DOF'
    bl_label = "6 DOF Mouse"

    def port_callback(self, context):
        ports = [(str(item).split(" ")[0], str(item), '')
                 for item in list(serial.tools.list_ports.comports())]
        return ports if ports else (('-1', 'No device found', ''),)

    bpy.types.Scene.port_dropdown_list = EnumProperty(
        name="Port",
        items=port_callback,
    )

    bpy.types.Scene.baudrate_dropdown_list = EnumProperty(
        name="Baudrate",
        items=[('115200', '115200', '')],
    )

    def create_axis(num, axis):
        def update_redraw(self, context):
            pass  # Just an empty function to force update of IntProperties

        DEF = 512
        MIN = 0
        MAX = 1023
        return IntProperty(
            name="Joy{}{}".format(axis, num),
            description="Joystick {} {}-axis".format(num, axis),
            default=DEF,
            min=MIN,
            max=MAX,
            update=update_redraw
        )

    bpy.types.WindowManager.JoyX1 = create_axis(1, 'X')
    bpy.types.WindowManager.JoyY1 = create_axis(1, 'Y')
    bpy.types.WindowManager.JoyX2 = create_axis(2, 'X')
    bpy.types.WindowManager.JoyY2 = create_axis(2, 'Y')
    bpy.types.WindowManager.JoyX3 = create_axis(3, 'X')
    # bpy.types.WindowManager.JoyY3 = create_axis(3, 'Y')
    # stop_thread = False

    # def worker_thread():
    #     while not stop_thread:
    #         bpy.context.window_manager.JoyX1 = 123
    #         bpy.context.window_manager.JoyX2 = 123
    #         bpy.context.window_manager.JoyX3 = 123

    # # Start the worker thread
    # thread = threading.Thread(daemon=True, target=worker_thread)
    # thread.start()

    # # Later, when you want to stop the thread
    # stop_thread = True
    # thread.join()

    # bpy.context.window_manager.JoyX1 = 123
    # value = bpy.context.window_manager.JoyX1

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="USB Settings")

        row = layout.row()
        wm = context.window_manager
        label = "Disconnect" if wm.is_running else "Connect"
        row.prop(wm, 'is_running', text=label, toggle=True)

        row = layout.row()
        row.prop(context.scene, "port_dropdown_list")

        row = layout.row()
        row.prop(context.scene, "baudrate_dropdown_list")

        row = layout.row()
        row.label(text="Axis")
        row.enabled = False

        row = layout.row()
        row.label(text="")
        row.label(text="X")
        row.label(text="Y")
        row.enabled = False

        for num in range(1, 4):
            row = layout.row()
            row.label(text="Joystick {}".format(num))
            row.prop(context.window_manager, "JoyX{}".format(num))
            row.prop(context.window_manager, "JoyY{}".format(num))
            row.enabled = False


classes = [SIX_DOF_PT_main_panel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

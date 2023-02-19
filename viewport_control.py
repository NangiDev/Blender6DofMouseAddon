from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty, PointerProperty
import bpy
import mathutils
import math
import time

import serial.tools.list_ports
import threading
import queue

bl_info = {
    "name": "6DOF Mouse Add-on",
    "catergory": "3D View",
    "author": "Joel Setterberg",
    "version": (0, 1),
    "blender": (3, 3, 3),
}


class MyThread(threading.Thread):
    def __init__(self, queue, port):
        threading.Thread.__init__(self)
        self.daemon = True
        self._queue = queue
        self._is_running = False
        self._is_reading = False

    def run(self):
        while self._is_running and self._is_reading:
            self._queue.put(2)
            print("Back Thread: {}".format(self._queue.qsize()))
            self._is_reading = self._queue.qsize() < 6


class MyAddonProperties(PropertyGroup):
    def update_is_running(self, context):
        self.read_tread._is_running = self.is_running
        self.read_tread._is_reading = self.is_running
        self.queue.queue.clear()
        self.read_tread.run()

    def port_callback_list(self, context):
        ports = [(str(item).split(" ")[0], str(item), '')
                 for item in list(serial.tools.list_ports.comports())]
        return ports if ports else (('-1', 'No device found', ''),)

    is_running: BoolProperty(default=False, update=update_is_running)

    port_dropdown_list: EnumProperty(
        name="Port",
        items=port_callback_list,
    )

    queue = queue.Queue()
    read_tread = MyThread(queue=queue, port='COM10')
    read_tread.start()


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


class OT_fetch_data_operator(Operator):
    bl_label = "Fetch USB data"
    bl_idname = "object.fetch_usb_data"

    def execute(self, context):
        properties = context.scene.my_addon
        while (not properties.read_tread._is_reading) and properties.is_running:
            print("Main Thread: {}".format(properties.queue.get()))
            properties.read_tread._is_reading = properties.queue.qsize() <= 0
        if properties.read_tread._is_reading:
            properties.read_tread.run()
        return {'FINISHED'}


classes = [MyAddonProperties, SIX_DOF_PT_main_panel, OT_fetch_data_operator]


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

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
    def __init__(self, context, queue):
        threading.Thread.__init__(self)
        self.daemon = True
        self.context = context
        self.queue = queue
        self._is_running = False
        self.ser = None
        try:
            self.ser = serial.Serial(port='COM10', baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, timeout=0.01)
            self.ser.close()
            self.ser.open()
        except:
            print("Ser could not connect")

    def run(self):
        if not self.ser == None:
            self.ser.flush()
            while self._is_running and self.queue.qsize() < 6:
                data = self.ser.read(2)
                self.ser.read(2)
                result = int.from_bytes(data, byteorder='little')
                print(result)
                self.queue.put(result)
                self._is_running = self.queue.qsize() < 6


class MyAddonProperties(PropertyGroup):
    def update_is_running(self, context):
        self.read_tread._is_running = self.is_running
        self.read_tread.run()

    def port_callback_list(self, context):
        ports = [(str(item).split(" ")[0], str(item), '')
                 for item in list(serial.tools.list_ports.comports())]
        return ports if ports else (('-1', 'No device found', ''),)

    is_running: BoolProperty(
        name="_is_running", default=False, update=update_is_running)

    port_dropdown_list: EnumProperty(
        name="Port",
        items=port_callback_list,
    )

    queue = queue.Queue()
    read_tread = MyThread(context=bpy.context, queue=queue)
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

        if properties.queue.qsize() > 0:
            print(properties.queue.get())


classes = [MyAddonProperties, SIX_DOF_PT_main_panel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_addon = PointerProperty(
        type=MyAddonProperties)


def unregister():
    if not bpy.context.scene.my_addon.read_tread.ser == None:
        bpy.context.scene.my_addon.read_tread.ser.close()
    del bpy.types.Scene.my_addon
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

import mathutils
import math
# Define three points that define the plane

mid = mathutils.Vector((0, 0, 0))

up = mathutils.Vector((0, 0, 1))
planePoint1 = mid + mathutils.Vector((math.sin(0), -math.cos(0), 0))
planePoint2 = mid + \
    mathutils.Vector((math.sin(2*math.pi / 3), -math.cos(2*math.pi / 3), 0))
planePoint3 = mid + \
    mathutils.Vector((math.sin(2*2*math.pi / 3), -
                     math.cos(2*2*math.pi / 3), 0))
side1 = up.cross(planePoint1)
side2 = up.cross(planePoint2)
side3 = up.cross(planePoint3)

joystick1 = mathutils.Vector((0, 1, 0))
joystick2 = mathutils.Vector((0, 1, 0))
joystick3 = mathutils.Vector((0, 1, 0))

point1 = planePoint1 + side1 * joystick1.x + up * joystick1.y
point2 = planePoint2 + side2 * joystick2.x + up * joystick2.y
point3 = planePoint3 + side3 * joystick3.x + up * joystick3.y

# Calculate two direction vectors
v1 = point2 - point1
v2 = point3 - point1

# Calculate the normal vector
normal = v1.cross(v2)
normal.normalize()

# Calculate the rotation matrix
# up = mathutils.Vector((0, 0, 1))
rotation = normal.rotation_difference(up).to_matrix()
# Om denna funkar så multiplicera denna matris på kamerans rotationsmatris

# # Apply the rotation to get the X and Y axes of the plane
# x_axis = v1 @ rotation
# y_axis = v2 @ rotation

# Calculate the position of the plane
centroid = (point1 + point2 + point3) / 3

# Print the results
print("Position:", centroid)
print("Normal:", normal)
print("Up:", up)
# print("X-Axis:", x_axis)
# print("Y-Axis:", y_axis)

# multiplicera centroid med kamera rotationsmatris för att få ut riktiningsvektorn
# så att upp blir kamerans upp
# translation = centroid * camera.rotation_matrix

# Flytta sedan kamerans position med riktiningsvektorn * speed
# camera.matrix += translation * speed

# multiplicera up och normal med kameran matrisen
# new_up = up * camera.rotation_matrix
# new_normal = normal * camera.rotation_matrix
# skillanden på de nya värden (Rotations skillnad)
# camera.matrix *= rotationsmatris (Håll koll på positionen)
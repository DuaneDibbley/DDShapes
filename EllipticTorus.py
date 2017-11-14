# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
  "name" : "Elliptic Torus",
  "author" : "Duane Dibbley",
  "version" : (0, 3, 1),
  "blender" : (2, 79, 0),
  "location" : "View3D > Add > Mesh",
  "description" : "Add an elliptic torus with the cross-section correctly following the ellipse",
  "category" : "Add Mesh"
}

import sys
import bpy
from bpy.types import Panel, Menu, Operator
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, EnumProperty
from math import cos, sin, pi, fabs, sqrt, atan2
from mathutils import Vector, Matrix, Euler

try:
  from scipy.integrate import quad
  from scipy.optimize import fsolve
  from scipy.special import hyp2f1
except ImportError:
  pass

#Function to integrate to get the arc length
def arcFunc(theta, major, minor):
  return sqrt((-major*sin(theta))**2+(minor*cos(theta))**2)

#Integrate arcFunc
def arcLength(theta, major, minor, arc_length):
  return quad(arcFunc, a=0.0, b=theta, args=(major, minor))[0]-arc_length

def getParamAndNormal(major, minor, input_param, steps, spacing_type):
  if input_param == 0:
    return 0.0, 0.0

  if major == minor:
    spacing_type = "spacing.area"

  if spacing_type == "spacing.normal":
    normal_angle = 2*pi*input_param/steps
    output_param = atan2(minor*sin(2*pi*input_param/steps), major*cos(2*pi*input_param/steps))

  elif spacing_type == "spacing.radius":
    output_param = atan2(major*sin(2*pi*input_param/steps), minor*cos(2*pi*input_param/steps))
    normal_angle = atan2(major*sin(output_param), minor*cos(output_param))

  elif spacing_type == "spacing.arc":
    circumference = 2*pi*max(major, minor)*hyp2f1(-.5, .5, 1, 1-(min(major, minor)/max(major, minor))**2)
    arc_length = circumference*input_param/steps
    output_param = fsolve(arcLength, [0.0], args=(major, minor, arc_length))[0]
    normal_angle = atan2(major*sin(output_param), minor*cos(output_param))

  else:
    output_param = 2*pi*input_param/steps
    normal_angle = atan2(major*sin(2*pi*input_param/steps), minor*cos(2*pi*input_param/steps))

  return output_param, normal_angle

def getTwistAngle(twist, amplitude, twist_type, v, step):
  if twist_type == "twist.sine":
    twist_angle = amplitude*sin(twist*2*v*pi/step)
  else:
    twist_angle = amplitude*twist*v/step
  return twist_angle

def getSpacingTypes(self, context):
  spacing_types = []
  spacing_types.append(("spacing.area", "Equal Area", "Equally increment the parameter phi equally for each point (standard ellipse equations)"))
  spacing_types.append(("spacing.normal", "Equiangular Normal", "Space between points equiangularly by the direction of the normals"))
  spacing_types.append(("spacing.radius", "Equiangular Radius", "Space between points equiangularly by the direction of the radii"))
  #Functions requiring SciPy aren't added to the list unless SciPy has been properly loaded
  if "scipy" in sys.modules:
    spacing_types.append(("spacing.arc", "Equal Arc Length", "Place points at equal arc distance along the circumference of ellipse"))
  return spacing_types

def getTwistTypes(self, context):
  twist_types = []
  twist_types.append(("twist.linear", "Linear", "Linearly increase the twist angle along the cicrumference of the ring"))
  twist_types.append(("twist.sine", "Sinusoidal", "Twist back and forth like a sine wave"))
  return twist_types

def getThicknessMethods(self, context):
  thickness_methods = []
  thickness_methods.append(("thickness.cross", "Equal Cross-Sections", "Keep the cross-sections equally sized"))
  thickness_methods.append(("thickness.tube", "Constant Tube Thickness", "Scale cross-sections to keep constant tube thickness"))
  return thickness_methods

class MESH_OT_elliptic_torus_add(Operator):
  bl_idname = "mesh.elliptic_torus_add"
  bl_label = "Elliptic Torus"
  bl_options = {"REGISTER", "UNDO", "PRESET"}
  major_axes = FloatVectorProperty(name="Ring's Semi-Axes", description="The semi-axes of the ring", default=(2.3, 1.05), min=0.0, max=100.0, step=1, precision=3, subtype="NONE", unit="NONE", size=2)
  vstep = IntProperty(name="Ring Segments", description="Number of segments for the ellipse", default=48, min=4, max=1024)
  ring_spacing_type = EnumProperty(items=getSpacingTypes, name="Ring Spacing", description="Define how to calculate the space between the points on the ring")
  minor_axes = FloatVectorProperty(name="Cross-Section's Semi-Axes", description="The semi-axes of the cross-section", default=(0.2, 0.1), min=0.0, max=100.0, step=1, precision=3, subtype="NONE", unit="NONE", size=2)
  ustep = IntProperty(name="Cross-Section Segments", description="Number of segments for the cross-section", default=12, min=4, max=1024)
  cross_spacing_type = EnumProperty(items=getSpacingTypes, name="Cross-Section Spacing", description="Define how to calculate the space between the points on the cross-section")
  cross_twist = IntProperty(name="Cross-Section Twists", description="Number of twists of the cross-section", default=0, min=0, max=256)
  cross_twist_amplitude = FloatProperty(name="Twist Amplitude", description="The angle each twist equals", default=pi, min=0, soft_max=2*pi, step=10, precision=3, subtype="ANGLE")
  cross_twist_type = EnumProperty(items=getTwistTypes, name="Twist Type", description="Define how the twisting is done")
  cross_rotation = FloatProperty(name="Cross-Section Initial Twist", description="Initial twist of the cross-section", default=0.0, min=-pi/2.0, max=pi/2.0, step=10, precision=3, subtype="ANGLE")
  tube_thickness_method = EnumProperty(items=getThicknessMethods, name="Tube Thickness Method", description="How to calculate the tube thickness")
  ring_location = FloatVectorProperty(name="Location", description="Location", default=(0.0, 0.0, 0.0), step=1, precision=3, subtype="XYZ", unit="LENGTH", size=3)
  ring_rotation = FloatVectorProperty(name="Rotation", description="Rotation", default=(0.0, 0.0, 0.0), step=10, precision=3, subtype="XYZ", unit="ROTATION", size=3)

  def execute(self, context):
    #Create the base shape of the cross-section
    cross = []
    for u in range(self.ustep):
      theta, cross_normal_angle = getParamAndNormal(self.minor_axes[0], self.minor_axes[1], u, self.ustep, self.cross_spacing_type)
      x = self.minor_axes[0]*cos(theta)
      y = 0.0
      z = self.minor_axes[1]*sin(theta)
      cross.append(Vector((x, y, z)))

    #Create the base shape of the ring, and combine it with information on how to rotate and align the cross-section
    ring_vert = []
    ring_norm = []
    for v in range(self.vstep):
      phi, ring_normal_angle = getParamAndNormal(self.major_axes[0], self.major_axes[1], v, self.vstep, self.ring_spacing_type)
      x = self.major_axes[0]*cos(phi)
      y = self.major_axes[1]*sin(phi)
      z = 0.0
      ring_vert.append(Vector((x, y, z)))
      ring_norm.append(ring_normal_angle)

    #Calculate cross-section transformation matrix for each of the vertices of the ring
    cross_trans = []
    for v in range(self.vstep):
      prev_vert = ring_vert[(self.vstep+v-1)%self.vstep]
      this_vert = ring_vert[v]
      next_vert = ring_vert[(v+1)%self.vstep]
      angle = (this_vert-prev_vert).angle(this_vert-next_vert)/2.0
      cross_trans_mat = Matrix().Rotation(self.cross_rotation+getTwistAngle(self.cross_twist, self.cross_twist_amplitude, self.cross_twist_type, v, self.vstep), 4, Vector((0.0, 1.0, 0.0)))
      if self.tube_thickness_method == "thickness.tube":
        cross_trans_mat = Matrix().Scale(1.0/sin(angle), 4, Vector((1.0, 0.0, 0.0)))*cross_trans_mat
      cross_trans_mat = Matrix().Rotation(ring_norm[v], 4, Vector((0.0, 0.0, 1.0)))*cross_trans_mat
      cross_trans.append(cross_trans_mat)

    vertices = []
    faces = []
    for v in range(self.vstep):
      for u in range(self.ustep):
        cross_vert = cross_trans[v]*cross[u]+ring_vert[v]

        #Append the vertex coordinates to the list of vertices, and append a face to the list of faces.
        #The list of faces uses vertices that have not yet been created when appending intermediate faces,
        #however this is remedied at the end, as then it bridges with the vertices created at the beginning.
        #It uses modulo to make sure it doesn't overflow.
        vertices.append(cross_vert)
        #Offset the bridge if the angle is obtuse
        if (cos(getTwistAngle(self.cross_twist, self.cross_twist_amplitude, self.cross_twist_type, (v+1)%self.vstep, self.vstep)-getTwistAngle(self.cross_twist, self.cross_twist_amplitude, self.cross_twist_type, v, self.vstep)) < 0.0):
          u_bridge_pos = (u+self.ustep//2)%self.ustep
        else:
          u_bridge_pos = u
        faces.append([v*self.ustep+u, ((v+1)%self.vstep)*self.ustep+u_bridge_pos, ((v+1)%self.vstep)*self.ustep+((u_bridge_pos+1)%self.ustep), v*self.ustep+((u+1)%self.ustep)])

    #Deselect everything
    bpy.ops.object.select_all(action="DESELECT")

    #Create the mesh and the object, select it and make it active.
    elliptic_torus_mesh = bpy.data.meshes.new("Elliptic Torus")
    elliptic_torus_mesh.from_pydata(vertices, [], faces)
    elliptic_torus_mesh.update()
    elliptic_torus_object = bpy.data.objects.new("Elliptic Torus", elliptic_torus_mesh)
    elliptic_torus_object.location = self.ring_location
    elliptic_torus_object.rotation_euler = Euler(self.ring_rotation, "XYZ")
    context.scene.objects.link(elliptic_torus_object)
    elliptic_torus_object.select = True
    bpy.context.scene.objects.active = elliptic_torus_object
    return {"FINISHED"}

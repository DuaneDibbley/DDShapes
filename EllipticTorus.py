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
  "version" : (0, 1, 0),
  "blender" : (2, 79, 0),
  "location" : "View3D > Add > Mesh",
  "description" : "Add an elliptic torus with the cross-section correctly following the ellipse",
  "category" : "Add Mesh"
}

import bpy
from bpy.types import Panel, Menu, Operator, INFO_MT_mesh_add
from bpy.props import IntProperty, FloatProperty
from math import cos, sin, atan2, pi
from mathutils import Vector

class EllipticTorusOperator(Operator):
  bl_idname = "mesh.add_elliptic_torus"
  bl_label = "Elliptic Torus"
  bl_options = {"REGISTER", "UNDO"}
  major_semi_radius = FloatProperty(name="Major Semi-Radius", description="Half the major axis of the ellipse", default=2.4, min=0.0001, max=100.0)
  minor_semi_radius = FloatProperty(name="Minor Semi-Radius", description="Half the major axis of the ellipse", default=0.9, min=0.0001, max=100.0)
  tube_radius = FloatProperty(name="Tube Radius", description="Radius of the cross-section", default=0.1, min=0.0001, max=100.0)
  vstep = IntProperty(name="Ellipse Segments", description="Number of segments for the ellipse", default=48, min=1, max=1024)
  ustep = IntProperty(name="Tube Segments", description="Number of segments for the cross-section", default=16, min=1, max=1024)

  def execute(self, context):
    vertices = []
    faces = []
    for v in range(self.vstep):
      for u in range(self.ustep):

        #Calculate theta
        theta = 2*u*pi/self.ustep

        #Calculate phi
        phi = 2*v*pi/self.vstep

        #Calculate the angle of the tangent to the ellipse
        tangent_angle = atan2(self.major_semi_radius*sin(phi), self.minor_semi_radius*cos(phi))

        #Calculate the X, Y and Z coordinates; place a circle at the origin on the YZ plane,
        #rotate it on the Z axis by the angle of the tangent to the ellipse, and finally,
        #move it to the correct position on the ellipse.
        x = self.tube_radius*sin(theta)*cos(tangent_angle)+self.major_semi_radius*cos(phi)
        y = self.tube_radius*sin(theta)*sin(tangent_angle)+self.minor_semi_radius*sin(phi)
        z = self.tube_radius*cos(theta)

        #Append the vertex coordinates to the list of vertices, and append a face to the list of faces.
        #The list of faces uses vertices that have not yet been created when appending intermediate faces,
        #however this is remedied at the end, as then it bridges with the vertices created at the beginning.
        #It uses modulo to make sure it doesn't overflow.
        vertices.append(Vector((x, y, z)))
        faces.append([v*self.ustep+u, v*self.ustep+((u+1)%self.ustep), ((v+1)%self.vstep)*self.ustep+((u+1)%self.ustep), ((v+1)%self.vstep)*self.ustep+u])

    #Create the mesh and the object, select it and make it active.
    elliptic_torus_mesh = bpy.data.meshes.new("Elliptic Torus")
    elliptic_torus_mesh.from_pydata(vertices, [], faces)
    elliptic_torus_mesh.update()
    elliptic_torus_object = bpy.data.objects.new("Elliptic Torus", elliptic_torus_mesh)
    context.scene.objects.link(elliptic_torus_object)
    elliptic_torus_object.select = True
    bpy.context.scene.objects.active = elliptic_torus_object
    return {"FINISHED"}

def register():
  bpy.utils.register_class(EllipticTorusOperator)
  bpy.utils.register_class(EllipticTorusMenuItem)

def unregister():
  bpy.utils.unregister_class(EllipticTorusOperator)
  bpy.utils.unregister_class(EllipticTorusMenuItem)

if __name__ == "__main__":
  register()

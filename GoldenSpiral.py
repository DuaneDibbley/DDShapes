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
    "name": "Golden Spiral",
    "author": "Duane Dibbley",
    "version": (0, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add a golden spiral",
    "warning": "",
    "wiki_url": "https://github.com/DuaneDibbley/DDShapes/wiki/DD-Shapes",
    "category": "Add Mesh"
}

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty
from math import sin, cos, atan2, pi, log, sqrt
from mathutils import Vector, Matrix

class MESH_OT_golden_spiral_add(Operator):
    bl_idname = "mesh.golden_spiral_add"
    bl_label = "Golden Spiral"
    bl_options = {"REGISTER", "UNDO"}

    #Define properties
    turns = IntProperty(name="Turns", description="Number of 90 degree turns", default=4, min=1)
    resolution = IntProperty(name="Resolution", description="Number of segments for each 90 degree turn", default=4, min=1, max=16)
    initial_radius = FloatProperty(name="Initial Radius", description="Initial radius of the spiral", default=1.0, min=0.01, step=1, precision=2)
    cross_segments = IntProperty(name="Cross-Section Segments", description="Number of segments of the cross-section", default=4, min=1, max=256)
    thickness_scaling = FloatProperty(name="Thickness Scaling", description="Cross-section thickness as a fraction of spiral radius", default=0.25, min=0.0, max=1.0, step=1, precision=2)

    #Variable definitions
    phi = (1+sqrt(5))/2 #Golden ratio

    #Function definitions
    #Derivative of the X equation for the spiral
    def xDerivative(self, theta):
        return -self.phi**(-2*theta/pi)*(2*cos(theta)*log(self.phi)+pi*sin(theta))/pi

    #Derivative of the Y equation for the spiral
    def yDerivative(self, theta):
        return self.phi**(-2*theta/pi)*(-2*sin(theta)*log(self.phi)+pi*cos(theta))/pi

    #Angle of the tangent line to the spiral
    def normalAngle(self, theta):
        return atan2(-self.xDerivative(theta), self.yDerivative(theta))

    #Create the mesh
    def execute(self, context):

        #Define the base shape of the cross-sections
        cross_vertices = []
        for v in range(self.cross_segments):
            theta = 2*v*pi/self.cross_segments
            x = cos(theta)
            y = 0.0
            z = sin(theta)
            cross_vertices.append(Vector((x, y, z)))

        #Define the base shape of the spiral
        spiral_vertices = []
        cross_transform = []
        for u in range(self.resolution*self.turns+1):
            theta = u*pi/(2*self.resolution)
            r = self.phi**(-u/self.resolution)
            x = r*cos(theta)
            y = r*sin(theta)
            z = 0.0
            spiral_vertices.append(Vector((x, y, z)))
            scale = Matrix().Scale(r*self.thickness_scaling, 4)
            rotation = Matrix().Rotation(self.normalAngle(theta), 4, Vector((0.0, 0.0, 1.0)))
            cross_transform.append(rotation*scale)

        vertices = []
        faces = []

        for u in range(self.resolution*self.turns+1):
            for v in range(self.cross_segments):
                vertices.append(cross_transform[u]*cross_vertices[v]+spiral_vertices[u])
                if u < self.resolution*self.turns:
                    faces.append([u*self.cross_segments+v, (u+1)*self.cross_segments+v, (u+1)*self.cross_segments+(v+1)%self.cross_segments, u*self.cross_segments+(v+1)%self.cross_segments])

        bpy.ops.object.select_all(action="DESELECT")

        golden_spiral_mesh = bpy.data.meshes.new("Golden Spiral")
        golden_spiral_mesh.from_pydata(vertices, [], faces)
        golden_spiral_mesh.update()
        golden_spiral_object = bpy.data.objects.new("Golden Spiral", golden_spiral_mesh)
        context.scene.objects.link(golden_spiral_object)
        golden_spiral_object.select = True
        bpy.context.scene.objects.active = golden_spiral_object

        return {"FINISHED"}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
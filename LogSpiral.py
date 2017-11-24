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
    "name": "Logarithmic Spiral",
    "author": "Duane Dibbley",
    "version": (0, 2, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add a logarithmic spiral",
    "warning": "",
    "wiki_url": "https://github.com/DuaneDibbley/DDShapes/wiki/DD-Shapes",
    "category": "Add Mesh"
}

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty
from math import sin, cos, atan2, pi, log, sqrt
from mathutils import Vector, Matrix

class MESH_OT_log_spiral_add(Operator):
    bl_idname = "mesh.log_spiral_add"
    bl_label = "Add Logarithmic Spiral"
    bl_options = {"REGISTER", "UNDO"}

    #Callbacks for enum properties
    #Cap fill types
    def getCapFillTypes(self, context):
        fill_types = []
        fill_types.append(("cap.none",
                           "None",
                           "Don't fill at all"))
        fill_types.append(("cap.ngon",
                           "Ngon",
                           "Use ngons"))
        fill_types.append(("cap.fan",
                           "Triangle Fan",
                           "Use triangle fans"))
        return fill_types

    #Define properties
    turns = IntProperty(name="Turns",
                        description="Number of 90 degree turns",
                        default=4,
                        min=1)
    resolution = IntProperty(name="Resolution",
                             description="Number of segments for each 90 degree turn",
                             default=4,
                             min=1,
                             max=16)
    initial_radius = FloatProperty(name="Initial Radius",
                                   description="Initial radius of the spiral",
                                   default=1.0,
                                   min=0.01,
                                   step=1,
                                   precision=2)
    radius_scaling = FloatProperty(name="Radius Scaling",
                                   description="Factor by which the radius shrinks for each 90 degree turn",
                                   default=(1+sqrt(5))/2,
                                   min=0.01,
                                   step=1,
                                   precision=2)
    cross_segments = IntProperty(name="Cross-Section Segments",
                                 description="Number of segments of the cross-section",
                                 default=4,
                                 min=1,
                                 max=256)
    cross_twist = FloatProperty(name="Cross-Section Twist",
                                description="The amount to twist the cross-sections for each 90 degree turn of the spiral",
                                default=0.0,
                                soft_min=-pi/2.0,
                                soft_max=pi/2.0,
                                step=10,
                                precision=3,
                                subtype="ANGLE")
    thickness_scaling = FloatProperty(name="Thickness Scaling",
                                      description="Cross-section thickness as a fraction of spiral radius",
                                      default=2/(1+sqrt(5)),
                                      min=0.0,
                                      max=1.0,
                                      step=1,
                                      precision=2)
    cap_fill = EnumProperty(items=getCapFillTypes,
                            name="Cap Fill Type",
                            description="How to fill the ends of the tube")

    #Function definitions
    #Derivative of the X equation for the spiral
    def xDerivative(self, theta):
        return -self.radius_scaling**(-2*theta/pi)*(2*cos(theta)*log(self.radius_scaling)+pi*sin(theta))/pi

    #Derivative of the Y equation for the spiral
    def yDerivative(self, theta):
        return self.radius_scaling**(-2*theta/pi)*(-2*sin(theta)*log(self.radius_scaling)+pi*cos(theta))/pi

    #Angle of the tangent line to the spiral
    def normalAngle(self, theta):
        return atan2(-self.xDerivative(theta), self.yDerivative(theta))

    #Create the mesh
    def execute(self, context):

        #Initial values
        cross_vertices = []
        cross_transform = []
        spiral_vertices = []
        vertices = []
        faces = []

        #Define the base shape of the cross-sections
        for v in range(self.cross_segments):
            theta = 2*v*pi/self.cross_segments
            x = cos(theta)
            y = 0.0
            z = sin(theta)
            cross_vertices.append(Vector((x, y, z)))

        #Define the base shape of the spiral
        for u in range(self.resolution*self.turns+1):
            theta = u*pi/(2*self.resolution)
            r = self.initial_radius*self.radius_scaling**(-u/self.resolution)
            x = r*cos(theta)
            y = r*sin(theta)
            z = 0.0
            spiral_vertices.append(Vector((x, y, z)))
            twist_angle = u*pi*self.cross_twist/(2*self.resolution)
            scale = Matrix().Scale(r*self.thickness_scaling, 4)
            rotation = Matrix().Rotation(self.normalAngle(theta), 4, Vector((0.0, 0.0, 1.0)))
            twist = Matrix().Rotation(twist_angle, 4, Vector((0.0, 1.0, 0.0)))
            cross_transform.append(rotation*twist*scale)

        if self.cap_fill == "cap.fan":
            vert_offset = 1
        else:
            vert_offset = 0

        for u in range(self.resolution*self.turns+1):
            for v in range(self.cross_segments):
                vertices.append(cross_transform[u]*cross_vertices[v]+spiral_vertices[u])
                if u < self.resolution*self.turns:
                    faces.append([u*self.cross_segments+v+vert_offset,
                                  (u+1)*self.cross_segments+v+vert_offset,
                                  (u+1)*self.cross_segments+(v+1)%self.cross_segments+vert_offset,
                                  u*self.cross_segments+(v+1)%self.cross_segments+vert_offset])

        if self.cap_fill == "cap.ngon":
            faces.insert(0, range(self.cross_segments))
            faces.append(range((self.resolution*self.turns+1)*self.cross_segments-1,
                                self.resolution*self.turns*self.cross_segments-1,
                                -1))
        elif self.cap_fill == "cap.fan":
            vertices.insert(0, spiral_vertices[0])
            vertices.append(spiral_vertices[self.resolution*self.turns])
            start_cap = []
            end_cap = []
            for v in range(self.cross_segments):
                start_cap.append([0,
                                  v+1,
                                  (v+1)%self.cross_segments+1])
                end_cap.append([(self.resolution*self.turns+1)*self.cross_segments+1,
                                (self.resolution*self.turns+1)*self.cross_segments-v,
                                (self.resolution*self.turns+1)*self.cross_segments-(v+1)%self.cross_segments])
            faces = start_cap+faces+end_cap

        bpy.ops.object.select_all(action="DESELECT")

        log_spiral_mesh = bpy.data.meshes.new("Logarithmic Spiral")
        log_spiral_mesh.from_pydata(vertices, [], faces)
        log_spiral_mesh.update()
        log_spiral_object = bpy.data.objects.new("Logarithmic Spiral", log_spiral_mesh)
        context.scene.objects.link(log_spiral_object)
        log_spiral_object.select = True
        bpy.context.scene.objects.active = log_spiral_object

        return {"FINISHED"}
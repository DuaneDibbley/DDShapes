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
    "name": "Elliptic Torus",
    "author": "Duane Dibbley",
    "version": (0, 3, 2),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add an elliptic torus with the cross-section correctly following the ellipse",
    "warning": "Some functionality depends on SciPy, however, this functionally is gracefully disabled if SciPy is unavailable.",
    "wiki_url": "https://github.com/DuaneDibbley/Tori/wiki/Tori",
    "category": "Add Mesh"
}

import sys
import bpy
from bpy.types import Panel, Menu, Operator
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, EnumProperty
from math import cos, sin, pi, fabs, sqrt, atan2
from mathutils import Vector, Matrix, Euler
from numpy import sinc

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

def getParamAndNormal(major, minor, steps, spacing_type):
    param_list = []
    normal_list = []
    for step in range(steps):
        if step == 0:
            param_list.append(0.0)
            normal_list.append(0.0)
        #All the algorithms yield the same result for circles,
        #thus we ignore spacing_type if major and minor are equal
        elif major == minor or spacing_type == "spacing.area":
            param_list.append(2*pi*step/steps)
            normal_list.append(atan2(major*sin(2*pi*step/steps), minor*cos(2*pi*step/steps)))
        elif spacing_type == "spacing.normal":
            normal_list.append(2*pi*step/steps)
            param_list.append(atan2(minor*sin(2*pi*step/steps), major*cos(2*pi*step/steps)))
        elif spacing_type == "spacing.radius":
            param_list.append(atan2(major*sin(2*pi*step/steps), minor*cos(2*pi*step/steps)))
            normal_list.append(atan2(major*sin(param_list[step]), minor*cos(param_list[step])))
        elif spacing_type == "spacing.arc":
            circumference = 2*pi*max(major, minor)*hyp2f1(-.5, .5, 1, 1-(min(major, minor)/max(major, minor))**2)
            arc_length = circumference*step/steps
            param_list.append(fsolve(arcLength, [0.0], args=(major, minor, arc_length))[0])
            normal_list.append(atan2(major*sin(param_list[step]), minor*cos(param_list[step])))

    return param_list, normal_list

def getTwistAngle(twist, amplitude, twist_type, v, step):
    if twist_type == "twist.sine":
        twist_angle = amplitude*sin(twist*2*v*pi/step)
    elif twist_type == "twist.sincn":
        twist_angle = amplitude*sinc(twist*(2*v/step-1.0))
    elif twist_type =="twist.sinc":
        twist_angle = amplitude*sinc(twist*(2*v/step-1.0)/pi)
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
    twist_types.append(("twist.sinc", "Cardinal Sine (un-normalized)", "Twist back and forth like a sinc function"))
    twist_types.append(("twist.sincn", "Cardinal Sine (normalized)", "Twist back and forth like a sinc function"))
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
    ring_axes = FloatVectorProperty(name="Ring's Semi-Axes", description="The semi-axes of the ring", default=(2.3, 1.05), min=0.0, max=100.0, step=1, precision=3, subtype="NONE", unit="NONE", size=2)
    vstep = IntProperty(name="Ring Segments", description="Number of segments for the ellipse", default=48, min=4, max=1024)
    ring_spacing_type = EnumProperty(items=getSpacingTypes, name="Ring Spacing", description="Define how to calculate the space between the points on the ring")
    cross_axes = FloatVectorProperty(name="Cross-Section's Semi-Axes", description="The semi-axes of the cross-section", default=(0.2, 0.1), min=0.0, max=100.0, step=1, precision=3, subtype="NONE", unit="NONE", size=2)
    ustep = IntProperty(name="Cross-Section Segments", description="Number of segments for the cross-section", default=12, min=4, max=1024)
    cross_spacing_type = EnumProperty(items=getSpacingTypes, name="Cross-Section Spacing", description="Define how to calculate the space between the points on the cross-section")
    cross_twist = IntProperty(name="Cross-Section Twists", description="Number of twists of the cross-section", default=0, min=0, max=256)
    cross_twist_amplitude = FloatProperty(name="Twist Amplitude", description="The angle each twist equals", default=pi, min=0, soft_max=2*pi, step=10, precision=3, subtype="ANGLE")
    cross_twist_type = EnumProperty(items=getTwistTypes, name="Twist Type", description="Define how the twisting is done")
    cross_rotation = FloatProperty(name="Cross-Section Initial Twist", description="Initial twist of the cross-section", default=0.0, min=-pi/2.0, max=pi/2.0, step=10, precision=3, subtype="ANGLE")
    tube_thickness_method = EnumProperty(items=getThicknessMethods, name="Tube Thickness Method", description="How to calculate the tube thickness")

    def execute(self, context):
        #Create the base shape of the cross-section
        cross_base_vertices = []
        cross_params, cross_normals = getParamAndNormal(self.cross_axes[0], self.cross_axes[1], self.ustep, self.cross_spacing_type)
        for u in range(self.ustep):
            x = self.cross_axes[0]*cos(cross_params[u])
            y = 0.0
            z = self.cross_axes[1]*sin(cross_params[u])
            cross_base_vertices.append(Vector((x, y, z)))

        #Create the base shape of the ring, and combine it with information on how to rotate and align the cross-section
        ring_vertices = []
        ring_params, ring_normals = getParamAndNormal(self.ring_axes[0], self.ring_axes[1], self.vstep, self.ring_spacing_type)
        for v in range(self.vstep):
            x = self.ring_axes[0]*cos(ring_params[v])
            y = self.ring_axes[1]*sin(ring_params[v])
            z = 0.0
            ring_vertices.append(Vector((x, y, z)))

        #Calculate cross-section transformation matrix for each of the vertices of the ring
        cross_transforms = []
        for v in range(self.vstep):
            prev_vertex = ring_vertices[(self.vstep+v-1)%self.vstep]
            this_vertex = ring_vertices[v]
            next_vertex = ring_vertices[(v+1)%self.vstep]
            angle = (this_vertex-prev_vertex).angle(this_vertex-next_vertex)/2.0
            cross_trans_mat = Matrix().Rotation(self.cross_rotation+getTwistAngle(self.cross_twist, self.cross_twist_amplitude, self.cross_twist_type, v, self.vstep), 4, Vector((0.0, 1.0, 0.0)))
            if self.tube_thickness_method == "thickness.tube":
                cross_trans_mat = Matrix().Scale(1.0/sin(angle), 4, Vector((1.0, 0.0, 0.0)))*cross_trans_mat
            cross_trans_mat = Matrix().Rotation(ring_normals[v], 4, Vector((0.0, 0.0, 1.0)))*cross_trans_mat
            cross_transforms.append(cross_trans_mat)

        vertices = []
        faces = []
        for v in range(self.vstep):
            for u in range(self.ustep):
                cross_vertex = cross_transforms[v]*cross_base_vertices[u]+ring_vertices[v]

                #Append the vertex coordinates to the list of vertices, and append a face to the list of faces.
                #The list of faces uses vertices that have not yet been created when appending intermediate faces,
                #however this is remedied at the end, as then it bridges with the vertices created at the beginning.
                #It uses modulo to make sure it doesn't overflow.
                vertices.append(cross_vertex)
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
        context.scene.objects.link(elliptic_torus_object)
        elliptic_torus_object.select = True
        bpy.context.scene.objects.active = elliptic_torus_object
        return {"FINISHED"}

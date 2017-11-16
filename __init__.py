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
    "name": "DD Shapes",
    "author": "Duane Dibbley",
    "version": (0, 3, 2),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "description": "Add-ons for creating various mathematically generated shapes.",
    "warning": "Some functionality depends on SciPy, however, this functionally is gracefully disabled if SciPy is unavailable.",
    "wiki_url": "https://github.com/DuaneDibbley/DDShapes/wiki/DD-Shapes",
    "category": "Add Mesh"
}

import bpy
from bpy.types import Menu, INFO_MT_mesh_add
from . import EllipticTorus

class INFO_MT_dd_shapes_menu(Menu):
    bl_idname = "INFO_MT_dd_shapes_menu"
    bl_label = "DD Shapes"

    def draw(self, context):
        layout.label(text="DD Shapes", icon='MESH_DATA')
        self.layout.menu("INFO_MT_mesh_elliptic_torus_add", icon="MESH_TORUS")

class INFO_MT_mesh_elliptic_torus_add(Menu):
    bl_idname = "INFO_MT_mesh_elliptic_torus_add"
    bl_label = "Elliptic Torus"

    def draw(self, context):
        self.layout.operator("mesh.elliptic_torus_add")

    INFO_MT_dd_shapes_menu.append(draw)

def menu_func(self, context):
    self.layout.menu("INFO_MT_dd_shapes_menu", text="DD Shapes", icon="MESH_DATA")

def register():
    bpy.types.INFO_MT_mesh_add.append(menu_func)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

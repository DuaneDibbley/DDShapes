from . import EllipticTorusOperator
from bpy.types import Menu

class EllipticTorusMenuItem(Menu):
  bl_idname = "OBJECT_MT_elliptic_torus"
  bl_label = "Elliptic Torus"

  def draw(self, context):
    self.layout.operator("mesh.add_elliptic_torus")

  INFO_MT_mesh_add.append(draw)

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

from math import cos, sin, atan2, pi, sqrt
from scipy.integrate import quad
from scipy.optimize import fsolve
from scipy.special import hyp2f1

def arcFunc(theta, major, minor):
  return sqrt((-major*sin(theta))**2+(minor*cos(theta))**2)

def arcLength(theta, major, minor, arc_length):
  return quad(arcFunc, a=0.0, b=theta, args=(major, minor))[0]-arc_length

def getParamAndNormal(major, minor, input_param, steps, spacing_type):
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
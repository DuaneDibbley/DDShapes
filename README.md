# Tori
Blender add-ons for creating tori of varying configurations

Some functionality depends on SciPy. The existence of SciPy is checked for at run-time, and if it is not available, this functionality is gracefully disabled.  
For information on how to get SciPy to work in Blender, take a look at [Using 3rd party Python modules](https://blender.stackexchange.com/questions/5287/using-3rd-party-python-modules) at [Blender Stack Exchange](https://blender.stackexchange.com/).

-----

## Installation
1. Click the **Clone or download** button and save the zip file to your harddrive, but do not unzip it.
2. Open up Blender and hit Ctrl+Alt+U or click _File_ -> _User Preferences_
3. Click _Add-ons_
4. Click _Install Add-on from File..._
5. Select the file you downloaded in step 1 and click _Install Add-on from File..._
6. The name _Add Mesh: Tori_ should appear in the list of add-ons. Click the check box next to it, to enable it.
7. _(Optional):_ To make the change persist, click _Save User Settings_
8. Close the user preferences window.

-----

## Usage

### EllipticTorus
Click _Add_ -> _Mesh_ -> _Elliptic Torus_ or press Shift+A followed by M then click _Elliptic Torus_.  
This creates an elliptic torus with the cross-section correctly following the ellipse. It does so by calculating the normal of the ellipse and rotating the cross-section accordingly.

#### Settings
_Ring's Semi-Axes_ is a 2D vector with the length of the ring's semi-axes.  
_Ring Segments_ is the number of segements into which the ring is divided.  
_Ring Spacing_ defines how to calculate the distance between the the cross-sections along the ring.  
_Cross-Section's Semi-Axes_ is a 2D vector with the length of the ring's semi-axes.  
_Cross-Section Segments_ is the number of segements into which the cross-section is divided.  
_Cross-Section Twists_ is the number of twists to do along the ring.  
_Twist Amplitude_ is the angle that each twist represents. Playing with this if the twist type is set to linear will cause an abrupt twist at the bridging between the first and the last cross-section, unless 
_Twist Type_ sets the algorithm to use for calculating the twists.  
_Cross-Section Initial Twist_ rotates the cross-section on the Y axis **before** aligning it with the ring's normal and moving it to its position. This is the starting rotation, from which the twisting is calculated.  
_Cross-Section Spacing_ defines how to calculate the distance between the vertices of the cross-section.  
_Tube Thickness Method_ defines how to calculate the tube thickness.  

Setting the major and minor semi-axes to the same value, makes a circle.

Setting the major semi-axis to a smaller value than the minor semi-axis is perfectly fine. While semantically an error, it doesn't pose a mathematical problem; if you do this with the ring, it will be stretched on the Y axis rather than on the X axis, and if you do this on the cross-section, it will be taller than it is wide.

##### Spacing
Equal Area spacing just uses the standard equations for an ellipse, which cause the sectors of the ellipse to have an equal area.  
Equiangular Normal places the vertices of the ellipse such that the angle between the normals to the ellipse is constant.  
Equirectangular Radius places vertices of the ellipse the such that the angle between the radii is constant.  
[SciPy] Equal Arc Length places the vertices of the ellipse at (roughly) equal distance along the limit curve's arc length. This is a bit slow, however, calculating the arc length is non-trivial, though I have optimised it quite a bit.

##### Twisting
Causes the torus to be twisted. This is calculated as if the distance between two adjacent cross-sections is constant along the circumference of the ring, so the appearance is affected by the ring spacing of the ring.

###### Twist Type
Linear increases the twist linearly between each cross-section.
Sinusoidal twists back and forth like a sine wave along the tube.  
Cardinal Sin (un-normalized) twists back and forth like a sinc function (sin(x)/x).
Cardinal Sine (normalized) twists back and forth like a normalized sinc function (sin(pi*x)/(pi*x)).

###### Twist amplitude
If you set the twist type to linear, you need to make sure <_number of twists_>x<_amplitude_> is divisible by 180 (if using degrees) or pi (if using radians), or you will see an abrupt twist where the first and last cross-sections are bridged together.

##### Tube thickness
Equal Cross-Sections leaves the cross-sections at the size defined by the cross-section axes settings. However, if the ring is highly eccentric and/or has a very low segment count, this will cause the tube to be visibly thinner near accute angles and visibly thicker near obtuse angles.  
Constant Tube Thickness scales the cross-sections to accommodate for the varying thickness with highly eccentric rings and rings with a low segment count. However, if you then subdivide using a smoothing algorithm like Catmull-Clark, this may backfire and actually make the tube visibly thicker at accute angles and visible thinner at obtuse angles.

I've not been able to find an all purpose algorithm, and these are the best I've been able to come up with so far. You need to choose on a case by case basis.
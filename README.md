# Tori
Blender add-ons for creating tori of varying configurations

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
_Ring's Major Semi-Axis_ is half the length of the major axis of the ellipse.  
_Ring's Minor Semi-Axis_ is half the length of the major axis of the ellipse.  
_Ring Segments_ is the number of segements into which the ring is divided.  
_Spacing_ defines how to calculate the distance between the the cross-sections along the ring.  
_Cross-Section's Major Semi-Axis_ is half the length of the major axis of the cross-section.  
_Cross-Section's Minor Semi-Axis_ is half the length of the minor axis of the cross-section.  
_Cross-Section Segments_ is the number of segements into which the cross-section is divided.

Setting the major and minor semi-axes to the same value, makes a circular torus. The vertex order may differ from the torus built into Blender, but in all other respects it will be identical.

Setting the major semi-axis to a smaller value than the minor semi-axis is perfectly fine. While semantically an error, it doesn't pose a mathematical problem; the resulting torus will simply appear to have been rotated by 90 degress on the Z axis.

##### Spacing
Equal Area spacing just uses the standard equations for an ellipse, which cause the sectors of the ellipse to have an equal area.  
Equiangular Normal places the circles of the cross-section such that the angle between the normals to the ellipse is constant.  
Equirectangular Radius  places the circles of the cross-section such that the angle between the radii is constant

# Tori
Blender add-ons for creating tori of varying configurations

-----
## EllipticTorus
This creates an elliptic torus with the cross-section correctly following the ellipse. It does so by calculating the normal of the ellipse and rotating the cross-section accordingly.

### Settings
_Major Semi-Radius_ is half the size of the major axis of the ellipse.  
_Minor Semi-Radius_ is half the size of the major axis of the ellipse.  
_Ellipse Segments_ is the number of segements into which the ellipse is divided.  
_Spacing_ defines how to calculate the distance between the circles of the cross-section along the ellipse.  
_Tube Radius_ is the radius of the cross-section.  
_Tube Segments_ is the number of segements into which the cross-section is divided.

Setting the major and minor semi-radii to the same value, makes a circular torus. The vertex order may differ from the torus built into Blender, but in all other respects it will be identical.

Setting the major semi-radius to a smaller value than the minor semi-radius is perfectly fine. While semantically an error, it doesn't pose a mathematical problem; the resulting torus will simply appear to have been rotated by 90 degress on the Z axis.

#### Spacing
Simple spacing just uses the standard equations for an ellipse.  
Equiangular Normal places the circles of the cross-section such that the angle between the normals to the ellipse is constant.  
Equirectangular Radius  places the circles of the cross-section such that the angle between the radii is constant

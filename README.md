# AnimAll

A fork of [AnimAll](https://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Animation/AnimAll) by [Daniel "ZanQdo" Salazar](https://github.com/ZanQdo)

## Changes

* This patch allows keying only selected points for meshes, curves and lattices.
* Fix keying POLY splines
* Add fcurves to groups by element (Vertex, Edge, etc.), to keep the dope sheet and graph editor less cluttered
* This does not currently work for curves: the fcurves are unassigned on switching modes. Presumably due to a bug in Blender, since it works for meshes.

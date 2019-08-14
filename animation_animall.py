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
    "name": "AnimAll",
    "author": "Daniel Salazar <zanqdo@gmail.com>",
    "version": (0, 8, 2),
    "blender": (2, 80, 0),
    "location": "3D View > Toolbox > Animation tab > AnimAll",
    "description": "Allows animation of mesh, lattice, curve and surface data",
    "warning": "",
    "wiki_url": "https://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Animation/AnimAll",
    "category": "Animation",
}

"""
Thanks to Campbell Barton and Joshua Leung for hes API additions and fixes
Daniel 'ZanQdo' Salazar
"""

import bpy
from bpy.types import (
        Operator,
        Panel,
        AddonPreferences,
        )
from bpy.props import (
        BoolProperty,
        StringProperty,
        )


# Property Definitions
class AnimallProperties(bpy.types.PropertyGroup):
    key_selected: BoolProperty(
        name="Selected Only",
        description="Insert keyframes only on selected elements",
        default=True
    )
    key_shape: BoolProperty(
        name="Shape",
        description="Insert keyframes on active Shape Key layer",
        default=False
    )
    key_uvs: BoolProperty(
        name="UVs",
        description="Insert keyframes on active UV coordinates",
        default=False
    )
    key_ebevel: BoolProperty(
        name="E-Bevel",
        description="Insert keyframes on edge bevel weight",
        default=False
    )
    key_vbevel: BoolProperty(
        name="V-Bevel",
        description="Insert keyframes on vertex bevel weight",
        default=False
    )
    key_crease: BoolProperty(
        name="Crease",
        description="Insert keyframes on edge creases",
        default=False
    )
    key_vcols: BoolProperty(
        name="V-Cols",
        description="Insert keyframes on active Vertex Color values",
        default=False
    )
    key_vgroups: BoolProperty(
        name="V-groups",
        description="Insert keyframes on active Vertex group values",
        default=False
    )
    key_points: BoolProperty(
        name="Points",
        description="Insert keyframes on point locations",
        default=False
    )
    key_radius: BoolProperty(
        name="Radius",
        description="Insert keyframes on point radius (Shrink/Fatten)",
        default=False
    )
    key_tilt: BoolProperty(
        name="Tilt",
        description="Insert keyframes on point tilt",
        default=False
    )


# Utility functions

def refresh_ui_keyframes():
    try:
        for area in bpy.context.screen.areas:
            if area.type in ('TIMELINE', 'GRAPH_EDITOR', 'DOPESHEET_EDITOR'):
                area.tag_redraw()
    except:
        pass


def insert_key(data, key, group=''):
    try:
        data.keyframe_insert(key, group=group)
    except:
        pass


def delete_key(data, key):
    try:
        data.keyframe_delete(key)
    except:
        pass


# GUI (Panel)

class VIEW3D_PT_animall(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Animation"
    bl_label = 'AnimAll'

    @classmethod
    def poll(self, context):
        return context.active_object and context.active_object.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}

    def draw(self, context):
        obj = context.active_object
        animall_properties = context.window_manager.animall_properties

        layout = self.layout
        col = layout.column(align=True)
        row = col.row()
        row.prop(animall_properties, "key_selected")
        col.separator()

        row = col.row()

        if obj.type == 'LATTICE':
            row.prop(animall_properties, "key_points")
            row.prop(animall_properties, "key_shape")

        elif obj.type == 'MESH':
            row.prop(animall_properties, "key_points")
            row.prop(animall_properties, "key_shape")
            row = col.row()
            row.prop(animall_properties, "key_ebevel")
            row.prop(animall_properties, "key_vbevel")
            row = col.row()
            row.prop(animall_properties, "key_crease")
            row.prop(animall_properties, "key_uvs")
            row = col.row()
            row.prop(animall_properties, "key_vcols")
            row.prop(animall_properties, "key_vgroups")

        elif obj.type == 'CURVE':
            row.prop(animall_properties, "key_points")
            row.prop(animall_properties, "key_shape")
            row = col.row()
            row.prop(animall_properties, "key_radius")
            row.prop(animall_properties, "key_tilt")

        elif obj.type == 'SURFACE':
            row.prop(animall_properties, "key_points")
            row.prop(animall_properties, "key_shape")
            row = col.row()
            row.prop(animall_properties, "key_radius")
            row.prop(animall_properties, "key_tilt")

        layout.separator()
        row = layout.row(align=True)
        row.operator("anim.insert_keyframe_animall", icon="KEY_HLT")
        row.operator("anim.delete_keyframe_animall", icon="KEY_DEHLT")
        row = layout.row()
        row.operator("anim.clear_animation_animall", icon="X")

        if animall_properties.key_shape:
            shape_key = obj.active_shape_key
            shape_key_index = obj.active_shape_key_index

            split = layout.split()
            row = split.row()

            if shape_key_index > 0:
                row.label(text=shape_key.name, icon="SHAPEKEY_DATA")
                row.prop(shape_key, "value", text="")
                row.prop(obj, "show_only_shape_key", text="")
                if shape_key.value < 1:
                    row = layout.row()
                    row.label(text='Maybe set "%s" to 1.0?' % shape_key.name, icon="INFO")
            elif shape_key:
                row.label(text="Cannot key on Basis Shape", icon="ERROR")
            else:
                row.label(text="No active Shape Key", icon="ERROR")

        if animall_properties.key_points and animall_properties.key_shape:
            row = layout.row()
            row.label(text='"Points" and "Shape" are redundant?', icon="INFO")


class ANIM_OT_insert_keyframe_animall(Operator):
    bl_label = "Insert"
    bl_idname = "anim.insert_keyframe_animall"
    bl_description = "Insert a Keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.execute(context)

        return {'FINISHED'}

    def execute(op, context):
        obj = context.active_object
        animall_properties = context.window_manager.animall_properties

        # Set object mode
        if obj.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}:
            mode = obj.mode
            bpy.ops.object.mode_set(mode='OBJECT')

            data = obj.data

        if obj.type == 'MESH':
            for v_i, vert in enumerate(data.vertices):
                if not animall_properties.key_selected or vert.select:
                    if animall_properties.key_points:
                        insert_key(vert, 'co', group="vertex %s" % v_i)
                    if animall_properties.key_vbevel:
                        insert_key(vert, 'bevel_weight', group="vertex %s" % v_i)
                    if animall_properties.key_vgroups:
                        for group in vert.groups:
                            insert_key(group, 'weight', group="vertex %s" % v_i)

            for e_i, edge in enumerate(data.edges):
                if not animall_properties.key_selected or edge.select:
                    if animall_properties.key_ebevel:
                        insert_key(edge, 'bevel_weight', group="edge %s" % e_i)
                    if animall_properties.key_crease:
                        insert_key(edge, 'crease', group="edge %s" % e_i)

            if animall_properties.key_shape:
                if obj.active_shape_key_index > 0:
                    for v_i, vert in enumerate(obj.active_shape_key.data):
                        insert_key(vert, 'co', group="vertex %s" % v_i)

            if animall_properties.key_uvs:
                if data.uv_layers.active is not None:
                    for uv_i, uv in enumerate(data.uv_layers.active.data):
                        insert_key(uv, 'uv', group="UV layer %s" % uv_i)

            if animall_properties.key_vcols:
                for v_col_layer in data.vertex_colors:
                    if v_col_layer.active:  # only insert in active VCol layer
                        for v_i, data in enumerate(v_col_layer.data):
                            insert_key(data, 'color', group="Loop %s" % v_i)

        elif obj.type == 'LATTICE':
            if animall_properties.key_shape:
                if obj.active_shape_key_index > 0:
                    for p_i, point in enumerate(obj.active_shape_key.data):
                        insert_key(point, 'co', group="Point %s" % p_i)

            if animall_properties.key_points:
                for p_i, point in enumerate(data.points):
                    if not animall_properties.key_selected or point.select:
                        insert_key(point, 'co_deform', group="Point %s" % p_i)

        elif obj.type in {'CURVE', 'SURFACE'}:
            # run this outside the splines loop (only once)
            if animall_properties.key_shape:
                if obj.active_shape_key_index > 0:
                    for CV in obj.active_shape_key.data:
                        insert_key(CV, 'co')
                        insert_key(CV, 'handle_left')
                        insert_key(CV, 'handle_right')

            for s_i, spline in enumerate(data.splines):
                if spline.type == 'BEZIER':

                    for v_i, CV in enumerate(spline.bezier_points):
                        if (not animall_properties.key_selected
                                or CV.select_control_point
                                or CV.select_left_handle
                                or CV.select_right_handle):
                            if animall_properties.key_points:
                                insert_key(CV, 'co', group="spline %s CV %s" % (s_i, v_i))
                                insert_key(CV, 'handle_left', group="spline %s CV %s" % (s_i, v_i))
                                insert_key(CV, 'handle_right', group="spline %s CV %s" % (s_i, v_i))

                            if animall_properties.key_radius:
                                insert_key(CV, 'radius', group="spline %s CV %s" % (s_i, v_i))

                            if animall_properties.key_tilt:
                                insert_key(CV, 'tilt', group="spline %s CV %s" % (s_i, v_i))

                elif spline.type in ('POLY', 'NURBS'):
                    for v_i, CV in enumerate(spline.points):
                        if not animall_properties.key_selected or CV.select:
                            if animall_properties.key_points:
                                insert_key(CV, 'co', group="spline %s CV %s" % (s_i, v_i))

                            if animall_properties.key_radius:
                                insert_key(CV, 'radius', group="spline %s CV %s" % (s_i, v_i))

                            if animall_properties.key_tilt:
                                insert_key(CV, 'tilt', group="spline %s CV %s" % (s_i, v_i))

        # Set previous mode
        if obj.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}:
            bpy.ops.object.mode_set(mode=mode)

        refresh_ui_keyframes()

        return {'FINISHED'}


class ANIM_OT_delete_keyframe_animall(Operator):
    bl_label = "Delete"
    bl_idname = "anim.delete_keyframe_animall"
    bl_description = "Delete a Keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.execute(context)

        return {'FINISHED'}

    def execute(op, context):
        obj = context.active_object
        animall_properties = context.window_manager.animall_properties

        # Set object mode
        if obj.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}:
            mode = obj.mode
            bpy.ops.object.mode_set(mode='OBJECT')

            data = obj.data

        if obj.type == 'MESH':
            if animall_properties.key_shape:
                if obj.active_shape_key:
                    for vert in obj.active_shape_key.data:
                        delete_key(vert, 'co')

            if animall_properties.key_points:
                for vert in data.vertices:
                    delete_key(vert, 'co')

            if animall_properties.key_ebevel:
                for edge in data.edges:
                    delete_key(edge, 'bevel_weight')

            if animall_properties.key_vbevel:
                for vert in data.vertices:
                    delete_key(vert, 'bevel_weight')

            if animall_properties.key_crease:
                for edge in data.edges:
                    delete_key(edge, 'crease')

            if animall_properties.key_vgroups:
                for vert in data.vertices:
                    for group in vert.groups:
                        delete_key(group, 'weight')

            if animall_properties.key_uvs:
                for UV in data.uv_layers.active.data:
                    delete_key(UV, 'uv')

            if animall_properties.key_vcols:
                for v_col_layer in data.vertex_colors:
                    if v_col_layer.active:  # only delete in active VCol layer
                        for data in v_col_layer.data:
                            delete_key(data, 'color')

        if obj.type == 'LATTICE':
            if animall_properties.key_shape:
                if obj.active_shape_key:
                    for point in obj.active_shape_key.data:
                        delete_key(point, 'co')

            if animall_properties.key_points:
                for point in data.points:
                    delete_key(Point, 'co_deform')

        if obj.type in {'CURVE', 'SURFACE'}:
            # run this outside the splines loop (only once)
            if animall_properties.key_shape:
                if obj.active_shape_key_index > 0:
                    for CV in obj.active_shape_key.data:
                        delete_key(CV, 'co')
                        delete_key(CV, 'handle_left')
                        delete_key(CV, 'handle_right')

            for spline in data.splines:
                if spline.type == 'BEZIER':
                    for CV in spline.bezier_points:
                        if animall_properties.key_points:
                            delete_key(CV, 'co')
                            delete_key(CV, 'handle_left')
                            delete_key(CV, 'handle_right')
                        if animall_properties.key_radius:
                            delete_key(CV, 'radius')
                        if animall_properties.key_tilt:
                            delete_key(CV, 'tilt')

                elif spline.type == 'NURBS':
                    for CV in spline.points:
                        if animall_properties.key_points:
                            delete_key(CV, 'co')
                        if animall_properties.key_radius:
                            delete_key(CV, 'radius')
                        if animall_properties.key_tilt:
                            delete_key(CV, 'tilt')

        # Set previous mode
        if obj.type in {'MESH', 'LATTICE', 'CURVE', 'SURFACE'}:
            bpy.ops.object.mode_set(mode=mode)

        refresh_ui_keyframes()

        return {'FINISHED'}


class ANIM_OT_clear_animation_animall(Operator):
    bl_label = "Clear Animation"
    bl_idname = "anim.clear_animation_animall"
    bl_description = ("Delete all keyframes for this object\n"
                      "If in a specific case it doesn't work\n"
                      "try to delete the keys manually")
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_confirm(self, event)

    def execute(self, context):
        try:
            data = context.active_object.data
            data.animation_data_clear()
        except:
            self.report({'WARNING'}, "Clear Animation could not be performed")
            return {'CANCELLED'}

        refresh_ui_keyframes()

        return {'FINISHED'}


# Add-ons Preferences Update Panel

# Define Panel classes for updating
panels = [
        VIEW3D_PT_animall
        ]


def update_panel(self, context):
    message = "AnimAll: Updating Panel locations has failed"
    try:
        for panel in panels:
            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)

        for panel in panels:
            panel.bl_category = context.preferences.addons[__name__].preferences.category
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass


class AnimallAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    category: StringProperty(
        name="Tab Category",
        description="Choose a name for the category of the panel",
        default="Animation",
        update=update_panel
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()

        col.label(text="Tab Category:")
        col.prop(self, "category", text="")


def register():
    bpy.utils.register_class(AnimallProperties)
    bpy.types.WindowManager.animall_properties = bpy.props.PointerProperty(type=AnimallProperties)
    bpy.utils.register_class(VIEW3D_PT_animall)
    bpy.utils.register_class(ANIM_OT_insert_keyframe_animall)
    bpy.utils.register_class(ANIM_OT_delete_keyframe_animall)
    bpy.utils.register_class(ANIM_OT_clear_animation_animall)
    bpy.utils.register_class(AnimallAddonPreferences)
    update_panel(None, bpy.context)


def unregister():
    del bpy.types.WindowManager.animall_properties
    bpy.utils.unregister_class(AnimallProperties)
    bpy.utils.unregister_class(VIEW3D_PT_animall)
    bpy.utils.unregister_class(ANIM_OT_insert_keyframe_animall)
    bpy.utils.unregister_class(ANIM_OT_delete_keyframe_animall)
    bpy.utils.unregister_class(ANIM_OT_clear_animation_animall)
    bpy.utils.unregister_class(AnimallAddonPreferences)

if __name__ == "__main__":
    register()

'''
@file       ui.py
@brief      Handles all Beamblend UI panels.
@author     Alyssa Greenwell

Detailed Description:
Contains all the panels displayed for the Beamblend add-on.
'''
import bpy
from .helpers import get_object_root

class LibraryPanel(bpy.types.Panel):
    '''
    Contains the library of Beamblend objects that can be spawned into the 
    scene. Also contains miscellaneous operations that pertain to the scene.
    '''
    bl_idname = "VIEW3D_PT_Lighting_Library"
    bl_label = "Lighting Library"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BeamBlend"
    
    def draw(self, context):
        self.layout.label(text="Fixtures")
        
        op = self.layout.operator("beamblend.import_model", 
                                  text="Source 4 750 Ellipsoidal")
        op.model_name = "Source4750"
        
        op = self.layout.operator("beamblend.import_model", 
                                  text="ColorSource Fresnel V")
        op.model_name = "ColorSourceFresnelV"
        
        op = self.layout.operator("beamblend.import_model",
                                  text="PAR 64 FFS WFL")
        op.model_name = "PAR64"
        
        self.layout.label(text="Stages")
        
        op = self.layout.operator("beamblend.import_model", 
                                  text="Proscenium Stage")
        op.model_name = "ProsceniumStage"
        
        self.layout.label(text="Electrics")
        
        op = self.layout.operator("beamblend.import_model", 
                             text = "Pipe")
        op.model_name = "Pipe"
        
        self.layout.label(text="Operations")
        
        self.layout.operator("beamblend.snap_to_pipe", 
                             text = "Snap To Pipe")
        
        self.layout.operator("beamblend.delete_object", 
                             text = "Delete Objects")
        
        self.layout.operator("beamblend.toggle_extras", text="Toggle Spot Outlines")

class FixtureProperties(bpy.types.Panel):
    '''
    Contains all customizable Beamblend fixture properties (see properties.py)
    that represent physical operations. In other words, all the properties that
    are not stored in a cue. Things that would have to be physically set before
    a show and cannot be changed during a show.
    '''
    bl_idname = "PROPERTIES_PT_fixture_properties"
    bl_label = "Fixture Properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        obj = get_object_root(context.active_object)

        return (
            obj is not None and
            obj.get("obj_type") == "FIXTURE"
        )

    def draw(self, context):
        layout = self.layout
        obj = get_object_root(context.active_object)
        fixture_type = obj.get("fix_type")
        
        self.layout.label(text="Fixture Position (degrees)")
        layout.prop(obj.beamblend, "pan", slider=True)
        layout.prop(obj.beamblend, "tilt", slider=True)
        
        if fixture_type == "SOURCE4" or fixture_type == "PAR64":
            self.layout.label(text="Light Properties")
        
        if fixture_type == "SOURCE4":
            layout.prop(obj.beamblend, "focus", slider=True)
            
        if fixture_type == "SOURCE4" or fixture_type == "PAR64":
            layout.prop(obj.beamblend, "gel")
        
class FixtureProgrammables(bpy.types.Panel):
    '''
    Contains all customizable Beamblend fixture properties (see properties.py)
    that represent things that can be programmed, including intensity and all 
    DMX controlled properties of the light. Everything in this panel can be
    stored as a fixture state in a cue.
    '''
    bl_idname = "PROPERTIES_PT_fixture_programmables"
    bl_label = "Fixture Programming"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
        
    @classmethod
    def poll(cls, context):
        obj = get_object_root(context.active_object)

        return (
            obj is not None and
            obj.get("obj_type") == "FIXTURE"
        )

    def draw(self, context):
        layout = self.layout
        obj = get_object_root(context.active_object)
        fixture_type = obj.get("fix_type")
        
        # Intensity
        layout.prop(obj.beamblend, "intensity", slider=True)
        row = layout.row()
        op = row.operator("beamblend.set_intensity", text="OFF")
        op.intensity = 0.0
        op = row.operator("beamblend.set_intensity", text="50%")
        op.intensity = 50.0
        op = row.operator("beamblend.set_intensity", text="FULL")
        op.intensity = 100.0
        
        # DMX Properties
        if fixture_type == "COLORSOURCE":
            layout.prop(obj.beamblend, "zoom", slider=True)
            layout.prop(obj.beamblend, "color")


class BEAMBLEND_UL_cues(bpy.types.UIList):
    '''
    UI List of cues.
    '''

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index
    ):
        cue = item
        
        split1 = layout.split(factor=0.25)
        col1 = split1.column()
        col1.prop(cue, "index", text="")
        
        split2 = split1.split(factor=0.66)
        col2 = split2.column()
        col2.prop(cue, "name", text="")
        
        col3 = split2.column()
        col3.prop(cue, "transition_time", text="")


class CueList(bpy.types.Panel):
    '''
    Panel that contains the UI list of cues (above) as well as all cue-related
    operations.
    '''
    bl_idname = "VIEW3D_PT_Cue_List"
    bl_label = "Cue List"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BeamBlend"
    
    def draw(self, context):
        layout = self.layout
        programming = context.scene.beamblend_programming
        
        split1 = layout.split(factor=0.25)
        col1 = split1.column()
        col1.label(text="Index") 
        
        split2 = split1.split(factor=0.66)
        col2 = split2.column()
        col2.label(text="Name")
        
        col3 = split2.column()
        col3.label(text="Duration")
        
        layout.template_list(
            "BEAMBLEND_UL_cues","",
            programming,"cues",
            programming,"current_cue"
        )
        
        row = layout.row()
        
        row.operator("beamblend.record_cue", 
                            text = "Record Cue")
        row.operator("beamblend.update_cue", 
                             text = "Update Cue")
        row.operator("beamblend.delete_cue", 
                             text = "Delete Cue")
        
        self.layout.operator("beamblend.go",
                             text = "GO")

        
classes = (
    LibraryPanel, FixtureProperties, FixtureProgrammables, BEAMBLEND_UL_cues, CueList,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
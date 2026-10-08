"""
@file       properties.py
@brief      List of Property Groups.
@author     Alyssa Greenwell

Detailed Description:
Property groups for Beamblend that function as custom data types.
"""
import bpy
from bpy.props import FloatProperty, FloatVectorProperty, StringProperty, CollectionProperty, IntProperty
from .fixture import update_pan, update_tilt, update_focus, update_gel, update_color, update_intensity, update_zoom
from .cuelist import update_cue_index, update_current_cue

class FixtureProperties(bpy.types.PropertyGroup):
    '''
    Properties for fixture objects. Not all properties are applicable to every
    type of fixture. Most properties map to functions (see fixture.py) that 
    control the variable aspects of each fixture via the UI FixtureProperties 
    and FixtureProgrammables panels (see ui.py).
    '''

    fixture_id: StringProperty(
        name="Fixture ID"
    )
    
    # PHYSICAL PROPERTIES
    
    pan: FloatProperty(
        name="Pan",
        min=-180,
        max=180,
        update=update_pan
    )

    tilt: FloatProperty(
        name="Tilt",
        min=-120,
        max=120,
        update=update_tilt
    )
    
    focus: FloatProperty(
        name="Focus",
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        default=0.0,
        update=update_focus
    )
    
    gel: FloatVectorProperty(
        name="Gel",
        subtype='COLOR',
        size=3,
        min=0.0, 
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_gel
    )
    
    # PROGRAMMABLE PROPERTIES
    
    intensity: FloatProperty(
        name="Intensity",
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        default=100.0,
        update=update_intensity
    )
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0, 
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_color
    )
    
    zoom: FloatProperty(
        name="Zoom",
        min=13.0,
        max=44.0,
        default=44.0,
        update=update_zoom
    )

    
class CueFixtureState(bpy.types.PropertyGroup):
    '''
    Stores the properties of a fixture that are recorded with a cue. Each
    fixture has a CueFixtureState in each cue.
    '''

    fixture_id: StringProperty(
        name="Fixture ID"
    )
    
    intensity: FloatProperty(
        name="Intensity",
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        default=100.0,
    )
    
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0, 
        max=1.0,
        default=(1.0, 1.0, 1.0),
    )
    
    zoom: FloatProperty(
        name="Zoom",
        min=13.0,
        max=44.0,
        default=44.0,
    )

class Cue(bpy.types.PropertyGroup):
    '''
    Stores the properties of a cue. Includes a collection of CueFixtureStates
    that holds the fixture state of each fixture in the scene.
    '''

    index: FloatProperty(
        name="Index",
        min=0.0,
        update=update_cue_index
    )    

    name: StringProperty(
        name="Name",
        default="New Cue"
    )

    transition_time: FloatProperty(
        name="Transition Time",
        default=1.0,
        min=0.0
    )
    
    fixture_states: CollectionProperty(
        type=CueFixtureState
    )

class ProgrammingProperties(bpy.types.PropertyGroup):
    '''
    Stores the cue list and the current selected cue.
    '''
    cues: CollectionProperty(
        type=Cue
    )

    current_cue: IntProperty(
        name="Current Cue",
        default=0,
        update=update_current_cue
    )


classes = (
    FixtureProperties, CueFixtureState, Cue, ProgrammingProperties
    )

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.beamblend = bpy.props.PointerProperty(
        type=FixtureProperties
    )

    bpy.types.Scene.beamblend_programming = bpy.props.PointerProperty(
        type=ProgrammingProperties
    )


def unregister():

    del bpy.types.Scene.beamblend_programming
    del bpy.types.Object.beamblend

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
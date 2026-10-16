"""
@file       fixture.py
@brief      Handles fixture property changes.
@author     Alyssa Greenwell

Detailed Description:
Contains all update functions called by properties under FixtureProperties (see
properties.py). Translates the UI facing metric into blender metric and updates
appropriate function.
"""
import bpy
from .helpers import get_object_root, get_part

# PHYSICAL PROPERTIES
GEL_COLORS = {
    'OPEN_WHITE': (1.0, 1.0, 1.0),
    'R33': (1.0, 0.35, 0.45), # No Color Pink
    'R32': (1.0, 0.255, 0.235), # Medium Salmon Pink
    'R23': (1.0, 0.4, 0.25), # Orange
    'R02': (1.0, 0.55, 0.2), # Bastard Amber
    'R08': (1.0, 0.875, 0.75), # Pale Gold
    'R60': (0.8, 0.85, 1.0), # No Color Blue
    'R70': (0.425, 0.9, 1.0), # Nile Blue
    'R80': (0.05, 0.1, 1.0), # Primary Blue
    'R54': (0.45, 0.25, 1.0), # Lavender
    'R48': (0.7, 0.01, 0.7), # Rose Purple
}

def update_pan(self, context):
    obj = context.object
    yoke = get_part("YOKE", obj)
    if yoke != None:
        yoke.rotation_euler.z = self.pan*-1*(3.14/180)

def update_tilt(self, context):
    obj = context.object
    body = get_part("BODY", obj)
    if body != None:
        body.rotation_euler.x = self.tilt*(3.14/180)

def update_focus(self, context):
    obj = context.object
    spot = get_part("SPOT", obj)
    if spot != None and spot.get("phys_focus", False):
        spot.data.spot_blend = 0.15 + (self.focus / 100.0) * (1.0 - 0.15)

def update_gel(self, context):
    obj = self.id_data
    spot = get_part("SPOT", obj)
    if spot is not None and spot.get("phys_gel", False):
        spot.data.color = GEL_COLORS.get(self.gel, (1.0, 1.0, 1.0))
        if spot.get("amber_shift", False):
            apply_amber_shift(obj)

def apply_amber_shift(fixture):
    '''
    Applies an approximate amber shift to light depending on intensity and gel 
    color.
    
    Args:
        fixture: fixture to apply amber shift to.
    '''
    spot = get_part("SPOT", fixture)

    if spot is None:
        return

    gel = fixture.beamblend.gel
    base_color = GEL_COLORS.get(gel, (1.0, 1.0, 1.0))

    intensity = fixture.beamblend.intensity / 100
    strength = 0.55
    exponent = 1.5
    
    amber = strength * (1.0 - intensity) ** exponent
    r, g, b = base_color

    spot.data.color = (r, g * (1.0 - 0.55 * amber), b * (1.0 - 1.5 * amber))

# PROGRAMMABLE PROPERTIES

def update_color(self, context):
    obj = self.id_data
    spot = get_part("SPOT", obj)
    if spot != None and spot.get("dmx_color", False):
        spot.data.color = self.color

def update_intensity(self, context):
    obj = self.id_data
    spot = get_part("SPOT", obj)
    if spot != None:
        spot.data.energy = (self.intensity / 100.0) * spot.get("max_intensity")
        if spot.get("amber_shift", False):
            apply_amber_shift(obj)

def update_zoom(self, context):
    obj = self.id_data
    spot = get_part("SPOT", obj)
    if spot != None and spot.get("dmx_zoom", False):
        spot.data.spot_size = self.zoom*(3.14/180)
            

    
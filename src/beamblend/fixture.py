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
    if spot != None:
        spot.data.spot_blend = 0.15 + (self.focus / 100.0) * (1.0 - 0.15)
 
def update_gel(self, context):
    obj = context.object
    spot = get_part("SPOT", obj)
    if spot != None:
        spot.data.color = self.gel       

# PROGRAMMABLE PROPERTIES

def update_color(self, context):
    obj = self.id_data
    if get_object_root(obj).get("fix_type") == "COLORSOURCE":
        spot = get_part("SPOT", obj)
        if spot != None:
            spot.data.color = self.color

def update_intensity(self, context):
    obj = self.id_data
    spot = get_part("SPOT", obj)
    if spot != None:
        spot.data.energy = (self.intensity / 100.0) * spot.get("max_intensity")

def update_zoom(self, context):
    obj = self.id_data
    if get_object_root(obj).get("fix_type") == "COLORSOURCE":
        spot = get_part("SPOT", obj)
        if spot != None:
            spot.data.spot_size = self.zoom*(3.14/180)
            

    
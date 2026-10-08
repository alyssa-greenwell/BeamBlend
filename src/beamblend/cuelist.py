"""
@file       cuelist.py
@brief      Handles updates called by cue properties.
@author     Alyssa Greenwell

Detailed Description:
Contains functions that are called by properties that pertain to cues or the
cue list (see properties.py).
"""
from .helpers import find_fixture_by_id

def update_cue_index(self, context):
    '''
    Orders the cue list from lowest cue index to highest cue index. Called when 
    an index is changed.
    '''
    programming = context.scene.beamblend_programming
    cues = programming.cues
    
    for target_index in range(len(cues)):

        lowest_index = target_index
        lowest_value = cues[target_index].index

        for i in range(target_index + 1, len(cues)):

            if cues[i].index < lowest_value:
                lowest_index = i
                lowest_value = cues[i].index

        if lowest_index != target_index:
            cues.move(lowest_index, target_index)

def update_current_cue(self, context):
    '''
    Changes the scene when a new cue is selected to display the state of the
    lights stored in that cue.
    '''
    programming = context.scene.beamblend_programming

    if len(programming.cues) == 0:
        return

    cue = programming.cues[self.current_cue]

    for state in cue.fixture_states:
        obj = find_fixture_by_id(context.scene, state.fixture_id)
        obj.beamblend.intensity = state.intensity
        obj.beamblend.color = state.color
        obj.beamblend.zoom = state.zoom

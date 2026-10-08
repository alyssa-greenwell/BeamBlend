'''
@file       operators.py
@brief      Handles operations controlled by UI buttons.
@author     Alyssa Greenwell

Detailed Description:
This file contains the full list of bpy.types.Operator classes used for 
Beamblend. Each operator is associated with a button on the UI.
'''
import bpy
import os
from bpy.props import StringProperty, FloatProperty
from math import floor
from .helpers import delete_object_recursive, find_fixture_by_id, get_pipe_endpoints, get_object_root, get_part, initialize_fixture

class DeleteObject(bpy.types.Operator):
    '''
    Deletes all beamblend objects that are currently selected. This includes 
    any parents and children of the selected body.
    '''
    bl_idname = "beamblend.delete_object"
    bl_label = "Delete Object"
    bl_description = "Deletes Selected Objects"
    
    def execute(self, context):
        selected = context.selected_objects
        for obj in selected:
            root = get_object_root(obj)
            delete_object_recursive(root)
        return {'FINISHED'}

class ImportModel(bpy.types.Operator):
    '''
    Imports beamblend object by name and spawns it in the scene at the origin.
    
    Args:
        model_name: file name of the object to spawn.
    
    Raises:
        Error if no file exists in the Builds folder with the given model name.
        Error if the root of the object does not have the "obj_type" custom 
        property.
    '''
    bl_idname = "beamblend.import_model"
    bl_label = "Import Model"
    bl_description = "Spawns object."

    model_name: StringProperty(name="Model Name")

    def execute(self, context):
        # Open file
        addon_dir = os.path.dirname(__file__)

        blend_file = os.path.join(
            addon_dir,
            "Builds",
            f"{self.model_name}.blend"
        )

        print("Blend file:", blend_file)
        print("Exists:", os.path.exists(blend_file))

        if not os.path.exists(blend_file):
            self.report({'ERROR'}, f"File not found: {blend_file}")
            return {'CANCELLED'}
        
        # Load all objects
        with bpy.data.libraries.load(blend_file) as (data_from, data_to):
            data_to.objects = data_from.objects
      
        for obj in data_to.objects:
            if obj:
                context.collection.objects.link(obj)
        
        # Make root the active selected object
        for obj in data_to.objects:
            if obj.get("obj_type") is not None:
                root = obj
                break
        
        if root is None:
            raise RuntimeError("Could not find root.")
            return {'CANCELLED'}
        
        bpy.ops.object.select_all(action='DESELECT')
        root.select_set(True)
        bpy.context.view_layer.objects.active = root
        
        #If object is fixture, then initialize
        if root.get("obj_type") == "FIXTURE":
            initialize_fixture(root)

        return {'FINISHED'}

class SetIntensity(bpy.types.Operator):
    '''
    Sets the intensity of the selected fixture to a given percent.
    
    Args:
        intensity: float between 0.0 and 1.0 inclusive that determines the 
        percent intensity to set the light to.
    
    Raises:
        Error if no fixture is the active selected object.
    '''
    bl_idname = "beamblend.set_intensity"
    bl_label = "Set Intensity"
    
    intensity: FloatProperty()
    
    def execute(self, context):
        obj = context.object
        root = get_object_root(obj)
        if root is None or root.get("obj_type") != "FIXTURE":
            self.report({'ERROR'}, "Fixture is not selected.")
            return {'CANCELLED'}
        root.beamblend.intensity = self.intensity
        return {'FINISHED'}

class SnapToPipe(bpy.types.Operator):
    '''
    Given a selected fixture and pipe (it does not matter which is the active
    selected object), moves the fixture from its original position to the 
    closest point on the pipe.
    
    Raises:
        Error if more or less than two objects are selected.
        Error if the two objects selected are not one fixture (body and yoke 
        both acceptable) and one pipe.
    '''
    bl_idname = "beamblend.snap_to_pipe"
    bl_label = "Snap to Pipe"
    bl_description = "Snaps selected fixture to selected pipe"
        
    def execute(self, context):
        # Get pipe and fixture
        selected = context.selected_objects
        
        if len(selected) != 2:
            self.report({'ERROR'}, "Incorrect amount of objects selected.")
            return {'CANCELLED'}
        
        obj1 = get_object_root(selected[0])
        obj2 = get_object_root(selected[1])
        
        if obj1 is None or obj2 is None:
            self.report({'ERROR'}, "Could not determine object type.")
            return {'CANCELLED'}
        
        if obj1.get("obj_type") == "FIXTURE" and obj2.get("obj_type") == "ELECTRIC":
            fixture = obj1
            pipe = obj2
        elif obj1.get("obj_type") == "ELECTRIC" and obj2.get("obj_type") == "FIXTURE":
            fixture = obj2
            pipe = obj1
        else:
            self.report({'ERROR'}, "Incorrect object types selected.")
            return {'CANCELLED'}
        
        # Calculate shortest distance to pipe
        start, end = get_pipe_endpoints(pipe)
        
        pipe_vector = end - start
        
        fixture_vector = fixture.matrix_world.translation - start
        
        t = fixture_vector.dot(pipe_vector)
        t /= pipe_vector.dot(pipe_vector)
        
        t = max(0.0, min(1.0, t))
        
        closest_point = start + t * pipe_vector
        
        # Move fixture to closest location on pipe
        fixture.matrix_world.translation = closest_point
        
        # Set selected object to just fixture
        bpy.ops.object.select_all(action='DESELECT')
        fixture.select_set(True)
        bpy.context.view_layer.objects.active = fixture
        
        return {'FINISHED'}

class ToggleExtras(bpy.types.Operator):
    '''
    Toggles Extras under Objects in the Viewport Overlay. Mainly for the
    purposes of toggling on and off the spot outlines.
    '''
    bl_idname = "beamblend.toggle_extras"
    bl_label = "Toggle Spot Outlines"
    bl_description = "Toggles outlines for spots"
    
    def execute(self, context):
        if context.space_data.overlay.show_extras:
            context.space_data.overlay.show_extras = False
        else:
            context.space_data.overlay.show_extras = True
        return {'FINISHED'}


# CUE OPERATORS

class DeleteCue(bpy.types.Operator):
    '''
    Deletes selected cue from cuelist.
    '''
    bl_idname = "beamblend.delete_cue"
    bl_label = "Delete Cue"
    bl_description = "Deletes selected cue."

    def execute(self, context):

        programming = context.scene.beamblend_programming
        toDelete = programming.current_cue

        if 0 <= toDelete < len(programming.cues):

            programming.cues.remove(toDelete)

            if len(programming.cues) == 0:
                programming.current_cue = 0
            
            elif toDelete >= len(programming.cues):
                programming.current_cue = len(programming.cues) - 1
            
            else:
                programming.current_cue = toDelete

        return {'FINISHED'}

class Go(bpy.types.Operator):
    '''
    Moves to the next cue in the cuelist, animating the transition between the
    two cues using the duration time of the next cue.
    '''
    bl_idname = "beamblend.go"
    bl_label = "Go"
    bl_description = "Plays transition to next cue."
    
    def execute(self, context):
        scene = context.scene
        programming = scene.beamblend_programming
        cues = programming.cues

        # Handle if animation is already playing
        if scene.get("beamblend_playing", False):
            end_frame = scene.get("beamblend_end_frame")
            if end_frame is not None:
                scene.frame_set(end_frame)
            return {'FINISHED'}
        
        current_index = programming.current_cue
        next_index = current_index + 1

        if next_index >= len(cues):
            return {'FINISHED'}

        current_cue = cues[current_index]
        next_cue = cues[next_index]

        start_frame = 0

        # Calculate number of frames for duration
        fps = scene.render.fps
        transition_frames = int(next_cue.transition_time * fps)

        end_frame = start_frame + transition_frames

        # Set start and end keyframes for each light
        for state in current_cue.fixture_states:
            fixture = find_fixture_by_id(scene, state.fixture_id)
            if fixture is None:
                continue
            
            light = get_part("SPOT", fixture)
            light.data.keyframe_insert(data_path="energy", frame=start_frame)
            light.data.keyframe_insert(data_path="color", frame=start_frame)
            light.data.keyframe_insert(data_path="spot_size", frame=start_frame)

        programming.current_cue = next_index

        for state in next_cue.fixture_states:
            fixture = find_fixture_by_id(scene, state.fixture_id)
            if fixture is None:
                continue
            
            light = get_part("SPOT", fixture)
            light.data.keyframe_insert(data_path="energy", frame=end_frame)
            light.data.keyframe_insert(data_path="color", frame=end_frame)
            light.data.keyframe_insert(data_path="spot_size", frame=end_frame)


        # Set animation parameters
        scene["beamblend_end_frame"] = end_frame
        scene["beamblend_start_frame"] = start_frame
        scene["beamblend_playing"] = True
        
        scene.frame_set(start_frame)

        if scene.frame_end <= end_frame:
            scene.frame_end = end_frame + 5

        bpy.ops.screen.animation_play(sync=True)
        
        return {'FINISHED'}

def beamblend_stop_at_end(scene):
    '''
    Helper function to Go: Stops animation at correct keyframe and cleans up
    keyframes after animation finishes.
    '''
    if not scene.get("beamblend_playing", False):
        return

    end_frame = scene.get("beamblend_end_frame", None)

    if end_frame is None:
        return

    if scene.frame_current >= end_frame:

        if bpy.context.screen and bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        scene.frame_set(end_frame)

        start_frame = scene.get("beamblend_start_frame", 0)

        for fixture in scene.objects:
            if fixture.get("obj_type") != "FIXTURE":
                continue

            light = get_part("SPOT", fixture)
            if light and light.data.animation_data and light.data.animation_data.action:
                light.data.keyframe_delete(data_path="energy", frame=start_frame)
                light.data.keyframe_delete(data_path="energy", frame=end_frame)
                light.data.keyframe_delete(data_path="color", frame=start_frame)
                light.data.keyframe_delete(data_path="color", frame=end_frame)
                light.data.keyframe_delete(data_path="spot_size", frame=start_frame)
                light.data.keyframe_delete(data_path="spot_size", frame=end_frame)

        scene["beamblend_playing"] = False

class RecordCue(bpy.types.Operator):
    '''
    Records a new cue. Sets name to "New Cue", transition time to 2.0 seconds,
    and index to the next whole number after the current last cue in the list,
    effectively placing the new cue at the bottom of the cue list. The fixture
    states are recorded as what they currently are in the scene.
    '''
    bl_idname = "beamblend.record_cue"
    bl_label = "Record Cue"
    bl_description = "Records new cue with current look and adds to bottom of cue list."

    def execute(self, context):
        programming = context.scene.beamblend_programming

        cue = programming.cues.add()

        cue.index = floor(programming.cues[len(programming.cues)-2].index + 1)
        cue.name = "New Cue"
        cue.transition_time = 2.0
        
        for obj in context.scene.objects:
            if obj.get("obj_type") == "FIXTURE":    
                state = cue.fixture_states.add()            
                state.fixture_id = obj.beamblend.fixture_id
                state.intensity = obj.beamblend.intensity
                state.color = obj.beamblend.color
                state.zoom = obj.beamblend.zoom

        programming.current_cue = len(programming.cues) - 1

        return {'FINISHED'}

class UpdateCue(bpy.types.Operator):
    '''
    Updates selected cue fixture states to reflect the current fixture states
    in the scene.
    '''
    bl_idname = "beamblend.update_cue"
    bl_label = "Update Cue"
    bl_description = "Updates selected cue to current look."
    
    def execute(self, context):
        programming = context.scene.beamblend_programming
        cue = programming.cues[programming.current_cue]
        
        for state in cue.fixture_states:
            obj = find_fixture_by_id(context.scene, state.fixture_id)
            state.intensity = obj.beamblend.intensity
            state.color = obj.beamblend.color
            state.zoom = obj.beamblend.zoom
        
        return {'FINISHED'}

classes = (
    DeleteObject,ImportModel,SetIntensity,SnapToPipe,ToggleExtras,DeleteCue,Go,RecordCue,UpdateCue
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    if beamblend_stop_at_end not in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.append(beamblend_stop_at_end)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if beamblend_stop_at_end in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(beamblend_stop_at_end)
    bpy.context.preferences.edit.keyframe_new_interpolation_type = 'BEZIER'

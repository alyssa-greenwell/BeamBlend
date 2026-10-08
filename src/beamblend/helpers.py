"""
@file       helpers.py
@brief      Helper functions called by multiple files.
@author     Alyssa Greenwell

Detailed Description:
Assortment of helper functions that are called by any of the other Beamblend
files.
"""
import bpy
from mathutils import Vector
import uuid

def delete_object_recursive(obj):
    """
    Recursively deletes object and all children and nested children.
    
    Args:
        obj: root object to delete.
    """
    for child in obj.children:
        delete_object_recursive(child)
    bpy.data.objects.remove(obj, do_unlink=True)

def find_fixture_by_id(scene, fixture_id):
    '''
    Searches for fixture object in scene with given uuid.
    
    Args:
        scene: scene to search in.
        fixture_id: uuid of fixture you are trying to find.
    
    Returns:
        Object with matching ID if found; None otherwise.
    '''
    for obj in scene.objects:
        if obj.get("obj_type") == "FIXTURE" and obj.beamblend.fixture_id == fixture_id:
            return obj

    return None

def get_object_root(obj):
    """
    Returns the fixture root for any object inside a fixture hierarchy.
    
    Args:
        obj: fixture part
    
    Returns:
        Fixture root if found; None otherwise.
    """
    while obj is not None:
        if obj.get("obj_type") is not None:
            return obj
        obj = obj.parent

    return None

def get_part(part, fixture):
    """
    Returns object in the fixture that matches the part.
    
    Args:
        part: string defining the part to search for. Valid strings are "YOKE",
        "BODY", and "SPOT".
        fixture: any part of the fixture object in which to find a part.
        
    Returns:
        fixture part if found; None otherwise.
        
    Raises:
        RuntimeError: if specified part could not be found on fixture.
        RuntimeError: if part does not match any of the valid strings.
        
    """
    while fixture is not None:
        if fixture.get("obj_type") == "FIXTURE":
            root = fixture
            break
        fixture = fixture.parent
    
    if root is None:
        raise RuntimeError("Could not find root. Please select a fixture.")
        return None
    
    if part == "YOKE":
        return root
        
    for obj in root.children:
        if obj.get("part_type") == "BODY":
            body = obj
            break
    
    if body is None:
        raise RuntimeError("Error: Body not found.")
        return None
    
    if part == "BODY":
        return body
    
    if part == "SPOT":
        for obj in body.children:
            if obj.get("part_type") == "SPOT":
                return obj
        raise RuntimeError("Error: Yoke not found.")
        return None
    
    raise RuntimeError("Invalid Part.")
    return None
    

def get_pipe_endpoints(pipe):
    """
    Returns the world-space endpoints of a pipe.
    
    Args:
        pipe: pipe object.
    
    Returns:
        The world space points that define the start and end of a pipe.
    
    Raises:
        RuntimeError: if pipe is not labelled as a pipe object (aka "ELECTRIC").
    """
    if pipe.get("obj_type") != "ELECTRIC":
        raise RuntimeError("Error: No valid electric selected.")
        return None
    
    center = pipe.matrix_world.translation
    
    direction = pipe.matrix_world.to_3x3() @ Vector((1, 0, 0))
    direction.normalize()
    
    half = pipe.dimensions.x / 2
    
    start = center - direction * half
    end = center + direction * half

    return start, end

def initialize_fixture(yoke):
    """
    Initializes fixture properties.
    
    Args:
        yoke: The yoke/root of the fixture object.
    """
    props = yoke.beamblend
    props.fixture_id = "bb_" + str(uuid.uuid4())
    props.pan = 0.0
    props.tilt = 0.0

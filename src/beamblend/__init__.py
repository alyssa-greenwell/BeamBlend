import bpy
import importlib

# Add-on Metadata    
bl_info = {
    "name": "BeamBlend",
    "blender": (2, 80, 0),
    "category": "Object",
}

# Load / Relaod Submodules
if "operators" in locals():
    importlib.reload(properties)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from . import properties
    from . import operators
    from . import ui

def register():
    properties.register()
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()
    properties.unregister()

if __name__ == "__main__":
    register()
    
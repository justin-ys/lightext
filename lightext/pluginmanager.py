import json
import importlib
import inspect

from lightext.widgets import bases
from lightext.widgets.popups import Popup

try:
    with open("config/plugins.json") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

def get_editor():
    try:
        path = config["editor"]
        editor = importlib.import_module(path).Editor()
        if (not isinstance(editor, bases.LightextEditor)):
            Popup("Plugin Error", "Editor %s is not derived from LightextEditor" % path, "Error").exec()
            raise AttributeError
    except (KeyError, ModuleNotFoundError, AttributeError):
        editor = importlib.import_module("lightext.default.editor").Editor()
    return editor

def get_editor_paint_addons():
    paths = []
    try:
        paths = config["painters"]
    except KeyError:
        pass
    actions = []
    for path in paths:
        try:
            action = importlib.import_module(path).paint
            # Make sure painter function only takes one argument (editor class)
            if (len(inspect.getargspec(action)[0]) != 1):
                Popup("Plugin Error", "Painter Plugin %s must take exactly one argument" % path, "Error").exec()
            else:
                actions.append(action)
        except (ModuleNotFoundError, AttributeError):
            Popup("Plugin Error", "%s is not a valid plugin path" % path, "Error").exec()
    return actions
import json
import importlib
import importlib.util
import inspect
import os

from lightext.widgets import bases
from lightext.widgets.popups import Popup
from lightext.config import get_plugin_folder

try:
    with open("config/plugins.json") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

def _get_plugin_module(path):
    if path.startswith("lightext"):
        return importlib.import_module(path)
    location = get_plugin_folder() + "/" + path.replace(".","/") + ".py"
    if not os.path.isfile(location):
        raise ModuleNotFoundError
    spec = importlib.util.spec_from_file_location(path, location)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def get_editor():
    try:
        path = config["editor"]
        editor = _get_plugin_module(path).Editor()
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
            action = _get_plugin_module(path).paint
            # Make sure painter function only takes one argument (editor class)
            if (len(inspect.signature(action).parameters) != 1):
                Popup("Plugin Error", "Painter Plugin %s must take exactly one argument" % path, "Error").exec()
            else:
                actions.append(action)
        except (ModuleNotFoundError, AttributeError):
            Popup("Plugin Error", "%s is not a valid plugin path" % path, "Error").exec()
    return actions
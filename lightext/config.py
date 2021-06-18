import os
import sys
from lightext.widgets.popups import Popup
import platform

_home = os.path.expanduser("~")
if platform.system() == "Linux":
    if not os.path.isdir(_home + "/.local/lightext"):
        os.mkdir(_home + "/.local/lightext")
elif platform.system() == "Windows":
    if not os.path.isdir(_home + "/AppData/Local/lightext"):
        os.mkdir(_home + "/AppData/Local/lightext")

class ResourceBank():
    def __init__(self):
        with open("resources/current_pack.txt", "r") as f:
            data = f.read()
            self.pack = data.split("\n")[0]
        if not os.path.isdir("resources/%s" % self.pack):
            Popup("Resource Error", "Pack '%s' not found, reverting to default" % self.pack, "error").exec()
            if os.path.isdir("resources/default"):
                self.pack = "default"
            else:
                sys.exit(Popup("Resource Error", "Default resource pack not found, exiting", "critical").exec())
        self.__load__()

    def __load__(self):
        if not os.path.isfile("resources/" + self.pack + "/index.txt"):
            if self.pack == "default":
                sys.exit(Popup("Resource Error", "Default resource pack invalid (no index file), exiting", "critical").exec())
            Popup("Resource Error", "Resource pack invalid (No index file), reverting to default", "error").exec()
            self.pack = "default"
            self.__load__()
            return

        with open("resources/" + self.pack + "/index.txt", "r") as f:
            data = f.read()

        items = data.split("\n")
        self.resources = {}
        for item in items:
            name, location = item.split(" ")
            if not os.path.isfile("resources/" + self.pack + "/" + location):
                print("Resource %s not found" % name)
            self.resources[name] = location

    def load_resource(self, resource):
        try:
            location = "resources/" + self.pack + "/" + self.resources[resource]
        except IndexError:
            return "resources/error.png"

        if os.path.isfile(location):
            return location
        else:
            return "resources/error.png"

def get_plugin_folder():
    if platform.system() == "Linux":
        path = os.path.expanduser("~") + "/.local/lightext/plugins"
    elif platform.system() == "Windows":
        path = os.path.expanduser("~") + "/AppData/Local/lightext/plugins"

    if not os.path.isdir(path):
        os.mkdir(path)
    return path

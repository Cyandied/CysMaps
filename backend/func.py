from os.path import join
from os import listdir
import zipfile
from backend.classes import MapSettings, Marker
import json

def make_new_map(file:zipfile.ZipFile,name,session):
    test = file.testzip()
    accept_zoomlvls = [
        "map_tiles/0/",
        "map_tiles/1/",
        "map_tiles/2/",
        "map_tiles/3/",
        "map_tiles/4/",
        "map_tiles/5/",
    ]
    accept_folders = []
    for path in file.namelist():
        for zoomlvl in accept_zoomlvls:
            if zoomlvl in path:
                accept_folders.append(path)
    if accept_folders:
        if not test:
            file.extractall(
                path=join("static",
                    "userfolders",
                    session["user"]["id"],
                    name,
                ),
                members=accept_folders,
            )
            update_map_settings(session,name)
            return f"New map {name} has been uploaded sucessfully!",True
        else:
            return f"Found a bad file, please check that {test} is good and try again",False
    else:
        return "Seems something went wrong when trying to validate your zip file, ensure that your tiles are in a parent folder named 'map_tiles'! If you are using my tile-cutter, simply zip the 'map_tiles' folder after cutting!",False
    
def update_map_settings(session, map_name, start_pos=None, start_zoom=None, title=None, bg_color=None):
    map_settings = MapSettings([0,0],0,map_name,"#FFFFFF")
    if "map_settings.json" in listdir(join("static","userfolders",session["user"]["id"],map_name)):
        with open(join("static","userfolders",session["user"]["id"],map_name,"map_settings.json"),"r") as f:
            map_dict = json.load(f)
        map_settings = MapSettings(exsisting_dict=map_dict)
        map_settings.start_pos = start_pos
        map_settings.start_zoom = start_zoom
        map_settings.title = title
        map_settings.bg_color = bg_color

    with open(join("static","userfolders",session["user"]["id"],map_name,"map_settings.json"),"w") as f:
        f.write(json.dumps(map_settings.__dict__))

def update_map_marker(session, map_name,name:str, desc:str, icon:str,attributes:dict,pos:list[float],id = None):
    map_markers = {}
    print("making marker!")
    if "map_markers.json" in listdir(join("static","userfolders",session["user"]["id"],map_name)):
        with open(join("static","userfolders",session["user"]["id"],map_name,"map_markers.json"),"r") as f:
            map_dict = json.load(f)
        map_markers = map_dict
    if id:
        map_markers[id] = Marker(name, desc,icon,attributes,pos,id=id).__dict__
    else:
        marker = Marker(name, desc,icon,attributes,pos).__dict__
        map_markers[marker["id"]] = marker

    with open(join("static","userfolders",session["user"]["id"],map_name,"map_markers.json"),"w") as f:
        f.write(json.dumps(map_markers))

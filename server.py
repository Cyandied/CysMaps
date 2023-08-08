import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
import zipfile
from zipfile import ZipFile
from os import listdir, remove, mkdir, makedirs
from os.path import isfile, join
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from pocketbase import PocketBase
import json

from backend.func import make_new_map, update_map_settings, update_map_marker

from backend.classes import *

# Start server:
# flask --app server run --debug

client = PocketBase("http://127.0.0.1:8090")
UPLOAD_FOLDER = "/temp"
ALLOWED_EXTENSIONS = {"zip"}
app = Flask(
    __name__, static_url_path="", static_folder="static", template_folder="html"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.secret_key = "i/2r:='d8$V{[:gHm5x?#YBB-D-6)N"
adminPass = "7ABC44E3647B1ACE58E5065FD0E8D82BF353418556AF1A80F983D44808640E8F"

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    users = client.collection("users").get_full_list()

    for user in users:
        packs = []
        games = {}

        all_user_packs = client.collection("user_packs").get_full_list()
        all_user_games = client.collection("user_games").get_full_list()

        for pack in all_user_packs:
            if pack.user_id == user.id:
                packs.append(client.collection("packs").get_one(pack.pack_id).name)

        if user.role in ["admin", "dm"]:
            for game in all_user_games:
                if game.user_id == user.id:
                    user_game = client.collection("games").get_one(game.game_id)
                    games[user_game.name] = game.id

        email = None
        if user.email_visibility:
            email = user["email"]

        if user_id == user.id:
            return User(
                user.username,
                email,
                user.role,
                games,
                user.id,
                packs,
                user.secret,
                user.allowed_maps,
                user.nr_maps,
                user.max_maps,
            )


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        if session["user"]:
            flash(
                f'Sorry, you are already logged in as {session["user"]["name"]}. Log out first if you wish to log into a different account.'
            )
            return redirect(url_for("home"))
    if request.method == "POST":
        try:
            response = client.collection("users").auth_with_password(
                request.form["user"], request.form["pass"]
            )
        except:
            response = "code"
            flash("Sorry, check if the username and password is correct.")

        verified_user = False
        if "code" != response:
            user = response.record
            packs = []
            games = {}

            all_user_packs = client.collection("user_packs").get_full_list()
            all_user_games = client.collection("user_games").get_full_list()

            for pack in all_user_packs:
                if pack.user_id == user.id:
                    packs.append(client.collection("packs").get_one(pack.pack_id).name)

            if user.role in ["admin", "dm"]:
                for game in all_user_games:
                    if game.user_id == user.id:
                        user_game = client.collection("games").get_one(game.game_id)
                        games[user_game.name] = game.id

            email = None
            if user.email_visibility:
                email = user["email"]

            verified_user = User(
                user.username,
                email,
                user.role,
                games,
                user.id,
                packs,
                user.secret,
                user.allowed_maps,
                user.nr_maps,
                user.max_maps,
            )

        if verified_user:
            session["user"] = verified_user.__dict__
            session["hw"] = None
            login_user(verified_user)
            flash(f'sucessfully logged in! Welcome {session["user"]["name"]}')
            return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    with open(join("static", "ToS.txt"), "r") as f:
        ToS = f.read()
    if "user" in session:
        if session["user"]:
            flash(
                f'Sorry, you are already logged in as {session["user"]["name"]}. Log out first if you wish to log into a different account.'
            )
            return redirect(url_for("home"))

    data = {"username": "", "email": ""}

    if request.method == "POST":
        form = request.form
        if "button" in form:
            if form["button"] == "sign-up":
                data = {
                    "username": form["username"],
                    "email": form["email"],
                    "emailVisibility": False,
                    "password": form["password"],
                    "passwordConfirm": form["password2"],
                    "role": form["role"],
                    "secret": False,
                }

                try:
                    record = client.collection("users").create(data)
                    flash("User sucessfully created! You can now log in!")
                    return redirect(url_for("login"))
                except Exception as e:
                    message = []
                    users = client.collection("users").get_full_list()
                    names = []
                    for user in users:
                        names.append(user.username)
                    if form["username"] in names:
                        message.append("username taken")
                    email = form["email"].split("@")
                    if form["password"] != form["password2"]:
                        message.append("your passwords do not match up")
                    if len(form["password"]) < 8:
                        message.append("password too short")
                    if len(email) == 2:
                        email = email[1].split(".")
                        if len(email) != 2:
                            message.append("email does not have a valid format")
                    else:
                        message.append("email does not have a valid format")
                    flash(
                        "User not created, follwing errors occured: "
                        + " :: ".join(message)
                    )

    return render_template(
        "signup.html", ToS=ToS, username=data["username"], email=data["email"]
    )


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/mapmanager", methods=["GET", "POST"])
@login_required
def mapman():
    avaible_maps = ["genericMap"]
    if session["user"]["allowed_maps"]:
        if session["user"]["id"] in listdir("static/userfolders"):
            user_maps = listdir(join("static","userfolders", session["user"]["id"]))
            for user_map in user_maps:
                avaible_maps.append(user_map)

    else:
        print("no")

    if request.method == "POST":
        form = request.form
        if "direct-to-map" in form:
            return redirect(url_for("display_map", selected_map=form["direct-to-map"]))
        if "map_zip" in request.files:
            file = request.files["map_zip"]
            if zipfile.is_zipfile(file):
                map_name = file.filename.split(".")[0]
                if session["user"]["id"] not in listdir("static/userfolders"):
                    mkdir(join("static","userfolders", session["user"]["id"]))
                makedirs(join("static","userfolders", session["user"]["id"], map_name))
                file = ZipFile(file)
                msg_bool = make_new_map(file,map_name,session)
                if msg_bool[1]:
                    avaible_maps.append(map_name)
                    flash(msg_bool[0])
                else:
                    flash(msg_bool[0])
            else:
                flash(
                    f"Sorry, the file you uploaded is not an accepted filetype. Accepted filetypes are: {ALLOWED_EXTENSIONS}"
                )

    return render_template("mapman.html", maps=avaible_maps)


@app.route(f"/map/<selected_map>", methods=["GET", "POST"])
@login_required
def display_map(selected_map):
 
    if request.method == "POST":
        form = request.form
        update_map_settings(session, selected_map,form["start_pos"],form["start_zoom"],form["title"],form["bg_color"])
        if "edit-marker" in form:
            target = form["edit-marker"]
            attribs = {}
            if f'{target}.attribute.key' in form:
                keys = form.getlist(f'{target}.attribute.key')
                vals = form.getlist(f'{target}.attribute.val')
                for i, key in enumerate(keys):
                    if key:
                        attribs[key] = vals[i]
            update_map_marker(session, selected_map,form[f'{target}.name'],form[f'{target}.desc'],form[f'{target}.icon'],attribs,[form[f'{target}.lat'],form[f'{target}.lang']],target)
        if "make-marker" in form:
            update_map_marker(session,selected_map,"New Marker","","1.png",{},[form["curr.lat"],form["curr.lang"]])

    map_markers = {}
    path = join("userfolders", session["user"]["id"], selected_map, "map_tiles")
    zoomlvls = listdir(join("static",path))
    icons = listdir(join("static","images","icons"))
    with open(join("static","userfolders",session["user"]["id"],selected_map,"map_settings.json"),"r") as f:
        map_settings = json.load(f)
    if "map_markers.json" in listdir(join("static","userfolders",session["user"]["id"],selected_map)):
        with open(join("static","userfolders",session["user"]["id"],selected_map,"map_markers.json"),"r") as f:
            map_markers = json.load(f)


    return render_template("display_map.html", map=selected_map, maxzoom=zoomlvls[-1],minzoom=zoomlvls[0],path=path, map_settings=map_settings, map_markers=map_markers, icons= icons)

@app.route(f"/map/<selected_map>/map_markers", methods=["GET", "POST"])
@login_required
def map_markers(selected_map):
    if "map_markers.json" in listdir(join("static","userfolders",session["user"]["id"],selected_map)):
        with open(join("static","userfolders",session["user"]["id"],selected_map,"map_markers.json"),"r") as f:
            map_markers = json.load(f)
    return map_markers

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash(f'You are now logged out! Hope to see you soon, {session["user"]["name"]}')
    session["user"] = None
    session["hw"] = None
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run("127.0.0.1", 5030, debug=True)

import re
import secrets
import sqlite3

from flask import Flask, abort, flash, make_response, redirect, render_template, request, session
import markupsafe

import config
import db
import items
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.template_filter()
def format_date(date_str):
    if not date_str or len(date_str) != 10:
        return date_str
    parts = date_str.split('-')
    return f"{parts[2]}.{parts[1]}.{parts[0]}"

@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_items = users.get_items(user_id)
    return render_template("show_user.html", user=user, items=user_items)

@app.route("/find_item")
def find_item():
    query = request.args.get("query")
    if query:
        results = items.find_items(query)
    else:
        query = ""
        results = []
    return render_template("find_item.html", query=query, results=results)

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = items.get_item(item_id)
    if not item:
        abort(404)
    location = items.get_location(item_id)
    visits = items.get_visits(item_id)
    images = items.get_images(item_id)
    return render_template("show_item.html", item=item, location=location,
                           visits=visits, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = items.get_image(image_id)
    if not image:
        abort(404)
    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/new_item")
def new_item():
    require_login()
    classes = items.get_all_classes()
    return render_template("new_item.html", classes=classes)

@app.route("/create_item", methods=["POST"])
def create_item():
    require_login()
    check_csrf()

    title = request.form["title"]
    description = request.form["description"]
    coordinates = request.form["coordinates"]
    created_date = request.form["created_date"]
    location = request.form.get("location")

    if not title or len(title) > 50 or not description or len(description) > 1000 or not coordinates:
        abort(403)
        
    if not location or ":" not in location:
        abort(403)
        
    if not re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", created_date):
        abort(403)

    loc_title, loc_value = location.split(":")
    user_id = session["user_id"]

    item_id = items.add_item(title, description, coordinates, created_date, user_id, loc_title, loc_value)
    return redirect("/item/" + str(item_id))

@app.route("/create_visit", methods=["POST"])
def create_visit():
    require_login()
    check_csrf()

    visit_date = request.form["visit_date"]
    if not re.search("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", visit_date):
        abort(403)
    
    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item:
        abort(403)
        
    cache_creation_date = items.get_cache_creation_date(item_id)
    if visit_date < cache_creation_date:
        flash("VIRHE: Havaintopäivämäärä ei voi olla ennen kätkön luontipäivämäärää.")
        return redirect("/item/" + str(item_id))

    user_id = session["user_id"]
    items.add_visit(item_id, user_id, visit_date)
    return redirect("/item/" + str(item_id))

@app.route("/edit_item/<int:item_id>")
def edit_item(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    all_classes = items.get_all_classes()
    location = items.get_location(item_id)

    return render_template("edit_item.html", item=item, location=location, all_classes=all_classes)

@app.route("/images/<int:item_id>")
def edit_images(item_id):
    require_login()
    item = items.get_item(item_id)
    if not item:
        abort(404)
    if item["user_id"] != session["user_id"]:
        abort(403)

    images = items.get_images(item_id)
    return render_template("images.html", item=item, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item or item["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".png"):
        flash("VIRHE: Vain .png-tiedostot ovat sallittuja")
        return redirect("/images/" + str(item_id))

    image = file.read()
    if len(image) > 100 * 1024:
        flash("VIRHE: Kuva on liian suuri")
        return redirect("/images/" + str(item_id))

    items.add_image(item_id, image)
    return redirect("/images/" + str(item_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item or item["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        items.remove_image(item_id, image_id)

    return redirect("/images/" + str(item_id))

@app.route("/update_item", methods=["POST"])
def update_item():
    require_login()
    check_csrf()

    item_id = request.form["item_id"]
    item = items.get_item(item_id)
    if not item or item["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    description = request.form["description"]
    coordinates = request.form["coordinates"]
    location = request.form.get("location")

    if not title or len(title) > 50 or not description or len(description) > 1000 or not coordinates:
        abort(403)
    if not location or ":" not in location:
        abort(403)

    loc_title, loc_value = location.split(":")
    items.update_item(item_id, title, description, coordinates, loc_title, loc_value)

    return redirect("/item/" + str(item_id))

@app.route("/remove_item/<int:item_id>", methods=["GET", "POST"])
def remove_item(item_id):
    require_login()

    item = items.get_item(item_id)
    if not item or item["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_item.html", item=item)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            items.remove_item(item_id)
            flash("Kätkö poistettiin onnistuneesti.")
            return redirect("/")
        else:
            return redirect("/item/" + str(item_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    
    if not username or not password1:
        flash("VIRHE: Täytä kaikki kentät")
        return redirect("/register")
    
    if password1 != password2:
        flash("VIRHE: Salasanat eivät täsmää")
        return redirect("/register")

    try:
        users.create_user(username, password1)
        flash("Käyttäjätunnus luotu onnistuneesti! Voit nyt kirjautua sisään.")
        return redirect("/login")
    except sqlite3.IntegrityError:
        flash("VIRHE: Tunnus on jo varattu")
        return redirect("/register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("VIRHE: Väärä tunnus tai salasana")
            return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

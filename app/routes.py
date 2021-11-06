# CircleTable — Christopher Liu, Yusuf Elsharawy, Deven Maheshwari, Naomi Naranjo
# SoftDev
# P00: CircleStories

"""Routes

Handles all of the Flask app routes for CircleStories.
"""

import sqlite3

from flask import render_template, redirect, request, url_for, session

from app import app
from app import storydb
from app import auth
from app.auth import authenticate_user, create_user

DB_FILE = "circlestories.db"

STORY_DB = storydb.StoryDB(DB_FILE)


@app.route("/")
@app.route("/index")
def index():
    """CircleStories homepage."""
    if "username" in session:
        return render_template("homepage.html", username=session["username"])

    return render_template("guest.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Displays login form and handles form response."""
    if "username" in session:
        return redirect(url_for("index"))

    # GET request: display the form
    if request.method == "GET":
        return render_template("login.html")

    # POST request: handle the form response and redirect
    username = request.form.get("username", default="")
    password = request.form.get("password", default="")

    if authenticate_user(username, password):
        session["username"] = username
        return redirect(url_for("index"))

    return render_template("login.html", error="Username or password incorrect")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Displays registration form and handles form response."""

    if "username" in session:
        return redirect(url_for("index"))

    # GET request: display the form
    if request.method == "GET":
        return render_template("register.html")

    # POST request: handle the form response and redirect
    username = request.form.get("username", default="")
    email = request.form.get("email", default="")
    password = request.form.get("password", default="")
    password_check = request.form.get("password_check", default="")

    errors = create_user(username, email, password, password_check)
    if errors:
        return render_template("register.html", errors=errors)

    # Maybe put a flash message here to confirm everything works
    return redirect(url_for("login"))

@app.route("/new_story", methods=["GET", "POST"])
def new_story():
    """Allows user to create to a new story"""
    # GET request: display the form
    if request.method == "GET":
        return render_template("new_story.html")

    # POST request: handle the form response and redirect
    created_story_title = request.form.get("title", default="")
    created_story_content = request.form.get("start", default="")
    username = auth.get_user_id(session['username'])

    STORY_DB.add_story(username, created_story_title)
    STORY_DB.add_block(username, created_story_content)

    return redirect(url_for("get_story"))

@app.route("/logout")
def logout():
    """Logs out the current user."""

    if "username" in session:
        del session["username"]
    return redirect(url_for("index"))


@app.route("/story/<story_id>")
def get_story(story_id):
    if "username" not in session:
        # "You need to login!"
        # or non-users should be allowed to contibute? idk
        return render_template(
            "error.html",
            error_title="Login Required",
            error_msg="You must log in to view this page.",
        )
    else:
        user_id = auth.get_user_id(session["username"])
        # if this user has contributed to this story, display the whole text
        if STORY_DB.is_contributor(user_id, story_id):
            text = STORY_DB.get_story(story_id).full_text()
            return render_template("view.html", entire_story=text)
        else:
            story = STORY_DB.get_story(story_id)
            if story is not None:  # otherwise, if the story exists, show form to append
                return render_template(
                    "append.html", last_block=STORY_DB.get_story(story_id).last_block()
                )
            return render_template(
                "error.html",
                error_title="Story Not Found",
                error_msg="Either this story was deleted, or never existed to begin with. Please go back.",
            )

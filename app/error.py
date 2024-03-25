from flask import Blueprint, render_template

error = Blueprint("error", __name__)


@error.app_errorhandler(404)
def page_not_found(e):
    return render_template("index.html", main_template="./content/404.html"), 404


@error.app_errorhandler(500)
def internal_server_error(e):
    return render_template("index.html", main_template="./content/404.html"), 500

from flask import Blueprint, render_template, session, request, jsonify, make_response
from . import db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if "firstname" in session:
        return render_template(
            "index.html",
            main_template="./content/homepage.html",
            firstname=session["firstname"],
        )
    else:
        return render_template("index.html", main_template="./content/homepage.html")


@main.route("/profile", methods=["GET", "PUT", "DELETE"])
def profile():
    if request.method == "PUT":
        data = request.get_json()

        data["rgpd_right"] = request.form.get("rgpd_right", None) is not None
        data["id"] = session["user_id"]

        db.update_user(data)
        user = db.get_user(session["user_id"])
        session["firstname"] = user[0]
        session["rgpd_right"] = user[2]
        return make_response(jsonify({"firstname": user[0]}), 200)

    if request.method == "DELETE":
        db.delete_user(session["user_id"])
        session.pop("firstname", None)
        session.pop("user_id", None)
        session.pop("rgpd_right", None)
        return make_response(jsonify({"message": "User deleted"}), 200)

    if "firstname" not in session:
        return render_template(
            "index.html",
            main_template="./content/login.html",
            error="Vous n'êtes pas connecté. Merci de vous diriger la page de connexion.",
        )

    user = db.get_user(session["user_id"])
    return render_template(
        "index.html",
        main_template="./content/profile.html",
        firstname=session["firstname"],
        user=user,
    )


@main.route("/profile/password", methods=["PUT"])
def password():
    data = request.get_json()
    data["id"] = session["user_id"]
    result = db.update_password(data)
    if result["code"] == 400:
        return make_response(jsonify(result), 400)
    return make_response(jsonify(result), 200)

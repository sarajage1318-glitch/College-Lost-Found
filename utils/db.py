"""Small MySQL connection helper shared by all blueprints."""

import mysql.connector
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            database=current_app.config["MYSQL_DATABASE"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
        )
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()
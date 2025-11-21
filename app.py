from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/commande", methods=["GET", "POST"])
def commande():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        nom = request.form.get("nom")
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")

        # Inserer client
        cursor.execute("""
            INSERT INTO clients (nom, telephone, adresse)
            VALUES (%s, %s, %s)
        """, (nom, telephone, adresse))
        conn.commit()
        id_client = cursor.lastrowid

        # Insérer commande
        cursor.execute("INSERT INTO commandes (id_client) VALUES (%s)", (id_client,))
        conn.commit()
        id_commande = cursor.lastrowid

        # pizza
        croute = request.form.get("croute")
        sauce = request.form.get("sauce")
        garnitures = request.form.getlist("garnitures")

        cursor.execute("""
            INSERT INTO pizzas (id_commande, id_croute, id_sauce, taille, prix)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_commande, croute, sauce, "Moyenne", 15.99))
        conn.commit()

        id_pizza = cursor.lastrowid

        for i in garnitures:
            cursor.execute("""
                INSERT INTO pizzas_garniture (id_pizza, id_garniture)
                VALUES (%s, %s)
            """, (id_pizza, i))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("resume", id=id_commande))

    # GET : récupérer options
    cursor.execute("SELECT * FROM croutes")
    croutes = cursor.fetchall()

    cursor.execute("SELECT * FROM sauces")
    sauces = cursor.fetchall()

    cursor.execute("SELECT * FROM garnitures")
    garnitures = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("commande.html",croutes=croutes,sauces=sauces,garnitures=garnitures)

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/livraisons")
def livraisons():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.id, c.nom, c.adresse, cmd.id AS id_commande
        FROM livraisons_attente l
        JOIN commandes cmd ON cmd.id = l.id_commande
        JOIN clients c ON c.id = cmd.id_client
    """)
    livraisons = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("livraisons.html", livraisons=livraisons)

@app.route("/complete/<int:id_commande>")
def complete(id_commande):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM livraisons_attente WHERE id_commande = %s", (id_commande,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("livraisons"))

if __name__ == "__main__":
    app.run(debug=True)

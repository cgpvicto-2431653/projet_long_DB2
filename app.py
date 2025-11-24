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


@app.route("/api/client/<int:id>")
def api_client(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM clients WHERE id = %s", (id,))
    client = cursor.fetchone()

    cursor.close()
    conn.close()

    if client:
        return {
            "nom": client["nom"],
            "telephone": client["telephone"],
            "adresse": client["adresse"]
        }
    return {"error": "not found"}, 404



@app.route("/commande", methods=["GET", "POST"])
def commande():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM croutes")
    croutes = cursor.fetchall()

    cursor.execute("SELECT * FROM sauces")
    sauces = cursor.fetchall()

    cursor.execute("SELECT * FROM garnitures")
    garnitures = cursor.fetchall()

    if request.method == "POST":
        client_id = request.form.get("client_id")

        # Connexion client
        if client_id and client_id.strip() != "":
            cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
            client = cursor.fetchone()

            if not client:
                return "Client introuvable", 400

            id_client = client_id

        # Nouveau client 
        else:
            nom = request.form.get("nom")
            telephone = request.form.get("telephone")
            adresse = request.form.get("adresse")

            if not nom or not telephone or not adresse:
                return "Champs client manquants", 400

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

        # Pizza 
        croute = request.form.get("croute")
        sauce = request.form.get("sauce")
        garnitures = request.form.getlist("garnitures")

        cursor.execute("""
            INSERT INTO pizzas (id_commande, id_croute, id_sauce, taille, prix)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_commande, croute, sauce, "Moyenne", 15.99))
        conn.commit()

        id_pizza = cursor.lastrowid

        for g in garnitures:
            cursor.execute("""
                INSERT INTO pizzas_garniture (id_pizza, id_garniture)
                VALUES (%s, %s)
            """, (id_pizza, g))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("resume", id=id_commande))

    cursor.close()
    conn.close()
    return render_template("commande.html", croutes=croutes, sauces=sauces, garnitures=garnitures)



@app.route("/resume")
def resume():
    id_commande = request.args.get("id")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Info commande + client
    cursor.execute("""
        SELECT cmd.id, c.nom, c.telephone, c.adresse, cmd.date_commande
        FROM commandes cmd
        JOIN clients c ON c.id = cmd.id_client
        WHERE cmd.id = %s
    """, (id_commande,))
    commande = cursor.fetchone()

    # Info pizza
    cursor.execute("""
        SELECT p.id, cr.nom AS croute, s.nom AS sauce, p.taille, p.prix
        FROM pizzas p
        JOIN croutes cr ON cr.id = p.id_croute
        JOIN sauces s ON s.id = p.id_sauce
        WHERE p.id_commande = %s
    """, (id_commande,))
    pizza = cursor.fetchone()

    # Garnitures
    cursor.execute("""
        SELECT g.nom
        FROM pizzas_garniture pg
        JOIN garnitures g ON g.id = pg.id_garniture
        WHERE pg.id_pizza = %s
    """, (pizza["id"],))
    garnitures = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("resume.html",commande=commande,pizza=pizza,garnitures=garnitures)




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

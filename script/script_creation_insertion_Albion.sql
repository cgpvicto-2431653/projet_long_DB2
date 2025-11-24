CREATE DATABASE IF NOT EXISTS database_pizza;
USE database_pizza;

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    telephone VARCHAR(255) NOT NULL,
    adresse VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS commandes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_client INT NOT NULL,
    date_commande DATETIME NOT NULL DEFAULT NOW(),
    date_livraison DATETIME NULL,
    FOREIGN KEY (id_client) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS croutes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS sauces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS garnitures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS pizzas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL,
    id_croute INT NOT NULL,
    id_sauce INT NOT NULL,
    taille VARCHAR(255) NOT NULL,
    prix DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes(id),
    FOREIGN KEY (id_croute) REFERENCES croutes(id),
    FOREIGN KEY (id_sauce) REFERENCES sauces(id)
);

CREATE TABLE IF NOT EXISTS pizzas_garniture (
    id_pizza INT NOT NULL,
    id_garniture INT NOT NULL,
    PRIMARY KEY (id_pizza, id_garniture),
    FOREIGN KEY (id_pizza) REFERENCES pizzas(id),
    FOREIGN KEY (id_garniture) REFERENCES garnitures(id)
);

CREATE TABLE IF NOT EXISTS livraisons_attente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_commande INT NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes(id)
);

DROP TRIGGER IF EXISTS ajout_livraison_attente;
DELIMITER $$

CREATE TRIGGER ajout_livraison_attente
AFTER INSERT ON commandes
FOR EACH ROW
BEGIN
    INSERT INTO livraisons_attente (id_commande)
    VALUES (NEW.id);
END$$

DELIMITER ;



-- ========================================================================================================================
-- 															INSERTIONS
-- ========================================================================================================================

INSERT INTO croutes (nom) VALUES
('Classique'),
('Mince'),
('Épaisse');


INSERT INTO sauces (nom) VALUES
('Tomate'),
('Spaghetti'),
('Alfredo');


INSERT INTO garnitures (nom) VALUES
('Pepperoni'),
('Champignons'),
('Oignons'),
('Poivrons'),
('Olives'),
('Anchois'),
('Bacon'),
('Poulet'),
('Maïs'),
('Fromage'),
('Piments forts');


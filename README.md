# PassChecker - Gestionnaire de Mots de Passe

PassChecker est un gestionnaire de mots de passe sécurisé avec une interface graphique moderne. Il permet de stocker, gérer et vérifier vos mots de passe tout en s'assurant qu'ils n'ont pas été compromis.

## Fonctionnalités

- Interface graphique moderne avec thème sombre
- Stockage sécurisé des mots de passe avec chiffrement
- Vérification des mots de passe via l'API HaveIBeenPwned
- Système de favoris
- Historique des actions
- Critères de sécurité pour les mots de passe
- Copie sécurisée dans le presse-papiers

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-nom/passchecker.git
cd passchecker
```

2. Créez un environnement virtuel :
```bash
python -m venv myenv
source myenv/bin/activate  # Sur Unix
myenv\Scripts\activate     # Sur Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Structure de la Base de Données

Le gestionnaire utilise SQLite avec les tables suivantes :

### Table `master_password`
- `id`: INTEGER PRIMARY KEY (toujours 1)
- `salt`: BLOB - Sel pour le hachage
- `key_hash`: TEXT - Hash du mot de passe maître
- `encryption_key`: BLOB - Clé de chiffrement des mots de passe

### Table `stored_passwords`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `site`: TEXT - URL ou nom du site
- `username`: TEXT - Nom d'utilisateur
- `encrypted_password`: TEXT - Mot de passe chiffré
- `key_id`: INTEGER - Référence vers master_password

### Table `favoris`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `password_id`: INTEGER - Référence vers stored_passwords
- `date_ajout`: TIMESTAMP - Date d'ajout aux favoris

### Table `historique`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `password_id`: INTEGER - Référence vers stored_passwords
- `date_action`: TIMESTAMP - Date de l'action
- `type_action`: TEXT - Type d'action (CREATION, MODIFICATION, etc.)
- `details_action`: TEXT - Détails supplémentaires

## Utilisation

1. Lancez l'application :
```bash
python main.py
```

2. À la première utilisation, créez un mot de passe maître
3. Utilisez l'interface pour :
   - Ajouter des mots de passe
   - Vérifier leur sécurité
   - Gérer vos favoris
   - Consulter l'historique

## Sécurité

- Les mots de passe sont chiffrés avec Fernet (bibliothèque cryptography)
- Vérification des mots de passe compromis via HaveIBeenPwned
- Protection contre les injections SQL avec SQLite
- Critères de sécurité stricts pour les mots de passe

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
import sqlite3
import hashlib
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime
from .leak_checker import LeakChecker

class PasswordManager:
    def __init__(self, db_path="passwords.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.key = None
        self.cipher_suite = None
        self.leak_checker = LeakChecker()
        self.setup_database()

    def setup_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        
        # Table pour le mot de passe maître
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                salt BLOB NOT NULL,
                key_hash TEXT NOT NULL
            )
        ''')
        
        # Table pour les mots de passe stockés
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stored_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password TEXT NOT NULL
            )
        ''')
        
        # Table pour les favoris
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS favoris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password_id INTEGER NOT NULL,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (password_id) REFERENCES stored_passwords(id) ON DELETE CASCADE
            )
        ''')
        
        # Table pour l'historique
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historique (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password_id INTEGER NOT NULL,
                date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type_action TEXT NOT NULL,
                details_action TEXT,
                FOREIGN KEY (password_id) REFERENCES stored_passwords(id) ON DELETE CASCADE
            )
        ''')
        
        self.connection.commit()

    def is_initialized(self):
        """Vérifie si un mot de passe maître existe déjà"""
        self.cursor.execute("SELECT COUNT(*) FROM master_password")
        return self.cursor.fetchone()[0] > 0

    def set_master_password(self, master_password):
        """Configure le mot de passe maître initial"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        key_hash = hashlib.sha256(key).hexdigest()
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO master_password (id, salt, key_hash)
            VALUES (1, ?, ?)
        ''', (salt, key_hash))
        self.connection.commit()
        
        self.cipher_suite = Fernet(key)

    def verify_master_password(self, master_password):
        """Vérifie si le mot de passe maître est correct"""
        self.cursor.execute("SELECT salt, key_hash FROM master_password WHERE id = 1")
        result = self.cursor.fetchone()
        if not result:
            return False
            
        salt, stored_hash = result
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        key_hash = hashlib.sha256(key).hexdigest()
        
        if key_hash == stored_hash:
            self.cipher_suite = Fernet(key)
            return True
        return False

    def add_to_history(self, password_id, type_action, details=""):
        """Ajoute une action à l'historique"""
        self.cursor.execute('''
            INSERT INTO historique (password_id, type_action, details_action)
            VALUES (?, ?, ?)
        ''', (password_id, type_action, details))
        self.connection.commit()

    def add_to_favorites(self, password_id):
        """Ajoute un mot de passe aux favoris"""
        try:
            self.cursor.execute('''
                INSERT INTO favoris (password_id)
                VALUES (?)
            ''', (password_id,))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def remove_from_favorites(self, password_id):
        """Retire un mot de passe des favoris"""
        self.cursor.execute('''
            DELETE FROM favoris
            WHERE password_id = ?
        ''', (password_id,))
        self.connection.commit()

    def is_favorite(self, password_id):
        """Vérifie si un mot de passe est en favori"""
        self.cursor.execute('''
            SELECT COUNT(*) FROM favoris
            WHERE password_id = ?
        ''', (password_id,))
        return self.cursor.fetchone()[0] > 0

    def get_favorites(self):
        """Récupère tous les mots de passe favoris"""
        self.cursor.execute('''
            SELECT sp.* FROM stored_passwords sp
            JOIN favoris f ON sp.id = f.password_id
        ''')
        return self.cursor.fetchall()

    def get_history(self, password_id=None):
        """Récupère l'historique des actions"""
        if password_id:
            self.cursor.execute('''
                SELECT * FROM historique
                WHERE password_id = ?
                ORDER BY date_action DESC
            ''', (password_id,))
        else:
            self.cursor.execute('''
                SELECT * FROM historique
                ORDER BY date_action DESC
            ''')
        return self.cursor.fetchall()

    def add_password(self, site, username, password):
        """Ajoute un nouveau mot de passe"""
        if not self.cipher_suite:
            raise ValueError("Encryption not initialized")
        
        if self.leak_checker.check_password(password):
            return False, "Ce mot de passe a été compromis !"
        
        encrypted_password = self.cipher_suite.encrypt(password.encode()).decode()
        
        self.cursor.execute('''
            INSERT INTO stored_passwords (site, username, encrypted_password)
            VALUES (?, ?, ?)
        ''', (site, username, encrypted_password))
        
        password_id = self.cursor.lastrowid
        self.add_to_history(password_id, "CREATION", f"Site: {site}, Username: {username}")
        self.connection.commit()
        
        return True, "Mot de passe ajouté avec succès"

    def get_password(self, site, username):
        """Récupère un mot de passe stocké"""
        if not self.cipher_suite:
            raise ValueError("Encryption not initialized")
        
        self.cursor.execute('''
            SELECT id, encrypted_password FROM stored_passwords
            WHERE site = ? AND username = ?
        ''', (site, username))
        
        result = self.cursor.fetchone()
        if result:
            password_id, encrypted_password = result
            self.add_to_history(password_id, "ACCES", "Mot de passe consulté")
            decrypted_password = self.cipher_suite.decrypt(encrypted_password.encode()).decode()
            return decrypted_password
        return None

    def delete_password(self, id):
        """Supprime un mot de passe"""
        self.cursor.execute('''
            SELECT site, username FROM stored_passwords
            WHERE id = ?
        ''', (id,))
        result = self.cursor.fetchone()
        if result:
            site, username = result
            self.add_to_history(id, "SUPPRESSION", f"Site: {site}, Username: {username}")
            
            self.cursor.execute('''
                DELETE FROM stored_passwords
                WHERE id = ?
            ''', (id,))
            self.connection.commit()
            return True
        return False

    def update_password(self, id, new_password):
        """Met à jour un mot de passe existant"""
        if not self.cipher_suite:
            raise ValueError("Encryption not initialized")
        
        if self.leak_checker.check_password(new_password):
            return False, "Ce mot de passe a été compromis !"
        
        encrypted_password = self.cipher_suite.encrypt(new_password.encode()).decode()
        
        self.cursor.execute('''
            UPDATE stored_passwords
            SET encrypted_password = ?
            WHERE id = ?
        ''', (encrypted_password, id))
        
        self.add_to_history(id, "MODIFICATION", "Mot de passe modifié")
        self.connection.commit()
        return True, "Mot de passe mis à jour avec succès"

    def is_password_leaked(self, password):
        """Vérifie si un mot de passe est compromis"""
        return self.leak_checker.check_password(password)

    def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
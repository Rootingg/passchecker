import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import re

def validate_site(site):
    """
    Valide le format d'une URL de site.
    Retourne True si le format est valide, sinon False.
    """
    pattern = r"^(https?:\/\/)?([a-zA-Z0-9\.-]+)\.([a-zA-Z]{2,6})([\/\w \.-]*)*\/?$"
    return re.match(pattern, site)

def validate_password_strength(password):
    """
    Valide la robustesse d'un mot de passe.
    Retourne True si le mot de passe est suffisamment robuste, sinon False.
    """
    if len(password) < 8:
        raise ValueError("Le mot de passe doit comporter au moins 8 caractères.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Le mot de passe doit contenir au moins un caractère spécial.")
    return True

class AddPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.title("Ajouter un mot de passe")
        self.geometry("400x300")
        
        # Champs de saisie
        ctk.CTkLabel(self, text="Site:").pack(pady=5)
        self.site_entry = ctk.CTkEntry(self)
        self.site_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Nom d'utilisateur:").pack(pady=5)
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Mot de passe:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Confirmer le mot de passe:").pack(pady=5)
        self.confirm_entry = ctk.CTkEntry(self, show="*")
        self.confirm_entry.pack(pady=5)
        
        # Boutons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Ajouter", 
                     command=self.add_password).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Annuler", 
                     command=self.destroy).pack(side=tk.LEFT, padx=5)

def add_password(self):
    """Ajoute le mot de passe avec validation et gestion des erreurs."""
    try:
        # Récupération des champs d'entrée
        site = self.site_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get()

        # Validation des mots de passe
        if password != confirm_password:
            raise ValueError("Les mots de passe ne correspondent pas!")
        
        # Validation des champs obligatoires
        if not site or not username:
            raise ValueError("Veuillez remplir tous les champs!")
        
        # Validation du format du site
        if not validate_site(site):
            raise ValueError("Le format du site est invalide. Utilisez une URL correcte.")
        
        # Validation de la robustesse du mot de passe
        validate_password_strength(password)

        # Ajout du mot de passe via le manager
        success, message = self.manager.add_password(site, username, password)

        if success:
            messagebox.showinfo("Succès", message)
            self.destroy()
        else:
            raise ValueError(message)
    except ValueError as ve:
        messagebox.showerror("Erreur", str(ve))
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {str(e)}")
import customtkinter as ctk
from tkinter import messagebox
import re

def validate_master_password(password):
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

class CreateMasterPasswordDialog:
    def __init__(self, parent):
        from models.password_manager import PasswordManager
        self.manager = PasswordManager()  # Pour accéder au leak_checker
        self.password = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Créer un mot de passe maître")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        
        ctk.CTkLabel(self.dialog, text="Créez votre mot de passe maître:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.dialog, show="*")
        self.password_entry.pack(pady=5)
        
        ctk.CTkLabel(self.dialog, text="Confirmez le mot de passe:").pack(pady=5)
        self.confirm_entry = ctk.CTkEntry(self.dialog, show="*")
        self.confirm_entry.pack(pady=5)
        
        ctk.CTkButton(self.dialog, text="Créer", command=self.validate).pack(pady=20)
        
        self.dialog.protocol("WM_DELETE_WINDOW")
        self.dialog.grab_set()
        parent.wait_window(self.dialog)

    def validate(self):
        password = self.password_entry.get()
        
        if password != self.confirm_entry.get():
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas!")
            return
        
        try:
            validate_master_password(password)
        except ValueError as ve:
            messagebox.showerror("Erreur", str(ve))
            return

        if self.manager.leak_checker.check_password(password):
            messagebox.showerror("Erreur", "Ce mot de passe a été compromis! Veuillez en choisir un autre.")
            return
            
        self.password = password
        self.dialog.grab_release()
        self.dialog.destroy()
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

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
        """Ajoute le mot de passe"""
        if self.password_entry.get() != self.confirm_entry.get():
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas!")
            return
        
        if not self.site_entry.get() or not self.username_entry.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs!")
            return
        
        success, message = self.manager.add_password(
            self.site_entry.get(),
            self.username_entry.get(),
            self.password_entry.get()
        )
        
        if success:
            messagebox.showinfo("Succès", message)
            self.destroy()
        else:
            messagebox.showerror("Erreur", message)
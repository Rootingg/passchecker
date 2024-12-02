import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

class ChangeMasterPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.title("Changer le mot de passe maître")
        self.geometry("400x400")
        
        ctk.CTkLabel(self, text="Ancien mot de passe:").pack(pady=5)
        self.old_password_entry = ctk.CTkEntry(self, show="*")
        self.old_password_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Nouveau mot de passe:").pack(pady=5)
        self.new_password_entry = ctk.CTkEntry(self, show="*")
        self.new_password_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Confirmer le nouveau mot de passe:").pack(pady=5)
        self.confirm_entry = ctk.CTkEntry(self, show="*")
        self.confirm_entry.pack(pady=5)
        
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Changer", 
                     command=self.change_password).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Annuler", 
                     command=self.destroy).pack(side=tk.LEFT, padx=5)

    def change_password(self):
        """Change le mot de passe maître"""
        if self.new_password_entry.get() != self.confirm_entry.get():
            messagebox.showerror("Erreur", "Les nouveaux mots de passe ne correspondent pas!")
            return
        
        if len(self.new_password_entry.get()) < 8:
            messagebox.showerror("Erreur", "Le nouveau mot de passe doit faire au moins 8 caractères!")
            return
        
        try:
            if not self.manager.verify_master_password(self.old_password_entry.get()):
                messagebox.showerror("Erreur", "Ancien mot de passe incorrect!")
                return
            
            self.manager.set_master_password(self.new_password_entry.get())
            messagebox.showinfo("Succès", "Mot de passe maître changé avec succès")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import pyperclip
from datetime import datetime


class PasswordDetailsDialog(ctk.CTkToplevel):
    def __init__(self, parent, manager, site, username, password_id):
        super().__init__(parent)
        self.manager = manager
        self.site = site
        self.username = username
        self.password_id = password_id
        
        self.title(f"Détails - {site}")
        self.geometry("500x300")
        
        ctk.CTkLabel(self, text=f"Site: {site}").pack(pady=5)
        ctk.CTkLabel(self, text=f"Nom d'utilisateur: {username}").pack(pady=5)
        
        password = self.manager.get_password(site, username)
        
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        # Bouton favori avec état
        self.fav_text = tk.StringVar()
        self.update_favorite_button_text()
        ctk.CTkButton(button_frame, text=self.fav_text.get(),
                     command=self.toggle_favorite).pack(side=tk.LEFT, padx=5)
        
        ctk.CTkButton(button_frame, text="Copier le mot de passe",
                     command=lambda: self.copy_to_clipboard(password)).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Supprimer",
                     command=self.delete_password).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="Fermer",
                     command=self.destroy).pack(side=tk.LEFT, padx=5)

        # Historique des actions pour ce mot de passe
        history_frame = ctk.CTkFrame(self)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ctk.CTkLabel(history_frame, text="Historique", 
                    font=("Arial", 12, "bold")).pack(pady=5)
        
        history = self.manager.get_history(self.password_id)
        history_text = ""
        for h in history:
            date = datetime.strptime(h[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            history_text += f"{date} - {h[3]}: {h[4]}\n"
        
        history_label = ctk.CTkTextbox(history_frame, height=100)
        history_label.pack(fill=tk.BOTH, expand=True, padx=5)
        history_label.insert("1.0", history_text)
        history_label.configure(state="disabled")

    def update_favorite_button_text(self):
        """Met à jour le texte du bouton favori"""
        is_fav = self.manager.is_favorite(self.password_id)
        self.fav_text.set("♥ Retirer des favoris" if is_fav else "♡ Ajouter aux favoris")
        
    def toggle_favorite(self):
        """Ajoute ou retire des favoris, avec vérification de la persistance"""
        try:
            if self.manager.is_favorite(self.password_id):
                self.manager.remove_from_favorites(self.password_id)
                self.manager.add_to_history(self.password_id, "FAVORI", "Retiré des favoris")
            else:
                self.manager.add_to_favorites(self.password_id)
                self.manager.add_to_history(self.password_id, "FAVORI", "Ajouté aux favoris")
            
            # Vérification de la persistance
            if self.manager.is_favorite(self.password_id):
                messagebox.showinfo("Succès", "Le mot de passe est désormais en favoris")
            else:
                messagebox.showinfo("Succès", "Le mot de passe a été retiré des favoris")
                
            self.update_favorite_button_text()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification du favori : {str(e)}")

    def copy_to_clipboard(self, text):
        """Copie le texte dans le presse-papiers"""
        pyperclip.copy(text)
        messagebox.showinfo("Succès", "Mot de passe copié dans le presse-papiers")
        self.manager.add_to_history(self.password_id, "COPIE", "Mot de passe copié")

    # Modification dans password_details.py
    def delete_password(self):
        """Supprime le mot de passe et toutes les données associées"""
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer ce mot de passe et ses données associées ?"):
            try:
                self.manager.cursor.execute('DELETE FROM historique WHERE password_id = ?', (self.password_id,))
                self.manager.cursor.execute('DELETE FROM favoris WHERE password_id = ?', (self.password_id,))
                self.manager.delete_password(self.password_id)
                self.manager.connection.commit()
                messagebox.showinfo("Succès", "Mot de passe et données associées supprimés avec succès")
                self.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")
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
        self.setup_window()
        self.create_widgets()
        self.load_password()

    def setup_window(self):
        self.title("Détails du mot de passe")
        self.geometry("500x650")
        self.configure(fg_color=("#1A1A1A", "#1A1A1A"))
        
        # Centrer la fenêtre
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 650) // 2
        self.geometry(f"+{x}+{y}")

    def create_info_section(self, text: str, value: str, can_copy: bool = True):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=6, anchor="w")
        
        label = ctk.CTkLabel(
            container,
            text=text,
            font=("Inter", 13),
            text_color="#8E8E93"
        )
        label.pack(anchor="w", pady=(0, 2))
        
        value_frame = ctk.CTkFrame(
            container,
            height=35,
            fg_color="#2C2C2E",
            border_color="#48484A",
            border_width=1
        )
        value_frame.pack(fill="x")
        
        value_label = ctk.CTkLabel(
            value_frame,
            text=value,
            font=("Inter", 13),
            text_color="white"
        )
        value_label.pack(side="left", padx=10)
        
        if can_copy:
            copy_button = ctk.CTkButton(
                value_frame,
                text="Copier",
                font=("Inter", 12),
                height=25,
                width=60,
                corner_radius=6,
                fg_color="#30D158",
                hover_color="#25A344",
                command=lambda: self.copy_to_clipboard(value)
            )
            copy_button.pack(side="right", padx=5, pady=5)

    def create_widgets(self):
        # Titre avec site
        title = ctk.CTkLabel(
            self,
            text=f"Détails - {self.site}",
            font=("Inter", 22, "bold"),
            justify="left"
        )
        title.pack(anchor="w", padx=30, pady=20)

        # Les sections seront remplies par load_password()

        # Section historique
        history_label = ctk.CTkLabel(
            self,
            text="Historique",
            font=("Inter", 16, "bold"),
            justify="left"
        )
        history_label.pack(anchor="w", padx=30, pady=(20, 10))

        # Zone d'historique stylisée
        self.history_box = ctk.CTkTextbox(
            self,
            height=150,
            fg_color="#2C2C2E",
            border_color="#48484A",
            border_width=1,
            corner_radius=6,
            font=("Inter", 12)
        )
        self.history_box.pack(fill="x", padx=30)

        # Boutons d'action
        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x", padx=30, pady=20)

        # Bouton favori
        self.fav_text = tk.StringVar()
        self.fav_button = ctk.CTkButton(
            button_container,
            textvariable=self.fav_text,
            font=("Inter", 13, "bold"),
            height=35,
            corner_radius=8,
            fg_color="#FF9F0A",
            hover_color="#D98609",
            command=self.toggle_favorite
        )
        self.fav_button.pack(fill="x", pady=(0, 6))

        # Bouton supprimer
        self.delete_button = ctk.CTkButton(
            button_container,
            text="Supprimer",
            font=("Inter", 13, "bold"),
            height=35,
            corner_radius=8,
            fg_color="#FF453A",
            hover_color="#D93D33",
            command=self.delete_password
        )
        self.delete_button.pack(fill="x", pady=(0, 6))

        # Bouton fermer
        self.close_button = ctk.CTkButton(
            button_container,
            text="Fermer",
            font=("Inter", 13, "bold"),
            height=35,
            corner_radius=8,
            fg_color="#2C2C2E",
            hover_color="#3C3C3E",
            command=self.destroy
        )
        self.close_button.pack(fill="x")

    def load_password(self):
        # Informations du mot de passe
        self.create_info_section("Site", self.site)
        self.create_info_section("Nom d'utilisateur", self.username)
        password = self.manager.get_password(self.site, self.username)
        self.create_info_section("Mot de passe", password)

        # Mise à jour du bouton favori
        self.update_favorite_button_text()

        # Charger l'historique
        history = self.manager.get_history(self.password_id)
        history_text = ""
        for h in history:
            date = datetime.strptime(h[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            history_text += f"{date} - {h[3]}: {h[4]}\n"
        
        self.history_box.delete("1.0", tk.END)
        self.history_box.insert("1.0", history_text)
        self.history_box.configure(state="disabled")

    def update_favorite_button_text(self):
        is_fav = self.manager.is_favorite(self.password_id)
        heart = "♥" if is_fav else "♡"
        text = f"{heart} {'Retirer des' if is_fav else 'Ajouter aux'} favoris"
        self.fav_text.set(text)
        
        # Mettre à jour les couleurs du bouton
        if is_fav:
            self.fav_button.configure(
                fg_color="#2C2C2E",
                hover_color="#3C3C3E"
            )
        else:
            self.fav_button.configure(
                fg_color="#FF9F0A",
                hover_color="#D98609"
            )

    def toggle_favorite(self):
        if self.manager.is_favorite(self.password_id):
            self.manager.remove_from_favorites(self.password_id)
            self.manager.add_to_history(self.password_id, "FAVORI", "Retiré des favoris")
        else:
            self.manager.add_to_favorites(self.password_id)
            self.manager.add_to_history(self.password_id, "FAVORI", "Ajouté aux favoris")
        
        self.update_favorite_button_text()
        self.load_password()  # Recharger l'historique

    def copy_to_clipboard(self, text):
        pyperclip.copy(text)
        messagebox.showinfo(
            "Succès",
            "Mot de passe copié dans le presse-papiers"
        )
        self.manager.add_to_history(self.password_id, "COPIE", "Mot de passe copié")
        self.load_password()  # Recharger l'historique

    def delete_password(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous vraiment supprimer ce mot de passe ?"
        ):
            if self.manager.delete_password(self.password_id):
                self.destroy()
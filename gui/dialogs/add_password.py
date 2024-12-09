import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import re
from typing import Tuple

class PasswordCriteria(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.criteria = {
            "length": ("8 caractères minimum", False),
            "uppercase": ("Une majuscule", False),
            "lowercase": ("Une minuscule", False),
            "number": ("Un chiffre", False),
            "special": ("Un caractère spécial", False)
        }
        self.create_widgets()

    def create_widgets(self):
        for key, (text, _) in self.criteria.items():
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", pady=1)  # Réduit de 2 à 1
            
            self.criteria[key] = (text, ctk.CTkLabel(
                frame, 
                text="✓",
                font=("Inter", 12),
                text_color="#30D158"
            ))
            
            ctk.CTkLabel(
                frame,
                text=text,
                font=("Inter", 12),
                text_color="#8E8E93",
                anchor="w"
            ).pack(side="left")
            
            self.criteria[key][1].pack(side="right")
            self.criteria[key][1].pack_forget()

    def update(self, password: str):
        checks = {
            "length": len(password) >= 8,
            "uppercase": bool(re.search(r"[A-Z]", password)),
            "lowercase": bool(re.search(r"[a-z]", password)),
            "number": bool(re.search(r"[0-9]", password)),
            "special": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
        }
        
        for key, is_valid in checks.items():
            if is_valid:
                self.criteria[key][1].pack(side="right")
            else:
                self.criteria[key][1].pack_forget()

class AddPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()

    def setup_window(self):
        self.title("Ajouter un mot de passe")
        self.geometry("450x680")  # Réduit de 750 à 680
        self.configure(fg_color=("#1A1A1A", "#1A1A1A"))
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 450) // 2
        y = (screen_height - 680) // 2  # Ajusté aussi ici
        self.geometry(f"+{x}+{y}")

    def create_entry_with_label(self, text: str, show: str = "", help_text: str = None) -> Tuple[ctk.CTkLabel, ctk.CTkEntry, ctk.CTkLabel]:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=6, anchor="w")  # Réduit de 8 à 6
        
        label = ctk.CTkLabel(container, text=text, font=("Inter", 13), text_color="#8E8E93")
        label.pack(anchor="w", pady=(0, 2))  # Réduit de 4 à 2
        
        entry = ctk.CTkEntry(container, show=show, height=35,  # Réduit de 40 à 35
                           fg_color="#2C2C2E", 
                           border_color="#48484A",
                           border_width=1,
                           corner_radius=8,
                           font=("Inter", 13))
        entry.pack(fill="x")
        
        help_label = None
        if help_text:
            help_label = ctk.CTkLabel(
                container,
                text=help_text,
                font=("Inter", 11),
                text_color="#8E8E93",
                justify="left"
            )
            help_label.pack(anchor="w", pady=(2, 0))  # Réduit de 4 à 2
        
        return label, entry, help_label

    def create_widgets(self):
        title = ctk.CTkLabel(self, 
                           text="Nouveau mot de passe", 
                           font=("Inter", 22, "bold"),
                           justify="left")
        title.pack(anchor="w", padx=30, pady=20)  # Réduit de 25 à 20

        self.site_label, self.site_entry, self.site_help = self.create_entry_with_label(
            "Site",
            help_text="Format: http(s)://exemple.com ou exemple.com"
        )
        self.username_label, self.username_entry, _ = self.create_entry_with_label("Nom d'utilisateur")
        self.password_label, self.password_entry, _ = self.create_entry_with_label("Mot de passe", show="●")
        self.confirm_label, self.confirm_entry, _ = self.create_entry_with_label("Confirmer le mot de passe", show="●")

        self.criteria = PasswordCriteria(self)
        self.criteria.pack(fill="x", padx=30, pady=10, anchor="w")  # Réduit de 15 à 10

        self.strength_bar = ctk.CTkProgressBar(self, height=3,
                                             fg_color="#2C2C2E",
                                             progress_color="#30D158")
        self.strength_bar.pack(fill="x", padx=30)
        self.strength_bar.set(0)

        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x", padx=30, pady=20)  # Réduit de 25 à 20

        self.submit_button = ctk.CTkButton(button_container,
                                        text="Ajouter",
                                        font=("Inter", 13, "bold"),
                                        height=35,  # Réduit de 40 à 35
                                        corner_radius=8,
                                        fg_color="#30D158",
                                        hover_color="#25A344",
                                        command=self.add_password)
        self.submit_button.pack(fill="x", pady=(0, 6))  # Réduit de 8 à 6

        self.cancel_button = ctk.CTkButton(button_container,
                                       text="Annuler",
                                       font=("Inter", 13, "bold"),
                                       height=35,  # Réduit de 40 à 35
                                       corner_radius=8,
                                       fg_color="#2C2C2E",
                                       hover_color="#3C3C3E",
                                       command=self.destroy)
        self.cancel_button.pack(fill="x")

    def setup_bindings(self):
        self.password_entry.bind("<KeyRelease>", self.on_password_change)

    def on_password_change(self, event=None):
        password = self.password_entry.get()
        self.criteria.update(password)
        
        criteria_met = sum([
            len(password) >= 8,
            bool(re.search(r"[A-Z]", password)),
            bool(re.search(r"[a-z]", password)),
            bool(re.search(r"[0-9]", password)),
            bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
        ])
        
        strength = criteria_met / 5
        self.strength_bar.set(strength)
        
        if strength < 0.4:
            color = "#FF453A"
        elif strength < 0.8:
            color = "#FFD60A"
        else:
            color = "#30D158"
            
        self.strength_bar.configure(progress_color=color)

    def validate_site(self, site: str) -> bool:
        pattern = r"^(https?:\/\/)?([a-zA-Z0-9\.-]+)\.([a-zA-Z]{2,6})([\/\w \.-]*)*\/?$"
        return bool(re.match(pattern, site))

    def add_password(self):
        try:
            site = self.site_entry.get().strip()
            username = self.username_entry.get().strip()
            password = self.password_entry.get()
            confirm_password = self.confirm_entry.get()

            if not all([site, username, password, confirm_password]):
                raise ValueError("Veuillez remplir tous les champs")
                
            if password != confirm_password:
                raise ValueError("Les mots de passe ne correspondent pas")
                
            if not self.validate_site(site):
                raise ValueError("Format du site invalide")
                
            if len(password) < 8:
                raise ValueError("Critères du mot de passe non respectés")
            
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
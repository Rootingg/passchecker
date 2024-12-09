import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import re

class ChangeMasterPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, manager):
        super().__init__(parent)
        self.manager = manager
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()

    def setup_window(self):
        self.title("Changer le mot de passe maître")
        self.geometry("450x680")
        self.configure(fg_color=("#1A1A1A", "#1A1A1A"))
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 450) // 2
        y = (screen_height - 680) // 2
        self.geometry(f"+{x}+{y}")

    def create_entry_with_label(self, text: str, show: str = "●") -> tuple[ctk.CTkLabel, ctk.CTkEntry]:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=30, pady=6, anchor="w")
        
        label = ctk.CTkLabel(container, text=text, font=("Inter", 13), text_color="#8E8E93")
        label.pack(anchor="w", pady=(0, 2))
        
        entry = ctk.CTkEntry(container, show=show, height=35,
                           fg_color="#2C2C2E", 
                           border_color="#48484A",
                           border_width=1,
                           corner_radius=8,
                           font=("Inter", 13))
        entry.pack(fill="x")
        
        return label, entry

    def create_widgets(self):
        # Titre
        title = ctk.CTkLabel(self, 
                           text="Changer le mot de passe maître", 
                           font=("Inter", 22, "bold"),
                           justify="left")
        title.pack(anchor="w", padx=30, pady=20)

        # Champs de saisie
        self.old_password_label, self.old_password_entry = self.create_entry_with_label(
            "Ancien mot de passe"
        )
        self.new_password_label, self.new_password_entry = self.create_entry_with_label(
            "Nouveau mot de passe"
        )
        self.confirm_label, self.confirm_entry = self.create_entry_with_label(
            "Confirmer le nouveau mot de passe"
        )

        # Critères de mot de passe
        self.criteria = PasswordCriteria(self)
        self.criteria.pack(fill="x", padx=30, pady=10, anchor="w")

        # Barre de force
        self.strength_bar = ctk.CTkProgressBar(self, height=3,
                                             fg_color="#2C2C2E",
                                             progress_color="#30D158")
        self.strength_bar.pack(fill="x", padx=30)
        self.strength_bar.set(0)

        # Boutons
        button_container = ctk.CTkFrame(self, fg_color="transparent")
        button_container.pack(fill="x", padx=30, pady=20)

        self.submit_button = ctk.CTkButton(button_container,
                                        text="Changer",
                                        font=("Inter", 13, "bold"),
                                        height=35,
                                        corner_radius=8,
                                        fg_color="#30D158",
                                        hover_color="#25A344",
                                        command=self.change_password)
        self.submit_button.pack(fill="x", pady=(0, 6))

        self.cancel_button = ctk.CTkButton(button_container,
                                       text="Annuler",
                                       font=("Inter", 13, "bold"),
                                       height=35,
                                       corner_radius=8,
                                       fg_color="#2C2C2E",
                                       hover_color="#3C3C3E",
                                       command=self.destroy)
        self.cancel_button.pack(fill="x")

    def setup_bindings(self):
        self.new_password_entry.bind("<KeyRelease>", self.on_password_change)

    def on_password_change(self, event=None):
        password = self.new_password_entry.get()
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

    def change_password(self):
        try:
            old_password = self.old_password_entry.get()
            new_password = self.new_password_entry.get()
            confirm_password = self.confirm_entry.get()

            if not all([old_password, new_password, confirm_password]):
                raise ValueError("Veuillez remplir tous les champs")
                
            if new_password != confirm_password:
                raise ValueError("Les nouveaux mots de passe ne correspondent pas")
                
            if len(new_password) < 8:
                raise ValueError("Le nouveau mot de passe doit faire au moins 8 caractères")
            
            criteria_met = sum([
                len(new_password) >= 8,
                bool(re.search(r"[A-Z]", new_password)),
                bool(re.search(r"[a-z]", new_password)),
                bool(re.search(r"[0-9]", new_password)),
                bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password))
            ])
            
            if criteria_met < 5:
                raise ValueError("Le nouveau mot de passe ne respecte pas tous les critères de sécurité")

            success, message = self.manager.change_master_password(old_password, new_password)
            if success:
                messagebox.showinfo("Succès", message)
                self.destroy()
            else:
                raise ValueError(message)
                
        except ValueError as ve:
            messagebox.showerror("Erreur", str(ve))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur inattendue : {str(e)}")

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
            frame.pack(fill="x", pady=1)
            
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
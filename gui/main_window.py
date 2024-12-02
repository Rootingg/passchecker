import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from datetime import datetime
from typing import Optional
import sys
# Import des dialogues
from .dialogs.create_master_password import CreateMasterPasswordDialog
from .dialogs.password_details import PasswordDetailsDialog
from .dialogs.add_password import AddPasswordDialog
from .dialogs.change_master_password import ChangeMasterPasswordDialog

class PasswordManagerGUI:
    def __init__(self):
        from models.password_manager import PasswordManager
        self.manager = PasswordManager()
        self.root = ctk.CTk()
        
        # Authentification avant de créer l'interface
        if not self.authenticate():
            self.root.destroy()
            sys.exit()
            
        self.setup_main_window()

    def authenticate(self):
        """Gère l'authentification de l'utilisateur"""
        if not self.manager.is_initialized():
            dialog = CreateMasterPasswordDialog(self.root)
            if dialog.password is None:
                return False
            try:
                self.manager.set_master_password(dialog.password)
                return True
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
                return False
        else:
            dialog = ctk.CTkInputDialog(title="Mot de passe maître", 
                                    text="Entrez votre mot de passe maître:")
            password = dialog.get_input()
            if password is None:
                return False
            
            # Vérification des fuites avant la vérification du mot de passe
            if self.manager.leak_checker.check_password(password):
                messagebox.showwarning("Attention", 
                    "Votre mot de passe maître a été compromis! " +
                    "Veuillez le changer dès que possible.")
            
            if not self.manager.verify_master_password(password):
                messagebox.showerror("Erreur", "Mot de passe maître incorrect")
                return False
            return True

    def initialize_app(self):
        """Initialise l'application avec vérification du mot de passe"""
        # Créer une fenêtre temporaire invisible pour les dialogues
        temp_root = ctk.CTk()
        temp_root.withdraw()  # Cache la fenêtre

        success = False
        if not self.manager.is_initialized():
            dialog = CreateMasterPasswordDialog(temp_root)
            if dialog.password:
                try:
                    self.manager.set_master_password(dialog.password)
                    success = True
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
        else:
            dialog = ctk.CTkInputDialog(master=temp_root, title="Mot de passe maître", 
                                      text="Entrez votre mot de passe maître:")
            password = dialog.get_input()
            if password and self.manager.verify_master_password(password):
                success = True
            elif password is not None:
                messagebox.showerror("Erreur", "Mot de passe maître incorrect")

        temp_root.destroy()
        return success

    def setup_main_window(self):
        """Configure la fenêtre principale"""
        self.root = ctk.CTk()
        self.root.title("Password Keeper and Checker")
        self.root.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        
        # Frame principal avec trois colonnes
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.setup_favorites_list()
        self.setup_password_list()
        self.setup_action_and_history()
        self.refresh_lists()

    def setup_favorites_list(self):
        """Configure la liste des favoris"""
        fav_frame = ctk.CTkFrame(self.main_frame)
        fav_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ctk.CTkLabel(fav_frame, text="Favoris", font=("Arial", 16, "bold")).pack(pady=10)
        
        style = ttk.Style()
        style.configure("Favorites.Treeview", background="#2b2b2b", 
                       fieldbackground="#2b2b2b", foreground="white")
        
        columns = ("Site", "Username")
        self.favorites_tree = ttk.Treeview(fav_frame, columns=columns, 
                                         show="headings", style="Favorites.Treeview")
        
        for col in columns:
            self.favorites_tree.heading(col, text=col)
            self.favorites_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(fav_frame, orient=tk.VERTICAL, 
                                command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=scrollbar.set)
        
        self.favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.favorites_tree.bind("<Double-1>", self.on_favorite_double_click)

    def setup_password_list(self):
        """Configure la liste des mots de passe"""
        list_frame = ctk.CTkFrame(self.main_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        ctk.CTkLabel(list_frame, text="Mots de passe stockés", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        style = ttk.Style()
        style.configure("Treeview", background="#2b2b2b", 
                       fieldbackground="#2b2b2b", foreground="white")
        
        columns = ("Site", "Username")
        self.password_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.password_tree.heading(col, text=col)
            self.password_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                command=self.password_tree.yview)
        self.password_tree.configure(yscrollcommand=scrollbar.set)
        
        self.password_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.password_tree.bind("<Double-1>", self.on_password_double_click)

    def setup_action_and_history(self):
        """Configure les boutons d'action et l'historique"""
        right_frame = ctk.CTkFrame(self.main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Section Actions
        action_frame = ctk.CTkFrame(right_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(action_frame, text="Actions", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        actions = [
            ("Ajouter un mot de passe", self.add_password_dialog),
            ("Vérifier un mot de passe", self.check_password_dialog),
            ("Changer le mot de passe maître", self.change_master_password)
        ]
        
        for text, command in actions:
            ctk.CTkButton(action_frame, text=text, 
                         command=command).pack(pady=5, fill=tk.X)
        
        # Section Historique
        history_frame = ctk.CTkFrame(right_frame)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(history_frame, text="Historique", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        columns = ("Date", "Action", "Détails")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                       show="headings")
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, 
                                command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_lists(self):
        """Actualise toutes les listes"""
        self.refresh_password_list()
        self.refresh_favorites_list()
        self.refresh_history_list()

    def refresh_favorites_list(self):
        """Actualise la liste des favoris"""
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
        
        favorites = self.manager.get_favorites()
        for fav in favorites:
            self.favorites_tree.insert("", tk.END, values=(fav[1], fav[2]))

    def refresh_history_list(self):
        """Actualise la liste de l'historique"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.manager.get_history()
        for h in history:
            date = datetime.strptime(h[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.history_tree.insert("", 0, values=(date, h[3], h[4]))

    def refresh_password_list(self):
        """Actualise la liste des mots de passe"""
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
        
        self.manager.cursor.execute("SELECT id, site, username FROM stored_passwords")
        for id, site, username in self.manager.cursor.fetchall():
            self.password_tree.insert("", tk.END, values=(site, username), tags=(str(id),))

    def initialize_database(self):
        """Initialise la base de données avec gestion des erreurs"""
        if not self.manager.is_initialized():
            password = self.create_master_password()
            if password is None:  # Si l'utilisateur ferme la fenêtre
                self.root.quit()
                return False
                
            try:
                self.manager.set_master_password(password)
                self.refresh_lists()
                return True
            except Exception as e:
                messagebox.showerror("Erreur", 
                    f"Impossible d'initialiser la base de données : {str(e)}")
                self.root.quit()
                return False
        else:
            password = self.ask_master_password()
            if password is None:  # Si l'utilisateur ferme la fenêtre
                self.root.quit()
                return False
                
            if self.manager.verify_master_password(password):
                self.refresh_lists()
                return True
            else:
                messagebox.showerror("Erreur", "Mot de passe maître incorrect")
                self.root.quit()
                return False

    def create_master_password(self) -> Optional[str]:
        """Demande la création d'un nouveau mot de passe maître"""
        dialog = CreateMasterPasswordDialog(self.root)
        self.root.wait_window(dialog)
        return dialog.password

    def ask_master_password(self) -> Optional[str]:
        """Demande le mot de passe maître à l'utilisateur"""
        dialog = ctk.CTkInputDialog(title="Mot de passe maître", 
                                text="Entrez votre mot de passe maître:")
        result = dialog.get_input()
        if result is None:  # Si l'utilisateur ferme la fenêtre
            self.root.quit()
        return result

    def on_password_double_click(self, event):
        """Gère le double-clic sur un mot de passe"""
        selection = self.password_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        site, username = self.password_tree.item(item, "values")
        id = self.password_tree.item(item, "tags")[0]
        
        dialog = PasswordDetailsDialog(self.root, self.manager, site, username, id)
        self.root.wait_window(dialog)
        self.refresh_lists()

    def on_favorite_double_click(self, event):
        """Gère le double-clic sur un favori"""
        selection = self.favorites_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        site, username = self.favorites_tree.item(item, "values")
        
        self.manager.cursor.execute('''
            SELECT id FROM stored_passwords
            WHERE site = ? AND username = ?
        ''', (site, username))
        result = self.manager.cursor.fetchone()
        if result:
            id = result[0]
            dialog = PasswordDetailsDialog(self.root, self.manager, site, username, id)
            self.root.wait_window(dialog)
            self.refresh_lists()

    def add_password_dialog(self):
        """Affiche la boîte de dialogue pour ajouter un mot de passe"""
        dialog = AddPasswordDialog(self.root, self.manager)
        self.root.wait_window(dialog)
        self.refresh_lists()

    def check_password_dialog(self):
        """Affiche la boîte de dialogue pour vérifier un mot de passe"""
        password = simpledialog.askstring("Vérifier un mot de passe", 
                                        "Entrez le mot de passe à vérifier:",
                                        show="*")
        if password:
            if self.manager.is_password_leaked(password):
                messagebox.showwarning("Attention", 
                                     "Ce mot de passe a été compromis !")
            else:
                messagebox.showinfo("Sécurité", 
                                  "Ce mot de passe n'a pas été trouvé dans la base des fuites.")

    def change_master_password(self):
        """Change le mot de passe maître"""
        dialog = ChangeMasterPasswordDialog(self.root, self.manager)
        self.root.wait_window(dialog)
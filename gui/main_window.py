import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import customtkinter as ctk
from datetime import datetime
from typing import Optional
import sys

from .dialogs.create_master_password import CreateMasterPasswordDialog
from .dialogs.password_details import PasswordDetailsDialog
from .dialogs.add_password import AddPasswordDialog
from .dialogs.change_master_password import ChangeMasterPasswordDialog

class PasswordManagerGUI:
    def __init__(self):
        from models.password_manager import PasswordManager
        self.manager = PasswordManager()
        self.root = ctk.CTk()
        self.setup_dark_theme()
        
        if not self.authenticate():
            self.root.destroy()
            sys.exit()
        
        self.setup_main_window()

    def authenticate(self):
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
                
                if self.manager.leak_checker.check_password(password):
                    messagebox.showwarning("Attention", 
                        "Votre mot de passe maître a été compromis! " +
                        "Veuillez le changer dès que possible.")
                
                if not self.manager.verify_master_password(password):
                    messagebox.showerror("Erreur", "Mot de passe maître incorrect")
                    return False
                return True

    def setup_dark_theme(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", 
            background="#2b2b2b",
            fieldbackground="#2b2b2b", 
            foreground="white",
            rowheight=25,
            borderwidth=0)
        style.configure("Treeview.Heading",
            background="#1e1e1e",
            foreground="white",
            relief="flat",
            borderwidth=0)
        style.map("Treeview",
            background=[("selected", "#404040")],
            foreground=[("selected", "white")])
        style.map("Treeview.Heading",
            background=[("active", "#404040")],
            foreground=[("active", "white")])
            
        # Supprimer les bordures
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def setup_main_window(self):
        self.root.title("Password Keeper and Checker")
        self.root.geometry("1000x600")
        
        self.main_frame = ctk.CTkFrame(self.root, fg_color="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.setup_favorites_list()
        self.setup_password_list()
        self.setup_action_and_history()
        self.refresh_lists()

    def setup_favorites_list(self):
        fav_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        fav_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        ctk.CTkLabel(fav_frame, text="Favoris", 
                    font=("Arial", 16, "bold"),
                    text_color="white").pack(pady=10)
        
        columns = ("Site", "Username")
        self.favorites_tree = ttk.Treeview(fav_frame, columns=columns, 
                                         show="headings")
        
        for col in columns:
            self.favorites_tree.heading(col, text=col)
            self.favorites_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(fav_frame, orient=tk.VERTICAL)
        scrollbar.configure(command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=scrollbar.set)
        
        self.favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.favorites_tree.bind("<Double-1>", self.on_favorite_double_click)

    def setup_password_list(self):
        list_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        ctk.CTkLabel(list_frame, text="Mots de passe stockés", 
                    font=("Arial", 16, "bold"),
                    text_color="white").pack(pady=10)
        
        columns = ("Site", "Username")
        self.password_tree = ttk.Treeview(list_frame, columns=columns, 
                                        show="headings")
        
        for col in columns:
            self.password_tree.heading(col, text=col)
            self.password_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.configure(command=self.password_tree.yview)
        self.password_tree.configure(yscrollcommand=scrollbar.set)
        
        self.password_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.password_tree.bind("<Double-1>", self.on_password_double_click)

    def setup_action_and_history(self):
        right_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        action_frame = ctk.CTkFrame(right_frame, fg_color="black")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        ctk.CTkLabel(action_frame, text="Actions", 
                    font=("Arial", 16, "bold"),
                    text_color="white").pack(pady=10)
        
        actions = [
            ("Ajouter un mot de passe", self.add_password_dialog),
            ("Vérifier un mot de passe", self.check_password_dialog),
            ("Changer le mot de passe maître", self.change_master_password)
        ]
        
        for text, command in actions:
            ctk.CTkButton(action_frame, text=text,
                         fg_color="#333333",
                         hover_color="#444444",
                         text_color="white",
                         command=command).pack(pady=5, fill=tk.X)
        
        history_frame = ctk.CTkFrame(right_frame, fg_color="black")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(history_frame, text="Historique", 
                    font=("Arial", 16, "bold"),
                    text_color="white").pack(pady=10)
        
        columns = ("Date", "Action", "Détails")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                       show="headings")
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)
        scrollbar.configure(command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_lists(self):
        self.refresh_password_list()
        self.refresh_favorites_list()
        self.refresh_history_list()

    def refresh_favorites_list(self):
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
        
        favorites = self.manager.get_favorites()
        for fav in favorites:
            self.favorites_tree.insert("", tk.END, values=(fav[1], fav[2]))

    def refresh_history_list(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        history = self.manager.get_history()
        for h in history:
            date = datetime.strptime(h[2], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            self.history_tree.insert("", 0, values=(date, h[3], h[4]))

    def refresh_password_list(self):
        for item in self.password_tree.get_children():
            self.password_tree.delete(item)
        
        self.manager.cursor.execute("SELECT id, site, username FROM stored_passwords")
        for id, site, username in self.manager.cursor.fetchall():
            self.password_tree.insert("", tk.END, values=(site, username), tags=(str(id),))

    def on_password_double_click(self, event):
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
        dialog = AddPasswordDialog(self.root, self.manager)
        self.root.wait_window(dialog)
        self.refresh_lists()

    def check_password_dialog(self):
        dialog = ctk.CTkInputDialog(
            title="Vérifier un mot de passe",
            text="Entrez le mot de passe à vérifier:"
        )
        
        dialog.configure(fg_color="black")
        
        for child in dialog.winfo_children():
            if isinstance(child, ctk.CTkEntry):
                child.configure(
                    show="●",
                    height=35,
                    fg_color="#F5F5F5",
                    border_color="#CCCCCC",
                    border_width=1,
                    corner_radius=8,
                    font=("Inter", 13)
                )
            elif isinstance(child, ctk.CTkButton):
                child.configure(
                    font=("Inter", 13),
                    height=35,
                    corner_radius=8,
                    fg_color="#1E88E5",
                    hover_color="#1565C0"
                )

        password = dialog.get_input()
        if password:
            if self.manager.is_password_leaked(password):
                messagebox.showwarning(
                    "Attention",
                    "Ce mot de passe a été compromis !"
                )
            else:
                messagebox.showinfo(
                    "Sécurité",
                    "Ce mot de passe n'a pas été trouvé dans la base des fuites."
                )

    def change_master_password(self):
        dialog = ChangeMasterPasswordDialog(self.root, self.manager)
        self.root.wait_window(dialog)
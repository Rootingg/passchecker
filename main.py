import sys
from gui.main_window import PasswordManagerGUI

def main():
    try:
        app = PasswordManagerGUI()
        app.root.mainloop()
    except Exception as e:
        print(f"Erreur fatale: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
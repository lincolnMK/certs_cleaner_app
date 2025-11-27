# run.py

import tkinter as tk
from gui.main_gui import CertCleanerGUI

def main():
    root = tk.Tk()
    app = CertCleanerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
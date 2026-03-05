# Tkinter GUI wrapper
# gui/main_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from cert_cleaner import cert_cleaner, titleplan_cleaner, merger, verifier
import logging

class GuiHandler(logging.Handler):
    """Custom logging handler to redirect logs to a GUI widget."""
    def __init__(self, gui_callback, tab_name):
        super().__init__()
        self.gui_callback = gui_callback
        self.tab_name = tab_name

    def emit(self, record):
        msg = self.format(record)
        self.gui_callback(self.tab_name, msg)

class CertCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Certificate Processing App")
        self.root.geometry("800x600")
        self.log_widgets = {}
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = {}
        for stage in ["Clean Certs", "Clean Title Plans", "Merge & Move", "Verify"]:
            self.tabs[stage] = ttk.Frame(self.notebook)
            self.notebook.add(self.tabs[stage], text=stage)

        self.setup_clean_certs_tab()
        self.setup_titleplan_tab()
        self.setup_merge_tab()
        self.setup_verify_tab()

    def setup_clean_certs_tab(self):
        tab = self.tabs["Clean Certs"]
        self._add_folder_inputs(tab, "Cert Input", "Cert Output")
        self._add_dry_run(tab)
        self._add_run_button(tab, cert_cleaner.run_cert_cleaner)
        self._add_log_area(tab, "Clean Certs")

    def setup_titleplan_tab(self):
        tab = self.tabs["Clean Title Plans"]
        self._add_folder_inputs(tab, "Title Plan Input", "Title Plan Output")
        self._add_dry_run(tab)
        self._add_run_button(tab, titleplan_cleaner.main)
        self._add_log_area(tab, "Clean Title Plans")

    def setup_merge_tab(self):
        tab = self.tabs["Merge & Move"]
        self._add_folder_inputs(tab, "Cert Folder", "Title Plan Folder")
        self._add_folder_inputs(tab, "Merged Output", None)
        self._add_run_button(tab, merger.main)
        self._add_log_area(tab, "Merge & Move")

    def setup_verify_tab(self):
        tab = self.tabs["Verify"]
        self._add_folder_inputs(tab, "Merged Folder", None)
        self._add_folder_inputs(tab, "Ready for Print", "Review Folder")
        self._add_run_button(tab, verifier.main)
        self._add_log_area(tab, "Verify")

    # Reusable GUI components
    def _add_folder_inputs(self, parent, label1, label2):
        for label in [label1, label2] if label2 else [label1]:
            row = ttk.Frame(parent)
            row.pack(fill="x", pady=5)
            ttk.Label(row, text=label + ":").pack(side="left")
            entry = ttk.Entry(row, width=60)
            entry.pack(side="left", padx=5)
            ttk.Button(row, text="Browse", command=lambda e=entry: self._browse_folder(e)).pack(side="left")
            setattr(self, self._field_name(label), entry)



    def _write_log(self, tab_name, message):
        if tab_name in self.log_widgets:
            widget = self.log_widgets[tab_name]
            widget.configure(state="normal")
            widget.insert(tk.END, message + "\n")
            widget.see(tk.END)
            widget.configure(state="disabled")

    def _add_entry(self, parent, label):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=5)
        ttk.Label(row, text=label + ":").pack(side="left")
        entry = ttk.Entry(row, width=60)
        entry.pack(side="left", padx=5)
        setattr(self, self._field_name(label), entry)

    def _field_name(self, label):
        return label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "").replace("__", "_")

    def _add_dry_run(self, parent):
        self.dry_run_var = tk.BooleanVar()
        ttk.Checkbutton(parent, text="Dry Run", variable=self.dry_run_var).pack(anchor="w", padx=10)

    def _add_run_button(self, parent, callback):
        ttk.Button(parent, text="Run", command=lambda: self._run_stage(callback)).pack(pady=10)

    def _add_log_area(self, parent, tab_name):
        log_widget = scrolledtext.ScrolledText(parent, height=10, state="disabled")
        log_widget.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_widgets[tab_name] = log_widget
        self._write_log(tab_name, "Logs will appear here...\n")

    
    def _browse_folder(self, entry_widget):
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)

    def _run_stage(self, callback):
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            in_folder = self.cert_input.get()
            out_folder = self.cert_output.get()
            dry_run = self.dry_run_var.get()

            # Setup GUI logging
            gui_handler = GuiHandler(self._write_log, current_tab)
            gui_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

            # Optional: also keep terminal output
            logging.getLogger().handlers = []  # clear old handlers
            logging.getLogger().addHandler(gui_handler)
            logging.getLogger().addHandler(logging.StreamHandler())  # terminal optional
            logging.getLogger().setLevel(logging.INFO)

            # Run the actual stage
            callback(in_folder, out_folder, dry_run)

            messagebox.showinfo("Success", f"{current_tab}: Certificate processing completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e})")



if __name__ == "__main__":
    root = tk.Tk()
    app = CertCleanerGUI(root)
    root.mainloop()
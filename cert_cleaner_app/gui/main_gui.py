# Tkinter GUI wrapper
# gui/main_gui.py
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from cert_cleaner import cert_cleaner, titleplan_cleaner, merger, verifier

class CertCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Certificate Processing App")
        self.root.geometry("800x600")

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
        self._add_entry(tab, "TLMA Code")
        self._add_entry(tab, "TA Code (optional)")
        self._add_dry_run(tab)
        self._add_run_button(tab, cert_cleaner.run_cert_cleaner)
        self._add_log_area(tab)

    def setup_titleplan_tab(self):
        tab = self.tabs["Clean Title Plans"]
        self._add_folder_inputs(tab, "Title Plan Input", "Title Plan Output")
        self._add_dry_run(tab)
        self._add_run_button(tab, titleplan_cleaner.main)
        self._add_log_area(tab)

    def setup_merge_tab(self):
        tab = self.tabs["Merge & Move"]
        self._add_folder_inputs(tab, "Cert Folder", "Title Plan Folder")
        self._add_folder_inputs(tab, "Merged Output", None)
        self._add_dry_run(tab)
        self._add_run_button(tab, merger.main)
        self._add_log_area(tab)

    def setup_verify_tab(self):
        tab = self.tabs["Verify"]
        self._add_folder_inputs(tab, "Merged Folder", None)
        self._add_folder_inputs(tab, "Ready for Print", "Review Folder")
        self._add_run_button(tab, verifier.main)
        self._add_log_area(tab)

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



    def _write_log(self, message):
            if hasattr(self, "log_widget"):
                self.log_widget.configure(state="normal")
                self.log_widget.insert(tk.END, message + "\n")
                self.log_widget.see(tk.END)
                self.log_widget.configure(state="disabled")

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

    def _add_log_area(self, parent):
        self.log_widget = scrolledtext.ScrolledText(parent, height=10, state="disabled")
        self.log_widget.pack(fill="both", expand=True, padx=10, pady=10)
        self._write_log("Logs will appear here...\n")

    
    def _browse_folder(self, entry_widget):
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)

    def _run_stage(self, callback):
        try:
            current_tab = self.notebook.select()
            tab_text = self.notebook.tab(current_tab, "text")

            if tab_text == "Clean Certs":
                in_folder = self.cert_input.get()
                out_folder = self.cert_output.get()
                tlma = self.tlma_code.get()
                ta = self.ta_code_optional.get()
            elif tab_text == "Clean Title Plans":
                in_folder = self.title_plan_input.get()
                out_folder = self.title_plan_output.get()
                tlma = None
                ta = None

            elif tab_text == "Merge & Move":
                cert_folder = self.cert_folder.get()
                titleplan_folder = self.title_plan_folder.get()
                output_folder = self.merged_output.get()
                tlma = None
                ta = None

                dry_run = self.dry_run_var.get()
                callback(cert_folder, titleplan_folder, output_folder, tlma, ta, dry_run, self._write_log)
                messagebox.showinfo("Success", f"{tab_text} stage completed.")
                return

            elif tab_text == "Verify":
                cert_folder = self.merged_folder.get()         # merged PDFs
                titleplan_folder = None                         # not needed
                output_folder = self.ready_for_print.get()     # verified files go here
                tlma = None
                ta = None

                dry_run = self.dry_run_var.get()
                callback(cert_folder, titleplan_folder, output_folder, tlma, ta, dry_run, self._write_log)
                messagebox.showinfo("Success", f"{tab_text} stage completed.")
                return



            else:
                raise ValueError("Unknown tab selected.")

            dry_run = self.dry_run_var.get()

            callback(in_folder, out_folder, tlma, ta, dry_run, self._write_log)
            messagebox.showinfo("Success", f"{tab_text} stage completed.")
        except Exception as e:
            self._write_log(f"Error: {e}")
            messagebox.showerror("Error", f"Something went wrong:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CertCleanerGUI(root)
    root.mainloop()
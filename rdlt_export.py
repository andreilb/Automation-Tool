import tkinter as tk
from tkinter import filedialog, messagebox
import os
import csv
import json
from datetime import datetime

class ResultsExporter:
    """
    Utility class for exporting RDLT processing results
    in various formats (CSV, JSON, TXT)
    """
    
    def __init__(self, matrix_data=None, violations=None, activity_profile=None):
        self.matrix_data = matrix_data
        self.violations = violations
        self.activity_profile = activity_profile
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def export_to_csv(self, filepath):
        """Export matrix data to CSV format"""
        try:
            if not self.matrix_data:
                raise ValueError("No matrix data available for export")
                
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Arc", "x", "y", "l", "c", "eRU", "cv", "op", "cycle", "loop", "out", "safe"])
                
                # Write data
                for row in self.matrix_data:
                    writer.writerow(row)
                    
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to CSV: {str(e)}")
            return False
    
    def export_to_json(self, filepath):
        """Export all data to JSON format"""
        try:
            export_data = {
                "timestamp": self.timestamp,
                "matrix_data": self.matrix_data,
                "violations": self.violations,
                "activity_profile": self.activity_profile
            }
            
            with open(filepath, 'w') as jsonfile:
                json.dump(export_data, jsonfile, indent=4)
                
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to JSON: {str(e)}")
            return False
    
    def export_to_txt(self, filepath):
        """Export violations and summary data to text format"""
        try:
            with open(filepath, 'w') as txtfile:
                txtfile.write(f"RDLT Analysis Results - {self.timestamp}\n")
                txtfile.write("="*50 + "\n\n")
                
                # Write violations section
                if self.violations:
                    txtfile.write("VIOLATIONS DETECTED:\n")
                    txtfile.write("-"*30 + "\n")
                    for i, violation in enumerate(self.violations, 1):
                        txtfile.write(f"Violation #{i}: {violation}\n")
                    txtfile.write("\n")
                else:
                    txtfile.write("No violations detected.\n\n")
                
                # Write activity profile summary
                if self.activity_profile:
                    txtfile.write("ACTIVITY PROFILE:\n")
                    txtfile.write("-"*30 + "\n")
                    for key, value in self.activity_profile.items():
                        txtfile.write(f"{key}: {value}\n")
                
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to TXT: {str(e)}")
            return False
    
    def batch_export(self, directory, basename, formats=None):
        """Export data to multiple formats at once"""
        if formats is None:
            formats = ["csv", "json", "txt"]
            
        success = True
        results = {}
        
        for fmt in formats:
            filepath = os.path.join(directory, f"{basename}_{self.timestamp}.{fmt}")
            
            if fmt.lower() == "csv":
                result = self.export_to_csv(filepath)
            elif fmt.lower() == "json":
                result = self.export_to_json(filepath)
            elif fmt.lower() == "txt":
                result = self.export_to_txt(filepath)
            else:
                messagebox.showwarning("Export Warning", f"Unsupported format: {fmt}")
                result = False
                
            results[fmt] = filepath if result else None
            success = success and result
            
        return success, results
    
    def show_export_dialog(self, parent_window=None):
        """Show a dialog to select export options"""
        dialog = tk.Toplevel(parent_window)
        dialog.title("Export Results")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Format selection
        tk.Label(dialog, text="Select export formats:").pack(anchor="w", padx=20, pady=(20, 0))
        
        csv_var = tk.BooleanVar(value=True)
        json_var = tk.BooleanVar(value=True)
        txt_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(dialog, text="CSV (Matrix Data)", variable=csv_var).pack(anchor="w", padx=40)
        tk.Checkbutton(dialog, text="JSON (All Data)", variable=json_var).pack(anchor="w", padx=40)
        tk.Checkbutton(dialog, text="TXT (Violations & Summary)", variable=txt_var).pack(anchor="w", padx=40)
        
        # Filename base
        tk.Label(dialog, text="Base filename:").pack(anchor="w", padx=20, pady=(20, 0))
        filename_var = tk.StringVar(value="rdlt_results")
        tk.Entry(dialog, textvariable=filename_var, width=30).pack(anchor="w", padx=40)
        
        # Directory selection
        dir_var = tk.StringVar(value=os.path.expanduser("~"))
        tk.Label(dialog, text="Export directory:").pack(anchor="w", padx=20, pady=(20, 0))
        dir_frame = tk.Frame(dialog)
        dir_frame.pack(fill="x", padx=20)
        
        tk.Entry(dir_frame, textvariable=dir_var, width=30).pack(side="left")
        
        def browse_dir():
            directory = filedialog.askdirectory(initialdir=dir_var.get())
            if directory:
                dir_var.set(directory)
                
        tk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side="left", padx=5)
        
        # Export button
        def do_export():
            formats = []
            if csv_var.get(): formats.append("csv")
            if json_var.get(): formats.append("json")
            if txt_var.get(): formats.append("txt")
            
            if not formats:
                messagebox.showwarning("Export Warning", "Please select at least one export format.")
                return
                
            success, results = self.batch_export(
                dir_var.get(), 
                filename_var.get(),
                formats
            )
            
            if success:
                message = "Export completed successfully:\n\n"
                for fmt, path in results.items():
                    if path:
                        message += f"{fmt.upper()}: {os.path.basename(path)}\n"
                messagebox.showinfo("Export Complete", message)
                dialog.destroy()
            else:
                failed = [fmt for fmt, path in results.items() if path is None]
                messagebox.showerror("Export Error", f"Failed to export: {', '.join(failed)}")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right")
        tk.Button(button_frame, text="Export", command=do_export).pack(side="right", padx=10)
        
        # Center the dialog relative to parent
        if parent_window:
            dialog.transient(parent_window)
            dialog.update_idletasks()
            parent_x = parent_window.winfo_rootx()
            parent_y = parent_window.winfo_rooty()
            parent_width = parent_window.winfo_width()
            parent_height = parent_window.winfo_height()
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            dialog.geometry(f"+{x}+{y}")
        
        dialog.grab_set()  # Make dialog modal
        return dialog
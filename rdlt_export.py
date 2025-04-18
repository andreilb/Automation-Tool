"""
RDLT Export Module

This module provides functionality to export RDLT processing results 
to text files. It includes a GUI dialog for file export configuration and handles the 
formatting of analysis results in a structured text format.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

class ResultsExporter:
    """
    Utility class for exporting RDLT processing results in text format
    that matches the GUI output.
    
    This class takes various analysis data components and formats them into
    a comprehensive text report that can be saved to disk. It also provides
    a GUI dialog for configuring the export options.
    
    Attributes:
        matrix_data (list): Matrix evaluation data showing RDLT properties
        violations (list): List of detected violations in the RDLT
        activity_profile (dict): Activity profiles for arcs in the RDLT
        input_data (dict): Original input RDLT data
        processed_data (dict): Processed RDLT data after analysis
        contraction_paths (list): Path contraction data for violations
        timestamp (str): Timestamp for the export filename
        default_export_dir (str): Default directory for exports
    """
    
    def __init__(self, matrix_data=None, violations=None, activity_profile=None, 
                 input_data=None, processed_data=None, contraction_paths=None):
        """
        Initialize the ResultsExporter with RDLT analysis data.
        
        Args:
            matrix_data (list, optional): Matrix evaluation results. Defaults to None.
            violations (list, optional): List of detected violations. Defaults to None.
            activity_profile (dict, optional): Activity profiles for arcs. Defaults to None.
            input_data (dict, optional): Original input RDLT data. Defaults to None.
            processed_data (dict, optional): Processed RDLT data. Defaults to None.
            contraction_paths (list, optional): Path contraction data. Defaults to None.
        """
        self.matrix_data = matrix_data
        self.violations = violations
        self.activity_profile = activity_profile
        self.input_data = input_data
        self.processed_data = processed_data
        self.contraction_paths = contraction_paths
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set up default export directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.default_export_dir = os.path.join(script_dir, "exports")
        
        # Create exports directory if it doesn't exist
        if not os.path.exists(self.default_export_dir):
            os.makedirs(self.default_export_dir)
    
    def export_to_txt(self, filepath):
        """
        Export processing results to a text format matching GUI output.
        
        This method writes all available analysis data to a structured text file,
        including input data, processing information, matrix evaluation results,
        violations, contraction paths, and activity profiles.
        
        Args:
            filepath (str): The full path where the text file will be saved
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            with open(filepath, 'w') as txtfile:
                # Extract filename from the input data if available
                filename = ""
                if self.input_data and 'filename' in self.input_data:
                    input_path = self.input_data['filename']
                    filename = f"_{os.path.splitext(os.path.basename(input_path))[0]}"
                
                # Write header with timestamp and filename
                txtfile.write(f"RDLT Analysis Results - {self.timestamp}{filename}\n")
                txtfile.write("="*60 + "\n\n")
                
                # Write input data section
                if self.input_data:
                    txtfile.write("Input RDLT: \n")
                    txtfile.write("-"*20 + "\n")
                    txtfile.write(f"Arcs List ({len(self.input_data['Arcs_list'])}):  {self.input_data['Arcs_list']}\n")
                    txtfile.write(f"Vertices List ({len(self.input_data['Vertices_list'])}):  {self.input_data['Vertices_list']}\n")
                    txtfile.write(f"C-attribute List ({len(self.input_data['C_attribute_list'])}):  {self.input_data['C_attribute_list']}\n")
                    txtfile.write(f"L-attribute List ({len(self.input_data['L_attribute_list'])}):  {self.input_data['L_attribute_list']}\n")
                    txtfile.write("-"*20 + "\n")
                    
                    if self.input_data.get('Centers_list'):
                        txtfile.write("RBS components:\n")
                        txtfile.write("-"*20 + "\n")
                        txtfile.write(f"Centers ({len(self.input_data['Centers_list'])}):  {self.input_data['Centers_list']}\n")
                        txtfile.write(f"In ({len(self.input_data['In_list'])}):  {self.input_data['In_list']}\n")
                        txtfile.write(f"Out ({len(self.input_data['Out_list'])}):  {self.input_data['Out_list']}\n")
                    
                    txtfile.write("="*60 + "\n\n")
                
                # Write processing information
                if self.processed_data:
                    if self.processed_data.get('R2'):
                        txtfile.write("Processing RBS components...\n\n")
                        txtfile.write("="*60 + "\n\n")
                        txtfile.write("All joins in R2 are OR-joins. Processing R2 separately and using only R1 for matrix evaluation.\n\n")
                        txtfile.write("="*60 + "\n")
                        txtfile.write("R2:\n")
                        txtfile.write("-"*20 + "\n")
                        txtfile.write(f"Arcs List ({len(self.processed_data['R2']['Arcs_list'])}): {self.processed_data['R2']['Arcs_list']}\n")
                        txtfile.write(f"Vertices List ({len(self.processed_data['R2']['Vertices_list'])}): {self.processed_data['R2']['Vertices_list']}\n")
                        txtfile.write(f"C-attribute List ({len(self.processed_data['R2']['C_attribute_list'])}): {self.processed_data['R2']['C_attribute_list']}\n")
                        txtfile.write(f"L-attribute List ({len(self.processed_data['R2']['L_attribute_list'])}): {self.processed_data['R2']['L_attribute_list']}\n")
                        txtfile.write(f"eRU List ({len(self.processed_data['R2']['eRU_list'])}): {self.processed_data['R2']['eRU_list']}\n")
                        txtfile.write("="*60 + "\n")
                    
                    txtfile.write("R1:\n")
                    txtfile.write("-"*20 + "\n")
                    txtfile.write(f"Arcs List ({len(self.processed_data['R1']['Arcs_list'])}): {self.processed_data['R1']['Arcs_list']}\n")
                    txtfile.write(f"C-attribute List ({len(self.processed_data['R1']['C_attribute_list'])}): {self.processed_data['R1']['C_attribute_list']}\n")
                    txtfile.write(f"L-attribute List ({len(self.processed_data['R1']['L_attribute_list'])}): {self.processed_data['R1']['L_attribute_list']}\n")
                    txtfile.write(f"eRU List ({len(self.processed_data['R1']['eRU_list'])}): {self.processed_data['R1']['eRU_list']}\n")
                    txtfile.write("="*60 + "\n\n")
                    
                    txtfile.write("RDLT Structure:\n")
                    for row in self.processed_data.get('RDLT_structure', []):
                        txtfile.write(f"{row}\n")
                    txtfile.write("="*60 + "\n\n")
                
                # Write evaluation results
                l_safe = all(row[-1] == "True" for row in self.matrix_data) if self.matrix_data else False
                txtfile.write("JOIN-Safe: " + ("Satisfied.\n" if l_safe else "Not Satisfied.\n"))
                txtfile.write("Loop-Safe NCAs: Satisfied.\n")
                txtfile.write("Safe CAs: Satisfied.\n\n")
                
                txtfile.write("\nMatrix Evaluation Result: RDLT is " + 
                            ("L-Safe." if l_safe else "NOT L-Safe.") + "\n\n")
                txtfile.write("="*60 + "\n")
                
                # Write matrix data
                if self.matrix_data:
                    txtfile.write("Generated Matrix:\n\n")
                    for row in self.matrix_data:
                        txtfile.write(f"{row}\n")
                    txtfile.write("="*60 + "\n\n")
                
                # Write violations
                if self.violations:
                    for violation in self.violations:
                        txtfile.write(f"{violation['type']} Violation:\n")
                        txtfile.write(f"  r-id: {violation.get('r-id', 'N/A')}\n")
                        txtfile.write(f"  arc: {violation.get('arc', 'N/A')}\n")
                        txtfile.write(f"  Violation: {violation.get('violation', 'N/A')}\n\n")
                    
                    txtfile.write(f"Found {len(self.violations)} violations in total.\n")
                    txtfile.write("="*60 + "\n\n")
                
                # Write contraction paths
                if self.contraction_paths:
                    txtfile.write("--- Contraction Paths for Violations ---\n\n")
                    for path_data in self.contraction_paths:
                        txtfile.write(f"Violating Arc: {path_data.get('arc', 'N/A')}\n")
                        txtfile.write("Contracted Path:\n")
                        txtfile.write(f"{path_data.get('path', [])}\n\n")
                        txtfile.write("Successful Contractions:\n")
                        txtfile.write(f"{path_data.get('successful', [])}\n\n")
                    txtfile.write("="*60 + "\n\n")
                
                # Write activity profiles
                if self.activity_profile:
                    for arc, profile in self.activity_profile.items():
                        txtfile.write(f"--- Activity Profile for {arc} ---\n")
                        for step, activities in profile.get('S', {}).items():
                            txtfile.write(f"S({step}) = {list(activities)}\n")
                        
                        txtfile.write("\nS = {")
                        txtfile.write(", ".join([f"S({step})" for step in profile.get('S', {}).keys()]))
                        txtfile.write("}\n\n")
                        
                        if profile.get('sink_timestep'):
                            txtfile.write(f"Sink was reached at timestep {profile['sink_timestep']}\n\n")
                        else:
                            txtfile.write("Sink was not reached\n\n")
                    txtfile.write("="*60 + "\n\n")
                
                # Write final summary
                txtfile.write("\n=========== SUMMARY ===========\n\n")
                txtfile.write(f"RDLT is {'L-safe and CLASSICAL SOUND.' if l_safe else 'not L-safe.'}\n")
                
            return True
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to TXT: {str(e)}")
            return False
    
    def show_export_dialog(self, parent_window=None):
        """
        Show a dialog to export results to text file.
        
        Creates and displays a tkinter dialog allowing the user to configure
        export options such as filename and directory. The dialog is modal
        and returns when the export is complete or canceled.
        
        Args:
            parent_window (tk.Tk or tk.Toplevel, optional): Parent window for the dialog.
                If provided, the dialog will be positioned relative to this window.
                
        Returns:
            tk.Toplevel: The dialog window instance
        """
        dialog = tk.Toplevel(parent_window)
        dialog.title("Export Results")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Filename base
        tk.Label(dialog, text=" Base Filename:").pack(anchor="w", padx=20, pady=(20, 0))
        filename_var = tk.StringVar(value="rdlt_export")
        tk.Entry(dialog, textvariable=filename_var, width=30).pack(anchor="w", padx=20)
        
        # Directory selection - use default export directory
        dir_var = tk.StringVar(value=self.default_export_dir)
        tk.Label(dialog, text="Export directory:").pack(anchor="w", padx=20, pady=(10, 0))
        dir_frame = tk.Frame(dialog)
        dir_frame.pack(fill="x", padx=20)
        
        tk.Entry(dir_frame, textvariable=dir_var, width=30).pack(side="left")
        
        def browse_dir():
            """Open file dialog to select export directory"""
            directory = filedialog.askdirectory(initialdir=dir_var.get())
            if directory:
                dir_var.set(directory)
                
        tk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side="left", padx=5)
        
        # Export button
        def do_export():
            """Export the results using configured options"""
            filepath = os.path.join(dir_var.get(), f"{filename_var.get()}_{self.timestamp}.txt")
            success = self.export_to_txt(filepath)
            
            if success:
                messagebox.showinfo("Export Complete", 
                                  f"Results exported successfully to:\n\n{filepath}")
                dialog.destroy()
            else:
                messagebox.showerror("Export Error", "Failed to export results")
        
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
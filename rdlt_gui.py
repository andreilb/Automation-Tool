import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import os
import sys
import io
from contextlib import redirect_stdout
from rdlt_export import ResultsExporter

# Import your existing modules
# Assuming these imports are in the same directory as this script
from input_rdlt import Input_RDLT
from cycle import Cycle
from create_r2 import ProcessR2
from create_r1 import ProcessR1
from joins import TestJoins
from matrix import Matrix
from mod_extract import ModifiedActivityExtraction
from contraction import ContractionPath

class RDLTProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RDLT Processor")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Store the selected file path
        self.selected_file_path = ""
        
        # Create main frame
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File selection section
        file_frame = tk.LabelFrame(main_frame, text="Input File Selection", bg="#f0f0f0")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=70)
        self.file_path_entry.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)
        
        browse_button = tk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Sample files section
        samples_frame = tk.LabelFrame(main_frame, text="Quick Select Sample Files", bg="#f0f0f0")
        samples_frame.pack(fill=tk.X,padx=10, pady=5)
        
        # Sample files buttons
        samples = [
            "sample_rdlt.txt", 
            "sample_lsafe.txt", 
            "sample_rbs.txt", 
            "sample_relaxed.txt", 
            "sample_js_tc1.txt",
            "sample_js_tc2.txt",
            "sample_js_tc3.txt",
            "sample_js_tc4.txt",
            "sample_js_tc5.txt",
            "sample_deadlock.txt",
            "sample_multi_CA.txt",
            "sample_multi_center.txt"
             
        ]
        
        buttons_frame = tk.Frame(samples_frame, bg="#f0f0f0")
        buttons_frame.pack(fill=tk.X)
        
        for i, sample in enumerate(samples):
            # Remove file extension from display text
            display_text = os.path.splitext(sample)[0]
            
            # Create button with display text but pass full filename to the command
            button = tk.Button(buttons_frame, text=display_text, 
                            command=lambda s=sample: self.select_sample(s))
            row = i // 4
            col = i % 4
            button.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            buttons_frame.columnconfigure(col, weight=1)
        
        # Process button
        process_button = tk.Button(main_frame, text="Process RDLT", command=self.process_rdlt, 
                                  bg="#7393B3", fg="white", font=("Arial", 12, "bold"),
                                  padx=5)
        process_button.pack(pady=5)
        
        # Output section
        output_frame = tk.LabelFrame(main_frame, text="Processing Results", bg="#f0f0f0", padx=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(output_frame, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create output text area with scrollbar
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=70, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Access the vertical scrollbar
        scrollbar = self.output_text.vbar

        # Configure the scrollbar's width and other properties
        scrollbar.configure(width=20)  # Change the width of the scrollbar

        # Create a frame to hold the Clear and Export buttons
        button_frame = tk.Frame(output_frame, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=5)

        # Clear button (in column 0)
        clear_button = tk.Button(button_frame, text="Clear Output", command=self.clear_output)
        clear_button.grid(row=0, column=0, padx=5)

        # Export button (in column 1)
        export_button = tk.Button(button_frame, text="Export Results", command=self.export_results)
        export_button.grid(row=0, column=1, padx=30)

        # Center the buttons in the frame
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Add this to rdlt_gui.py in the __init__ method
        help_button = tk.Button(main_frame, text="Help", command=self.show_help)
        help_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def browse_file(self):
        """Open file dialog to select an RDLT input file"""
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.file_path_var.set(filepath)
            self.selected_file_path = filepath
    
    def select_sample(self, sample_name):
        """Select one of the predefined sample files"""
        # Determine the directory where sample files might be located
        # Assuming they're in the same directory as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sample_dir = os.path.join(script_dir, "rdlt_text")
        
        # If the rdlt_text directory doesn't exist, create it
        if not os.path.exists(sample_dir):
            os.makedirs(sample_dir)
            self.output_text.insert(tk.END, f"Created directory for sample files: {sample_dir}\n")
            self.output_text.insert(tk.END, f"Please place your sample files in this directory.\n")
            return
        
        filepath = os.path.join(sample_dir, sample_name)
        self.file_path_var.set(filepath)
        self.selected_file_path = filepath
        
        # Check if the file exists
        if not os.path.exists(filepath):
            self.output_text.insert(tk.END, f"Sample file not found: {filepath}\n")
            self.output_text.insert(tk.END, f"Please place your sample files in the rdlt_text directory.\n")
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)

    def show_help(self):
        """Display the help dialog"""
        try:
            # Import the help dialog module
            from help_dialog import HelpDialog
            # Create the help dialog
            help_instance = HelpDialog(self.root)
        except Exception as e:
            self.output_text.insert(tk.END, f"Error displaying help: {str(e)}\n")
            import traceback
            self.output_text.insert(tk.END, traceback.format_exc())
    
    def process_rdlt(self):
        """Process the selected RDLT file"""
        filepath = self.file_path_var.get()
        
        if not filepath:
            self.output_text.insert(tk.END, "Error: No file selected. Please select a file first.\n")
            return
        
        if not os.path.exists(filepath):
            self.output_text.insert(tk.END, f"Error: File not found at {filepath}\n")
            return
        
        self.output_text.delete(1.0, tk.END)
        # self.output_text.insert(tk.END, f"Processing file: {filepath}\n\n")
        self.status_var.set("Processing...")
        self.root.update_idletasks()
        
        # Redirect stdout to capture print statements
        captured_output = io.StringIO()
        
        try:
            with redirect_stdout(captured_output):
                # Here we'll call the main processing logic from your original script
                self.run_rdlt_processing(filepath)
            
            # Get the captured output and display it
            output = captured_output.getvalue()
            self.output_text.insert(tk.END, output)
            self.status_var.set("Processing completed")
        
        except Exception as e:
            self.output_text.insert(tk.END, f"Error during processing: {str(e)}\n")
            import traceback
            self.output_text.insert(tk.END, traceback.format_exc())
            self.status_var.set("Error occurred")

    def export_results(self):
        """Export the processing results using the ResultsExporter class"""
        try:
            # Check if the matrix data is available
            if not hasattr(self, 'matrix_instance'):
                messagebox.showwarning("Export Warning", "No results to export. Please process a file first.")
                return
            
            # Get the matrix data, violations, and activity profile
            matrix_data = self.matrix_instance.get_matrix_data()  # Assuming get_matrix_data() returns the matrix data
            violations = self.matrix_instance.get_violations()  # Assuming get_violations() returns the violations
            activity_profile = self.activity_profile if hasattr(self, 'activity_profile') else None  # Assuming activity_profile is stored as an attribute
            
            # Create an instance of ResultsExporter
            exporter = ResultsExporter(matrix_data, violations, activity_profile)
            
            # Show the export dialog
            exporter.show_export_dialog(self.root)
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def run_rdlt_processing(self, input_filepath):
        """Run the RDLT processing logic from the original script"""
        # Initialize activity_profile to None
        self.activity_profile = None

        # Initialize the RDLT input processor
        input_instance = Input_RDLT(input_filepath)
        input_instance.evaluate()
        # Retrieve extracted RDLT components
        Centers_list = input_instance.Centers_list
        In_list = input_instance.In_list
        Out_list = input_instance.Out_list
        Arcs_list = input_instance.Arcs_List
        L_attribute_list = input_instance.L_attribute_list
        C_attribute_list = input_instance.C_attribute_list

        # Get R1 from input_rdlt
        initial_R1 = input_instance.getR('R1')
        
        # Process R2 (RBS) if centers exist
        if Centers_list:
            print("\nProcessing RBS components...\n")
            print('=' * 60)
            initial_R2 = input_instance.getRs()  # Get all regions except 'R1'
            
            # Use TestJoins to check if all joins in R2 are OR-joins
            flattened_R2 = []
            for r2_dict in initial_R2:
                for r2_key, r2_value in r2_dict.items():
                    flattened_R2.extend(r2_value)
            
            check_result = TestJoins.checkSimilarTargetVertexAndUpdate(initial_R1, flattened_R2)
            
            if check_result == initial_R1:
                # All joins are OR-joins, process R2 separately and use only R1 as input
                print("All joins in R2 are OR-joins. Processing R2 separately and using only R1 for matrix evaluation.\n")
                
                # Process R2
                processed_R2 = ProcessR2(initial_R2)
                
                # Process R1 with abstract arcs (using processed R2)
                processed_R1 = ProcessR1(
                    Arcs_list,
                    initial_R1,
                    Centers_list,
                    In_list,
                    Out_list,
                    processed_R2
                )

                cycle_R2 = Cycle(processed_R2)
                C_R2 = cycle_R2.evaluate_cycle()
                cycle_list_R2 = cycle_R2.get_cycle_list()
                
                # Cycle detection for processed R1
                cycle_R1 = Cycle(processed_R1)
                C_R1 = cycle_R1.evaluate_cycle()
                cycle_list_R1 = cycle_R1.get_cycle_list()
                
                # Store cycles for later use
                self.cycle_list = cycle_list_R1
                self.current_R = processed_R1  # Store processed R1 for later use
                
                # Convert data from dict to matrix (R1 only)
                self.matrix_instance = Matrix(processed_R1, self.cycle_list)
                # Perform matrix evaluation to determine L-Safeness
                l_safe, matrix = self.matrix_instance.evaluate()
                print(f"\nMatrix Evaluation Result: {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
                print('=' * 60)
                print("Generated Matrix:\n")
                self.matrix_instance.print_matrix()
                print('=' * 60)
                
            else:
                # Not all joins are OR-joins, process both R1 and R2 together
                print("R2 contains non-OR joins. Processing both R1 and R2 together.\n")
                
                # Process R2 first
                processed_R2 = ProcessR2(initial_R2)
                
                # Process R1 with abstract arcs (using processed R2)
                processed_R1 = ProcessR1(
                    Arcs_list,
                    initial_R1,
                    Centers_list,
                    In_list,
                    Out_list,
                    processed_R2
                )
                
                # Combine processed R1 and R2 into a single list
                combined_R = processed_R1 + processed_R2

                # Create cycle instance and detect cycles
                cycle_combined = Cycle(combined_R)
                C_combined = cycle_combined.evaluate_cycle()

                # Update eRU values in combined_R based on cycle participation
                combined_R = cycle_combined.update_eRU_values()

                # Get the updated cycle list
                self.cycle_list = cycle_combined.get_cycle_list()
                self.current_R = combined_R  # Store combined R for later use
                
                # Print the combined list for debugging
                print("Processed R1 and R2:")
                print('-' * 20)
                arcs_list_combined = [r['arc'] for r in combined_R if isinstance(r, dict) and 'arc' in r]
                vertices_list_combined = sorted(set([v for arc in arcs_list_combined for v in arc.split(', ')]))
                c_attribute_list_combined = [r.get('c-attribute', '') for r in combined_R if isinstance(r, dict)]
                l_attribute_list_combined = [r.get('l-attribute', '') for r in combined_R if isinstance(r, dict)]
                eRU_list_combined = [str(r.get('eRU', '0')) for r in combined_R]
                
                print(f"Arcs List ({len(arcs_list_combined)}): {arcs_list_combined}")
                print(f"Vertices List ({len(vertices_list_combined)}): {vertices_list_combined}")
                print(f"C-attribute List ({len(c_attribute_list_combined)}): {c_attribute_list_combined}")
                print(f"L-attribute List ({len(l_attribute_list_combined)}): {l_attribute_list_combined}")
                print(f"eRU List ({len(eRU_list_combined)}): {eRU_list_combined}")
                print('=' * 60)
                
                # Convert data from dict to matrix (combined processed R1 and R2)
                self.matrix_instance = Matrix(combined_R, self.cycle_list, In_list, Out_list)
                # Perform matrix evaluation to determine L-Safeness
                l_safe, matrix = self.matrix_instance.evaluate()
                print(f"\nMatrix Evaluation Result: {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
                print('=' * 60)
                print("Generated Matrix:\n")
                self.matrix_instance.print_matrix()
                print('=' * 60)
        else:
            # No centers found, process R1 directly
            print("\nNo centers found. Processing R1 directly...\n")
            print('=' * 60)
            
            # Process R1 with no abstract arcs
            print("\nProcessing R1 components...\n")
            print('=' * 60)
            R1 = initial_R1
            
            # Detect cycles in R1
            cycle_R1 = Cycle(R1)
            C_R1 = cycle_R1.evaluate_cycle()
            self.cycle_list = cycle_R1.get_cycle_list()
            self.current_R = R1  # Store R1 for later use
            
            # Convert data from dict to matrix
            self.matrix_instance = Matrix(R1, self.cycle_list)
            # Perform matrix evaluation to determine L-Safeness
            l_safe, matrix = self.matrix_instance.evaluate()
            print(f"\nMatrix Evaluation Result: {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
            print('=' * 60)
            print("Generated Matrix:\n")
            self.matrix_instance.print_matrix()
            print('=' * 60)
        
        # Print final verification result
        if l_safe == True:
            print("\n=========== SUMMARY ===========")
            print("\n RDLT is L-safe and CLASSICAL SOUND.\n")
        else:
            violations = self.matrix_instance.get_violations()
            print('=' * 60)

            # Initialize Contraction Path with current R (could be R1 or combined_R)
            contraction_path = ContractionPath(self.current_R, violations)

            # Call the contraction process and store the results
            path, failed = contraction_path.get_contraction_paths()
            # Print the final contraction paths
            # print(f"\nContraction path: {path}\n")
            # print(f"Failed contractions: {failed}\n")

            # contraction_path.print_contraction_paths()

            # Run Modified Activity Extraction with the stored cycle list
            modified_activity = ModifiedActivityExtraction(
                self.current_R,  # Use the stored R (R1 or combined_R)
                violations, 
                path, 
                self.cycle_list  # Using the stored cycle list
            )
            
            self.activity_profile = modified_activity.extract_activity_profiles()
            # Print all activity profiles
            modified_activity.print_activity_profiles()

            print("\n=========== SUMMARY ===========")
            print("\n RDLT is not L-safe.\n")


def main():
    """Main entry point for the application"""
    root = tk.Tk()
    app = RDLTProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
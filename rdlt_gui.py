"""
Main GUI Script for RDLT Processing and Classical Soundness Verification
-----------------------------------------------------------------------

This script provides a graphical user interface (GUI) for the Robustness Diagram with Loop and Time Controls (RDLT) processing and verification system. 
It enables users to select and load RDLT input files, automatically process them through the underlying verification engine, view detailed results in a 
formatted output area, and export analysis outcomes. The GUI seamlessly integrates all core RDLT evaluation functionality while offering an intuitive 
interface for user interaction.

The GUI enables:
    - File selection via browse dialog or quick-select sample files
    - Automatic processing of RDLT data to determine L-Safeness and Classical Soundness
    - Display of processing results in a scrollable text area
    - Export functionality for saving results
    - Help documentation access

The system automates the full evaluation of an RDLT to determine both L-Safeness and Classical Soundness. This includes:
    - Extracting and interpreting RDLT structure from text-based input files.
    - Processing R2 (Reset-Bound Subsystem) when centers are present.
    - Creating and analyzing R1 with R2 regions represented as abstract arcs.
    - Performing cycle detection for both R1 and R2 components.
    - Evaluating OR-JOIN conditions within the RBS.
    - Executing matrix operations to verify L-Safeness.
    - Generating contraction paths and activity profiles in case of violations for further diagnosis.

Dependencies:
    - tkinter: Provides the GUI framework and widgets
    - input_rdlt: Handles RDLT input processing from text input to dict
    - cycle: Contains the Cycle class for cycle detection
    - abstract: AbstractArc class to create abstract arcs for R1 (EVSA)
    - create_r2: ProcessR2 function for processing EVSA for RBS (R2) components
    - create_r1: ProcessR1 function for processing EVSA for non-RBS (R1) components
    - joins: TestJoins class to determine types of JOINs within the RBS (R2)
    - matrix: Matrix class to convert RDLT data (dict) to matrix representation
    - mod_extract: ModifiedActivityExtraction class generates activity profiles for violating component(s)
    - contraction: ContractionPath class to generate contraction paths for violating components
    - utils: Provides utility functions for graph processing, path finding, and vertex identification
    - rdlt_export: ResultsExporter class for exporting results to text file
    - help_dialog: HelpDialog class for displaying help information

Author: Andrei Luz B. Asoy
Code Version 3.2 (as of 04-15-25)
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import os
import io
from contextlib import redirect_stdout
from rdlt_export import ResultsExporter

# Import RDLT processing modules
from input_rdlt import Input_RDLT
from cycle import Cycle
from create_r2 import ProcessR2
from create_r1 import ProcessR1
from joins import TestJoins
from matrix import Matrix
from mod_extract import ModifiedActivityExtraction
from contraction import ContractionPath

class RDLTProcessorGUI:
    """
    Main GUI class that orchestrates the RDLT processing interface.
    
    This class creates the GUI elements, handles user interactions,
    and integrates with the RDLT processing engine to analyze inputs
    and display results.
    """
    def __init__(self, root):
        """
        Initialize the GUI components and layout.
        
        Args:
            root: The tkinter root window object
        """
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
        
        browse_button = tk.Button(file_frame, text="Browse", command=self.browse_file)
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

        # Help button
        help_button = tk.Button(main_frame, text="Help", command=self.show_help)
        help_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def browse_file(self):
        """
        Open file dialog to select an RDLT input file.
        
        Updates the file path entry when a file is selected.
        """
        filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.file_path_var.set(filepath)
            self.selected_file_path = filepath
    
    def select_sample(self, sample_name):
        """
        Select one of the predefined sample files.
        
        Checks if the rdlt_text directory exists and contains the
        requested sample file. Creates the directory if needed.
        
        Args:
            sample_name: Name of the sample file to select
        """
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
        """
        Clear the output text area to prepare for new results.
        """
        self.output_text.config(state="normal")  # Enable clearing
        self.output_text.delete(1.0, tk.END)

    def show_help(self):
        """
        Display the help dialog with user instructions.
        
        Imports and initializes the HelpDialog class to show guidance.
        """
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
        """
        Process the selected RDLT file and display results.
        
        Validates file selection, clears previous output if needed,
        redirects stdout to capture console output, and runs the
        RDLT processing logic.
        """
        # Check if output needs to be cleared first
        if self.output_text.get(1.0, tk.END).strip():
            if not messagebox.askyesno(
                "Clear Output Required",
                "You need to clear the previous results before processing a new file.\n\n"
                "Would you like to clear the output now?",
                parent=self.root
            ):
                return  # User chose not to clear
            self.clear_output()

        filepath = self.file_path_var.get()
        
        if not filepath:
            self.output_text.insert(tk.END, "Error: No file selected. Please select a file first.\n")
            self.output_text.config(state="disabled")  # Disable after error message
            return
        
        if not os.path.exists(filepath):
            self.output_text.insert(tk.END, f"Error: File not found at {filepath}\n")
            self.output_text.config(state="disabled")  # Disable after error message
            return
        
        self.output_text.delete(1.0, tk.END)  # Clear existing content
        self.status_var.set("Processing...")
        self.root.update_idletasks()
        
        captured_output = io.StringIO()
        try:
            with redirect_stdout(captured_output):
                self.run_rdlt_processing(filepath)
            
            # Insert captured output
            output = captured_output.getvalue()
            self.output_text.insert(tk.END, output)
            
            # DISABLE HERE (after all text is inserted)
            self.output_text.config(state="disabled")
            self.status_var.set("Processing completed")
        
        except Exception as e:
            self.output_text.insert(tk.END, f"Error during processing: {str(e)}\n")
            import traceback
            self.output_text.insert(tk.END, traceback.format_exc())
            self.output_text.config(state="disabled")  # Disable after error
            self.status_var.set("Error occurred")

    def export_results(self):
        """
        Export the processing results to a file format of user's choice.
        
        Uses the ResultsExporter class to collect and format result data,
        then presents export options to the user.
        """
        try:
            # Check if the matrix data is available
            if not hasattr(self, 'matrix_instance'):
                messagebox.showwarning("Export Warning", "No results to export. Please process a file first.")
                return
            
            # Get the basic data needed for export
            matrix_data = self.matrix_instance.get_matrix_data()
            violations = self.matrix_instance.get_violations()
            activity_profile = self.activity_profile if hasattr(self, 'activity_profile') else None
            
            # Prepare input data for export
            input_data = {
                'filename': self.selected_file_path,
                'Arcs_list': [f"({arc.split(', ')[0]}, {arc.split(', ')[1]})" 
                            for arc in self.input_instance.Arcs_List],
                'Vertices_list': sorted(set([v for arc in self.input_instance.Arcs_List 
                                        for v in arc.split(', ')])),
                'C_attribute_list': self.input_instance.C_attribute_list,
                'L_attribute_list': self.input_instance.L_attribute_list,
                'Centers_list': self.input_instance.Centers_list,
                'In_list': [f"({in_arc.split(', ')[0]}, {in_arc.split(', ')[1]})" 
                            for in_arc in self.input_instance.In_list] if hasattr(self.input_instance, 'In_list') else [],
                'Out_list': [f"({out_arc.split(', ')[0]}, {out_arc.split(', ')[1]})" 
                            for out_arc in self.input_instance.Out_list] if hasattr(self.input_instance, 'Out_list') else []
            }
            
            # Prepare processed data for export
            processed_data = {
                'R1': {
                    'Arcs_list': [f"({r['arc'].split(', ')[0]}, {r['arc'].split(', ')[1]})" 
                                for r in self.current_R if isinstance(r, dict) and 'arc' in r],
                    'C_attribute_list': [r.get('c-attribute', '') 
                                    for r in self.current_R if isinstance(r, dict)],
                    'L_attribute_list': [r.get('l-attribute', '') 
                                    for r in self.current_R if isinstance(r, dict)],
                    'eRU_list': [str(r.get('eRU', '0')) 
                                for r in self.current_R if isinstance(r, dict)]
                },
                'RDLT_structure': [str(row) for row in matrix_data]  # Using matrix data as structure
            }
            
            # Prepare contraction paths data
            contraction_paths = []
            if hasattr(self, 'contraction_path'):
                path, _ = self.contraction_path.get_contraction_paths()
                for violation in violations:
                    contraction_paths.append({
                        'arc': violation.get('arc', 'N/A'),
                        'path': path,
                        'successful': path  # Assuming all paths are successful for simplicity
                    })
            
            # Create an instance of ResultsExporter with all collected data
            exporter = ResultsExporter(
                matrix_data=matrix_data,
                violations=violations,
                activity_profile=activity_profile,
                input_data=input_data,
                processed_data=processed_data,
                contraction_paths=contraction_paths
            )
            
            # Show the export dialog
            exporter.show_export_dialog(self.root)
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export results: {str(e)}")
    
    def run_rdlt_processing(self, input_filepath):
        """
        Execute the RDLT processing logic from the original script.
        
        This is the core processing function that integrates with the
        underlying RDLT verification engine to analyze the selected file.
        It follows the same logic as the original script but adapted for GUI use.
        
        Args:
            input_filepath: Path to the RDLT input file to process
        """
        # Initialize activity_profile to None
        self.activity_profile = None

        # Initialize the RDLT input processor and store it as an attribute
        self.input_instance = Input_RDLT(input_filepath)
        self.input_instance.evaluate()
        
        # Retrieve extracted RDLT components
        Centers_list = self.input_instance.Centers_list
        In_list = self.input_instance.In_list
        Out_list = self.input_instance.Out_list
        Arcs_list = self.input_instance.Arcs_List
        L_attribute_list = self.input_instance.L_attribute_list
        C_attribute_list = self.input_instance.C_attribute_list

        # Get R1 from input_rdlt
        initial_R1 = self.input_instance.getR('R1')
        
        # Process R2 (RBS) if centers exist
        if Centers_list:
            print("\nProcessing RBS components...\n")
            print('=' * 60)
            initial_R2 = self.input_instance.getRs()  # Get all regions except 'R1'
            
            # Use TestJoins to check if all joins in R2 are OR-joins
            flattened_R2 = []
            for r2_dict in initial_R2:
                for r2_key, r2_value in r2_dict.items():
                    flattened_R2.extend(r2_value)
            
            check_result = TestJoins.checkSimilarTargetVertexAndUpdate(initial_R1, flattened_R2)
            
            if check_result == initial_R1:
                # All joins are OR-joins, process R2 separately and use only R1 as input
                print("\nAll joins in R2 are OR-joins. Using only R1 for matrix evaluation.\n")
                print('=' * 60)
                
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
                print("\nR2 contains non-OR joins. Processing both R1 and R2 together.\n")
                print('=' * 60)
                
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

                def convert_arc_format(arc):
                    return f"({arc.split(', ')[0]}, {arc.split(', ')[1]})"

                def convert_arc_list_format(arc_list):
                    return [convert_arc_format(arc) for arc in arc_list]

                # Print the combined list for debugging
                print("Processed R1 and R2:")
                print('-' * 20)
                arcs_list_combined = [r['arc'] for r in combined_R if isinstance(r, dict) and 'arc' in r]
                vertices_list_combined = sorted(set([v for arc in arcs_list_combined for v in arc.split(', ')]))
                c_attribute_list_combined = [r.get('c-attribute', '') for r in combined_R if isinstance(r, dict)]
                l_attribute_list_combined = [r.get('l-attribute', '') for r in combined_R if isinstance(r, dict)]
                eRU_list_combined = [str(r.get('eRU', '0')) for r in combined_R]

                # Corrected print statements
                print(f"Arcs List ({len(arcs_list_combined)}): {convert_arc_list_format(arcs_list_combined)}")
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
            self.contraction_path = contraction_path  # Store for export use

            # Call the contraction process and store the results
            path, failed = contraction_path.get_contraction_paths()

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
    """
    Main entry point for the application.
    
    Creates the tkinter root window and initializes the GUI.
    """
    root = tk.Tk()
    app = RDLTProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
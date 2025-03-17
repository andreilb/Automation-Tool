import tkinter as tk
from tkinter import scrolledtext

class HelpDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("RDLT Processor Help")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure the dialog
        self.dialog.configure(bg="#f0f0f0")
        
        # Create notebook (tabbed interface)
        from tkinter import ttk
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        overview_tab = tk.Frame(notebook, bg="#f0f0f0")
        usage_tab = tk.Frame(notebook, bg="#f0f0f0")
        sample_tab = tk.Frame(notebook, bg="#f0f0f0")
        about_tab = tk.Frame(notebook, bg="#f0f0f0")
        
        notebook.add(overview_tab, text="Overview")
        notebook.add(usage_tab, text="Usage Guide")
        notebook.add(sample_tab, text="Sample Files")
        notebook.add(about_tab, text="About")
        
        # Overview tab content
        overview_frame = tk.Frame(overview_tab, bg="#f0f0f0", padx=10, pady=10)
        overview_frame.pack(fill=tk.BOTH, expand=True)
        
        overview_title = tk.Label(overview_frame, text="RDLT Processor", font=("Arial", 14, "bold"), bg="#f0f0f0")
        overview_title.pack(anchor=tk.W, pady=(0, 10))
        
        overview_text = scrolledtext.ScrolledText(overview_frame, wrap=tk.WORD, height=20)
        overview_text.pack(fill=tk.BOTH, expand=True)
        overview_text.insert(tk.END, """RDLT Processor - Robustness Diagram with Loop and Time Controls

This application automates the evaluation of an RDLT to determine its L-Safeness and Classical Soundness by:

• Extracting RDLT data from input files (text format)
• Processing R2 (Reset-Bound Subsystem) if centers are present
• Handling R1 (main structure with R2 represented as abstract arcs)
• Evaluating cycles in both R1 and R2
• Checking for OR-JOIN conditions within the RBS
• Running matrix operations to verify L-Safeness
• Extracting activity profiles in case of violations

The application provides a simple GUI to select input files, process them, and view the results.
""")
        overview_text.config(state=tk.DISABLED)
        
        # Usage tab content
        usage_frame = tk.Frame(usage_tab, bg="#f0f0f0", padx=10, pady=10)
        usage_frame.pack(fill=tk.BOTH, expand=True)
        
        usage_title = tk.Label(usage_frame, text="How to Use", font=("Arial", 14, "bold"), bg="#f0f0f0")
        usage_title.pack(anchor=tk.W, pady=(0, 10))
        
        usage_text = scrolledtext.ScrolledText(usage_frame, wrap=tk.WORD, height=20)
        usage_text.pack(fill=tk.BOTH, expand=True)
        usage_text.insert(tk.END, """1. Select an Input File:
   • Click the "Browse..." button to select a text file containing RDLT data
   • Alternatively, click one of the sample file buttons to select a predefined sample

2. Process the File:
   • Click the "Process RDLT" button to start the analysis
   • The application will read the file, extract RDLT components, and perform the evaluation

3. View Results:
   • The processing results will appear in the output text area
   • The status bar at the bottom will indicate whether processing was successful

4. Save or Clear Results:
   • Click "Save Output" to save the results to a text file
   • Click "Clear Output" to clear the output text area

File Format Requirements:
The input text file should follow the specific RDLT format. For examples, see the sample files provided.
""")
        usage_text.config(state=tk.DISABLED)
        
        # Sample Files tab content
        sample_frame = tk.Frame(sample_tab, bg="#f0f0f0", padx=10, pady=10)
        sample_frame.pack(fill=tk.BOTH, expand=True)
        
        sample_title = tk.Label(sample_frame, text="Sample Files", font=("Arial", 14, "bold"), bg="#f0f0f0")
        sample_title.pack(anchor=tk.W, pady=(0, 10))
        
        sample_text = scrolledtext.ScrolledText(sample_frame, wrap=tk.WORD, height=20)
        sample_text.pack(fill=tk.BOTH, expand=True)
        sample_text.insert(tk.END, """The application comes with several sample files demonstrating different RDLT structures:

• sample_rdlt.txt - Basic RDLT example
• sample_lsafe.txt - Example of an L-Safe RDLT
• sample_multiple_center.txt - RDLT with multiple centers
• sample_stuckrdlt.txt - Example of a stuck RDLT
• sample_relaxedwith multipleca.txt - Relaxed RDLT with multiple CAs
• sample_rdlt_andjoin.txt - RDLT with AND-join
• sample_1non_contractable.txt - RDLT with non-contractable elements

To use these samples:
1. Place the sample files in a folder named "rdlt_text" in the same directory as the application
2. Click the corresponding sample button in the Quick Select Sample Files section

If the rdlt_text directory doesn't exist, the application will create it automatically.
""")
        sample_text.config(state=tk.DISABLED)
        
        # About tab content
        about_frame = tk.Frame(about_tab, bg="#f0f0f0", padx=10, pady=10)
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        about_title = tk.Label(about_frame, text="About", font=("Arial", 14, "bold"), bg="#f0f0f0")
        about_title.pack(anchor=tk.W, pady=(0, 10))
        
        about_text = scrolledtext.ScrolledText(about_frame, wrap=tk.WORD, height=20)
        about_text.pack(fill=tk.BOTH, expand=True)
        about_text.insert(tk.END, """RDLT Processor
Version 3.0 (March 2025)

Author: Andrei Luz B. Asoy

This application is designed for processing and analyzing Robustness Diagrams with Loop and Time Controls (RDLT).

Dependencies:
• input_rdlt: Handles RDLT input processing
• cycle: Contains the Cycle class for cycle detection
• abstract: AbstractArc class to compute abstract arcs in RBS
• create_r2: ProcessR2 function for R2-specific processing
• create_r1: ProcessR1 function for R1-specific processing
• joins: TestJoins class to determine types of JOINs within the RBS
• matrix: Matrix class to convert RDLT data (dict) to matrix representation
• mod_extract: ModifiedActivityExtraction class generates the activity profile of violating component(s)
• contraction: ContractionPath for path contraction analysis

For questions or issues, please contact the developer.
""")
        about_text.config(state=tk.DISABLED)
        
        # Add close button
        close_button = tk.Button(self.dialog, text="Close", command=self.dialog.destroy)
        close_button.pack(pady=10)
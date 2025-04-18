"""
RDLT Processor Startup Module
-----------------------------

This module serves as the entry point for the RDLT Processor application. It provides:
- A splash screen during application startup
- Dependency checking to ensure all required modules are available
- Application initialization and main window launch

Dependencies:
    - tkinter: Provides the GUI framework for the splash screen
    - rdlt_gui: Contains the main application GUI implementation
    - input_rdlt: Handles RDLT input processing from text input to dict
    - cycle: Contains the Cycle class for cycle detection
    - create_r2: ProcessR2 function for processing EVSA for RBS (R2) components
    - create_r1: ProcessR1 function for processing EVSA for non-RBS (R1) components
    - joins: TestJoins class to determine types of JOINs within the RBS (R2)
    - matrix: Matrix class to convert RDLT data (dict) to matrix representation
    - mod_extract: ModifiedActivityExtraction class for activity profiles
    - contraction: ContractionPath class for contraction paths
    - rdlt_export: ResultsExporter class for exporting results
    - utils: Provides utility functions for graph processing and path finding
    - help_dialog: HelpDialog class for displaying help information

Author: Andrei Luz B. Asoy
Code Version 3.2 (as of 04-15-25)
"""

import tkinter as tk
from tkinter import ttk, messagebox

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window size and position
        width = 400
        height = 200
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create frame
        frame = tk.Frame(root, bg="#7393B3")
        frame.pack(fill="both", expand=True)
        
        # Add title
        title_label = tk.Label(frame, text="RDLT Processor", font=("Arial", 20, "bold"), bg="#7393B3", fg="white")
        title_label.pack(pady=(30, 10))
        
        # Add loading text
        self.loading_label = tk.Label(frame, text="Loading application...", font=("Arial", 12), bg="#7393B3", fg="white")
        self.loading_label.pack(pady=10)

        style = ttk.Style()
        style.theme_use('default')  # Use the default theme as a base
        style.configure("Custom.Horizontal.TProgressbar", 
                        troughcolor='lightgray',  # Background color of the progress bar
                        background='lightgreen',         # Color of the progress bar
                        thickness=10)             # Thickness of the progress bar
        
        # Add progress bar
        self.progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10)

        # Start the progress bar
        self.progress.start(10)
        
        # Add version info
        version_label = tk.Label(frame, text="Version 1.0 (March 2025)", font=("Arial", 8), bg="#7393B3", fg="white")
        version_label.pack(side="bottom", pady=10)

def check_dependencies():
    missing_modules = []
    required_modules = [
        'input_rdlt', 'cycle', 'create_r2', 'create_r1', 
        'joins', 'matrix', 'mod_extract', 'contraction',
        'utils', 'rdlt_export', 'help_dialog', 'abstract',
        'abstract',
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def launch_main_app():
    from rdlt_gui import RDLTProcessorGUI
    
    root = tk.Tk()
    app = RDLTProcessorGUI(root)
    return root

def main():
    # Create splash screen
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)
    splash_root.update()
    
    # Check for dependencies
    missing = check_dependencies()
    
    if missing:
        splash_root.destroy()
        error_msg = f"The following required modules are missing:\n\n{', '.join(missing)}\n\nPlease ensure all modules are in the same directory as this script."
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Missing Dependencies", error_msg)
        root.destroy()
        return
    
    # Simulate loading time (and actually import the modules)
    import time
    time.sleep(1.5)
    
    # Destroy splash screen and launch main app
    splash_root.destroy()
    main_root = launch_main_app()
    main_root.mainloop()

if __name__ == "__main__":
    main()
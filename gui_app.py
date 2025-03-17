import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select RDLT Input File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filepath)

def run_script():
    filepath = file_entry.get()
    if not filepath:
        messagebox.showerror("Error", "Please select a file first.")
        return
    
    try:
        # Run the main script with the selected file as input
        result = subprocess.run(
            ["python", "main.py", filepath],
            capture_output=True,
            text=True
        )
        
        # Display the output in a new window
        output_window = tk.Toplevel(root)
        output_window.title("Script Output")
        output_text = tk.Text(output_window, wrap=tk.WORD)
        output_text.pack(fill=tk.BOTH, expand=True)
        output_text.insert(tk.END, result.stdout)
        output_text.insert(tk.END, result.stderr)
        output_text.config(state=tk.DISABLED)  # Make the text read-only
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("RDLT Processor")

# Create and place the file selection widgets
file_label = tk.Label(root, text="Select RDLT Input File:")
file_label.grid(row=0, column=0, padx=5, pady=5)

file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=1, padx=5, pady=5)

browse_button = tk.Button(root, text="Browse", command=select_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Create and place the run button
run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.grid(row=1, column=1, padx=5, pady=5)

# Start the main event loop
root.mainloop()
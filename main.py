"""
Main Script for Processing RDLT and Verifying Classical Soundness
----------------------------------------------------
This script processes RDLT data, detects cycles in R2 and R1, and performs the 
necessary computations for abstract arcs and effective reusability (eRU).

Dependencies:
    - input_rdlt: Handles RDLT input processing.
    - cycle: Contains the Cycle class for cycle detection.
    - abstract: AbstractArc class to compute abstract arcs in RBS.
    - create_r2: ProcessR2 function for R2-specific processing.
    - create_r1: ProcessR1 function for R1-specific processing.

Author: Andrei Luz B. Asoy
Code Version 1 (as of 11-24-24)
"""

from input_rdlt import Input_RDLT
from cycle import Cycle
from abstract import AbstractArc
from create_r2 import ProcessR2
from create_r1 import ProcessR1

if __name__ == '__main__':
    # Input file path for RDLT data
    input_filepath = 'C:/Users/SAGE/Documents/Software/rdlt_text/sample_rdlt.txt'
    # Uncomment to use alternative test files:
    # input_filepath = 'C:/Users/SAGE/Documents/Software/rdlt_text/sample_lsafe.txt'
    # input_filepath = 'C:/Users/SAGE/Documents/Software/rdlt_text/sample_multiple_center.txt'

    # Initialize Input_RDLT with the file path
    input_instance = Input_RDLT(input_filepath)

    # Process the input file and categorize the data
    input_instance.evaluate()

    # Retrieve R2 data and RBS-related lists
    R2 = input_instance.getR('R2')  # Retrieve R2 arcs
    Centers_list = input_instance.Centers_list  # Centers in the RBS
    In_list = input_instance.In_list  # In-bridges
    Out_list = input_instance.Out_list  # Out-bridges

    # Debugging Output: Display initial RBS and R2 status
    print('-' * 60)
    if not Centers_list and not In_list and not Out_list:
        print("No RBS detected in the input data. Skipping R2 processing.")
    elif not R2:
        print("R2 is empty or None. Please check the input data.")
    else:
        # Process and display R2 details
        print(f"Processed R2:")
        print('-' * 30)
        ProcessR2(R2)

        # Detect cycles in R2
        print("Detecting cycles in R2:")
        print('-' * 30)
        cycle_R2 = Cycle(R2).evaluate_cycle()

        if not cycle_R2:
            print("No cycles detected in R2.")
        else:
            print(f"Cycles Detected in R2: ({len(cycle_R2)}) {cycle_R2}")
        print('-' * 60)

        # Retrieve R1 data
        R1 = input_instance.getR('R1')

        # Handle warnings or errors with R1 data
        if isinstance(R1, str) and "WARNING" in R1:
            print(R1)  # Display warning message for R1 retrieval
        else:
            # Process R1, updating with abstract arcs from RBS
            print("Processing R1:")
            print('-' * 30)
            updated_R1 = ProcessR1(
                input_instance.Arcs_List,  # List of all arcs
                input_instance.L_attribute_list,  # List of l-attributes
                input_instance.C_attribute_list,  # List of c-attributes
                R1,  # Original R1 data
                Centers_list,  # Centers in RBS
                In_list,  # In-bridges
                Out_list,  # Out-bridges
                R2  # R2 data for abstract arcs
            )

            # Detect cycles in updated R1
            print("Detecting cycles in updated R1:")
            print('-' * 30)
            cycle_R1 = Cycle(updated_R1).evaluate_cycle()

            if not cycle_R1:
                print("No cycles detected in updated R1.")
            else:
                print(f"Cycles Detected in R1: ({len(cycle_R1)}) {cycle_R1}")
            print('-' * 60)

    # Debugging: Print summary of processed data
    print("Summary of Input Data and Processing:")
    print('-' * 60)
    print(f"Arcs List: {input_instance.Arcs_List}")
    print(f"L-attribute List: {input_instance.L_attribute_list}")
    print(f"C-attribute List: {input_instance.C_attribute_list}")
    print(f"Centers List: {Centers_list}")
    print(f"In-bridges List: {In_list}")
    print(f"Out-bridges List: {Out_list}")
    print('-' * 60)

    # End of script
    print("RDLT processing complete.")

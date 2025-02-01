"""
Main Script for Processing RDLT and Verifying Classical Soundness
----------------------------------------------------

This script automates the evaluation of an RDLT (Robustness Diagram with Loop and Time Controls) to determine its L-Safeness and Classical 
Soundness by extracting RDLT data from an input file (text format), processing R2 (Reset-Bound Subsystem) if centers are present, 
handling R1 (the main structure with R2 represented as abstract arcs), evaluating cycles in both R1 and R2, checking for OR-JOIN 
conditions (within the RBS), running matrix operations to verify L-Safeness, and extracting an activity profile in case of violations.

Dependencies:
    - input_rdlt: Handles RDLT input processing.
    - cycle: Contains the Cycle class for cycle detection.
    - abstract: AbstractArc class to compute abstract arcs in RBS.
    - create_r2: ProcessR2 function for R2-specific processing.
    - create_r1: ProcessR1 function for R1-specific processing.
    - joins: TestJoins class to determine types of JOINs within the RBS.
    - matrix: Matrix class to convert RDLT data (dict) to matrix representation.
    - mod_extract: ModifiedActivityExtraction class generates the activity profile of violating component(s). //still in debugging process

Author: Andrei Luz B. Asoy
Code Version 2 (as of 01-28-25)
"""

from input_rdlt import Input_RDLT
from cycle import Cycle
from create_r2 import ProcessR2
from create_r1 import ProcessR1
from joins import TestJoins
from matrix import Matrix
from mod_extract import ModifiedActivityExtraction

if __name__ == '__main__':
    
    # Input file path for RDLT data
    
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_rdlt.txt'
    # Uncomment to use alternative test files:
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_lsafe.txt'
    input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_multiple_center.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_stuckrdlt.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_relaxedwith multipleca.txt'
    
    # Initialize the RDLT input processor
    input_instance = Input_RDLT(input_filepath)
    print('*' * 100)
    print("\nAutomation starting....\n")
    print('-' * 60)
    print("\nDisplaying extracted data from user input....\n")
    input_instance.evaluate()

    # Retrieve extracted RDLT components
    Centers_list = input_instance.Centers_list
    In_list = input_instance.In_list
    Out_list = input_instance.Out_list
    Arcs_list = input_instance.Arcs_List
    L_attribute_list = input_instance.L_attribute_list
    C_attribute_list = input_instance.C_attribute_list

    # Process R2 (RBS) if centers exist
    # Skip processing RBS/R2 if no centers are present
    if Centers_list:
        print('-' * 60)
        print("\nProcessing RBS components...\n")
        print('-' * 60)
        initial_R2 = input_instance.getRs()  # Get all regions except 'R1'
        R2 = ProcessR2(initial_R2)

        # Cycle detection for R2
        cycle_R2 = Cycle(R2)
        # Evaluate the cycle (this will fill the Cycle_List)
        C_R2 = cycle_R2.evaluate_cycle()
        # Print the cycle list
        cycle_list_R2 = cycle_R2.get_cycle_list()  # This will print the details of the cycles
        # print("This is cycle list R2:", cycle_list_R2)  # This will print the populated Cycle_List
    else:
        print('-' * 60)
        print("\nNo centers found. Skipping RBS processing...\n")
        print('-' * 60)
        R2 = []
    
    # Process R1 (Main Structure)
    print("\nProcessing R1 components...\n")
    print('-' * 60)
    initial_R1 = input_instance.getR('R1')
    # print("This is initial R1:~~~~~~~~~~~~~~~~~~", initial_R1)
    # print("This is Arcs List:~~~~~~~~~~~~~~~~~~", Arcs_list)
    # print("This is L-attribute List:~~~~~~~~~~~~~~~~~~", L_attribute_list)
    # print("This is C-attribute List:~~~~~~~~~~~~~~~~~~", C_attribute_list)
    # print("This is Centers List:~~~~~~~~~~~~~~~~~~", Centers_list)
    # print("This is R2:~~~~~~~~~~~~~~~~~~", R2)
    R1 = ProcessR1(
                Arcs_list,  # List of all arcs
                initial_R1,
                Centers_list,
                In_list,
                Out_list,
                R2
            )
    
    # Cycle detection for R1
    cycle_R1 = Cycle(R1)
    # Evaluate the cycle (this will fill the Cycle_List)
    C_R1 = cycle_R1.evaluate_cycle()
    # Print the cycle list
    cycle_list_R1 = cycle_R1.get_cycle_list()  # This will print the details of the cycles
    # print("This is cycle list R1:", cycle_list_R1)  # This will print the populated Cycle_List

    # print("This will be converted to matrix:", R1, cycle_list_R1) #debugger

    # Evaluate JOIN conditions and determine the appropriate matrix operations
    print("\nTesting JOINs in RBS...\n")
    check = TestJoins.checkSimilarTargetVertexAndUpdate(R1, R2)
    print('-' * 30)
    if check:
        print("\nAll are OR-JOIN. Evaluating R1 only.\n")
        print('-' * 30)
        
        # Convert data from dict to matrix 
        matrix_instance = Matrix(R1, cycle_R1.Cycle_List)
        # Perform matrix evaluation to determine L-Safeness
        l_safe, matrix = matrix_instance.evaluate()
        print(f"\nMatrix Evaluation Result (R1 only): {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
        print('-' * 60)
        print("Generated Matrix:\n")
        print("|  Arc  |   |x|   |y|  |l|  |c||eRU||cv| |op|  |cycle| |loop||out| |safe|")
        matrix_instance.print_matrix()
        print('-' * 60)
        
        # Print Result for L-safeness
        if l_safe == True:
            print("\nVerification: RDLT is CLASSICAL SOUND.\n")
        else:
            print("\nVerification: NEEDS FURTHER VERIFICATION.\n")
            # print(f"Matrix Operation Results:\n{matrix}")\
            print('-' * 60)
            violations = matrix_instance.get_violations()
            print('-' * 30)
            # Initialize Modified Activity Extraction  for further verification
            activity_extraction = ModifiedActivityExtraction(R1, cycle_list_R1, Out_list, violations)
            activity_extraction.print_activity_profile()
    else:
        print("Contains other JOINs. Evaluating both R1 and R2.")
        
        # Convert data from dict to matrix
        matrix_instance = Matrix(R1 + R2, cycle_R1.Cycle_List)
        print('-' * 30)

        # Perform matrix evaluation to determine L-Safeness
        l_safe, matrix = matrix_instance.evaluate()
        print('-' * 30)
        print(f"Matrix Evaluation Result (R1 and R2): {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}")
        print('-' * 30)
        
        # Print Result for L-safeness
        if l_safe == True:
            print("\nVerification: RDLT is CLASSICAL SOUND.\n")
        else:
            print("\nVerification: !!! NEEDS FURTHER VERIFICATION...\n")
            print('-' * 30)
            # print(f"Matrix Operation Results:\n{matrix}")\
            print('-' * 60)
            violations = matrix_instance.get_violations()
            print('-' * 30)
            # Initialize Modified Activity Extraction for further verification
            activity_extraction = ModifiedActivityExtraction(R1 + R2, cycle_list_R1 + cycle_list_R2, Out_list, violations)
            activity_extraction.print_activity_profile()

print('-' * 60)
print("\nEnd of process....\n")
print('*' * 100)
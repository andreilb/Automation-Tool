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
    - mod_extract: ModifiedActivityExtraction class generates the activity profile of violating component(s).

Author: Andrei Luz B. Asoy
Code Version 3 (as of 03-14-25)
"""

from input_rdlt import Input_RDLT
from cycle import Cycle
from create_r2 import ProcessR2
from create_r1 import ProcessR1
from joins import TestJoins
from matrix import Matrix
from mod_extract import ModifiedActivityExtraction
from contraction import ContractionPath

if __name__ == '__main__':
    
    # Input file path for RDLT data
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_rdlt.txt'
    # Uncomment to use alternative test files:
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_lsafe.txt'
    input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_multiple_center.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_two_center.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_stuckrdlt.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_relaxedwith multipleca.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_rdlt_andjoin.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_1non_contractable.txt'
    # input_filepath = 'D:/SCHOOL/Software/rdlt_text/sample_multisink.txt'  #problematic
    
    # Initialize the RDLT input processor
    input_instance = Input_RDLT(input_filepath)
    print('=' * 100)
    # print("\nAutomation starting....\n")
    # print('-' * 60)
    print("\nExtracted User Input:\n")
    input_instance.evaluate()

    # Retrieve extracted RDLT components
    Centers_list = input_instance.Centers_list
    In_list = input_instance.In_list
    Out_list = input_instance.Out_list
    Arcs_list = input_instance.Arcs_List
    L_attribute_list = input_instance.L_attribute_list
    C_attribute_list = input_instance.C_attribute_list

    # Get R1 and R2 from input_rdlt
    initial_R1 = input_instance.getR('R1')
    
    # Process R2 (RBS) if centers exist
    if Centers_list:
        # print('-' * 60)
        print("\nProcessing RBS components...\n")
        print('-' * 60)
        initial_R2 = input_instance.getRs()  # Get all regions except 'R1'
        
        # Use TestJoins to check if all joins in R2 are OR-joins
        from joins import TestJoins
        flattened_R2 = []
        for r2_dict in initial_R2:
            for r2_key, r2_value in r2_dict.items():
                flattened_R2.extend(r2_value)
        
        check_result = TestJoins.checkSimilarTargetVertexAndUpdate(initial_R1, flattened_R2)
        
        if check_result == initial_R1:
            # All joins are OR-joins, use the standard processing with abstract arcs
            # print("\nAll JOINs in R2 are OR-JOINs. Using R1 ONLY.\n")
            R2 = ProcessR2(initial_R2)
            
            # Process R1 with abstract arcs
            # print("\nProcessing R1 components with abstract arcs...\n")
            # print('-' * 60)
            R1 = ProcessR1(
                Arcs_list,
                initial_R1,
                Centers_list,
                In_list,
                Out_list,
                R2
            )
            
            # Cycle detection for R1 and R2
            cycle_R1 = Cycle(R1)
            C_R1 = cycle_R1.evaluate_cycle()
            cycle_list_R1 = cycle_R1.get_cycle_list()
            
            cycle_R2 = Cycle(R2)
            C_R2 = cycle_R2.evaluate_cycle()
            cycle_list_R2 = cycle_R2.get_cycle_list()
            
            # Convert data from dict to matrix (R1 only)
            # print(f"\nFor Matrix processing (R1 with abstract arcs): {len(R1)} arcs")
            matrix_instance = Matrix(R1, cycle_R1.Cycle_List)
            
            # Perform matrix evaluation to determine L-Safeness
            l_safe, matrix = matrix_instance.evaluate()
            print(f"\nMatrix Evaluation Result: {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
            # print('-' * 60)
            # print("Generated Matrix:\n")
            print("|  Arc  |   |x|   |y|  |l|  |c||eRU||cv| |op|  |cycle| |loop||out| |safe||join-safe| |r-id|")
            matrix_instance.print_matrix()
            print('-' * 60)
            
        else:
            # Not all joins are OR-joins, use direct processing without abstract arcs
            # print("\nR2 contains other types of JOINs. Using both R1 and R2 for processing.\n")
            
            # Extract and flatten R2 data
            R2 = []
            for r2_dict in initial_R2:
                for r2_key, r2_value in r2_dict.items():
                    R2.extend(r2_value)
            
            # Combine R1 and R2 into a single list
            combined_R = initial_R1 + R2

            # Create cycle instance and detect cycles
            cycle_combined = Cycle(combined_R)
            C_combined = cycle_combined.evaluate_cycle()

            # Update eRU values in combined_R based on cycle participation
            combined_R = cycle_combined.update_eRU_values()

            # Get the updated cycle list
            cycle_list_combined = cycle_combined.get_cycle_list()
            
            # Print the combined list for debugging
            print("R1 and R2:")
            print('-' * 30)
            # print(f"Total arcs: {len(combined_R)}")
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
            print('-' * 60)
            
            
            # Convert data from dict to matrix (combined R1 and R2)
            # print(f"\nFor Matrix processing (combined R1 and R2): {len(combined_R)} arcs") 
            matrix_instance = Matrix(combined_R, cycle_combined.Cycle_List, In_list, Out_list)
            
            # Perform matrix evaluation to determine L-Safeness
            l_safe, matrix = matrix_instance.evaluate()
            print(f"\nMatrix Evaluation Result: {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
            # print('-' * 60)
            # print("Generated Matrix:\n")
            print("|  Arc  |   |x|   |y|  |l|  |c||eRU||cv| |op|  |cycle| |loop||out| |safe||join-safe| |r-id|")
            matrix_instance.print_matrix()
            print('-' * 60)
    else:
        # No centers found, process R1 directly
        # print('-' * 60)
        print("\nNo centers found. Processing R1 directly...\n")
        print('-' * 60)
        
        # Process R1 with no abstract arcs
        print("\nProcessing R1 components...\n")
        print('-' * 60)
        R1 = initial_R1
        
        # Detect cycles in R1
        cycle_R1 = Cycle(R1)
        C_R1 = cycle_R1.evaluate_cycle()
        cycle_list_R1 = cycle_R1.get_cycle_list()
        
        # Convert data from dict to matrix
        # print(f"\nFor Matrix processing (R1 only): {len(R1)} arcs") 
        matrix_instance = Matrix(R1, cycle_R1.Cycle_List)
        
        # Perform matrix evaluation to determine L-Safeness
        l_safe, matrix = matrix_instance.evaluate()
        print(f"\nMatrix Evaluation Result: {'RDLT is L-Safe.' if l_safe == True else 'RDLT is NOT L-Safe.'}\n")
        print('-' * 60)
        # print("Generated Matrix:\n")
        print("|  Arc  |   |x|   |y|  |l|  |c||eRU||cv| |op|  |cycle| |loop||out| |safe||join-safe| |r-id|")
        matrix_instance.print_matrix()
        # print('-' * 60)
    
    # Print final verification result
    if l_safe == True:
        print("\n=========== SUMMARY ===========")
        print("\n RDLT is L-safe and CLASSICAL SOUND.\n")
    else:
        violations = matrix_instance.get_violations()
        print('-' * 60)
        # print("\nVEFIRICATION: NEEDS FURTHER VERIFICATION.\n")
        
        # print(violations) # dictionary format of violations
        # print('-' * 30)

        # Initialize Contraction Path
        contraction_path = ContractionPath(combined_R if 'combined_R' in locals() else R1, violations)

        # Call the contraction process and store the results
        contraction_path.contract_paths()
        path, failed_contractions = contraction_path.get_contractions_with_rid()
        list_path, list_failed = contraction_path.get_list_contraction_arcs()
        # Print the final contraction paths
        # print("\nGenerating contraction path...")
        print(f"\nContraction path: {list_path}\n")
        # print(f"Failed contractions: {list_failed}\n")

        # If using combined R1 and R2, pass In_list and Out_list to Modified Activity Extraction
        if 'combined_R' in locals():
            # Use cycle_list when creating ModifiedActivityExtraction
            if Centers_list:
                modified_activity = ModifiedActivityExtraction(combined_R, path, violations, failed_contractions, cycle_combined.Cycle_List, R2, In_list, Out_list)
                activity_profile= modified_activity.analyze_model()

            else:
                modified_activity = ModifiedActivityExtraction(combined_R, path, violations, failed_contractions, cycle_combined.Cycle_List)
                activity_profile, violations = modified_activity.analyze_model()
                is_sound, report = modified_activity.verify_classical_soundness()
                print(report)
        else:
            # Run Modified Activity Extraction without in_list and out_list
            modified_activity = ModifiedActivityExtraction(R1, path, violations, failed_contractions, cycle_R1.Cycle_List)
            # Analyze the model
            activity_profile = modified_activity.analyze_model()

# print('-' * 60)
# print("\nEnd of process....\n")
print('=' * 100)
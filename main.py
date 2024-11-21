from input_rdlt import Input_RDLT
from cycle import Cycle
from abstract import AbstractArc
from create_r2 import ProcessR2
from create_r1 import ProcessR1

if __name__ == '__main__':
    # Initialize Input_RDLT with the input file path
    # input_filepath = 'C:/Users/SAGE/Documents/Software/rdlt_text/sample_rdlt.txt'
    # input_filepath = 'C:/Users/SAGE/Documents/Software/rdlt_text/sample_lsafe.txt'
    input_filepath = 'C:/Users/SAGE/Documents/Software/rdlt_text/sample_multiple_center.txt'
    input_instance = Input_RDLT(input_filepath)

    # Process the RDLT data by reading and categorizing the file contents
    input_instance.evaluate()  # This will process the file and categorize the data

    # Retrieve R2 (since it will be needed for cycle detection and processing)
    R2 = input_instance.getR('R2')
    Centers_list = input_instance.Centers_list
    In_list = input_instance.In_list
    Out_list = input_instance.Out_list

    # Check for Centers, In_list, and Out_list
    if not Centers_list and not In_list and not Out_list:
        print("No RBS detected in the input data. Skipping R2 processing.")
    elif not R2:
        print("R2 is empty or None. Please check the input data.")
    else:
        # Process and print R2 details using the updated ProcessR2 function
        print(f"Processed R2:")
        print('-' * 30)
        ProcessR2(R2)

        # Detect cycles in R2 using the Cycle class
        print(f"Cycles List in R2:")
        print('-' * 30)
        cycle_R2 = Cycle(R2).evaluate_cycle()

        # Check if cycles were detected
        if cycle_R2 is None:
            print("No cycles detected in R2.")
        else:
            # Now, just process R1 after abstract arcs are handled in ProcessR1
            print("\nCalling ProcessR1 to handle R1 data and abstract arcs:")
            print('-' * 30)
            R1 = input_instance.getR('R1')  # Ensure R1 data is retrieved here

            # Debugging output: Check the value of R1
            print(f"Retrieved R1 data: {R1}")
            if isinstance(R1, str) and "WARNING" in R1:
                print(R1)  # If a warning, print it
            else:
                print("Successfully retrieved R1 data:", R1)

            # Debugging: Print additional data related to arcs, attributes
            print(f"Arcs List: {input_instance.Arcs_List}")
            print(f"L-attribute List: {input_instance.L_attribute_list}")
            print(f"C-attribute List: {input_instance.C_attribute_list}")
            print(f"Centers List: {Centers_list}")
            print(f"In List: {In_list}")
            print(f"Out List: {Out_list}")

            # Ensure all arguments are passed to ProcessR1 and capture the updated R1
            updated_R1 = ProcessR1(
                input_instance.Arcs_List,  # List of arcs
                input_instance.L_attribute_list,  # List of l-attributes
                input_instance.C_attribute_list,  # List of c-attributes
                R1,  # R1 data
                Centers_list,  # Centers list
                In_list,  # In-bridges list
                Out_list,  # Out-bridges list
                R2  # R2 data (for abstract arcs)
            )
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~ DEBUGGING ~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Updated R1: ", updated_R1)  # Now this will print the updated R1 after abstract arcs
            print("Arcs_List", input_instance.Arcs_List)
            print("L_attribute_list", input_instance.L_attribute_list)
            print("C_attribute_list", input_instance.C_attribute_list)
            print("Centers_list", Centers_list)
            print("In_list", In_list)
            print("Out_list", Out_list)
            print("R2: ", R2)
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~ END ~~~~~~~~~~~~~~~~~~~~~~~~~~")

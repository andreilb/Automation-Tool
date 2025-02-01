
# def ProcessR2(R2):
#     """
#     Processes all components in the dictionary except for 'R1'. It extracts arcs, vertices, 
#     and their respective attributes, using pre-calculated cycle and eRU values from the Cycle class.

#     Args:
#         R2 (list): List containing dictionaries for components (R2, R3, etc.).

#     Returns:
#         None: This function does not return a value. It prints the results of processing components.
    
#     Raises:
#         KeyError: If a component is missing or any arc data is malformed.
#     """
#     # Step 1: Merge the list of dictionaries into a single dictionary (For main)
#     print("BEFORE:::::::", R2)
#     R2_merged = [list(R.values()) for R in R2]
#     R2_final_merged =[]
#     for R2s in R2_merged:
#         R2_final_merged += R2s[0]
#     print("AFTER:::::::", R2_final_merged)
#     components_to_process = {"R2": R2_final_merged}
    
#     # # For processing (for ProcessR2)
#     # R_dict = {}
#     # for component_dict in R2:
#     #     # Each dictionary in the list has a single key-value pair, where the key is the component name
#     #     for key, value in component_dict.items():
#     #         R_dict[key] = value
    
#     # # Step 2: Filter out 'R1' and process the rest of the components
#     # to_process = {key: value for key, value in R_dict.items() if key != 'R1'}

#     # Step 3: Process each component
#     for component, arcs in components_to_process.items():
#         print('-' * 30)
#         print(f"Processing {component}:")
#         print('-' * 30)

#         # Initialize lists to store arcs, vertices, and attributes
#         arcs_list = []
#         vertices_list = []
#         c_attribute_list = []
#         l_attribute_list = []
#         eRU_list = []  # eRU values will be populated from the Cycle class

#         # Process each arc in the component
#         for r in arcs:
#             # Check that all necessary attributes are present in the arc
#             if 'arc' not in r or 'c-attribute' not in r or 'l-attribute' not in r:
#                 raise ValueError(f"Missing required attribute in arc: {r}")

#             # Extract the arc, c-attribute, and l-attribute
#             arc = r['arc']
#             c_attribute = r['c-attribute']
#             l_attribute = r['l-attribute']

#             # Ensure non-empty and valid attributes
#             if not arc or not c_attribute or not l_attribute:
#                 raise ValueError(f"Invalid data in arc (empty or invalid values): {r}")

#             arcs_list.append(arc)
#             c_attribute_list.append(c_attribute)
#             l_attribute_list.append(l_attribute)

#             # Extract vertices from the arc and add them to the vertices list
#             vertices_list.extend(arc.split(', '))  # Add both vertices from the arc

#         # Remove duplicate vertices by converting to a set and back to a list
#         vertices_list = sorted(set(vertices_list))

#         # Initialize the Cycle object and use pre-calculated cycle and eRU values
#         # Initialize the Cycle object and evaluate cycles in R2
#         cycle_detector = Cycle(R2)  # Create the Cycle object using the R2 data
#         cycle_R2 = cycle_detector.evaluate_cycle()  # Evaluate cycles in R2
#         eRU_list = cycle_detector.calculate_eRU_for_arcs(l_attribute_list) # Default eRU value for each arc is 0
#         print("these are the l-attribute list: ~~~~~~~~~~~~~~~~~~~~~~~~~~", l_attribute_list)
        
#         # Check if cycles were detected in R2
#         if not cycle_R2:
#             print("No cycles detected in R2.")  # Print message if no cycles were found
#         # else:
#         #     # Flatten the cycle list for easier checking if an arc is part of any cycle
#         #     cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R2]  # Get list of arcs in each cycle

#         # Print the results for the current component
#         print(f"Arcs List ({len(arcs_list)}): {arcs_list}")  # List of arcs in the component
#         print(f"Vertices List ({len(vertices_list)}): {vertices_list}")  # Unique vertices in the component
#         print(f"C-attribute List ({len(c_attribute_list)}): {c_attribute_list}")  # List of c-attributes
#         print(f"L-attribute List ({len(l_attribute_list)}): {l_attribute_list}")  # List of l-attributes
#         print(f"eRU List ({len(eRU_list)}): {eRU_list}")  # List of eRU values for each arc
#         print('-' * 60)  # Divider for output
#         print("This is all of R2: ~~~~~~~~~~~~~~~~~~", R2_final_merged)
    
#     return components_to_process
from cycle import Cycle

def ProcessR2(R2):
    """
    Processes the R2 component of the Robustness Diagram with Loop and Time Controls (RDLT).
    It extracts arcs, vertices, and their respective attributes from the R2 component,
    evaluates the cycles present, and calculates the Expanded Reusability (eRU) for each arc.
    The results are printed to the console.

    Paramenters:
        - R2 (list): List of dictionaries, where each dictionary represents an arc in R2. 
                   Each dictionary must have the following keys:
                   - 'arc': A string representing the arc in the form 'vertex1, vertex2'.
                   - 'c-attribute': A string or number representing the c-attribute of the arc.
                   - 'l-attribute': A string or number representing the l-attribute of the arc.

    Returns:
        list: R2 components and computed eRU values.

    Raises:
        KeyError: If any expected key ('arc', 'c-attribute', or 'l-attribute') is missing in any arc dictionary.
    """
    # If R2 is a dictionary and contains 'R2', remove the 'R2' key and extract its value
    if isinstance(R2, dict) and 'R2' in R2:
        R2 = R2['R2']  # Extract the list of arcs inside R2

    # Now merge all components except 'R1'
    merged_arcs = []

    if isinstance(R2, dict):
        # If R2 is a dictionary (e.g., containing 'R1', 'R2', etc.)
        for key, value in R2.items():
            if key != 'R1':  # Exclude 'R1' from processing
                merged_arcs.extend(value)  # Merge arcs from other components
    elif isinstance(R2, list):
        # If R2 is a list of components (e.g., [{'R2': [...]}, {'R3': [...]}])
        for component_dict in R2:
            for key, value in component_dict.items():
                if key != 'R1':  # Exclude 'R1' from processing
                    merged_arcs.extend(value)  # Merge arcs from other components

    # Initialize lists to store arcs, vertices, and attributes
    arcs_list = []
    vertices_list = []
    c_attribute_list = []
    l_attribute_list = []
    eRU_list = []  # This will hold the eRU values (as strings)

    # Process each arc in the merged arcs
    for r in merged_arcs:
        if 'arc' not in r or 'c-attribute' not in r or 'l-attribute' not in r:
            raise ValueError(f"Missing required attribute in arc: {r}")

        # Extract arc attributes
        arc = r['arc']
        c_attribute = r['c-attribute']
        l_attribute = r['l-attribute']

        if not arc or not c_attribute or not l_attribute:
            raise ValueError(f"Invalid data in arc (empty or invalid values): {r}")

        arcs_list.append(arc)
        c_attribute_list.append(c_attribute)
        l_attribute_list.append(l_attribute)
        vertices_list.extend(arc.split(', '))

    # Remove duplicate vertices
    vertices_list = sorted(set(vertices_list))

    # Initialize the Cycle object and evaluate cycles in the merged arcs
    # print(f"Evaluating cycles in R2...")
    cycle_instance = Cycle({'merged': merged_arcs})  # Create an instance of the Cycle class
    cycle_R2 = cycle_instance.evaluate_cycle()  # Call the method on the instance

    if not cycle_R2:
        print("\nNo cycles detected in R2.")
        # If no cycle is found, set eRU to '0' (as a string) for all arcs
        for arc in merged_arcs:
            arc['eRU'] = '0'  # Set eRU to '0' by default (as string)
            eRU_list.append('0')  # Add '0' to eRU list
    else:
        print(f"\nCycles detected: {len(cycle_R2)} cycles found.")
        # Create a set to track processed arcs to avoid duplicate cycle detections
        processed_cycles = set()

        # Iterate over each cycle in the detected cycles
        for cycle_data in cycle_R2:
            cycle_arcs = cycle_data['cycle']
            cycle_l_attributes = []
            cycle_arcs_with_min_l = []

            # Iterate over the arcs in the cycle
            for cycle_arc in cycle_arcs:
                # Extract the r-id and arc name
                r_id, arc_name = cycle_arc.split(": ")
                arc_name = arc_name.strip()

                # Get the actual arc from merged_arcs using r-id (you may need to adjust how this lookup works)
                actual_arc = next((r for r in merged_arcs if r['arc'] == arc_name), None)

                if actual_arc:
                    # print(f"Processing arc: {actual_arc}")

                    # Check if l-attribute exists and process it
                    l_attribute = actual_arc.get('l-attribute', None)
                    if l_attribute is not None:
                        cycle_l_attributes.append(int(l_attribute))  # Convert to int
                    else:
                        print(f"Warning: 'l-attribute' not found for arc {actual_arc}")
                else:
                    print(f"Warning: No arc found for {arc_name}")

            # Assuming that the 'ca' (critical arc) value is the minimum l-attribute in the cycle
            ca = min(cycle_l_attributes) if cycle_l_attributes else None

            if ca is not None:
                # print(f"Critical arc 'ca' value: {ca}")

                # Iterate over all arcs in the cycle and set their eRU to the 'ca' value
                for cycle_arc in cycle_arcs:
                    r_id, arc_name = cycle_arc.split(": ")
                    arc_name = arc_name.strip()

                    # Get the actual arc from merged_arcs using r-id (you may need to adjust this)
                    actual_arc = next((r for r in merged_arcs if r['arc'] == arc_name), None)

                    if actual_arc:
                        # print(f"Processing arc: {actual_arc}")
    
                        # Set eRU of the arc to the critical arc's 'ca' value
                        actual_arc['eRU'] = str(ca)  # Set eRU to critical arc value (as string)
                        eRU_list.append(str(ca))  # Add the string version of 'ca' to eRU list
                        # print(f"Set eRU for arc {actual_arc['arc']} to {actual_arc['eRU']}")
                        if actual_arc['l-attribute'] == actual_arc['eRU']:
                            cycle_arcs_with_min_l.append(actual_arc)

            else:
                print("No critical arc found in this cycle.")

    # If no cycle was detected, we should have already set eRU to '0' for all arcs.
    if len(eRU_list) != len(merged_arcs):
        # Ensure every arc gets an eRU value, defaulting to '0' if not set during cycle processing
        for _ in range(len(merged_arcs) - len(eRU_list)):
            eRU_list.append('0')  # Append '0' as a string for missing eRU values
            
    # Print results for debugging
    print(f"\nArcs List ({len(arcs_list)}): {arcs_list}")
    print(f"Vertices List ({len(vertices_list)}): {vertices_list}")
    print(f"C-attribute List ({len(c_attribute_list)}): {c_attribute_list}")
    print(f"L-attribute List ({len(l_attribute_list)}): {l_attribute_list}")
    print(f"eRU List ({len(eRU_list)}): {eRU_list}")
    print(f"CAs_list ({len(cycle_arcs_with_min_l)}): , {cycle_arcs_with_min_l}")
    print('-' * 60)

    # Return the processed arcs
    return merged_arcs


# from cycle import Cycle

# def ProcessR2(R2):
#     """
#     Dynamically constructs and processes the R2 component of the Robustness Diagram with Loop and Time Controls (RDLT).
#     It extracts arcs, vertices, and their respective attributes, evaluates cycles, and calculates the 
#     Expanded Reusability (eRU) for each arc.

#     Args:
#         input_data (dict): Dictionary where keys are region IDs (e.g., 'R2', 'R3') and values are lists of arcs.
#         R (list): List of region names to process, e.g., ['R2', 'R3'].

#     Returns:
#         list: Processed R2 with updated eRU values for each arc.
#     """
#     # Dynamically construct R2 from the input data
#     R2 = []
#     for r_id in R:
#         arcs = input_data.get(r_id, [])
#         if arcs:
#             for arc in arcs:
#                 arc['r-origin'] = r_id  # Track the source region for debugging
#             R2.extend(arcs)

#     if not R2:
#         print("R2 is empty. No RBS detected or no additional components found.")
#         return R2

#     # Extract components from R2 (arcs, vertices, and attributes)
#     arcs_list_R2 = [r['arc'] for r in R2]
#     vertices_list_R2 = sorted(set([v for arc in arcs_list_R2 for v in arc.split(', ')]))  # Get unique vertices
#     c_attribute_list_R2 = [r['c-attribute'] for r in R2]  # List of c-attributes for each arc
#     l_attribute_list_R2 = [r['l-attribute'] for r in R2]  # List of l-attributes for each arc

#     # Initialize the Cycle object and evaluate cycles in R2
#     cycle_detector = Cycle(R2)
#     cycle_R2 = cycle_detector.evaluate_cycle()

#     # Initialize eRU list with default values
#     eRU_list_R2 = [0] * len(arcs_list_R2)

#     # Check if cycles were detected in R2
#     if cycle_R2:
#         cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R2]  # Get list of arcs in each cycle

#         for idx, arc in enumerate(arcs_list_R2):
#             arc_in_cycle = False
#             cycle_l_attributes = []

#             for cycle in cycle_arcs_list:
#                 if arc in cycle:
#                     arc_in_cycle = True
#                     for cycle_arc in cycle:
#                         for r in R2:
#                             if r['arc'] == cycle_arc:
#                                 cycle_l_attributes.append(int(r['l-attribute']))

#             eRU_list_R2[idx] = min(cycle_l_attributes) if arc_in_cycle and cycle_l_attributes else 0

#     # Update R2 with computed eRU
#     for idx, r in enumerate(R2):
#         r['eRU'] = eRU_list_R2[idx]

#     return R2


# this is the working one ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# from cycle import Cycle

# def ProcessR2(R2):
#     """
#     Processes the R2 component of the Robustness Diagram with Loop and Time Controls (RDLT).
#     It extracts arcs, vertices, and their respective attributes from the R2 component,
#     evaluates the cycles present, and calculates the Expanded Reusability (eRU) for each arc.
#     The results are printed to the console.

#     Args:
#         R2 (list): List of dictionaries, where each dictionary represents an arc in R2. 
#                    Each dictionary must have the following keys:
#                    - 'arc': A string representing the arc in the form 'vertex1, vertex2'.
#                    - 'c-attribute': A string or number representing the c-attribute of the arc.
#                    - 'l-attribute': A string or number representing the l-attribute of the arc.

#     Returns:
#         None: This function does not return a value. It prints the results of processing R2.

#     Raises:
#         KeyError: If any expected key ('arc', 'c-attribute', or 'l-attribute') is missing in any arc dictionary.
#     """
#     # Extract components from R2 (arcs, vertices, and attributes)
#     arcs_list_R2 = [r['arc'] for r in R2]
#     vertices_list_R2 = sorted(set([v for arc in arcs_list_R2 for v in arc.split(', ')]))  # Get unique vertices
#     c_attribute_list_R2 = [r['c-attribute'] for r in R2]  # List of c-attributes for each arc
#     l_attribute_list_R2 = [r['l-attribute'] for r in R2]  # List of l-attributes for each arc

#     # Initialize the Cycle object and evaluate cycles in R2
#     L_Attributes = [arc['l-attribute'] for arc in R2 if 'l-attribute' in arc]  # List of l-attributes
#     cycle_detector = Cycle(R2)  # Create the Cycle object using the R2 data
#     cycle_R2 = cycle_detector.evaluate_cycle()  # Evaluate cycles in R2

#     # Initialize eRU list with default values
#     eRU_list_R2 = [0] * len(arcs_list_R2)  # Default eRU value for each arc is 0
    
#     # Check if cycles were detected in R2
#     if not cycle_R2:
#         print("No cycles detected in R2.")  # Print message if no cycles were found
#     else:
#         # Flatten the cycle list for easier checking if an arc is part of any cycle
#         cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R2]  # Get list of arcs in each cycle

#         # Loop through each arc in R2 to compute eRU
#         for idx, arc in enumerate(arcs_list_R2):
#             arc_in_cycle = False  # Flag to check if the arc is in any cycle
#             cycle_l_attributes = []  # List to store l-attributes of arcs in the cycle

#             # Check if the current arc is part of any cycle
#             for cycle in cycle_arcs_list:
#                 if arc in cycle:  # If arc is part of the cycle
#                     arc_in_cycle = True
#                     # Collect the l-attributes of all arcs in the cycle
#                     for cycle_arc in cycle:
#                         for r in R2:
#                             if r['arc'] == cycle_arc:
#                                 cycle_l_attributes.append(int(r['l-attribute']))  # Store the l-attribute for each arc

#             # Calculate eRU for arcs that are part of a cycle
#             if arc_in_cycle:
#                 eRU_list_R2[idx] = min(cycle_l_attributes) if cycle_l_attributes else 0
#             else:
#                 # For arcs not part of a cycle, eRU remains 0 (default value)
#                 eRU_list_R2[idx] = 0

#     # Print the results for R2
#     print(f"R2:")  # Header for R2 output
#     print('-' * 20)
#     print(f"Arcs List ({len(arcs_list_R2)}): {arcs_list_R2}")  # List of arcs in R2
#     print(f"Vertices List ({len(vertices_list_R2)}): {vertices_list_R2}")  # Unique vertices in R2
#     print(f"C-attribute List ({len(c_attribute_list_R2)}): {c_attribute_list_R2}")  # List of c-attributes
#     print(f"L-attribute List ({len(l_attribute_list_R2)}): {l_attribute_list_R2}")  # List of l-attributes
#     print(f"eRU List ({len(eRU_list_R2)}): {eRU_list_R2}")  # List of eRU values for each arc
#     print('-' * 60)  # Divider for output

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# from cycle import Cycle

# def ProcessR2(r2_dict):
#     """
#     Processes the R2 components of the Robustness Diagram with Loop and Time Controls (RDLT).
#     It extracts arcs, vertices, and their respective attributes from multiple RBS components,
#     evaluates the cycles present, and calculates the Expanded Reusability (eRU) for each arc.
#     The results are printed to the console.

#     Args:
#         r2_dict (dict): A dictionary where each key is an RBS (e.g., 'R2', 'R3', 'R4', 'R5'), 
#                          and the value is a list of dictionaries, each representing an arc.
#                          Each dictionary must have the following keys:
#                          - 'arc': A string representing the arc in the form 'vertex1, vertex2'.
#                          - 'c-attribute': A string or number representing the c-attribute of the arc.
#                          - 'l-attribute': A string or number representing the l-attribute of the arc.
#                          - 'eRU': The expanded reusability value (typically calculated).

#     Returns:
#         None: This function does not return a value. It prints the results of processing the arcs.
#     """

#     # Ensure the r2_dict is a dictionary containing multiple RBS components
#     if isinstance(r2_dict, list):  # If r2_dict is a list, convert it to a dictionary
#         r2_dict = {'R2': r2_dict}

#     # Iterate through each RBS component in the dictionary
#     for R_key, R2 in r2_dict.items():
#         print(f"\nProcessing {R_key}...")  # Print which RBS is being processed

#         # Extract components from each RBS (arcs, vertices, and attributes)
#         arcs_list_R2 = [r['arc'] for r in R2]
#         vertices_list_R2 = sorted(set([v for arc in arcs_list_R2 for v in arc.split(', ')]))  # Get unique vertices
#         c_attribute_list_R2 = [r['c-attribute'] for r in R2]  # List of c-attributes for each arc
#         l_attribute_list_R2 = [r['l-attribute'] for r in R2]  # List of l-attributes for each arc

#         # Initialize the Cycle object and evaluate cycles in the current R2
#         cycle_detector = Cycle(R2)  # Create the Cycle object using the current R2 data
#         cycle_R2 = cycle_detector.evaluate_cycle()  # Evaluate cycles in R2
#         eRU_values = cycle_detector.calculate_eRU_for_arcs(l_attribute_list_R2)  # Calculate eRU for arcs in R2

#         # Initialize eRU list with default values
#         eRU_list_R2 = [0] * len(arcs_list_R2)  # Default eRU value for each arc is 0
        
#         # Check if cycles were detected in R2
#         if not cycle_R2:
#             print(f"No cycles detected in {R_key}.")  # Print message if no cycles were found
#         else:
#             # Flatten the cycle list for easier checking if an arc is part of any cycle
#             cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R2]  # Get list of arcs in each cycle

#             # Loop through each arc in R2 to compute eRU
#             for idx, arc in enumerate(arcs_list_R2):
#                 arc_in_cycle = False  # Flag to check if the arc is in any cycle
#                 cycle_l_attributes = []  # List to store l-attributes of arcs in the cycle

#                 # Check if the current arc is part of any cycle
#                 for cycle in cycle_arcs_list:
#                     if arc in cycle:  # If arc is part of the cycle
#                         arc_in_cycle = True
#                         # Collect the l-attributes of all arcs in the cycle
#                         for cycle_arc in cycle:
#                             for r in R2:
#                                 if r['arc'] == cycle_arc:
#                                     cycle_l_attributes.append(int(r['l-attribute']))  # Store the l-attribute for each arc

#                 # Calculate eRU for arcs that are part of a cycle
#                 if arc_in_cycle:
#                     eRU_list_R2[idx] = min(cycle_l_attributes) if cycle_l_attributes else 0
#                 else:
#                     # For arcs not part of a cycle, eRU remains 0 (default value)
#                     eRU_list_R2[idx] = 0

#         # Print the results for the current RBS
#         print(f"{R_key}:")  # Header for RBS output
#         print('-' * 20)
#         print(f"Arcs List ({len(arcs_list_R2)}): {arcs_list_R2}")  # List of arcs in R2
#         print(f"Vertices List ({len(vertices_list_R2)}): {vertices_list_R2}")  # Unique vertices in R2
#         print(f"C-attribute List ({len(c_attribute_list_R2)}): {c_attribute_list_R2}")  # List of c-attributes
#         print(f"L-attribute List ({len(l_attribute_list_R2)}): {l_attribute_list_R2}")  # List of l-attributes
#         print(f"eRU List ({len(eRU_list_R2)}): {eRU_list_R2}")  # List of eRU values for each arc
#         print('-' * 60)  # Divider for output

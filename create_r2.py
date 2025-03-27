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
    eRU_list = []

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
        # print(f"\nCycles detected: {len(cycle_R2)} cycles found.")
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
    
    def convert_arc_format(arc):
        return f"({arc.split(', ')[0]}, {arc.split(', ')[1]})"
        
    def convert_arc_list_format(arc_list):
        return [convert_arc_format(arc) for arc in arc_list] 
           
    # Print results for debugging
    print("R2:")
    print('-' * 20)
    print(f"Arcs List ({len(arcs_list)}): {convert_arc_list_format(arcs_list)}")
    print(f"Vertices List ({len(vertices_list)}): {vertices_list}")
    print(f"C-attribute List ({len(c_attribute_list)}): {c_attribute_list}")
    print(f"L-attribute List ({len(l_attribute_list)}): {l_attribute_list}")
    print(f"eRU List ({len(eRU_list)}): {eRU_list}")
    print('=' * 60)

    # Return the processed arcs
    return merged_arcs
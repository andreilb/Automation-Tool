from cycle import Cycle

def ProcessR2(R2):
    """
    Processes the R2 component of the Robustness Diagram with Loop and Time Controls (RDLT).
    It extracts arcs, vertices, and their respective attributes from the R2 component,
    evaluates the cycles present, and calculates the Expanded Reusability (eRU) for each arc.
    The results are printed to the console.

    Args:
        R2 (list): List of dictionaries, where each dictionary represents an arc in R2. 
                   Each dictionary must have the following keys:
                   - 'arc': A string representing the arc in the form 'vertex1, vertex2'.
                   - 'c-attribute': A string or number representing the c-attribute of the arc.
                   - 'l-attribute': A string or number representing the l-attribute of the arc.

    Returns:
        None: This function does not return a value. It prints the results of processing R2.

    Raises:
        KeyError: If any expected key ('arc', 'c-attribute', or 'l-attribute') is missing in any arc dictionary.
    """
    # Extract components from R2 (arcs, vertices, and attributes)
    arcs_list_R2 = [r['arc'] for r in R2]
    vertices_list_R2 = sorted(set([v for arc in arcs_list_R2 for v in arc.split(', ')]))  # Get unique vertices
    c_attribute_list_R2 = [r['c-attribute'] for r in R2]  # List of c-attributes for each arc
    l_attribute_list_R2 = [r['l-attribute'] for r in R2]  # List of l-attributes for each arc

    # Initialize the Cycle object and evaluate cycles in R2
    L_Attributes = [arc['l-attribute'] for arc in R2 if 'l-attribute' in arc]  # List of l-attributes
    cycle_detector = Cycle(R2)  # Create the Cycle object using the R2 data
    cycle_R2 = cycle_detector.evaluate_cycle()  # Evaluate cycles in R2
    eRU_values = cycle_detector.calculate_eRU_for_arcs(L_Attributes)  # Calculate eRU for arcs in R2

    # Initialize eRU list with default values
    eRU_list_R2 = [0] * len(arcs_list_R2)  # Default eRU value for each arc is 0
    
    # Check if cycles were detected in R2
    if not cycle_R2:
        print("No cycles detected in R2.")  # Print message if no cycles were found
    else:
        # Flatten the cycle list for easier checking if an arc is part of any cycle
        cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R2]  # Get list of arcs in each cycle

        # Loop through each arc in R2 to compute eRU
        for idx, arc in enumerate(arcs_list_R2):
            arc_in_cycle = False  # Flag to check if the arc is in any cycle
            cycle_l_attributes = []  # List to store l-attributes of arcs in the cycle

            # Check if the current arc is part of any cycle
            for cycle in cycle_arcs_list:
                if arc in cycle:  # If arc is part of the cycle
                    arc_in_cycle = True
                    # Collect the l-attributes of all arcs in the cycle
                    for cycle_arc in cycle:
                        for r in R2:
                            if r['arc'] == cycle_arc:
                                cycle_l_attributes.append(int(r['l-attribute']))  # Store the l-attribute for each arc

            # Calculate eRU for arcs that are part of a cycle
            if arc_in_cycle:
                eRU_list_R2[idx] = min(cycle_l_attributes) if cycle_l_attributes else 0
            else:
                # For arcs not part of a cycle, eRU remains 0 (default value)
                eRU_list_R2[idx] = 0

    # Print the results for R2
    print(f"R2:")  # Header for R2 output
    print('-' * 20)
    print(f"Arcs List ({len(arcs_list_R2)}): {arcs_list_R2}")  # List of arcs in R2
    print(f"Vertices List ({len(vertices_list_R2)}): {vertices_list_R2}")  # Unique vertices in R2
    print(f"C-attribute List ({len(c_attribute_list_R2)}): {c_attribute_list_R2}")  # List of c-attributes
    print(f"L-attribute List ({len(l_attribute_list_R2)}): {l_attribute_list_R2}")  # List of l-attributes
    print(f"eRU List ({len(eRU_list_R2)}): {eRU_list_R2}")  # List of eRU values for each arc
    print('-' * 60)  # Divider for output

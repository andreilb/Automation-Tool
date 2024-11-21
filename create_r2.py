from cycle import Cycle

def ProcessR2(R2):
    """
    Process R2 components: extract arcs, vertices, attributes, and calculate eRU.
    Automatically prints the results.

    Args:
        R2 (list): List of arcs in R2 (each arc is a dictionary with 'arc', 'c-attribute', 'l-attribute').
    """
    # Extract components from R2
    arcs_list_R2 = [r['arc'] for r in R2]
    vertices_list_R2 = sorted(set([v for arc in arcs_list_R2 for v in arc.split(', ')]))
    c_attribute_list_R2 = [r['c-attribute'] for r in R2]
    l_attribute_list_R2 = [r['l-attribute'] for r in R2]

    # Initialize the Cycle object and evaluate cycles
    L_Attributes = [arc['l-attribute'] for arc in R2 if 'l-attribute' in arc]
    cycle_detector = Cycle(R2)  # Create the Cycle object with R2 data
    cycle_R2 = cycle_detector.evaluate_cycle()  # Evaluate cycles in R2
    eRU_values = cycle_detector.calculate_eRU_for_arcs(L_Attributes)
  # Calculate eRU for arcs in R2

    # Initialize eRU_list_R2 to store eRU values for each arc
    eRU_list_R2 = [0] * len(arcs_list_R2)  # Default all eRU values to 0

    # Check if cycles were detected in R2
    if not cycle_R2:
        print("No cycles detected in R2.")
    else:
        # Flatten the cycle list to simplify checking if an arc is part of a cycle
        cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R2]  # Use the list from cycle['cycle']

        # Loop through each arc in R2 and compute its eRU
        for idx, arc in enumerate(arcs_list_R2):
            arc_in_cycle = False
            cycle_l_attributes = []

            # Check if the arc is part of any cycle
            for cycle in cycle_arcs_list:
                if arc in cycle:  # If the arc is in the cycle
                    arc_in_cycle = True
                    # Collect the l-attributes of the arcs in the cycle
                    for cycle_arc in cycle:
                        # Get the corresponding l-attribute for each arc in the cycle
                        for r in R2:
                            if r['arc'] == cycle_arc:
                                cycle_l_attributes.append(int(r['l-attribute']))

            # The eRU for arcs in the cycle is the minimum l-attribute in that cycle
            if arc_in_cycle:
                eRU_list_R2[idx] = min(cycle_l_attributes) if cycle_l_attributes else 0
            else:
                # For arcs not in the cycle, eRU remains 0 (already initialized)
                eRU_list_R2[idx] = 0

    # Print the results for R2
    print(f"R2:")
    print('-' * 20)
    print(f"Arcs List ({len(arcs_list_R2)}): {arcs_list_R2}")
    print(f"Vertices List ({len(vertices_list_R2)}): {vertices_list_R2}")
    print(f"C-attribute List ({len(c_attribute_list_R2)}): {c_attribute_list_R2}")
    print(f"L-attribute List ({len(l_attribute_list_R2)}): {l_attribute_list_R2}")
    print(f"eRU List ({len(eRU_list_R2)}): {eRU_list_R2}")
    print('-' * 60)

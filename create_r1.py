from abstract import AbstractArc  # Ensure the AbstractArc class is imported
from cycle import Cycle  # Ensure the Cycle class is imported

def ProcessR1(arcs_list, l_attribute_list, c_attribute_list, R1, Centers_list, In_list, Out_list, R2):
    """
    Process R1 components: extract arcs, vertices, attributes, and calculate eRU,
    including abstract arcs created from R2. After abstraction, detect cycles in R1
    and update eRU for each cycle.
    Automatically prints the results.
    Returns the updated R1 data.
    """

    # Initialize abstract_arc_data
    abstract_arc_data = []

    # Extract components from R1
    arcs_list_R1 = [r['arc'] for r in R1 if isinstance(r, dict) and 'arc' in r]
    vertices_list_R1 = sorted(set([v for arc in arcs_list_R1 for v in arc.split(', ')]))
    c_attribute_list_R1 = [r.get('c-attribute', '') for r in R1 if isinstance(r, dict)]
    l_attribute_list_R1 = [r.get('l-attribute', '') for r in R1 if isinstance(r, dict)]
    
    # Initialize AbstractArc class and generate abstract arcs
    abstract = AbstractArc(R1, R2, In_list, Out_list, Centers_list, arcs_list)

    # Find abstract vertices
    abstract_vertices = abstract.find_abstract_vertices()
    # print("Final Abstract vertices: ", abstract_vertices)

    # Create abstract arcs
    try:
        prepreFinal_abstractList = abstract.make_abstract_arcs_stepA(abstract_vertices)
    except Exception as e:
        print(f"[ERROR] Failed to generate abstract arcs in Step A: {e}")
        return

    # Add self-loops
    try:
        preFinal_abstractList = abstract.make_abstract_arcs_stepB(prepreFinal_abstractList)
    except Exception as e:
        print(f"[ERROR] Failed to add self-loops in Step B: {e}")
        return

    # Finalize abstract arcs
    try:
        final_abstract_arcs = abstract.make_abstract_arcs_stepC(preFinal_abstractList)
    except Exception as e:
        print(f"[ERROR] Failed to finalize abstract arcs in Step C: {e}")
        return

    # Add r-id to abstract arcs before finding cycles
    r_id_offset = max(
        int(arc['r-id'].split('-')[1]) for arc in R1 if 'r-id' in arc and arc['r-id'].startswith('R1-')
    ) + 1  # Start with the next available r-id

    for arc in final_abstract_arcs:
        # Assign unique r-id to each abstract arc
        arc['r-id'] = f'R1-{r_id_offset}'
        r_id_offset += 1
        abstract_arc_data.append(arc)

    # Add abstract arcs with r-id to R1
    R1.extend(abstract_arc_data)

   # Now detect cycles in the updated R1, which includes abstract arcs with r-id
    cycle_instance = Cycle(R1)  # Create an instance of the Cycle class
    cycle_R1 = cycle_instance.evaluate_cycle()  # Call the method on the instance

    if not cycle_R1:
        print("No cycles detected in R1.")
    else:
        # Create a set to track processed arcs to avoid duplicate cycle detections
        processed_cycles = set()
        
        # Iterate over each cycle
        for cycle in cycle_R1:
            cycle_arcs = tuple(cycle['cycle'])  # List of arcs in the cycle (convert to tuple)
            
            # Check if this cycle has already been processed
            if cycle_arcs not in processed_cycles:
                processed_cycles.add(cycle_arcs)  # Mark this cycle as processed
                
                # Create a set to track processed arcs to avoid duplicate l-attribute lookups
                processed_arcs = set()
                cycle_l_attributes = []
                
                # Iterate over the arcs in this cycle
                for arc in cycle_arcs:
                    if arc not in processed_arcs:
                        processed_arcs.add(arc)
                        
                        # Use next() to get the first matching 'l-attribute', and ensure it returns a valid value
                        l_attribute = next((r['l-attribute'] for r in R1 if r['arc'] == arc), None)
                        
                        # Check if l_attribute is found and convert it to an integer
                        if l_attribute is not None:
                            cycle_l_attributes.append(int(l_attribute))  # Convert to int
                        else:
                            print(f"Warning: 'l-attribute' not found for arc {arc}")
                
                # Now process cycle_l_attributes as needed, and do any further processing.
                print(f"Cycle: {cycle_arcs}, l-attributes: {cycle_l_attributes}")
            else:
                print(f"Cycle {cycle_arcs} already processed, skipping.")


            # Find the minimum l-attribute in the cycle
            min_l_attribute = min(cycle_l_attributes)

            # Update eRU for arcs in the cycle, except for abstract arcs (keep their eRU unchanged)
            for cycle_arc in cycle_arcs:
                for r in R1:
                    if r['arc'] == cycle_arc:
                        if 'eRU' not in r or r['eRU'] == 0:  # Only update if eRU is empty (0)
                            r['eRU'] = min_l_attribute
                            # print(f"Updated eRU for arc {r['arc']} to {r['eRU']}")

    # Print the updated R1 after processing
    print("R1:")
    print("--------------------")
    print(f"Arcs List ({len(R1)}): {[arc['arc'] for arc in R1]}")
    print(f"Vertices List ({len(set(vertex for arc in R1 for vertex in arc['arc'].split(', ')))}): {list(set(vertex for arc in R1 for vertex in arc['arc'].split(', ')))}")
    print(f"C-attribute List ({len(R1)}): {[arc['c-attribute'] for arc in R1]}")
    print(f"L-attribute List ({len(R1)}): {[arc['l-attribute'] for arc in R1]}")
    print(f"eRU List ({len(R1)}): {[arc['eRU'] for arc in R1]}")

    # Return the updated R1
    return R1

if __name__ == '__main__':
    # Define R1, Arcs_List, L_attribute_list, etc.
    R1 = [{'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
          {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0}]
    Arcs_List = ['x1, x2', 'x2, x3', 'x3, x2', 'x2, x4', 'x3, x4', 'x4, x5', 'x4, x6', 'x5, x6', 'x6, x2', 'x6, x7']
    L_attribute_list = ['1', '2', '3', '4', '1', '6', '7', '7', '5', '1']
    C_attribute_list = ['a', '0', '0', '0', '0', '0', 'b', 'a', 'a', '0']
    Centers_list = ['x2']
    In_list = ['x1, x2', 'x6, x2']
    Out_list = ['x4, x5', 'x4, x6']
    R2 = [{'r-id': 'R2-1', 'arc': 'x2, x3', 'l-attribute': '2', 'c-attribute': '0', 'eRU': 0},
          {'r-id': 'R2-2', 'arc': 'x3, x2', 'l-attribute': '3', 'c-attribute': '0', 'eRU': 0}]

    ProcessR1(Arcs_List, L_attribute_list, C_attribute_list, R1, Centers_list, In_list, Out_list, R2)

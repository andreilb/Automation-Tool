from abstract import AbstractArc  # Ensure the AbstractArc class is imported 
from cycle import Cycle  # Ensure the Cycle class is imported

def ProcessR1(arcs_list, l_attribute_list, c_attribute_list, R1, Centers_list, In_list, Out_list, R2):
    """
    Process R1 components: extract arcs, vertices, attributes, and calculate eRU,
    including abstract arcs created from R2.
    Automatically prints the results.
    Returns the updated R1 data.
    """

    # Extract components from R1
    arcs_list_R1 = [r['arc'] for r in R1 if isinstance(r, dict) and 'arc' in r]
    vertices_list_R1 = sorted(set([v for arc in arcs_list_R1 for v in arc.split(', ')]))
    c_attribute_list_R1 = [r['c-attribute'] for r in R1 if isinstance(r, dict) and 'c-attribute' in r]
    l_attribute_list_R1 = [r['l-attribute'] for r in R1 if isinstance(r, dict) and 'l-attribute' in r]
    
    # Initialize AbstractArc class and generate abstract arcs
    abstract = AbstractArc(R1, R2, In_list, Out_list, Centers_list, arcs_list)

    # Step 1: Find abstract vertices
    abstract_vertices = abstract.find_abstract_vertices()
    print("Final Abstract vertices: ", abstract_vertices)

    # Step 2: Create abstract arcs (Step A)
    try:
        prepreFinal_abstractList = abstract.make_abstract_arcs_stepA(abstract_vertices)
        print("AFTER Step A ~~~~~~~~~~~~~~~~~", prepreFinal_abstractList)
    except Exception as e:
        print(f"[ERROR] Failed to generate abstract arcs in Step A: {e}")
        return

    # Step 3: Add self-loops (Step B)
    try:
        preFinal_abstractList = abstract.make_abstract_arcs_stepB(prepreFinal_abstractList)
        print("AFTER Step B ~~~~~~~~~~~~~~~~~", preFinal_abstractList)
    except Exception as e:
        print(f"[ERROR] Failed to add self-loops in Step B: {e}")
        return

    # Step 4: Finalize abstract arcs (Step C)
    try:
        final_abstract_arcs = abstract.make_abstract_arcs_stepC(preFinal_abstractList)
        print("AFTER Step C ~~~~~~~~~~~~~~~~~", final_abstract_arcs)
    except Exception as e:
        print(f"[ERROR] Failed to finalize abstract arcs in Step C: {e}")
        return
        
    # Determine the starting r-id by finding the highest existing r-id in R1
    if R1:
        last_r_id = max(
            int(arc['r-id'].split('-')[1]) for arc in R1 if 'r-id' in arc and arc['r-id'].startswith('R1-')
        )
    else:
        last_r_id = -1  # Start with -1 if R1 is empty

    r_id_offset = last_r_id + 1  # Start with the next r-id after the highest existing one

    for arc in final_abstract_arcs:
        # Create a new dictionary with 'r-id' as the first key, followed by other attributes
        abstract_arc = {
            'r-id': f'R1-{r_id_offset}',  # Assign a unique r-id for each abstract arc
            'arc': arc['arc'],
            'l-attribute': arc['l-attribute'],
            'c-attribute': arc['c-attribute'],
            'eRU': arc['eRU']
        }
        abstract_arc_data.append(abstract_arc)
        r_id_offset += 1  # Increment the r-id for the next abstract arc

    # Add abstract arcs to R1 data
    R1.extend(abstract_arc_data)
    print("Updated R1 after adding abstract arcs:", R1)  # Print to check if arcs are appended correctly

    # Return the updated R1
    return R1


if __name__ == '__main__':
    # Sample R1, Arcs_List, L_attribute_list, etc.
    R1 = [{'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
          {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0},
          {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0},
          {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 0},
          {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 0},
          {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}]
    
    Arcs_List = ['x1, x2', 'x2, x3', 'x3, x2', 'x2, x4', 'x3, x4', 'x4, x5', 'x4, x6', 'x5, x6', 'x6, x2', 'x6, x7']
    L_attribute_list = ['1', '2', '3', '4', '1', '6', '7', '7', '5', '1']
    C_attribute_list = ['a', '0', '0', '0', '0', '0', 'b', 'a', 'a', '0']
    Centers_list = ['x2']
    In_list = ['x1, x2', 'x6, x2']
    Out_list = ['x4, x5', 'x4, x6']
    R2 = [{'r-id': 'R2-1', 'arc': 'x2, x3', 'l-attribute': '2', 'c-attribute': '0', 'eRU': 0},
          {'r-id': 'R2-2', 'arc': 'x3, x2', 'l-attribute': '3', 'c-attribute': '0', 'eRU': 0},
          {'r-id': 'R2-3', 'arc': 'x2, x4', 'l-attribute': '4', 'c-attribute': '0', 'eRU': 0},
          {'r-id': 'R2-4', 'arc': 'x3, x4', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}]

    ProcessR1(
        Arcs_List,
        L_attribute_list,
        C_attribute_list,
        R1,
        Centers_list,
        In_list,
        Out_list,
        R2)

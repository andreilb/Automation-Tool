# from abstract import AbstractArc  # Ensure you have this class defined correctly
# from cycle import Cycle  # Ensure you have this class defined correctly

# def ProcessR1(arcs_list, l_attribute_list, c_attribute_list, R1, Centers_list, In_list, Out_list, R2):
#     """
#     Process R1 components: extract arcs, vertices, attributes, and calculate eRU,
#     including abstract arcs created from R2.
#     Automatically prints the results.
#     """
#     input_rdlt_data = R1

#     if isinstance(input_rdlt_data, list):
#         R1 = input_rdlt_data
#         R2 = []  # Default empty if not provided
#     elif isinstance(input_rdlt_data, dict):
#         R1 = input_rdlt_data.get('R1', [])
#         R2 = input_rdlt_data.get('R2', [])
#     else:
#         print("[ERROR] Invalid input data format.")
#         return

#     # Extract components from R1
#     arcs_list_R1 = [r['arc'] for r in R1 if isinstance(r, dict) and 'arc' in r]
#     vertices_list_R1 = sorted(set([v for arc in arcs_list_R1 for v in arc.split(', ')]))
#     c_attribute_list_R1 = [r['c-attribute'] for r in R1 if isinstance(r, dict) and 'c-attribute' in r]
#     l_attribute_list_R1 = [r['l-attribute'] for r in R1 if isinstance(r, dict) and 'l-attribute' in r]
    
#     # Initialize AbstractArc class and generate abstract arcs
#     abstract = AbstractArc(R1, R2, In_list, Out_list, Centers_list, arcs_list)

#     abstract_vertices = abstract.find_abstract_vertices()
#     print("Final Abstract vertices: ", abstract_vertices)
#     # Step 2: Create abstract arcs (Step A)
#     prepreFinal_abstractList = abstract.make_abstract_arcs_stepA(abstract_vertices)
#     print("AFTER stepA ~~~~~~~~~~~~~~~~~", prepreFinal_abstractList)
#     # Step 3: Add self-loops (Step B)
#     preFinal_abstractList = abstract.make_abstract_arcs_stepB(prepreFinal_abstractList)
#     print("AFTER stepB ~~~~~~~~~~~~~~~~~", preFinal_abstractList)
#     # Step 4: Finalize abstract arcs (Step C)
#     final_abstract_arcs = abstract.make_abstract_arcs_stepC(preFinal_abstractList)
#     print("AFTER stepC ~~~~~~~~~~~~~~~~~", final_abstract_arcs)
    
#     # Assuming final_abstract_arcs is a list of dictionaries with keys 'start' and 'end'
#     abstract_arc_data = []
#     r_id_offset = len(R1)  # To create unique r-ids for the new abstract arcs

#     for arc in final_abstract_arcs:
#         if isinstance(arc, tuple) and len(arc) == 2:
#             arc_start, arc_end = arc  # Extract start and end directly if it's a tuple
#         else:
#             print(f"Unexpected arc format: {arc}")
#             continue  # Skip if the format is not as expected
        
#         # Assuming abstract arc has attributes already set (c-attribute, l-attribute, eRU)
#         abstract_arc = {
#             'r-id': f'R1-{r_id_offset}',  # Assign a unique r-id for each abstract arc
#             'arc': f"{arc_start}, {arc_end}",  # Define the arc format
#             'c-attribute': '0',  # Default c-attribute, will be updated later if needed
#             'l-attribute': 0,  # Default l-attribute, will be updated later
#             'eRU': 0  # Initial eRU, to be calculated
#         }
#         abstract_arc_data.append(abstract_arc)
#         r_id_offset += 1  # Increment the r-id for the next abstract arc

#     # Add abstract arcs to R1
#     R1.extend(abstract_arc_data)

#     # Initialize the Cycle object and evaluate cycles with the abstract arcs
#     cycle_detector = Cycle(R1)  # Now we pass R1 directly
#     cycle_R1 = cycle_detector.evaluate_cycle()  # This will store detected cycles in cycle_R1

#     # Initialize eRU_list_R1 to store eRU values for each arc
#     eRU_list_R1 = [0] * len(arcs_list_R1)

#     if not cycle_R1:
#         print("No cycles detected in R1.")
#     else:
#         # Loop through each arc in R1 and compute its eRU
#         cycle_arcs_list = [cycle['cycle'] for cycle in cycle_R1]
#         for idx, arc in enumerate(arcs_list_R1):
#             arc_in_cycle = False
#             cycle_l_attributes = []
#             for cycle in cycle_arcs_list:
#                 if arc in cycle:
#                     arc_in_cycle = True
#                     for cycle_arc in cycle:
#                         for r in R1:
#                             if r['arc'] == cycle_arc:
#                                 cycle_l_attributes.append(int(r['l-attribute']))
#             if arc_in_cycle:
#                 eRU_list_R1[idx] = min(cycle_l_attributes) if cycle_l_attributes else 0
#             else:
#                 eRU_list_R1[idx] = 0

#     # Print eRU values for the arcs
#     for arc, eRU in zip(arcs_list_R1, eRU_list_R1):
#         print(f"Arc: {arc}, eRU: {eRU}")

#     # Print the results for R1
#     print(f"\nR1:")
#     print('-' * 20)
#     print(f"Arcs List ({len(arcs_list_R1)}): {arcs_list_R1}")
#     print(f"Vertices List ({len(vertices_list_R1)}): {vertices_list_R1}")
#     print(f"C-attribute List ({len(c_attribute_list_R1)}): {c_attribute_list_R1}")
#     print(f"L-attribute List ({len(l_attribute_list_R1)}): {l_attribute_list_R1}")
#     print(f"eRU List ({len(eRU_list_R1)}): {eRU_list_R1}")
#     print('-' * 60)


# if __name__ == '__main__':
#     R1 =  [{'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0}, {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0}, {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0}, {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 0}, {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 0}, {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}]
#     Arcs_List = ['x1, x2', 'x2, x3', 'x3, x2', 'x2, x4', 'x3, x4', 'x4, x5', 'x4, x6', 'x5, x6', 'x6, x2', 'x6, x7']
#     L_attribute_list = ['1', '2', '3', '4', '1', '6', '7', '7', '5', '1']
#     C_attribute_list = ['a', '0', '0', '0', '0', '0', 'b', 'a', 'a', '0']
#     Centers_list = ['x2']
#     In_list = ['x1, x2', 'x6, x2']
#     Out_list = ['x4, x5', 'x4, x6']
#     R2 = [{'r-id': 'R2-1', 'arc': 'x2, x3', 'l-attribute': '2', 'c-attribute': '0', 'eRU': 0}, {'r-id': 'R2-2', 'arc': 'x3, x2', 'l-attribute': '3', 'c-attribute': '0', 'eRU': 0}, {'r-id': 'R2-3', 'arc': 'x2, x4', 'l-attribute': '4', 'c-attribute': '0', 'eRU': 0}, {'r-id': 'R2-4', 'arc': 'x3, x4', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}]

#     ProcessR1(
#         Arcs_List,
#         L_attribute_list,
#         C_attribute_list,
#         R1,
#         Centers_list,
#         In_list,
#         Out_list,
#         R2)

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
    
    # # Add abstract arcs to the R1 data (Make sure they are in the proper format)
    # abstract_arc_data = []
    # r_id_offset = len(R1)  # Start with the next r-id after the existing R1 data length

    # print("abstract arc data:", abstract_arc_data)
    # for arc in final_abstract_arcs:
    #     if isinstance(arc, tuple) and len(arc) == 2:
    #         arc_start, arc_end = arc  # Extract start and end directly if it's a tuple
    #     else:
    #         print(f"Unexpected arc format: {arc}")
    #         continue  # Skip if the format is not as expected
        
    #     # Create the abstract arc dictionary with the r-id and other necessary attributes
    #     abstract_arc = {
    #         'r-id': f'R1-{r_id_offset}',  # Assign a unique r-id for each abstract arc
    #         'arc': f"{arc_start}, {arc_end}",  # Arc format as a string
    #         'c-attribute': '0',  # Default c-attribute for abstract arcs
    #         'l-attribute': 0,  # Default l-attribute for abstract arcs
    #         'eRU': 0  # Initial eRU for abstract arcs, to be calculated later
    #     }
    #     abstract_arc_data.append(abstract_arc)
    #     r_id_offset += 1  # Increment the r-id for the next abstract arc

    # # Add abstract arcs to R1 data
    # R1.extend(abstract_arc_data)
    # print("Updated R1 after adding abstract arcs:", R1)  # Print to check if arcs are appended correctly

    # # Return the updated R1
    # return R1

    # Add r-id to each abstract arc and append to R1 data



    # abstract_arc_data = []
    # r_id_offset = len(R1)  # Start with the next r-id after the existing R1 data length

    # print("abstract arc data:", abstract_arc_data)
    # for arc in final_abstract_arcs:
    #     # Add r-id for each abstract arc and keep other attributes intact
    #     abstract_arc = arc.copy()  # Copy the original abstract arc data
        
    #     # Add the r-id to the abstract arc
    #     abstract_arc['r-id'] = f'R1-{r_id_offset}'  # Assign a unique r-id for each abstract arc
    #     abstract_arc_data.append(abstract_arc)
    #     r_id_offset += 1  # Increment the r-id for the next abstract arc

    # # Add abstract arcs to R1 data
    # R1.extend(abstract_arc_data)
    # print("Updated R1 after adding abstract arcs:", R1)  # Print to check if arcs are appended correctly

    # # Return the updated R1
    # return R1

    # Add abstract arcs to R1 data
    abstract_arc_data = []

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

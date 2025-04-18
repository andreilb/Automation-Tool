"""
RDLT EVSA R1 Processing Module

This module provides functionality for processing R1 components in the RDLT.
It handles the extraction of arcs, vertices, and attributes from R1, and performs abstraction operations when R2 exists.
The module includes cycle detection and expanded reusability (eRU) calculation.

Key operations performed:
1. Extraction of components from R1 (arcs, vertices, attributes)
2. Creation of abstract arcs from R2 when applicable
3. Integration of abstract arcs into R1
4. Cycle detection in R1 and calculation of eRU values using the Cycle class

"""

from abstract import AbstractArc
from cycle import Cycle
import utils

def ProcessR1(arcs_list, R1, Centers_list, In_list, Out_list, R2):
    """
    Process R1 components: extracts arcs, vertices, attributes, and calculates eRU.
    If R2 exists, abstract arcs are generated from R2 and added to R1.
    After the creation of abstract arcs, cycles are detected in R1 and eRU is updated accordingly.

    Parameters:
        arcs_list (list): List of arcs in the RDLT.
        R1 (list): List of dictionaries representing arcs with their attributes in R1.
        Centers_list (list): List of center vertices for Reset-Bound Subsystem (RBS).
        In_list (list): List of in-bridge arcs in RBS.
        Out_list (list): List of out-bridge arcs in RBS.
        R2 (list): The Reset-Bound Subsystem (RBS) structure.

    Returns:
        list: Updated R1 with abstract arcs (if applicable) and computed eRU values.
    """
    
    # Initialize abstract_arc_data
    abstract_arc_data = []
    added_abstract_arcs = []  # Initialize here to avoid reference before assignment
    
    # Extract components from R1
    arcs_list_R1 = [r['arc'] for r in R1 if isinstance(r, dict) and 'arc' in r]
    vertices_list_R1 = sorted(set([v for arc in arcs_list_R1 for v in arc.split(', ')]))
    c_attribute_list_R1 = [r.get('c-attribute', '') for r in R1 if isinstance(r, dict)]
    l_attribute_list_R1 = [r.get('l-attribute', '') for r in R1 if isinstance(r, dict)]

    # Check if R2 exists
    if R2:  # Check if R2 is not empty or None

        # Initialize AbstractArc class and generate abstract arcs
        abstract = AbstractArc(R1, R2, In_list, Out_list, Centers_list, arcs_list)

        # Identify abstract vertices
        abstract_vertices = abstract.find_abstract_vertices()
        # print("Final Abstract vertices: ", abstract_vertices)

        try:
            # Create initial abstract arcs
            prepreFinal_abstractList = abstract.make_abstract_arcs_stepA(abstract_vertices)
            # print("Step A PrepreFinal Abstract List on try: ", prepreFinal_abstractList)
        except Exception as e:
            print(f"[ERROR] Failed to generate abstract arcs in Step A: {e}")
            return

        try:
            # Add self-loops to abstract arcs
            preFinal_abstractList = abstract.make_abstract_arcs_stepB(prepreFinal_abstractList)
            # print("Step B PreFinal Abstract List on try: ", preFinal_abstractList)
        except Exception as e:
            print(f"[ERROR] Failed to add self-loops in Step B: {e}")
            return

        try:
            # Finalize abstract arcs
            final_abstract_arcs = abstract.make_abstract_arcs_stepC(preFinal_abstractList)
            # print("Step C Final Abstract Arcs on try: ", final_abstract_arcs)
        except Exception as e:
             print(f"[ERROR] Failed to finalize abstract arcs in Step C: {e}")
             return

        # Assign unique r-ids to abstract arcs before adding to R1
        a_id_offset = 1 

        for arc in final_abstract_arcs:
            # Assign unique r-id
            if 'r-id' not in arc or not arc['r-id']:  # Check if r-id is missing or empty
                arc['r-id'] = f'A-{a_id_offset}'
                a_id_offset += 1  # Increment the counter for the next abstract arc
                
            # Make sure c-attribute, l-attribute, and eRU are set
            if 'c-attribute' not in arc:
                arc['c-attribute'] = ''  # Set appropriate default value
            if 'l-attribute' not in arc:
                arc['l-attribute'] = '0'  # Set appropriate default value
            if 'eRU' not in arc:
                arc['eRU'] = '0'  # Set appropriate default value
                
            # Mark as abstract arc to prevent eRU update during cycle detection
            arc['is_abstract'] = True

            # Append a copy to prevent unintended modification
            abstract_arc_data.append(arc.copy())

        # Add abstract arcs with r-id to R1
        # Store initial length before adding abstract arcs
        initial_length = len(R1)  

        # Add abstract arcs to R1
        R1.extend(abstract_arc_data)

        # Extract only the added abstract arcs
        added_abstract_arcs = R1[initial_length:]

            # # Debug: Verify extracted list
            # print(f"Added Abstract Arcs: {added_abstract_arcs}")

            # print("Abstract Arcs Added to R1: ", abstract_arc_data)
    else:
        print("\nNo R2 provided, skipping abstract arc generation.\n")
        print('-' * 30)

    # Create a list to hold arcs with the minimum l-attribute across all cycles
    all_cycle_arcs_with_min_l = []

    # Detect cycles in the updated R1 (with abstract arcs included if applicable)
    cycle_instance = Cycle(R1)  # Create an instance of the Cycle class
    cycle_R1 = cycle_instance.evaluate_cycle()  # Call the method on the instance

    if cycle_R1:
        # Iterate over each cycle
        for cycle_data in cycle_R1:
            cycle_arcs = cycle_data['cycle']
            cycle_l_attributes = []
            cycle_arcs_with_min_l = []

            # Iterate over the arcs in the cycle
            for cycle_arc in cycle_arcs:
                # Extract the r-id and arc name
                r_id, arc_name = cycle_arc.split(": ")
                arc_name = arc_name.strip()

                # Get the actual arc from R1 using r-id
                actual_arc = utils.get_arc_from_rid(r_id, R1)

                if actual_arc:
                    # print(f"Processing arc: {actual_arc}")

                    # Check if l-attribute exists and process it
                    matching_arc = next((r for r in R1 if r['arc'] == actual_arc), None)
                    if matching_arc:
                        l_attribute = matching_arc.get('l-attribute', None)
                        if l_attribute is not None:
                            cycle_l_attributes.append(int(l_attribute))  # Convert to int
                        else:
                            print(f"Warning: 'l-attribute' not found for arc {actual_arc}")
                    else:
                        print(f"Warning: No matching arc found for {actual_arc} in R1")
                else:
                    print(f"Warning: No arc found in R1 for r-id {r_id}")

            # Assuming that the 'ca' (critical arc) value is the minimum l-attribute in the cycle
            ca = min(cycle_l_attributes) if cycle_l_attributes else None

            if ca is not None:
                # print(f"Critical arc 'ca' value: {ca}")

                # Iterate over all arcs in the cycle and set their eRU to the 'ca' value
                for cycle_arc in cycle_arcs:
                    r_id, arc_name = cycle_arc.split(": ")
                    arc_name = arc_name.strip()

                    # Get the actual arc from R1 using r-id
                    actual_arc = utils.get_arc_from_rid(r_id, R1)

                    if actual_arc:
                        # Find the matching arc in R1
                        matching_arc = next((r for r in R1 if r['arc'] == actual_arc), None)

                        if matching_arc:
                            # Check if the arc is an abstract arc
                            if matching_arc.get('is_abstract', False):
                                # Skip updating eRU for abstract arcs
                                # print(f"Skipping eRU update for abstract arc: {matching_arc['arc']}")
                                continue
                            else:
                                # Set eRU to the critical arc's 'ca' value
                                matching_arc['eRU'] = ca
                                # print(f"Set eRU for arc {matching_arc['arc']} to {matching_arc['eRU']}")

                            # Compare l-attribute and eRU for each arc, and append arcs with the minimum l-attribute value
                            # Only include non-abstract arcs in the critical arc list
                            if not matching_arc.get('is_abstract', False) and int(matching_arc['l-attribute']) == ca:
                                cycle_arcs_with_min_l.append(matching_arc)

            else:
                print("\nNo critical arc found in this cycle.\n")
                print('-' * 30)

            # Add all the arcs with the minimum l-attribute for this cycle to the global list
            all_cycle_arcs_with_min_l.extend(cycle_arcs_with_min_l)

    # Fixes incorrectly formatted eRU with no ''
    eRU_list = [str(r.get('eRU', '0')) for r in R1] 
    abstract_list = [str(r.get('arc')) for r in added_abstract_arcs] 
    abstract_l = [str(r.get('l-attribute')) for r in added_abstract_arcs] 
    abstract_c = [str(r.get('c-attribute')) for r in added_abstract_arcs] 

    def convert_arc_format(arc):
        """
        Converts an arc from the format "x, y" to the format "(x, y)".
        
        Parameters:
            arc (str): Arc string in the format "x, y".
            
        Returns:
            str: Arc string in the format "(x, y)".
        """
        return f"({arc.split(', ')[0]}, {arc.split(', ')[1]})"
        
    def convert_arc_list_format(arc_list):
        """
        Converts a list of arcs from the format "x, y" to the format "(x, y)".
        
        Parameters:
            arc_list (list): List of arc strings in the format "x, y".
            
        Returns:
            list: List of arc strings in the format "(x, y)".
        """
        return [convert_arc_format(arc) for arc in arc_list]

    # Print debugging results
    print("R1:")
    print('-' * 20)
    print(f"Arcs List ({len(arcs_list_R1 + abstract_list)}): {convert_arc_list_format(arcs_list_R1 + abstract_list)}")
    print(f"C-attribute List ({len(c_attribute_list_R1 + abstract_c)}): {c_attribute_list_R1 + abstract_c}")
    print(f"L-attribute List ({len(l_attribute_list_R1 + abstract_l)}): {l_attribute_list_R1 + abstract_l }")
    print(f"eRU List ({len(eRU_list)}): {eRU_list}")
    print('=' * 60)


    return R1
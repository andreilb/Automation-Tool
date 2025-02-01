class TestJoins:
    
    def get_target_vertex(arc):
        """
        Extracts the target vertex from the given arc string.

        This method splits the arc string and retrieves the last element, which represents the target vertex.

        Args:
            - arc (str): A string representing an arc, formatted as "start, end".

        Returns:
            str: The target vertex extracted from the arc.
        """
        target_vertex = arc.split(', ')[-1]
        # print(f"Extracted target vertex: {target_vertex}")  # Debugging output
        return target_vertex
    
    def group_arcs_by_target_vertex(R2):
        """
        Groups arcs in R2 by their target vertex and assigns a 'join-id' to each group.

        This method processes the arcs in R2 and groups them based on their target vertices. 
        Each group is assigned a unique 'join-id' and a list of arcs that share the same target vertex.

        Parameters:
            R2 (list): A list of dictionaries where each dictionary represents an arc with a 'arc' key.

        Returns:
            list: A list of dictionaries, each containing a 'join-id' and a list of 'join arcs'.
                  Each dictionary represents a group of arcs that share the same target vertex.
        """
        # print("Starting to group arcs by target vertex...")  # Debugging output
        target_vertex_groups = {}

        for r in R2:
            target_vertex = TestJoins.get_target_vertex(r['arc'])
            if target_vertex not in target_vertex_groups:
                target_vertex_groups[target_vertex] = []

            target_vertex_groups[target_vertex].append(r['arc'])

        result = []
        for idx, (target_vertex, arcs) in enumerate(target_vertex_groups.items(), start=1):
            result.append({
                'join-id': f'j{idx}-{target_vertex}',
                'join arcs': arcs
            })
            # print(f"Grouped arcs for target vertex '{target_vertex}': {arcs}")  # Debugging output

        return result

    def checkSimilarTargetVertexAndUpdate(R1, R2):
        """
        Checks if arcs in R2 with the same target vertex have consistent c-attributes. 
        Based on this check, the function decides whether to use only R1 data or combine R1 and R2 data.

        If all arcs in a group (sharing the same target vertex) have the same c-attribute, 
        only R1 data is used. Otherwise, data from both R1 and R2 is combined.

        Parameters:
            - R1 (dict): A dictionary of arcs and their associated attributes (e.g., 'c-attribute', 'l-attribute').
            - R2 (dict): A dictionary of arcs and their associated attributes to be checked for consistency with R1.

        Returns:
            list: If all c-attributes are consistent, returns R1. Otherwise, combines data from both R1 and R2.
        """
        # print("Checking if arcs in R2 with the same target vertex have the same c-attribute...")  # Debugging output
        
        target_vertex_groups = TestJoins.group_arcs_by_target_vertex(R2)

        all_groups_same_c_attribute = True
        for group in target_vertex_groups:
            c_attributes = {arc['c-attribute'] for arc in R2 if arc['arc'] in group['join arcs']}
            # print(f"Checking group {group['join-id']} with c-attributes: {c_attributes}")  # Debugging output
            if len(c_attributes) > 1:
                all_groups_same_c_attribute = False
                # print("Inconsistent c-attributes found in this group.")  # Debugging output
                break

        if all_groups_same_c_attribute:
            # print("\nAll JOINs in R2 are OR-JOINs.\n")
            # print("Using data only from R1...")
            # TestJoins.print_updated_data(R1)
            return R1  # Only use R1
        else:
            # print("Some groups of arcs in R2 with the same target vertex have different c-attributes.")
            # print("Using data from both R1 and R2:")
            # TestJoins.print_updated_data(R1)
            # print("R2:")
            # TestJoins.print_updated_data(R2)  # Debugging output for R2
            return R1 + R2  # Use both R1 and R2

    def print_updated_data(data):
        """
        Prints the updated data (arcs, vertices, c-attribute, l-attribute, and eRU) in a human-readable format.

        This method takes a list of arcs and prints the following details:
            - List of arcs
            - List of vertices (extracted from the arcs)
            - List of c-attributes
            - List of l-attributes
            - List of effective reusability (eRU) values

        Parameters:
            data (list): A list of dictionaries representing arcs and their associated attributes.

        Returns:
            None
        """
        print(f"Arcs List ({len(data)}): {[arc['arc'] for arc in data]}")
        print(f"Vertices List ({len(set(arc['arc'].split(', ')[-1] for arc in data))}): {[arc['arc'].split(', ')[-1] for arc in data]}")
        print(f"C-attribute List ({len(data)}): {[arc.get('c-attribute', 'N/A') for arc in data]}")
        print(f"L-attribute List ({len(data)}): {[arc.get('l-attribute', 'N/A') for arc in data]}")
        print(f"eRU List ({len(data)}): {[arc.get('eRU', 'N/A') for arc in data]}")

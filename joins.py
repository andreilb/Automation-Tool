"""
RDLT Join Analysis Module

This module provides functionality for analyzing and processing JOIN patterns in an RDLT.
It focuses on identifying, grouping, and analyzing arcs that share the same target vertex, which represent JOIN patterns in the RDLT.

"""

class TestJoins:
    """
    This class provides methods for analyzing JOIN patterns in an RDLT. It contains methods that identify, group, 
    and analyze arcs that share the same target vertex. These shared target vertices represent JOIN points 
    in the RDLT where multiple arcs converge.
    
    The class performs analysis to determine whether the RBS contains all OR-JOINs or not.
    
    Methods:
        get_target_vertex(arc): Extracts the target vertex from an arc string.
        group_arcs_by_target_vertex(R2): Groups arcs by their target vertex.
        checkSimilarTargetVertexAndUpdate(R1, R2): Checks for JOIN consistency and updates data accordingly.
        print_updated_data(data): Prints the processed data in a human-readable format.
    """
    
    @staticmethod
    def get_target_vertex(arc):
        """
        Extracts the target vertex from the given arc string.

        This method splits the arc string and retrieves the last element, which represents the target vertex.

        Args:
            arc (str): A string representing an arc, formatted as "start, end".

        Returns:
            str: The target vertex extracted from the arc.
        """
        target_vertex = arc.split(', ')[-1]
        # print(f"Extracted target vertex: {target_vertex}")  # Debugging output
        return target_vertex
    
    @staticmethod
    def group_arcs_by_target_vertex(R2):
        """
        Groups arcs in R2 by their target vertex and assigns a 'join-id' to each group.

        This method processes the arcs in R2 and groups them based on their target vertices. 
        Each group is assigned a unique 'join-id' and a list of arcs that share the same target vertex.

        Args:
            R2 (list): A list of dictionaries where each dictionary represents an arc with an 'arc' key.

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

    @staticmethod
    def checkSimilarTargetVertexAndUpdate(R1, R2):
        """
        Checks if arcs in R2 with the same target vertex have consistent c-attributes. 
        Based on this check, the function decides whether to use only R1 data or combine R1 and R2 data.

        If all arcs in a group (sharing the same target vertex) have the same c-attribute, 
        only R1 data is used (OR-JOIN case). Otherwise, data from both R1 and R2 is combined (mixed JOIN case).

        Args:
            R1 (list): A list of dictionaries representing arcs and their associated attributes from the R1 structure.
            R2 (list): A list of dictionaries representing arcs and their associated attributes from the R2 structure.

        Returns:
            list: If all c-attributes are consistent (OR-JOINs), returns R1. 
                  Otherwise (mixed JOINs), combines data from both R1 and R2.
        """
        # print("Checking if arcs in R2 with the same target vertex have the same c-attribute...")  # Debugging output
        
        target_vertex_groups = TestJoins.group_arcs_by_target_vertex(R2)

        all_groups_same_c_attribute = True
        for group in target_vertex_groups:
            c_attributes = {arc['c-attribute'] for arc in R2 if arc['arc'] in group['join arcs']}
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
            # print("\nR2 contains other types of JOINs.\n")
            # print("Using data from both R1 and R2:")
            # TestJoins.print_updated_data(R1)
            # print("R2:")
            # TestJoins.print_updated_data(R2)  # Debugging output for R2
            return R1 + R2  # Use both R1 and R2
    
    @staticmethod
    def print_updated_data(data):
        """
        Prints the updated data (arcs, vertices, c-attribute, l-attribute, and eRU) in a human-readable format.

        This method takes a list of arcs and prints the following details:
            - List of arcs
            - List of vertices (extracted from the arcs)
            - List of c-attributes
            - List of l-attributes
            - List of effective reusability (eRU) values

        Args:
            data (list): A list of dictionaries representing arcs and their associated attributes.

        Returns:
            None
        """
        print(f"Arcs List ({len(data)}): {[arc['arc'] for arc in data]}")
        print(f"Vertices List ({len(set(arc['arc'].split(', ')[-1] for arc in data))}): {[arc['arc'].split(', ')[-1] for arc in data]}")
        print(f"C-attribute List ({len(data)}): {[arc.get('c-attribute', 'N/A') for arc in data]}")
        print(f"L-attribute List ({len(data)}): {[arc.get('l-attribute', 'N/A') for arc in data]}")
        print(f"eRU List ({len(data)}): {[arc.get('eRU', 'N/A') for arc in data]}")

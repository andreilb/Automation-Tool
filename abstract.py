# import utils

# class AbstractArc:
#     def __init__(self, R1, R2, In_list, Out_list, Centers_list, Arcs_List):
#         """
#         Initialize the AbstractArc class with the required inputs.

#         Args:
#             R1 (list): List of dictionaries representing arcs outside the RBS with attributes.
#             R2 (list): List of dictionaries representing arcs inside the RBS with attributes.
#             In_list (list): List of in-bridges (arcs entering the RBS).
#             Out_list (list): List of out-bridges (arcs exiting the RBS).
#             Centers_list (list): List of center vertices marking RBS entry points.
#             Arcs_List (list): Complete list of arcs as strings.
#         """
#         self.R1 = R1
#         self.R2 = R2
#         self.In_list = In_list
#         self.Out_list = Out_list
#         self.Centers_list = Centers_list
#         self.Arcs_List = Arcs_List
#         self.abstract_arcs = []  # Store the final abstract arcs created.

#     def unique(self, Arcs_List):
#         """
#         Extract all unique vertices from a list of arcs.

#         Args:
#             Arcs_List (list): List of arcs as strings, e.g., "x1, x2".

#         Returns:
#             list: Sorted list of unique vertices.
#         """
#         unique_vertices = set()
#         for arc in Arcs_List:
#             # Split each arc string into its vertices and add to the set.
#             vertices = arc.split(', ')
#             unique_vertices.update(vertices)
#         return sorted(unique_vertices)  # Return sorted unique vertices.

#     def find_abstract_vertices(self):
#         """
#         Identify all abstract vertices used for creating abstract arcs.

#         Combines center vertices, in-bridge end vertices, and out-bridge start vertices.

#         Returns:
#             list: Unique list of abstract vertices.
#         """
#         # Extract the target vertex of in-bridges and source vertex of out-bridges.
#         abstract_v_in_list = [arc.split(', ')[1] for arc in self.In_list]
#         abstract_v_out_list = [arc.split(', ')[0] for arc in self.Out_list]

#         # Combine and remove duplicates.
#         abstract_vertices = self.Centers_list + abstract_v_in_list + abstract_v_out_list
#         return list(set(abstract_vertices))  # Ensure uniqueness.

#     def make_abstract_arcs_stepA(self, abstract_vertices):
#         """
#         Step A: Create abstract arcs between in-bridge and out-bridge vertices.

#         This method constructs abstract arcs by:
#         - Converting R2 to a graph structure.
#         - Finding all paths between in-bridge and out-bridge vertices.
#         - Filtering paths to retain only those involving abstract vertices.

#         Args:
#             abstract_vertices (list): List of vertices relevant to abstract arcs.

#         Returns:
#             list: Abstract arcs identified in this step.
#         """
#         abstract_arcs = []  # To store the final abstract arcs.
#         seen_pairs = set()  # To avoid redundant path calculations for vertex pairs.
#         all_paths = []  # For debugging or reference; stores all raw paths as arcs.

#         # Convert R2 arcs to a graph representation for pathfinding.
#         arc_list = [arc['arc'] for arc in self.R2]
#         graph = utils.list_to_graph(arc_list)

#         for in_bridge in self.In_list:
#             # Extract the in-bridge's target vertex (end vertex of the arc).
#             in_vertex = in_bridge.split(', ')[1]
#             if in_vertex not in abstract_vertices:
#                 # Skip if the vertex is not part of the abstract vertices.
#                 continue

#             for out_vertex in abstract_vertices:
#                 if in_vertex != out_vertex:
#                     # Avoid redundant processing for the same vertex pair.
#                     vertex_pair = (in_vertex, out_vertex)
#                     if vertex_pair in seen_pairs:
#                         continue
#                     seen_pairs.add(vertex_pair)

#                     # Find all paths from in_vertex to out_vertex.
#                     paths = utils.find_all_paths(graph, in_vertex, out_vertex)
#                     if paths:
#                         for path in paths:
#                             arcs = [
#                                 f"{path[i]}, {path[i + 1]}" for i in range(len(path) - 1)
#                             ]
#                             all_paths.append(arcs)

#                             # Filter paths to retain only those involving abstract vertices.
#                             if len(path) > 1:
#                                 start_vertex = path[0]
#                                 end_vertex = path[-1]
#                                 if start_vertex in abstract_vertices and end_vertex in abstract_vertices:
#                                     abstract_arcs.append(f"{start_vertex}, {end_vertex}")
#                             else:
#                                 # For single arcs, ensure both vertices are abstract vertices.
#                                 for arc in arcs:
#                                     if arc.split(', ')[0] in abstract_vertices and arc.split(', ')[1] in abstract_vertices:
#                                         abstract_arcs.append(arc)

#         return abstract_arcs

#     def make_abstract_arcs_stepB(self, abstract_arcs):
#         """
#         Step B: Add self-loops for in-bridge vertices to abstract arcs.

#         Identifies self-loops (paths from a vertex to itself) and adds them to the list.

#         Args:
#             abstract_arcs (list): List of existing abstract arcs.

#         Returns:
#             list: Updated list of abstract arcs including self-loops.
#         """
#         processed_in_vertices = set()  # Track processed vertices for self-loops.

#         for in_bridge in self.In_list:
#             # Extract the target vertex of the in-bridge.
#             in_vertex = in_bridge.split(', ')[1]
#             if in_vertex in processed_in_vertices:
#                 continue
#             processed_in_vertices.add(in_vertex)

#             # Find self-loops (paths from in_vertex to itself).
#             paths = utils.find_all_paths(self.R2, in_vertex, in_vertex)
#             if paths:
#                 for path in paths:
#                     if len(path) > 1:
#                         start_vertex = path[0]
#                         end_vertex = path[-1]
#                         if start_vertex == in_vertex and end_vertex == in_vertex:
#                             filtered_arc = f"{start_vertex}, {end_vertex}"
#                             if filtered_arc not in abstract_arcs:
#                                 abstract_arcs.append(filtered_arc)

#             # Directly add a formatted self-loop if no explicit paths are found.
#             formatted_arc = f"{in_vertex}, {in_vertex}"
#             if formatted_arc not in abstract_arcs:
#                 abstract_arcs.append(formatted_arc)

#         return abstract_arcs

#     def make_abstract_arcs_stepC(self, abstract_arcs):
#         """
#         Step C: Finalize abstract arcs by assigning attributes.

#         Adds derived attributes (e.g., `c-attribute`, `l-attribute`, `eRU`) to each abstract arc.

#         Args:
#             abstract_arcs (list): List of abstract arcs as strings.

#         Returns:
#             list: Finalized list of abstract arcs with attributes.
#         """
#         finalized_arcs = []  # To store the finalized abstract arcs.

#         for arc in abstract_arcs:
#             # Split arc into start and end vertices.
#             start, end = arc.split(', ') if isinstance(arc, str) else arc

#             # Assign attributes to the abstract arc.
#             c_attribute = 0  # Abstract arcs are unconstrained.
#             eRU = self.calculate_eRU(start, end)  # Effective reusability.
#             l_attribute = eRU + 1  # Derived l-attribute.

#             # Store the arc with attributes in dictionary format.
#             finalized_arcs.append({
#                 'arc': f"{start}, {end}",
#                 'c-attribute': c_attribute,
#                 'l-attribute': l_attribute,
#                 'eRU': eRU
#             })

#         return finalized_arcs

#     def calculate_eRU(self, start, end):
#         """
#         Calculate the effective reusability (eRU) for an abstract arc.

#         Args:
#             start (str): Start vertex of the arc.
#             end (str): End vertex of the arc.

#         Returns:
#             int: Effective reusability (eRU) for the arc.
#         """
#         eRU = 0  # Initialize eRU to zero.

#         # Loop through all in-bridge arcs to find relevant in-bridge vertices.
#         for in_bridge in self.In_list:
#             in_vertex = in_bridge.split(', ')[1]  # Extract the target vertex of the in-bridge.

#             # Check if the start vertex of the current arc matches the in-bridge vertex.
#             if start == in_vertex:
#                 # Look for the corresponding arc in R1 to retrieve its base l-attribute.
#                 for arc in self.R1:
#                     if arc['arc'] == in_bridge:  # Match the in-bridge arc.
#                         base_eRU = int(arc['l-attribute'])  # Retrieve the l-attribute for the in-bridge.

#                         # Calculate the reusability based on paths between start and end vertices.
#                         reusability = self.get_path_reusability(in_vertex, start, end)

#                         # Update eRU using the formula: base_eRU * (reusability + 1).
#                         eRU += base_eRU * (reusability + 1)

#         return eRU

#     def get_path_reusability(self, in_vertex, start, end):
#         """
#         Compute reusability for paths between start and end vertices.

#         Args:
#             in_vertex (str): In-bridge vertex.
#             start (str): Start vertex of the path.
#             end (str): End vertex of the path.

#         Returns:
#             int: Reusability for the path.
#         """
#         eRU = 0  # Initialize the eRU to zero.

#         # Find all paths from the start vertex to the end vertex in the RBS (R2).
#         paths = utils.find_all_paths(self.R2, start, end)

#         # Iterate through each path to check if it includes the in-bridge vertex.
#         for path in paths:
#             if in_vertex in path:
#                 # Increment eRU by the number of times the in-bridge vertex appears in the path.
#                 eRU += path.count(in_vertex)

#         return eRU


# if __name__ == '__main__':
#     # Define the input data
#     R1 = [
#         {'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
#         {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0},
#         {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0},
#         {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 0},
#         {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 0},
#         {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}
#     ]
#     Arcs_List = ['x1, x2', 'x2, x3', 'x3, x2', 'x2, x4', 'x3, x4', 'x4, x5', 'x4, x6', 'x5, x6', 'x6, x2', 'x6, x7']
#     L_attribute_list = ['1', '2', '3', '4', '1', '6', '7', '7', '5', '1']
#     C_attribute_list = ['a', '0', '0', '0', '0', '0', 'b', 'a', 'a', '0']
#     Centers_list = ['x2']
#     In_list = ['x1, x2', 'x6, x2']
#     Out_list = ['x4, x5', 'x4, x6']
#     R2 = [
#         {'r-id': 'R2-1', 'arc': 'x2, x3', 'l-attribute': '2', 'c-attribute': '0', 'eRU': 2},
#         {'r-id': 'R2-2', 'arc': 'x3, x2', 'l-attribute': '3', 'c-attribute': '0', 'eRU': 2},
#         {'r-id': 'R2-3', 'arc': 'x2, x4', 'l-attribute': '4', 'c-attribute': '0', 'eRU': 0},
#         {'r-id': 'R2-4', 'arc': 'x3, x4', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0}
#     ]

#     # Initialize the AbstractArc class
#     AA = AbstractArc(R1=R1, R2=R2, In_list=In_list, Out_list=Out_list, Centers_list=Centers_list, Arcs_List=Arcs_List)

#     # Find abstract vertices
#     abstract_vertices = AA.find_abstract_vertices()
#     # Create abstract arcs (Step A)
#     prepreFinal_abstractList = AA.make_abstract_arcs_stepA(abstract_vertices)
#     # Add self-loops (Step B)
#     preFinal_abstractList = AA.make_abstract_arcs_stepB(prepreFinal_abstractList)
#     # Finalize abstract arcs (Step C)
#     final_abstractList = AA.make_abstract_arcs_stepC(preFinal_abstractList)
#     # Add abstract arcs to R1
#     updated_R1 = R1 + final_abstractList  # Simplified merging for demonstration
#     # print(f"Updated R1 with Abstract Arcs: {updated_R1}")
# import utils

# class AbstractArc:
#     def __init__(self, R1, R2, In_list, Out_list, Centers_list, Arcs_List):
#         """
#         Initialize the AbstractArc class with the required inputs.
#         """
#         self.R1 = R1
#         self.R2 = R2  # Directly assigning the list here, without the 'R2' key.
#         self.In_list = In_list
#         self.Out_list = Out_list
#         self.Centers_list = Centers_list
#         self.Arcs_List = Arcs_List
#         self.abstract_arcs = []  # Store the final abstract arcs created.

#     def unique(self, Arcs_List):
#         """
#         Extract all unique vertices from a list of arcs.
#         """
#         unique_vertices = set()
#         for arc in Arcs_List:
#             vertices = arc.split(', ')
#             unique_vertices.update(vertices)
#         return sorted(unique_vertices)

#     def find_abstract_vertices(self):
#         """
#         Identify all abstract vertices used for creating abstract arcs.
#         """
#         abstract_v_in_list = [arc.split(', ')[1] for arc in self.In_list]
#         abstract_v_out_list = [arc.split(', ')[0] for arc in self.Out_list]
#         abstract_vertices = self.Centers_list + abstract_v_in_list + abstract_v_out_list
#         return list(set(abstract_vertices))  # Ensure uniqueness.

#     def make_abstract_arcs_stepA(self, abstract_vertices):
#         """
#         Step A: Create abstract arcs between in-bridge and out-bridge vertices.
#         """
#         abstract_arcs = []  
#         seen_pairs = set()  
#         all_paths = [] 

#         arc_list = [arc['arc'] for arc in self.R2 if isinstance(arc, dict) and 'arc' in arc]

#         # if not arc_list:
#         #     print("R2 contains no valid arcs.")
#         # else:
#         #     print("R2 arcs successfully extracted:", arc_list)

#         graph = utils.list_to_graph(arc_list)

#         for in_bridge in self.In_list:
#             in_vertex = in_bridge.split(', ')[1]
#             if in_vertex not in abstract_vertices:
#                 continue

#             for out_vertex in abstract_vertices:
#                 if in_vertex != out_vertex:
#                     vertex_pair = (in_vertex, out_vertex)
#                     if vertex_pair in seen_pairs:
#                         continue
#                     seen_pairs.add(vertex_pair)

#                     paths = utils.find_all_paths(graph, in_vertex, out_vertex)
#                     if paths:
#                         for path in paths:
#                             arcs = [
#                                 f"{path[i]}, {path[i + 1]}" for i in range(len(path) - 1)
#                             ]
#                             all_paths.append(arcs)

#                             if len(path) > 1:
#                                 start_vertex = path[0]
#                                 end_vertex = path[-1]
#                                 if start_vertex in abstract_vertices and end_vertex in abstract_vertices:
#                                     abstract_arcs.append({
#                                         'r-id': f"R1-{len(abstract_arcs)}",  
#                                         'arc': f'{start_vertex}, {end_vertex}',  # Add apostrophes here
#                                         'c-attribute': '0',  # Add apostrophes here
#                                         'l-attribute': '0',  # Add apostrophes here
#                                         'eRU': '0'  # Add apostrophes here
#                                     })
#                             else:
#                                 for arc in arcs:
#                                     if arc.split(', ')[0] in abstract_vertices and arc.split(', ')[1] in abstract_vertices:
#                                         abstract_arcs.append({
#                                             'r-id': f"R1-{len(abstract_arcs)}",  
#                                             'arc': f'{arc}',  # Add apostrophes here
#                                             'c-attribute': '0',  # Add apostrophes here
#                                             'l-attribute': '0',  # Add apostrophes here
#                                             'eRU': '0'  # Add apostrophes here
#                                         })

#         return abstract_arcs

#     def make_abstract_arcs_stepB(self, abstract_arcs):
#         """
#         Step B: Add self-loops for in-bridge vertices to abstract arcs.
#         """
#         processed_in_vertices = set()

#         for in_bridge in self.In_list:
#             in_vertex = in_bridge.split(', ')[1]
#             if in_vertex in processed_in_vertices:
#                 continue
#             processed_in_vertices.add(in_vertex)

#             paths = utils.find_all_paths(self.R2, in_vertex, in_vertex)
#             if paths:
#                 for path in paths:
#                     if len(path) > 1:
#                         start_vertex = path[0]
#                         end_vertex = path[-1]
#                         if start_vertex == in_vertex and end_vertex == in_vertex:
#                             filtered_arc = f'{start_vertex}, {end_vertex}'  # Add apostrophes here
#                             if filtered_arc not in abstract_arcs:
#                                 abstract_arcs.append({
#                                     'r-id': f"R1-{len(abstract_arcs)}",  
#                                     'arc': filtered_arc,
#                                     'c-attribute': '0',  
#                                     'l-attribute': '0',  
#                                     'eRU': '0'  
#                                 })

#             formatted_arc = f'{in_vertex}, {in_vertex}'  # Add apostrophes here
#             if formatted_arc not in abstract_arcs:
#                 abstract_arcs.append({
#                     'r-id': f"R1-{len(abstract_arcs)}",  
#                     'arc': formatted_arc,
#                     'c-attribute': '0',  
#                     'l-attribute': '0',  
#                     'eRU': '0'  
#                 })

#         return abstract_arcs

#     def make_abstract_arcs_stepC(self, abstract_arcs):
#         """
#         Step C: Finalize abstract arcs by assigning attributes.
#         """
#         finalized_arcs = []

#         for arc in abstract_arcs:
#             c_attribute = '0'  # Abstract arcs are unconstrained (add apostrophes)
#             eRU = self.calculate_eRU(arc['arc'].split(', ')[0], arc['arc'].split(', ')[1])  
#             l_attribute = f'{eRU + 1}'  # Derived l-attribute with apostrophes

#             finalized_arcs.append({
#                 'r-id': arc['r-id'],
#                 'arc': arc['arc'],
#                 'c-attribute': c_attribute,
#                 'l-attribute': l_attribute,
#                 'eRU': f'{eRU}'  # Add apostrophes here
#             })

#         return finalized_arcs

#     def calculate_eRU(self, start, end):
#         """
#         Calculate the effective reusability (eRU) for an abstract arc.
#         """
#         eRU = 0  

#         for in_bridge in self.In_list:
#             in_vertex = in_bridge.split(', ')[1]

#             if start == in_vertex:
#                 for arc in self.R1:
#                     if arc['arc'] == in_bridge:  
#                         base_eRU = int(arc['l-attribute'])  
#                         eRU = base_eRU + 1  
#                         break

#         return eRU



import utils

class AbstractArc:
    """
    This class generates abstract arcs from the input RDLT data.
    It processes arcs from R1 and R2, identifies abstract vertices,
    and forms new abstract arcs to integrate R2 processes into R1.
    """

    def __init__(self, R1, R2, In_list, Out_list, Centers_list, Arcs_List):
        """
        Initializes the AbstractArc class with the necessary lists for processing abstract arcs.
        
        Parameters:
            - R1 (dict): Dictionary representing arcs outside the RBS with attributes.
            - R2 (list): List of dictionaries representing arcs inside the RBS with attributes.
            - In_list (list): List of in-bridges (arcs entering the RBS).
            - Out_list (list): List of out-bridges (arcs exiting the RBS).
            - Centers_list (list): List of center vertices marking RBS entry points.
            - Arcs_List (list): Complete list of arcs as strings.
        """
        self.R1 = R1
        self.R2 = R2
        self.In_list = In_list
        self.Out_list = Out_list
        self.Centers_list = Centers_list
        self.Arcs_List = Arcs_List
        self.abstract_arcs = []

    def unique(self, Arcs_List):
        """
        Extracts all unique vertices from a list of arcs.
        
        Parameters:
            - Arcs_List (list): List of arcs as strings, e.g., "x1, x2".

        Returns:
            list: Sorted list of unique vertices.
        """
        unique_vertices = set()
        for arc in Arcs_List:
            # Split each arc string into its vertices and add to the set.
            vertices = arc.split(', ')
            unique_vertices.update(vertices)
        return sorted(unique_vertices)

    def find_abstract_vertices(self):
        """
        Identify all abstract vertices used for creating abstract arcs.
        Combines center vertices, in-bridge end vertices, and out-bridge start vertices.

        Returns:
            list: Unique list of abstract vertices.
        """
        # Extract the target vertex of in-bridges and source vertex of out-bridges.
        abstract_v_in_list = [arc.split(', ')[1] for arc in self.In_list]
        abstract_v_out_list = [arc.split(', ')[0] for arc in self.Out_list]
        # Combine and remove duplicates.
        abstract_vertices = self.Centers_list + abstract_v_in_list + abstract_v_out_list
        return list(set(abstract_vertices))

    def make_abstract_arcs_stepA(self, abstract_vertices):
        """
        Step A: Create abstract arcs between in-bridge and out-bridge vertices.

        This method constructs abstract arcs by:
            - Converting R2 to a graph structure.
            - Finding all paths between in-bridge and out-bridge vertices.
            - Filtering paths to retain only those involving abstract vertices.

        Parameters:
            - abstract_vertices (list): List of vertices relevant to abstract arcs.

        Returns:
            list: Abstract arcs identified in this step.
        """
        abstract_arcs = []  
        seen_pairs = set()  
        all_paths = [] 

        # Convert R2 arcs to a graph representation for pathfinding.
        arc_list = [arc['arc'] for arc in self.R2 if isinstance(arc, dict) and 'arc' in arc]
        graph = utils.list_to_graph(arc_list)

        for in_bridge in self.In_list:
            # Extract the in-bridge's target vertex (end vertex of the arc).
            in_vertex = in_bridge.split(', ')[1]
            if in_vertex not in abstract_vertices:
                # Skip if the vertex is not part of the abstract vertices.
                continue

            for out_vertex in abstract_vertices:
                if in_vertex != out_vertex:
                    # Avoid redundant processing for the same vertex pair.
                    vertex_pair = (in_vertex, out_vertex)
                    if vertex_pair in seen_pairs:
                        continue
                    seen_pairs.add(vertex_pair)
                    
                    # Find all paths from in_vertex to out_vertex.
                    paths = utils.find_all_paths(graph, in_vertex, out_vertex)
                    if paths:
                        for path in paths:
                            arcs = [
                                f"{path[i]}, {path[i + 1]}" for i in range(len(path) - 1)
                            ]
                            all_paths.append(arcs)

                            # Filter paths to retain only those involving abstract vertices.
                            if len(path) > 1:
                                abstract_arcs.append({
                                    'r-id': f"R1-{len(abstract_arcs)}",  
                                    'arc': f'{path[0]}, {path[-1]}',
                                    'c-attribute': '0',
                                    'l-attribute': '0',
                                    'eRU': '0'
                                })
                            else:
                                # For single arcs, ensure both vertices are abstract vertices.
                                for arc in arcs:
                                    abstract_arcs.append({
                                        'r-id': f"R1-{len(abstract_arcs)}",  
                                        'arc': arc,
                                        'c-attribute': '0',
                                        'l-attribute': '0',
                                        'eRU': '0'
                                    })

        return abstract_arcs

    def make_abstract_arcs_stepB(self, abstract_arcs):
        """
        Step B: Add self-loops for in-bridge vertices to abstract arcs.

        Identifies self-loops (paths from a vertex to itself) and adds them to the list.

        Args:
            - abstract_arcs (list): List of existing abstract arcs.

        Returns:
            list: Updated list of abstract arcs including self-loops.
        """
        processed_in_vertices = set()

        for in_bridge in self.In_list:
            # Extract the target vertex of the in-bridge.
            in_vertex = in_bridge.split(', ')[1]
            if in_vertex in processed_in_vertices:
                continue
            processed_in_vertices.add(in_vertex)

            # Find self-loops (paths from in_vertex to itself).
            paths = utils.find_all_paths(self.R2, in_vertex, in_vertex)
            if paths:
                for path in paths:
                    if len(path) > 1:
                        filtered_arc = f'{in_vertex}, {in_vertex}'
                        if filtered_arc not in abstract_arcs:
                            abstract_arcs.append({
                                'r-id': f"R1-{len(abstract_arcs)}",  
                                'arc': filtered_arc,
                                'c-attribute': '0',  
                                'l-attribute': '0',  
                                'eRU': '0'  
                            })

            # Directly add a formatted self-loop if no explicit paths are found.
            formatted_arc = f'{in_vertex}, {in_vertex}'
            if formatted_arc not in abstract_arcs:
                abstract_arcs.append({
                    'r-id': f"R1-{len(abstract_arcs)}",  
                    'arc': formatted_arc,
                    'c-attribute': '0',  
                    'l-attribute': '0',  
                    'eRU': '0'  
                })

        return abstract_arcs

    def make_abstract_arcs_stepC(self, abstract_arcs):
        """
        Step C: Finalize abstract arcs by assigning attributes.

        Adds derived attributes (e.g., `c-attribute`, `l-attribute`, `eRU`) to each abstract arc.

        Args:
            - abstract_arcs (list): List of abstract arcs as strings.

        Returns:
            list: Finalized list of abstract arcs with attributes.
        """
        finalized_arcs = []

        for arc in abstract_arcs:
            # Split arc into start and end vertices.
            eRU = self.calculate_eRU(arc['arc'].split(', ')[0], arc['arc'].split(', ')[1])
            # Derived l-attribute.
            l_attribute = f'{eRU + 1}'

            # Assign attributes to the abstract arc. 
            # Store the arc in dictionary format.
            finalized_arcs.append({
                'r-id': arc['r-id'],
                'arc': arc['arc'],
                'c-attribute': '0',
                'l-attribute': l_attribute,
                'eRU': f'{eRU}'
            })

        return finalized_arcs

    def calculate_eRU(self, start, end):
        """
        Calculate the effective reusability (eRU) for an abstract arc.

        Args:
            - start (str): Start vertex of the arc.
            - end (str): End vertex of the arc.

        Returns:
            int: Effective reusability (eRU) for the arc.
        """
        eRU = 0
        # Loop through all in-bridge arcs to find relevant in-bridge vertices.
        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]    # Extract the target vertex of the in-bridge.
            
            # Check if the start vertex of the current arc matches the in-bridge vertex.
            if start == in_vertex:
                # Find the corresponding arc in R1 to retrieve its base l-attribute.
                for arc in self.R1:
                    if arc['arc'] == in_bridge:
                        eRU = int(arc['l-attribute']) + 1  # Update eRU using the formula: base_eRU * (reusability + 1).
                        break
        return eRU

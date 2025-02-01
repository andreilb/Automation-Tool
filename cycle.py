# """ THIS VERSION STILL HAS A PROBLEM WITH STORING CRITICAL ARCS"""
# class Cycle:
#     def __init__(self, R):
#         self.R = R
#         self.Arcs_List = []
#         self.Vertices_List = []
#         self.processed_arcs = []
#         self.process_arcs()
#         self.graph = self.list_to_graph(self.Arcs_List)
#         self.global_cycle_counter = 0
#         self.Cycle_List = []
#         self.critical_arcs = []
#         self.store_to_cycle_list()

#     def process_arcs(self):
#         """Process the arcs and store them in Arcs_List and Vertices_List."""
#         self.Processing_Log = []

#         # Ensure correct processing based on R format (list or dict)
#         if isinstance(self.R, list):
#             arc_list = self.R
#         elif isinstance(self.R, dict):
#             arc_list = [arc_entry for subsystem in self.R.values() for arc_entry in subsystem]
#         else:
#             raise TypeError(f"Expected R to be a list or dictionary, found {type(self.R)}.")

#         for arc_entry in arc_list:
#             arc = arc_entry.get('arc')
#             r_id = arc_entry.get('r-id')

#             if isinstance(arc, str) and isinstance(r_id, (int, str)):
#                 start_vertex, end_vertex = arc.split(', ')  # Assuming 'arc' is in format 'x1, x2'
#                 self.Arcs_List.append((r_id, start_vertex, end_vertex))
#                 self.Processing_Log.append(arc_entry)

#         self.Vertices_List = list(set(vertex for _, start_vertex, end_vertex in self.Arcs_List for vertex in (start_vertex, end_vertex)))

#     def list_to_graph(self, edge_list):
#         """Convert edge list to a graph represented as an adjacency list."""
#         graph = {}
#         for arc in edge_list:
#             if isinstance(arc, tuple) and len(arc) == 3:
#                 r_id, start, end = arc
#                 if start not in graph:
#                     graph[start] = []
#                 graph[start].append(end)
#         return graph

#     def find_R_by_arc(self, arc_str):
#         """Search for an arc in R based on arc string format."""
#         print("Debug: R structure", self.R)
        
#         # Iterate through the components (if R is a dictionary)
#         if isinstance(self.R, dict):  
#             for r_component in self.R:
#                 if isinstance(self.R[r_component], list):
#                     for arc_entry in self.R[r_component]:
#                         arc = arc_entry.get('arc')
#                         if arc and arc == arc_str:  # Check if the arc matches
#                             return arc_entry
#         elif isinstance(self.R, list):  # If R is a list, iterate through it
#             for arc_entry in self.R:
#                 arc = arc_entry.get('arc')
#                 if arc and arc == arc_str:
#                     return arc_entry

#         return None  # Return None if arc is not found

#     def find_cycles(self, adj_list):
#         """Detect cycles in the graph."""
#         visited = set()
#         stack = set()
#         cycles = []
#         path = []

#         def dfs(node):
#             nonlocal cycles
#             if node in stack:
#                 cycle_start_index = path.index(node)
#                 cycle = path[cycle_start_index:]
#                 cycle_arcs = [(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)] + [(cycle[-1], cycle[0])]
#                 if cycle_arcs not in cycles:
#                     cycles.append(cycle_arcs)
#                 return

#             if node in visited:
#                 return

#             visited.add(node)
#             stack.add(node)
#             path.append(node)

#             for neighbor in adj_list.get(node, []):
#                 dfs(neighbor)

#             stack.remove(node)
#             path.pop()

#         for node in adj_list:
#             if node not in visited:
#                 dfs(node)

#         return cycles

#     def store_to_cycle_list(self):
#         """Store cycles and their corresponding arcs into Cycle_List."""
#         cycles = self.find_cycles(self.graph)
#         self.Cycle_List = []

#         for cycle in cycles:
#             cycle_in_r_format = []
#             # Collect arcs for this cycle in R format
#             for arc in cycle:
#                 arc_str = f"{arc[0]}, {arc[1]}"  # Convert arc to string
#                 r_arc = self.find_R_by_arc(arc_str)  # Look for the arc in R
#                 if r_arc:
#                     cycle_in_r_format.append(r_arc)

#             if cycle_in_r_format:
#                 cycle_id = f"c-{self.global_cycle_counter}"
#                 # Find critical arcs only for the arcs in this cycle
#                 critical_arcs = self.find_critical_arcs(cycle_in_r_format)  # Only look for critical arcs in the cycle

#                 cycle_critical_arcs = []

#                 for arc in critical_arcs:
#                     # Debugging step: Check the arc format and values
#                     print(f"Checking critical arc: {arc['arc']}")

#                     # Convert the arc to string format for easier comparison
#                     for arc_start, arc_end in cycle:
#                         cycle_arc_str = f"{arc_start}, {arc_end}"
#                         # Debugging: print the arc we are comparing
#                         print(f"Comparing with cycle arc: {cycle_arc_str}")

#                         # Check if the critical arc is present in the cycle
#                         if arc['arc'] == cycle_arc_str:
#                             cycle_critical_arcs.append(arc)
#                             print(f"Critical arc found in cycle: {arc['arc']}")

#                 # Add critical arcs (ca) to the cycle
#                 initial_cycle = {
#                     "cycle-id": cycle_id,
#                     "cycle": cycle_in_r_format,  # Keep the arcs in dictionary format
#                     "ca": cycle_critical_arcs  # Keep the critical arcs in dictionary format
#                 }
#                 self.Cycle_List.append(initial_cycle)
#                 self.global_cycle_counter += 1

#     # def store_to_cycle_list(self):
#     #     """Store cycles and their corresponding arcs into Cycle_List."""
#     #     cycles = self.find_cycles(self.graph)
#     #     self.Cycle_List = []

#     #     for cycle in cycles:
#     #         cycle_in_r_format = []
#     #         cycle_arcs = []

#     #         # Convert the cycle into R format and collect corresponding arcs
#     #         for arc in cycle:
#     #             arc_str = f"{arc[0]}, {arc[1]}"  # Convert arc to string
#     #             r_arc = self.find_R_by_arc(arc_str)  # Look for the arc in R
#     #             if r_arc:
#     #                 cycle_in_r_format.append(r_arc)
#     #                 cycle_arcs.append(r_arc)  # Collect the arcs for critical arc analysis

#     #         if cycle_in_r_format:
#     #             cycle_id = f"c-{self.global_cycle_counter}"

#     #             # Find critical arcs for this specific cycle
#     #             cycle_critical_arcs = self.find_critical_arcs(cycle_arcs)

#     #             # Add critical arcs (ca) to the cycle
#     #             initial_cycle = {
#     #                 "cycle-id": cycle_id,
#     #                 "cycle": cycle_in_r_format,  # Keep the arcs in dictionary format
#     #                 "ca": cycle_critical_arcs  # Keep the critical arcs in dictionary format
#     #             }
#     #             self.Cycle_List.append(initial_cycle)
#     #             self.global_cycle_counter += 1



#     def evaluate_cycle(self):
#         """Evaluate and display the detected cycles."""
#         self.store_to_cycle_list()
#         formatted_cycles = [cycle['cycle'] for cycle in self.Cycle_List if cycle['cycle']]
#         print(f"Cycles detected: {formatted_cycles}")
#         return self.Cycle_List
    
#     def find_critical_arcs(self, cycle_arcs):
#         ##########FUCKING CRITICAL ARC IS NOT BEING STORED PROPERLY. THERE SHOULD BE ONE OR MORE CRITICAL ARCS IN A CYCLE.
#         """Find critical arcs in the provided cycle arcs."""
        
#         # Ensure there's at least one arc in cycle_arcs before calling min
#         if not cycle_arcs:
#             print("No arcs found in cycle, returning empty list of critical arcs.")
#             return []

#         # Debug: Print the cycle arcs before processing
#         print("Cycle Arcs:", cycle_arcs)

#         # Extract l-attributes and identify the minimum value
#         l_attributes = [int(r_['l-attribute']) for r_ in cycle_arcs if r_.get('l-attribute') is not None]

#         # Debug: Print the extracted l-attributes
#         print("Extracted l-attributes:", l_attributes)

#         if not l_attributes:
#             print("No valid l-attributes found, returning empty list of critical arcs.")
#             return []

#         # Find the minimum l-attribute from the list of valid l-attributes
#         minimum_L = min(l_attributes)

#         # Debug: Print the minimum l-attribute
#         print(f"Minimum l-attribute for cycle: {minimum_L}")  

#         # Collect all arcs with the minimum l-attribute value
#         critical_arcs = [r for r in cycle_arcs if int(r.get('l-attribute', float('inf'))) == minimum_L]

#         # Debug: Print the critical arcs found
#         print(f"Critical arcs found in cycle: {[arc['arc'] for arc in critical_arcs]}")  
        
#         return critical_arcs




#     def readable_Cycle_List(self):
#         """Converts Cycle_List into a human-readable format."""
#         return [
#             {
#                 'cycle-id': cycle['cycle-id'],
#                 'cycle': self.format_readable_R(cycle['cycle']),
#                 'ca': self.format_readable_R(cycle.get('ca', []))  # Safely access 'ca' with default empty list
#             }
#             for cycle in self.Cycle_List
#         ]

#     def format_readable_R(self, R):
#         """Converts R into a human-readable format."""
#         return [f"{r['r-id']}: {r['arc']}" for r in R]  # This now works as R is a list of dictionaries

    
#     def calculate_eRU_for_arcs(self, L_Attributes): 
#         """
#         Calculates eRU (effective reset units) for arcs in the graph based on cycle participation.

#         Parameters:
#             L_Attributes (list): List of L-attributes corresponding to the arcs in Arcs_List.

#         Returns:
#             list: List of eRU values for each arc in Arcs_List.
#         """
#         eRU_list_R2 = []
#         cycle_arcs_list = [cycle['cycle'] for cycle in self.Cycle_List if cycle['cycle']] 

#         # Loop through the arcs
#         for arc in self.Arcs_List:
#             # Extract the r-id (which is the first element of the tuple) and vertices (remaining elements)
#             r_id, vertex_1, vertex_2 = arc
#             arc_vertices = f"{vertex_1}, {vertex_2}"  # Create the string of vertices to be used in cycle check

#             arc_in_cycle = False
#             cycle_l_attributes = []

#             # Check if the arc's vertices are part of any cycle
#             for cycle in cycle_arcs_list:
#                 if arc_vertices in cycle:
#                     arc_in_cycle = True
#                     try:
#                         # Get the index of the arc in the Arcs_List and corresponding L-attribute
#                         index_in_arcs = self.Arcs_List.index(arc)
#                         cycle_l_attributes.append(L_Attributes[index_in_arcs])
#                     except IndexError:
#                         print(f"IndexError: Arc {arc} at index {index_in_arcs} not found in L_Attributes.")
            
#             # Calculate eRU: the minimum L-attribute for arcs in a cycle, or 0 if not in any cycle
#             eRU = min(cycle_l_attributes) if arc_in_cycle and cycle_l_attributes else 0
#             eRU_list_R2.append(eRU)

#             # Optionally print the arc with its r-id and eRU for debugging
#             print(f"Arc:{arc_vertices},  r-id: {r_id}, eRU: {eRU}")

#         return eRU_list_R2

# if __name__ == "__main__":
#     R1 = [{'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
#           {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 5},
#           {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0},
#           {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 5},
#           {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 5},
#           {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0},
#           {'r-id': 'R1-10', 'arc': 'x2, x4', 'c-attribute': 0, 'l-attribute': 7, 'eRU': 6},
#           {'r-id': 'R1-11', 'arc': 'x2, x4', 'c-attribute': 0, 'l-attribute': 7, 'eRU': 6},
#           {'r-id': 'R1-12','arc': 'x2, x2', 'c-attribute': 0, 'l-attribute': 13, 'eRU': 12}]

#     Cycle_R1 = Cycle(R1)
#     Cycle_R1.evaluate_cycle()
#     print(Cycle_R1.readable_Cycle_List())


##### test

class Cycle:
    def __init__(self, R):
        """
        Initialize the Cycle object with the provided list of arcs (R) for cycle detection.

        Parameters:
            R (list): A list of dictionaries representing arcs. Each dictionary should contain:
                - 'arc': A string representing the arc in the format 'start_vertex, end_vertex'.
                - 'c-attribute': A string or number representing the c-attribute for the arc.
                - 'l-attribute': A string or number representing the l-attribute for the arc.
        
        Initializes the following attributes:
            - self.R : The list of arcs passed to the constructor.
            - self.Arcs_List: A list to store the arcs as tuples (start_vertex, end_vertex).
            - self.Vertices_List: A list of unique vertices extracted from the arcs.
            - self.graph: A graph representation of the arcs, created as an adjacency list.
            - self.Cycle_List: A list to store detected cycles in the graph.
            - self.processed_arcs: A list of processed arcs.
            - self.global_cycle_counter: A counter to track the total number of detected cycles.
            - self.critical_arcs: A list of critical arcs in detected cycles.
            - self.eRU_list_R2: A list to store calculated eRU values for each arc.
        """
        self.R = R
        self.Arcs_List = []
        self.Vertices_List = []
        self.processed_arcs = []
        self.process_arcs()
        self.graph = self.list_to_graph(self.Arcs_List)
        self.global_cycle_counter = 0  # Start cycle count from c-1
        self.Cycle_List = []
        self.critical_arcs = []
        self.eRU_list_R2 = []  # List to store the calculated eRU values for each arc

    def process_arcs(self):
        """
        Processes the arcs in self.R and stores them in Arcs_List and Vertices_List.

        This method processes each arc in self.R by splitting the arc string into its start and 
        end vertices, stores valid arcs as tuples in Arcs_List, and extracts unique vertices 
        into Vertices_List.

        Returns:
            - Arcs_List: List of arcs as tuples (start_vertex, end_vertex).
            - Vertices_List: List of unique vertices extracted from Arcs_List.
        """
        self.Processing_Log = []

        # Ensure correct processing based on R format (list or dict)
        if isinstance(self.R, list):
            arc_list = self.R
        elif isinstance(self.R, dict):
            arc_list = [arc_entry for subsystem in self.R.values() for arc_entry in subsystem]
        else:
            raise TypeError(f"Expected R to be a list or dictionary, found {type(self.R)}.")

        for arc_entry in arc_list:
            arc = arc_entry.get('arc')
            r_id = arc_entry.get('r-id')

            if isinstance(arc, str) and isinstance(r_id, (int, str)):
                start_vertex, end_vertex = arc.split(', ')  # Assuming 'arc' is in format 'x1, x2'
                self.Arcs_List.append((r_id, start_vertex, end_vertex))
                self.Processing_Log.append(arc_entry)
        
        # Extract vertices from arcs
        self.Vertices_List = list(set(vertex for _, start_vertex, end_vertex in self.Arcs_List for vertex in (start_vertex, end_vertex)))

    def list_to_graph(self, edge_list):
        """
        Converts an edge list into a graph represented as an adjacency list.

        Parameters:
            - edge_list (list): List of edges, where each edge is represented as a tuple (start_vertex, end_vertex).
        
        Returns:
            dict: Graph represented as an adjacency list where each vertex maps to a list of connected vertices.
        
        Returns:
            graph: A dictionary representing the adjacency list of the graph.
        """
        graph = {}
        for arc in edge_list:
            if isinstance(arc, tuple) and len(arc) == 3:
                r_id, start, end = arc
                if start not in graph:
                    graph[start] = []
                graph[start].append(end)
        return graph

    def find_R_by_arc(self, arc_str):
        """
        Detects cycles in the graph using Depth-First Search (DFS).

        Parameters:
            - adj_list (dict): The adjacency list representation of the graph.
        
        Returns:
            list: List of cycles found in the graph, where each cycle is a list of arcs.

        Returns:
            - cycles: List of cycles detected in the graph.
        """
        if isinstance(self.R, dict):
            for r_component in self.R:
                if isinstance(self.R[r_component], list):
                    for arc_entry in self.R[r_component]:
                        arc = arc_entry.get('arc')
                        if arc and arc == arc_str:
                            return arc_entry
        elif isinstance(self.R, list):
            for arc_entry in self.R:
                arc = arc_entry.get('arc')
                if arc and arc == arc_str:
                    return arc_entry

        return None

    def find_cycles(self, adj_list):
        """
        Detects all cycles in the directed graph represented by `adj_list` using Depth First Search (DFS).

        This method identifies simple cycles in the graph, where a cycle is defined as a sequence of nodes
        where the first node is the same as the last node, and there is a directed edge from each node to the next.

        Parameters:
            - adj_list (dict): The adjacency list of the graph, where the keys are node identifiers (vertices)
                            and the values are lists of neighboring nodes (edges). 

        Returns:
            list: A list of cycles, where each cycle is represented as a list of arcs (pairs of nodes),
                each arc is a tuple (start_node, end_node). 

        Notes:
            - This method uses DFS to traverse the graph and detect cycles.
            - Once a cycle is detected (when a node is revisited within the current DFS path), it is recorded as a cycle.
            - Cycles are stored as a list of arcs. If a cycle has already been recorded, it is not added again.
        """
        visited = set()
        stack = set()
        cycles = []
        path = []

        def dfs(node):
            nonlocal cycles
            if node in stack:
                cycle_start_index = path.index(node)
                cycle = path[cycle_start_index:]
                cycle_arcs = [(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1)] + [(cycle[-1], cycle[0])]
                if cycle_arcs not in cycles:
                    cycles.append(cycle_arcs)
                return

            if node in visited:
                return

            visited.add(node)
            stack.add(node)
            path.append(node)

            for neighbor in adj_list.get(node, []):
                dfs(neighbor)

            stack.remove(node)
            path.pop()

        for node in adj_list:
            if node not in visited:
                dfs(node)

        return cycles

    def store_to_cycle_list(self):
        """
        Stores detected cycles into the `Cycle_List` attribute with formatted Cycle IDs.

        This method:
        - Detects cycles in the graph using the `find_cycles` method.
        - Converts each detected cycle into a list of arcs in a specific format and retrieves corresponding R arcs.
        - Assigns a unique 'cycle-id' to each detected cycle, in the format 'Cycle ID: c-1', 'Cycle ID: c-2', etc.
        - Identifies the critical arcs within each cycle using the `find_critical_arcs` method.
        - Stores each cycle in `Cycle_List` along with its 'cycle-id' and its list of critical arcs.

        Updates:
            - The `Cycle_List` attribute with cycles, each containing:
                - A list of arcs in `r-id` format.
                - A list of critical arcs (empty initially and then filled with identified critical arcs).
            - The `global_cycle_counter` attribute, which is incremented for each detected cycle.

        """
        # print(f"Storing cycles...")  # Debug statement to track method execution
        # print('-' * 30)
        cycles = self.find_cycles(self.graph)
        self.Cycle_List = []  # Ensure this is a list, not a dict

        # print(f"Total detected cycles: {len(cycles)}")  # Debug statement to show total cycles detected

        # Iterate over each detected cycle
        for cycle in cycles:
            cycle_in_r_format = []
            for arc in cycle:
                arc_str = f"{arc[0]}, {arc[1]}"
                r_arc = self.find_R_by_arc(arc_str)
                if r_arc:
                    cycle_in_r_format.append(r_arc)

            if cycle_in_r_format:
                # Add cycle to Cycle_List as a dictionary
                self.Cycle_List.append({
                    "cycle": cycle_in_r_format,
                    "ca": []  # Critical arcs are initially empty
                })

                # Define cycle_id now that the cycle has been added
                cycle_id = f"c-{len(self.Cycle_List)}"
                critical_arcs = self.find_critical_arcs(cycle_in_r_format, cycle_id)

                # Update the corresponding cycle in Cycle_List with critical arcs
                self.Cycle_List[-1]["cycle-id"] = cycle_id
                self.Cycle_List[-1]["ca"] = critical_arcs['critical_arcs']  # Using the cycle_id for easier identification

                # Increment counter for each cycle added to the list
                self.global_cycle_counter += 1  

        # print(f"this is global cycle counter after all cycles: {self.global_cycle_counter}")  # Final debug statement


    def evaluate_cycle(self):
        """
        Evaluates the presence of cycles in the graph and formats the cycle list for output.

        Calls store_to_cycle_list to populate the Cycle_List, flattens the cycles, 
        and prints the result. If no cycles are found, prints a corresponding message.

        Returns:
            list: The list of cycles found in the graph, in formatted output.
        
        Returns:
            - A formatted list of cycles, or a message indicating no cycles were found.
        """
        self.store_to_cycle_list()

        # Debug: Check the contents of Cycle_List
        # print(f"Cycle_List after storing cycles: {self.Cycle_List}")

        # Retrieve and format the cycles and critical arcs
        formatted_cycles = [
            {
                'cycle-id': cycle['cycle-id'],
                'cycle': self.format_readable_R(cycle['cycle']),
                'ca': self.format_readable_R(cycle.get('ca', []))
            }
            for cycle in self.Cycle_List if cycle['cycle']
        ]
        
        # debugger
        # print(f"Formatted cycles: {formatted_cycles}")

        # Return the cycles in human-readable format
        return formatted_cycles

    def find_critical_arcs(self, cycle_arcs, cycle_id):
        """
    Finds critical arcs in the provided cycle arcs based on their l-attribute value and 
    returns them along with the cycle_id for identification.

    Parameters:
        - cycle_arcs (list): A list of arcs in the cycle, where each arc is represented
                            as a dictionary with keys like 'arc', 'l-attribute', and 'r-id'.
        - cycle_id (str): A unique identifier for the cycle.

    Returns:
        dict: A dictionary containing the 'cycle_id' and the 'critical_arcs' 
              that have the minimum l-attribute value in the cycle.
              Format: {'cycle_id': cycle_id, 'critical_arcs': list of critical arcs}

    Notes:
        - If the input `cycle_arcs` is a list of tuples, it is first converted to a dictionary format
          with an assumed 'l-attribute' value (you may need to update this to assign the actual l-attribute).
        - Critical arcs are defined as those that have the smallest l-attribute value in the cycle.
    """
        if not cycle_arcs:
            return {'cycle_id': cycle_id, 'critical_arcs': []}

        # Ensure that cycle_arcs contains dictionaries with the proper format
        if isinstance(cycle_arcs[0], tuple):
            # Convert tuple (start, end) to a dictionary format for l-attribute lookup
            cycle_arcs = [{
                'arc': f"{arc[0]}, {arc[1]}",
                'l-attribute': 'some_value',  # You can assign the correct l-attribute here
                'r-id': f"r-{i}"  # Similarly, assign a proper r-id
            } for i, arc in enumerate(cycle_arcs)]

        # Find the minimum l-attribute value across all arcs in the cycle
        l_attributes = [int(r_['l-attribute']) for r_ in cycle_arcs if 'l-attribute' in r_ and r_['l-attribute'] is not None]

        if not l_attributes:
            return {'cycle_id': cycle_id, 'critical_arcs': []}

        minimum_L = min(l_attributes)

        # Loop through all arcs in the cycle and collect arcs with the minimum l-attribute
        critical_arcs = []
        for arc in cycle_arcs:
            # Check if this arc has the minimum l-attribute
            if int(arc.get('l-attribute', float('inf'))) == minimum_L:
                critical_arcs.append(arc)

        # Return the cycle_id and critical arcs in a dictionary
        return {'cycle_id': cycle_id, 'critical_arcs': critical_arcs}


    def format_readable_R(self, R):
        """
    Converts the R list (a collection of arcs and their attributes) into a human-readable format.

    Parameters:
        R (list): A list of dictionaries, where each dictionary contains arc data,
                  including an 'r-id' and 'arc'.

    Returns:
        list: A list of strings where each string represents an arc in the format:
              'r-id: arc', making it easy to read and interpret the arcs.
              Example: ["r-0: (x1, x2)", "r-1: (x2, x3)"]

    Notes:
        - This method assumes that each dictionary in `R` contains 'r-id' and 'arc' keys.
    """
        return [f"{r['r-id']}: {r['arc']}" for r in R]

    def calculate_eRU_for_arcs(self, cycle_arcs):
        """
        Calculates the Effective Reset Units (eRU) for arcs based on their participation in cycles.

        Parameters:
            L_Attributes (list): List of l-attributes corresponding to the arcs in Arcs_List.
        
        Returns:
            list: List of eRU values for each arc in Arcs_List.
        
        Returns:
            - eRU values for each arc, printed in the format 'Arc: (start_vertex, end_vertex), eRU: value'.
        """
        
        # Clear the eRU list before starting the calculation
        self.eRU_list_R2.clear()

        # Find the critical arcs in the cycle
        critical_arcs = self.find_critical_arcs(cycle_arcs, cycle_id='')  # cycle_id can be passed from the context

        if not critical_arcs or 'critical_arcs' not in critical_arcs:
            print("Warning: No critical arcs found.")
            return self.eRU_list_R2

        # Get the l-attributes of the critical arcs
        cycle_l_attributes = [arc['l-attribute'] for arc in critical_arcs['critical_arcs']]  # Collect l-attributes for critical arcs

        # Ensure cycle_l_attributes has valid values before proceeding
        if not cycle_l_attributes:
            print("Warning: No l-attributes found for critical arcs.")
            return self.eRU_list_R2

        # Find the minimum l-attribute (critical arc's eRU value)
        min_l_attribute = min(cycle_l_attributes)  # This is the critical arc's eRU value

        print(f"Critical arc's eRU (min l-attribute): {min_l_attribute}")

        # Iterate over the critical arcs and update their eRU
        for arc in critical_arcs['critical_arcs']:
            r_id = arc.get('r-id', None)
            arc_name = arc.get('arc', None)
            
            if not r_id or not arc_name:
                print(f"Warning: Missing r-id or arc name for critical arc: {arc}")
                continue

            # Get the actual arc from R2 using r-id
            actual_arc = self.get_arc_from_rid(r_id)

            if actual_arc:
                print(f"Processing arc: {actual_arc}")

                # Set eRU of the arc to the minimum l-attribute (critical arc's eRU value)
                arc['eRU'] = f"'{min_l_attribute}'"  # Ensuring that eRU is stored with apostrophes
                self.eRU_list_R2.append(f"'{min_l_attribute}'")  # Append eRU value with apostrophe

                print(f"Set eRU for arc {arc_name} (r-id: {r_id}) to {min_l_attribute}")
            else:
                print(f"Warning: No arc found for r-id {r_id}")

        return self.eRU_list_R2

    def get_cycle_list(self):
            """
            Returns the list of detected cycles stored in `Cycle_List`.

            """
            return self.Cycle_List


if __name__ == "__main__":
    R1 = [
        {'r-id': 'R1-0', 'arc': 'x1, x2', 'l-attribute': '1', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-5', 'arc': 'x4, x5', 'l-attribute': '6', 'c-attribute': '0', 'eRU': 0},
        {'r-id': 'R1-6', 'arc': 'x4, x6', 'l-attribute': '7', 'c-attribute': 'b', 'eRU': 0},
        {'r-id': 'R1-7', 'arc': 'x5, x6', 'l-attribute': '7', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-8', 'arc': 'x6, x2', 'l-attribute': '5', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-9', 'arc': 'x6, x7', 'l-attribute': '1', 'c-attribute': '0', 'eRU': 0},
        {'r-id': 'R1-10', 'arc': 'x2, x4', 'l-attribute': '7', 'c-attribute': '0', 'eRU': 0},  
        {'r-id': 'R1-11', 'arc': 'x2, x4', 'l-attribute': '7', 'c-attribute': '0', 'eRU': 0}, 
        {'r-id': 'R1-12', 'arc': 'x2, x3', 'l-attribute': '9', 'c-attribute': 'a', 'eRU': 0},
        {'r-id': 'R1-13', 'arc': 'x3, x1', 'l-attribute': '5', 'c-attribute': 'b', 'eRU': 0},
    ]


    Cycle_R1 = Cycle(R1).evaluate_cycle()

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
            - self.R: The list of arcs passed to the constructor.
            - self.Arcs_List: A list to store the arcs as tuples (start_vertex, end_vertex).
            - self.Vertices_List: A list of unique vertices extracted from the arcs.
            - self.graph: A graph representation of the arcs, created as an adjacency list.
            - self.Cycle_List: A list to store detected cycles in the graph.
        """
        self.R = R  # Store the provided R list
        # print(f"Initial R: {self.R}")  # Debug: Print R for verification
        
        # Initialize lists for arcs and vertices
        self.Arcs_List = []
        self.Vertices_List = []
        
        # Process the arcs from the R list (handling the dictionary format with 'arc' key)
        self.process_arcs()

        # Convert Arcs_List to graph for cycle detection
        self.graph = self.list_to_graph(self.Arcs_List)

        # Detect cycles in the graph
        self.global_cycle_counter = 0  # Initialize global cycle counter to track unique cycle IDs
        self.Cycle_List = []  # Initialize the cycle list to store cycles
        self.store_to_cycle_list()

    def process_arcs(self):
        """
        Processes the arcs in self.R and stores them in Arcs_List and Vertices_List.

        This method processes each arc in self.R by splitting the arc string into its start and 
        end vertices, stores valid arcs as tuples in Arcs_List, and extracts unique vertices 
        into Vertices_List.

        Outputs:
            - Arcs_List: List of arcs as tuples (start_vertex, end_vertex).
            - Vertices_List: List of unique vertices extracted from Arcs_List.
        """
        for r in self.R:
            # print(f"Processing arc entry: {r}")  # Debug: Log the raw arc entry
            
            if isinstance(r, dict) and 'arc' in r:  # If it's a dictionary with an 'arc' key
                arc = r['arc']
                # print(f"Arc from dictionary: {arc}")  # Debug: Log the arc string from the dictionary
                
                # Check if the arc string is in the correct format
                split_r = arc.split(', ')  # Split the arc string into start and end vertices
                # print(f"Split arc string: {split_r}")  # Debug: Log the result of splitting
                
                if len(split_r) == 2:  # Only process if there are exactly two elements (arc format: 'x1, x2')
                    self.Arcs_List.append(tuple(split_r))  # Add as a tuple (x1, x2)
                else:
                    print(f"Skipping invalid arc: {arc}")  # Skip invalid arc format

        # Extract vertices from arcs (i.e., the unique vertices that appear in the arcs)
        self.Vertices_List = list(set([item for sublist in self.Arcs_List for item in sublist]))

        # print(f"Processed Arcs List: {self.Arcs_List}")
        # print(f"Processed Vertices List: {self.Vertices_List}")

    def list_to_graph(self, edge_list):
        """
        Converts an edge list into a graph represented as an adjacency list.

        Parameters:
            edge_list (list): List of edges, where each edge is represented as a tuple (start_vertex, end_vertex).
        
        Returns:
            dict: Graph represented as an adjacency list where each vertex maps to a list of connected vertices.
        
        Outputs:
            - graph: A dictionary representing the adjacency list of the graph.
        """
        graph = {}
        for arc in edge_list:
            if isinstance(arc, tuple) and len(arc) == 2:
                start, end = arc
                if start not in graph:
                    graph[start] = []
                graph[start].append(end)
            else:
                print(f"Skipping invalid arc: {arc}")
        return graph

    def find_cycles(self, adj_list):
        """
        Detects cycles in the graph using Depth-First Search (DFS).

        Parameters:
            adj_list (dict): The adjacency list representation of the graph.
        
        Returns:
            list: List of cycles found in the graph, where each cycle is a list of arcs.

        Outputs:
            - cycles: List of cycles detected in the graph.
        """
        visited = set()
        stack = set()
        cycles = []
        path = []
        cycle_arcs = []

        def dfs(node):
            nonlocal cycle_arcs

            if node in stack:
                cycle_start_index = path.index(node)
                cycle = path[cycle_start_index:]  # Extract the cycle
                cycle_arcs = [f"{cycle[i]}, {cycle[i + 1]}" for i in range(len(cycle) - 1)] + [f"{cycle[-1]}, {cycle[0]}"]
                if cycle_arcs not in cycles:  # Avoid duplicates
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
            path.pop()  # Backtrack

        for node in adj_list:
            if node not in visited:
                dfs(node)

        return cycles

    def store_to_cycle_list(self):
        """
        Stores detected cycles into the Cycle_List attribute with formatted Cycle IDs.
        
        Each cycle is assigned a unique 'cycle-id' in the format 'Cycle ID: c-1', 'Cycle ID: c-2', etc.
        The cycle-id is enclosed in [] and each cycle is saved to the cycle list.
        """
        cycles = self.find_cycles(self.graph)  # Find cycles using the graph
        self.Cycle_List = []  # Clear previous cycles from Cycle_List
        
        # Iterate over each detected cycle
        for cycle in cycles:
            # Format the cycle ID as 'Cycle ID: c-{counter}'
            cycle_id = f"c-{self.global_cycle_counter}"
            
            # Append the cycle with its unique ID to the Cycle_List
            self.Cycle_List.append({"cycle-id": cycle_id, f"cycle": cycle})
            
            # Increment the global cycle counter for the next cycle
            self.global_cycle_counter += 1

    def evaluate_cycle(self):
        """
        Evaluates the presence of cycles in the graph and formats the cycle list for output.

        Calls store_to_cycle_list to populate the Cycle_List, flattens the cycles, 
        and prints the result. If no cycles are found, prints a corresponding message.

        Returns:
            list: The list of cycles found in the graph, in formatted output.
        
        Outputs:
            - A formatted list of cycles, or a message indicating no cycles were found.
        """
        self.store_to_cycle_list()  # Populate Cycle_List with detected cycles
        
        cycle_list = self.Cycle_List
        formatted_cycles = [cycle['cycle'] for cycle in cycle_list if cycle['cycle']]
        
        # Flatten the cycles into a single list
        flat_cycles = [item for sublist in formatted_cycles for item in sublist]
        
        # Output the cycle count as the number of loops, not the arcs
        print(f"Cycles ({len(formatted_cycles)}): {formatted_cycles}")

        if not formatted_cycles:
            print("No cycles found.")
        print('-' * 60)
        return cycle_list

    def calculate_eRU_for_arcs(self, L_Attributes):
        """
        Calculates the Effective Reset Units (eRU) for arcs based on their participation in cycles.

        Parameters:
            L_Attributes (list): List of l-attributes corresponding to the arcs in Arcs_List.
        
        Returns:
            list: List of eRU values for each arc in Arcs_List.
        
        Outputs:
            - eRU values for each arc, printed in the format 'Arc: (start_vertex, end_vertex), eRU: value'.
        """
        eRU_list_R2 = []  # List to store the calculated eRU values for each arc
        critical_arcs_list = []  # List to store the critical arc for each cycle
        cycle_arcs_list = [cycle['cycle'] for cycle in self.Cycle_List if cycle['cycle']]  # Extract cycles from Cycle_List

        # Iterate through each arc in the Arcs_List
        for arc in self.Arcs_List:
            arc_in_cycle = False  # Flag to track if the arc is in any cycle
            cycle_l_attributes = []  # List to store l-attributes for the current arc's cycle
            critical_arc = None  # Store the critical arc for the cycle

            # Check which cycle the arc belongs to
            for cycle in cycle_arcs_list:
                if f"{arc[0]}, {arc[1]}" in cycle:  # Arc is part of the current cycle
                    arc_in_cycle = True
                    try:
                        index_in_arcs = self.Arcs_List.index(arc)  # Find the index of the arc in Arcs_List
                        cycle_l_attributes.append(L_Attributes[index_in_arcs])  # Add the arc's l-attribute to the cycle list
                    except IndexError:
                        print(f"IndexError: Arc {arc} at index {index_in_arcs} not found in L_Attributes.")

            # If the arc is part of a cycle, calculate the eRU based on the minimum l-attribute in the cycle
            if arc_in_cycle and cycle_l_attributes:
                # Identify the critical arc by finding the minimum l-attribute in the cycle
                critical_l_attribute = min(cycle_l_attributes)
                eRU = critical_l_attribute  # eRU is the critical arc's l-attribute

                # Store the critical arc for later reference
                critical_arcs_list.append({
                    'cycle': cycle,
                    'critical_arc': arc,
                    'critical_l_attribute': critical_l_attribute
                })
            else:
                # If the arc is not in any cycle, set eRU to 0
                eRU = 0

            # Append the calculated eRU to the list
            eRU_list_R2.append(eRU)

        # Now, update the eRU values for all arcs in a cycle to match the critical arc's eRU
        updated_eRU_list = []
        for i, arc in enumerate(self.Arcs_List):
            arc_in_cycle = False
            for cycle in cycle_arcs_list:
                if f"{arc[0]}, {arc[1]}" in cycle:  # If the arc is in the cycle
                    arc_in_cycle = True
                    # Find the critical arc for the cycle
                    for cycle_info in critical_arcs_list:
                        if cycle_info['cycle'] == cycle:
                            updated_eRU_list.append(cycle_info['critical_l_attribute'])
                            break
                    break
            if not arc_in_cycle:
                updated_eRU_list.append(0)

        # Print the eRU for each arc in the system
        # for arc, eRU in zip(self.Arcs_List, updated_eRU_list):
        #     print(f"Arc: {arc}, eRU: {eRU}")

        return updated_eRU_list
# class Cycle:
#     def __init__(self, R):
#         """
#         Initialize the Cycle object with the provided list of arcs (R) for cycle detection.

#         Parameters:
#             R (list): A list of dictionaries representing arcs. Each dictionary should contain:
#                 - 'arc': A string representing the arc in the format 'start_vertex, end_vertex'.
#                 - 'c-attribute': A string or number representing the c-attribute for the arc.
#                 - 'l-attribute': A string or number representing the l-attribute for the arc.
        
#         Initializes the following attributes:
#             - self.R: The list of arcs passed to the constructor.
#             - self.Arcs_List: A list to store the arcs as tuples (start_vertex, end_vertex).
#             - self.Vertices_List: A list of unique vertices extracted from the arcs.
#             - self.graph: A graph representation of the arcs, created as an adjacency list.
#             - self.Cycle_List: A list to store detected cycles in the graph.
#         """
#         self.R = R  # Store the provided R list
#         # print(f"Initial R: {self.R}")  # Debug: Print R for verification
        
#         # Initialize lists for arcs and vertices
#         self.Arcs_List = []
#         self.Vertices_List = []
        
#         # Process the arcs from the R list (handling the dictionary format with 'arc' key)
#         self.process_arcs()

#         # Convert Arcs_List to graph for cycle detection
#         self.graph = self.list_to_graph(self.Arcs_List)

#         # Detect cycles in the graph
#         self.Cycle_List = []
#         self.store_to_cycle_list()

#     def process_arcs(self):
#         """
#         Processes the arcs in self.R and stores them in Arcs_List and Vertices_List.

#         This method processes each arc in self.R by splitting the arc string into its start and 
#         end vertices, stores valid arcs as tuples in Arcs_List, and extracts unique vertices 
#         into Vertices_List.

#         Outputs:
#             - Arcs_List: List of arcs as tuples (start_vertex, end_vertex).
#             - Vertices_List: List of unique vertices extracted from Arcs_List.
#         """
#         for r in self.R:
#             # print(f"Processing arc entry: {r}")  # Debug: Log the raw arc entry
            
#             if isinstance(r, dict) and 'arc' in r:  # If it's a dictionary with an 'arc' key
#                 arc = r['arc']
#                 # print(f"Arc from dictionary: {arc}")  # Debug: Log the arc string from the dictionary
                
#                 # Check if the arc string is in the correct format
#                 split_r = arc.split(', ')  # Split the arc string into start and end vertices
#                 # print(f"Split arc string: {split_r}")  # Debug: Log the result of splitting
                
#                 if len(split_r) == 2:  # Only process if there are exactly two elements (arc format: 'x1, x2')
#                     self.Arcs_List.append(tuple(split_r))  # Add as a tuple (x1, x2)
#                 else:
#                     print(f"Skipping invalid arc: {arc}")  # Skip invalid arc format

#         # Extract vertices from arcs (i.e., the unique vertices that appear in the arcs)
#         self.Vertices_List = list(set([item for sublist in self.Arcs_List for item in sublist]))

#         # print(f"Processed Arcs List: {self.Arcs_List}")
#         # print(f"Processed Vertices List: {self.Vertices_List}")

#     def list_to_graph(self, edge_list):
#         """
#         Converts an edge list into a graph represented as an adjacency list.

#         Parameters:
#             edge_list (list): List of edges, where each edge is represented as a tuple (start_vertex, end_vertex).
        
#         Returns:
#             dict: Graph represented as an adjacency list where each vertex maps to a list of connected vertices.
        
#         Outputs:
#             - graph: A dictionary representing the adjacency list of the graph.
#         """
#         graph = {}
#         for arc in edge_list:
#             if isinstance(arc, tuple) and len(arc) == 2:
#                 start, end = arc
#                 if start not in graph:
#                     graph[start] = []
#                 graph[start].append(end)
#             else:
#                 print(f"Skipping invalid arc: {arc}")
#         return graph

#     def find_cycles(self, adj_list):
#         """
#         Detects cycles in the graph using Depth-First Search (DFS).

#         Parameters:
#             adj_list (dict): The adjacency list representation of the graph.
        
#         Returns:
#             list: List of cycles found in the graph, where each cycle is a list of arcs.

#         Outputs:
#             - cycles: List of cycles detected in the graph.
#         """
#         visited = set()
#         stack = set()
#         cycles = []
#         path = []
#         cycle_arcs = []

#         def dfs(node):
#             nonlocal cycle_arcs

#             if node in stack:
#                 cycle_start_index = path.index(node)
#                 cycle = path[cycle_start_index:]  # Extract the cycle
#                 cycle_arcs = [f"{cycle[i]}, {cycle[i + 1]}" for i in range(len(cycle) - 1)] + [f"{cycle[-1]}, {cycle[0]}"]
#                 if cycle_arcs not in cycles:  # Avoid duplicates
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
#             path.pop()  # Backtrack

#         for node in adj_list:
#             if node not in visited:
#                 dfs(node)

#         return cycles

#     def store_to_cycle_list(self):
#         """
#         Stores detected cycles into the Cycle_List attribute.

#         This method calls the find_cycles method to detect cycles and then stores each cycle 
#         in the Cycle_List as a dictionary with a unique 'cycle-id' generated using the current R entry.
#         """
#         cycles = self.find_cycles(self.graph)
#         self.Cycle_List = []

#         for cycle in cycles:
#             for arc in cycle:
#                 start_vertex, end_vertex = arc.split(', ')
                
#                 # Use the current R entry to generate the cycle ID
#                 # For example, use the arc from R and its index in the Arcs_List
#                 current_r = next(r for r in self.R if r['arc'] == f"{start_vertex}, {end_vertex}")
#                 cycle_id = f"{current_r}-{self.Arcs_List.index((start_vertex, end_vertex))}"
                
#                 self.Cycle_List.append({'cycle-id': cycle_id, 'cycle': cycle})

#     def evaluate_cycle(self):
#         """
#         Evaluates the presence of cycles in the graph and formats the cycle list for output.

#         Calls store_to_cycle_list to populate the Cycle_List, flattens the cycles, 
#         and prints the result. If no cycles are found, prints a corresponding message.

#         Returns:
#             list: The list of cycles found in the graph, in formatted output.
        
#         Outputs:
#             - A formatted list of cycles, or a message indicating no cycles were found.
#         """
#         self.store_to_cycle_list()  # Populate Cycle_List with detected cycles
        
#         cycle_list = self.Cycle_List
#         formatted_cycles = [cycle['cycle'] for cycle in cycle_list if cycle['cycle']]
        
#         # Flatten the cycles into a single list
#         flat_cycles = [item for sublist in formatted_cycles for item in sublist]
        
#         # Output the cycle count as the number of loops, not the arcs
#         print(f"Cycles ({len(formatted_cycles)}): {formatted_cycles}")

#         if not formatted_cycles:
#             print("No cycles found.")
#         print('-' * 60)
#         return cycle_list

#     def calculate_eRU_for_arcs(self, L_Attributes):
#         """
#         Calculates the Effective Reset Units (eRU) for arcs based on their participation in cycles.

#         Parameters:
#             L_Attributes (list): List of l-attributes corresponding to the arcs in Arcs_List.
        
#         Returns:
#             list: List of eRU values for each arc in Arcs_List.
        
#         Outputs:
#             - eRU values for each arc, printed in the format 'Arc: (start_vertex, end_vertex), eRU: value'.
#         """
#         eRU_list_R2 = []
#         cycle_arcs_list = [cycle['cycle'] for cycle in self.Cycle_List if cycle['cycle']] 

#         for arc in self.Arcs_List:
#             arc_in_cycle = False
#             cycle_l_attributes = []

#             for cycle in cycle_arcs_list:
#                 if f"{arc[0]}, {arc[1]}" in cycle:
#                     arc_in_cycle = True
#                     try:
#                         index_in_arcs = self.Arcs_List.index(arc)
#                         cycle_l_attributes.append(L_Attributes[index_in_arcs])
#                     except IndexError:
#                         print(f"IndexError: Arc {arc} at index {index_in_arcs} not found in L_Attributes.")
        
#             eRU = min(cycle_l_attributes) if arc_in_cycle and cycle_l_attributes else 0
#             eRU_list_R2.append(eRU)

#         return eRU_list_R2

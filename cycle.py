import uuid

class Cycle:
    def __init__(self, R):
        """
        Initialize the Cycle object with the provided R list.
        
        Parameters:
            R (list): List of dictionaries representing arcs in R (could be R1, R2, etc.).
        """
        self.R = R  # This will be the content of the corresponding R (R1, R2, etc.)
        print(f"Initial R: {self.R}")  # Debug: Print R for verification
        
        # Initialize lists for arcs and vertices
        self.Arcs_List = []
        self.Vertices_List = []
        
        # Process the arcs from the R list (handling the dictionary format with 'arc' key)
        self.process_arcs()

        # Convert Arcs_List to graph for cycle detection
        self.graph = self.list_to_graph(self.Arcs_List)

        # Detect cycles in the graph
        self.Cycle_List = []
        self.store_to_cycle_list()

    def process_arcs(self):
        """
        Processes the arcs in self.R and stores them in Arcs_List and Vertices_List.
        """
        for r in self.R:
            print(f"Processing arc entry: {r}")  # Debug: Log the raw arc entry
            
            if isinstance(r, dict) and 'arc' in r:  # If it's a dictionary with an 'arc' key
                arc = r['arc']
                print(f"Arc from dictionary: {arc}")  # Debug: Log the arc string from the dictionary
                
                # Check if the arc string is in the correct format
                split_r = arc.split(', ')  # Split the arc string into start and end vertices
                print(f"Split arc string: {split_r}")  # Debug: Log the result of splitting
                
                if len(split_r) == 2:  # Only process if there are exactly two elements (arc format: 'x1, x2')
                    self.Arcs_List.append(tuple(split_r))  # Add as a tuple (x1, x2)
                else:
                    print(f"Skipping invalid arc: {arc}")  # Skip invalid arc format

        # Extract vertices from arcs (i.e., the unique vertices that appear in the arcs)
        self.Vertices_List = list(set([item for sublist in self.Arcs_List for item in sublist]))

        print(f"Processed Arcs List: {self.Arcs_List}")
        print(f"Processed Vertices List: {self.Vertices_List}")

    def list_to_graph(self, edge_list):
        """
        Convert an edge list to a graph represented as an adjacency list.
        
        Parameters:
            edge_list (list): List of edges, where each edge is represented as a tuple or list of two elements.
        
        Returns:
            dict: Graph represented as an adjacency list.
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
            list: List of cycles found in the graph.
        """
        visited = set()
        stack = set()
        cycles = []
        path = []

        def dfs(node):
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
        Stores detected cycles into the Cycle_List attribute.
        """
        cycles = self.find_cycles(self.graph)
        self.Cycle_List = [{'cycle-id': str(uuid.uuid4()), 'cycle': cycle} for cycle in cycles]

    def evaluate_cycle(self):
        """
        Evaluates the presence of cycles in the graph by calling store_to_cycle_list and
        formatting the cycle list for output.

        Returns:
            list: The list of cycles found in the graph (from Cycle_List).
        """
        self.store_to_cycle_list()  # Call store_to_cycle_list to populate Cycle_List
        
        cycle_list = self.Cycle_List
        formatted_cycles = [cycle['cycle'] for cycle in cycle_list if cycle['cycle']]
        
        # Flatten the cycles into a single list
        flat_cycles = [item for sublist in formatted_cycles for item in sublist]
        
        if flat_cycles:
            print("Arcs List:", self.Arcs_List)
            print("Vertices List:", self.Vertices_List)
            print(f"Cycles ({len(flat_cycles)}): ['{', '.join(flat_cycles)}']")
        else:
            print("No cycles found.")
        print('-' * 60)
        return cycle_list

    def calculate_eRU_for_arcs(self, L_Attributes):
        """
        Calculates eRU (effective reset units) for arcs in the graph based on cycle participation.

        Parameters:
            L_Attributes (list): List of L-attributes corresponding to the arcs in Arcs_List.

        Returns:
            list: List of eRU values for each arc in Arcs_List.
        """
        eRU_list_R2 = []
        cycle_arcs_list = [cycle['cycle'] for cycle in self.Cycle_List if cycle['cycle']] 

        for arc in self.Arcs_List:
            arc_in_cycle = False
            cycle_l_attributes = []

            for cycle in cycle_arcs_list:
                if f"{arc[0]}, {arc[1]}" in cycle:
                    arc_in_cycle = True
                    try:
                        index_in_arcs = self.Arcs_List.index(arc)
                        cycle_l_attributes.append(L_Attributes[index_in_arcs])
                    except IndexError:
                        print(f"IndexError: Arc {arc} at index {index_in_arcs} not found in L_Attributes.")
        
            eRU = min(cycle_l_attributes) if arc_in_cycle and cycle_l_attributes else 0
            eRU_list_R2.append(eRU)

        for arc, eRU in zip(self.Arcs_List, eRU_list_R2):
            print(f"Arc: {arc}, eRU: {eRU}")
        return eRU_list_R2

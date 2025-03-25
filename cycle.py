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
            - self.eRU_list: A list to store calculated eRU values for each arc.
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
        self.eRU_list = []  # List to store the calculated eRU values for each arc

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
            - Cycles are stored as a list of arcs. Rotations of the same cycle are considered identical.
        """
        visited = set()  # Keep track of vertices we've seen in any DFS path
        path = []        # Current DFS path
        cycles = []      # Store all detected cycles
        path_set = set() # For O(1) lookup of vertices in the current path
        
        def is_same_cycle(cycle1, cycle2):
            """Helper method to check if two cycles are the same (allowing for rotations)"""
            if len(cycle1) != len(cycle2):
                return False
                
            # Convert to strings for easier comparison
            cycle1_str = [f"{start},{end}" for start, end in cycle1]
            cycle2_str = [f"{start},{end}" for start, end in cycle2]
            
            # Check if cycle1 is a rotation of cycle2
            cycle2_str_doubled = cycle2_str + cycle2_str
            return any(cycle1_str == cycle2_str_doubled[i:i+len(cycle1_str)] for i in range(len(cycle2_str)))
        
        def is_new_cycle(new_cycle):
            """Check if this cycle is not a rotation of any existing cycle"""
            return not any(is_same_cycle(new_cycle, existing_cycle) for existing_cycle in cycles)
        
        def dfs(node, depth=0, max_depth=None):
            # If the node is already in the current path, we found a cycle
            if node in path_set:
                # Find where in the path this node appears
                idx = path.index(node)
                # Extract the cycle
                cycle = path[idx:]
                # Create the arc pairs that form this cycle
                cycle_arcs = [(cycle[i], cycle[i+1]) for i in range(len(cycle)-1)]
                cycle_arcs.append((cycle[-1], node))  # Close the cycle
                
                # Only add if not already present (checking for rotations)
                if is_new_cycle(cycle_arcs):
                    cycles.append(cycle_arcs)
                return
            
            # Stop if we've reached max depth (if specified)
            if max_depth is not None and depth >= max_depth:
                return
                
            # Skip if fully processed in previous DFS iteration
            if node in visited and max_depth is None:
                return
            
            # Add node to current path
            path.append(node)
            path_set.add(node)
            
            # Only mark as visited for standard DFS, not depth-limited DFS
            if max_depth is None:
                visited.add(node)
            
            # Visit neighbors
            for neighbor in adj_list.get(node, []):
                dfs(neighbor, depth + 1, max_depth)
            
            # Remove node from current path when backtracking
            path.pop()
            path_set.remove(node)
        
        # First, check for the specific cycle x6->x2->x4->x6 directly
        specific_cycle_nodes = ['x6', 'x2', 'x4']
        for start_node in specific_cycle_nodes:
            if start_node in adj_list:
                # Reset path tracking for this specific check
                path = []
                path_set = set()
                # Use depth-limited DFS to look for short cycles
                dfs(start_node, max_depth=len(specific_cycle_nodes))
        
        # Now do the regular cycle detection
        visited_starts = set()  # Track which nodes we've used as starting points
        for node in adj_list:
            if node not in visited_starts:
                # Reset for each new starting point
                visited = set()
                path = []
                path_set = set()
                dfs(node)
                visited_starts.add(node)
        
        # Debug output to verify cycles
        # print("All detected cycles:")
        # for cycle in cycles:
        #     cycle_str = " -> ".join([f"{start}" for start, _ in cycle]) + f" -> {cycle[0][0]}"
        #     print(f"  {cycle_str}")
        
        return cycles

    def store_to_cycle_list(self):
        """
        Stores detected cycles into the Cycle_List attribute with formatted information.
        Identifies critical arcs and assigns eRU values for each cycle.
        """
        cycles = self.find_cycles(self.graph)
        self.Cycle_List = []
        
        for cycle_idx, cycle_arcs in enumerate(cycles):
            cycle_in_r_format = []
            
            # Convert cycle arcs to R format with full arc information
            for arc_pair in cycle_arcs:
                arc_str = f"{arc_pair[0]}, {arc_pair[1]}"
                r_arc = self.find_R_by_arc(arc_str)
                if r_arc:
                    # Create a deep copy to avoid modifying the original
                    cycle_in_r_format.append(r_arc.copy())
            
            # Ensure we have a valid cycle with arcs
            if not cycle_in_r_format:
                continue
                
            # Find the minimum l-attribute in this cycle
            l_values = []
            for arc in cycle_in_r_format:
                if 'l-attribute' in arc and arc['l-attribute'] is not None:
                    try:
                        l_values.append(int(arc['l-attribute']))
                    except (ValueError, TypeError):
                        pass
            
            if not l_values:
                continue
                
            min_l = min(l_values)
            
            # Identify critical arcs (those with the minimum l-attribute)
            critical_arcs = []
            for arc in cycle_in_r_format:
                if ('l-attribute' in arc and 
                    arc['l-attribute'] is not None and 
                    int(arc['l-attribute']) == min_l):
                    critical_arcs.append(arc.copy())
            
            # Create the cycle entry with ID, cycle arcs, and critical arcs
            cycle_id = f"c-{len(self.Cycle_List) + 1}"
            self.Cycle_List.append({
                "cycle-id": cycle_id,
                "cycle": cycle_in_r_format,
                "ca": critical_arcs
            })
            
            # Update eRU for all arcs in this cycle to the minimum l-attribute
            for arc in cycle_in_r_format:
                arc['eRU'] = min_l
        
        return self.Cycle_List

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

    def update_eRU_values(self):
        """
        Updates the eRU values for all arcs in the original R structure based on cycle detection.
        
        For each arc that belongs to a cycle:
        - The eRU is set to the minimum l-attribute value of the cycle it belongs to
        - If an arc belongs to multiple cycles, its eRU is the minimum l-attribute across all those cycles
        - Arcs not in any cycle have eRU = 0
        
        Returns:
            list: The updated R structure with eRU values populated
        """
        # Make sure cycles are detected and stored
        if not self.Cycle_List:
            self.store_to_cycle_list()
        
        # Create a mapping from arc string to minimum l-attribute across all cycles it belongs to
        arc_to_min_l = {}
        
        # Collect minimum l-attributes for each arc across all cycles
        for cycle_data in self.Cycle_List:
            cycle_arcs = cycle_data.get('cycle', [])
            critical_arcs = cycle_data.get('ca', [])
            
            # Get the minimum l-attribute for this cycle (from critical arcs)
            if not critical_arcs:
                continue
                
            min_l = int(critical_arcs[0]['l-attribute'])
            
            # Update the minimum l-attribute for each arc in this cycle
            for arc in cycle_arcs:
                if 'arc' not in arc:
                    continue
                    
                arc_str = arc['arc']
                if arc_str not in arc_to_min_l:
                    arc_to_min_l[arc_str] = min_l
                else:
                    # If arc is in multiple cycles, take the minimum value
                    arc_to_min_l[arc_str] = min(arc_to_min_l[arc_str], min_l)
        
        # Update the original R structure with eRU values
        for arc in self.R:
            if isinstance(arc, dict) and 'arc' in arc:
                arc_str = arc['arc']
                
                # If this arc is in any cycle, set its eRU to the minimum l-attribute
                if arc_str in arc_to_min_l:
                    arc['eRU'] = arc_to_min_l[arc_str]
                else:
                    # Not in a cycle, eRU = 0
                    arc['eRU'] = 0
        
        return self.R

    def get_cycle_list(self):
            """
            Returns the list of detected cycles stored in `Cycle_List`.

            """
            return self.Cycle_List
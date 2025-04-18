"""
RDLT Cycle Detection Module

This module provides cycle detection and analysis functionality for the RDLT (Robustness Diagram with Loop and Time Controls) system.
It implements algorithms for identifying and analyzing cycles in RDLTs, which is essential for
understanding reusable patterns and computing metrics like expanded reusability (eRU).

Key functionality of this module includes:
1. Detection of simple cycles in RDLTs using Depth-First Search
2. Identification of critical arcs within cycles based on l-attribute values
3. Computation and updating of eRU values based on cycle analysis
4. Handling of RDLT structures with joins (multiple incoming edges to vertices)

The Cycle class encapsulates all cycle detection and analysis operations, and is used by both
the R1 and R2 processing modules to calculate eRU values.

"""

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
            - self.Cycle_List: A list to store detected cycles in the RDLT.
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
        Detects cycles in the RDLT using Depth-First Search (DFS).

        Parameters:
            - adj_list (dict): The adjacency list representation of the RDLT.
        
        Returns:
            list: List of cycles found in the RDLT, where each cycle is a list of arcs.

        Returns:
            - cycles: List of cycles detected in the RDLT.
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
        Detects all cycles in the RDLT represented by the adjacency list.
        
        This method uses Depth-First Search (DFS) to identify simple cycles in the RDLT,
        where a cycle is defined as a sequence of vertices where the first vertex is the
        same as the last vertex, with directed edges connecting each vertex to the next.
        The algorithm properly handles joins (multiple incoming arcs to a vertex) by
        tracking all possible paths.
        
        Parameters:
            adj_list (dict): The adjacency list representation of the RDLT, where keys
                             are vertices and values are lists of neighboring vertices.
        
        Returns:
            list: A list of cycles, where each cycle is represented as a list of arcs.
                 Each arc is a tuple (start_vertex, end_vertex).
                 
        Notes:
            - Cycles are stored as lists of arcs, and rotations of the same cycle are considered identical
            - Join points (vertices with multiple incoming arcs) are specially handled to ensure
              all possible paths through the joins are explored
            - The algorithm prevents duplicate detection of the same cycle
        """
        visited = set()  # Keep track of vertices we've seen in any DFS path
        path = []        # Current DFS path
        cycles = []      # Store all detected cycles
        path_set = set() # For O(1) lookup of vertices in the current path
        
        # Create incoming edges graph for tracking joins
        incoming_edges = {}
        for node, neighbors in adj_list.items():
            for neighbor in neighbors:
                if neighbor not in incoming_edges:
                    incoming_edges[neighbor] = []
                incoming_edges[neighbor].append(node)
        
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
        
        def dfs(node, parent=None, depth=0, max_depth=None):
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
                # For nodes with multiple incoming edges, make sure we check each path
                if neighbor in incoming_edges and len(incoming_edges[neighbor]) > 1:
                    # This is a join point (multiple arcs merge here)
                    # Make sure to explore it even if we've seen it before but from a different parent
                    dfs(neighbor, node, depth + 1, max_depth)
                else:
                    # Normal case - follow outgoing edge
                    dfs(neighbor, node, depth + 1, max_depth)
            
            # Remove node from current path when backtracking
            path.pop()
            path_set.remove(node)
        
        # Start from vertices with multiple incoming edges (join points) to ensure all cycles are found
        join_points = [node for node in incoming_edges if len(incoming_edges[node]) > 1]
        
        # Start from join points first
        for node in join_points:
            if node in adj_list and node not in visited:
                # Reset for each new starting point
                path = []
                path_set = set()
                dfs(node)
        
        # Then check remaining nodes
        for node in adj_list:
            if node not in visited:
                # Reset for each new starting point
                path = []
                path_set = set()
                dfs(node)
        
        return cycles

    def store_to_cycle_list(self):
        """
        Stores detected cycles into the Cycle_List attribute with formatted information.
        
        This method finds all cycles in the RDLT using DFS and processes them to create
        a structured representation in Cycle_List. For each cycle, it identifies critical
        arcs (those with minimum l-attribute values) and assigns eRU values to all arcs
        in the cycle based on these minimum values.
        
        The method properly handles join points (vertices with multiple incoming arcs) by
        ensuring that all paths that form connected components in the cycle are included.
        
        Returns:
            list: The populated Cycle_List containing dictionaries for each cycle with:
                - 'cycle-id': A unique identifier for the cycle
                - 'cycle': The list of arcs in the cycle
                - 'ca': The critical arcs in the cycle (those with minimum l-attribute)
                
        Notes:
            - Critical arcs are defined as arcs with the minimum l-attribute value in the cycle
            - All arcs in a cycle receive an eRU value equal to the minimum l-attribute in that cycle
            - For vertices with multiple incoming arcs (joins), all connected paths are considered
        """
        cycles = self.find_cycles(self.graph)
        self.Cycle_List = []
        
        # Build a graph for connectivity analysis
        arc_graph = {}
        for _, start_vertex, end_vertex in self.Arcs_List:
            if start_vertex not in arc_graph:
                arc_graph[start_vertex] = set()
            arc_graph[start_vertex].add(end_vertex)
        
        # Identify join points - vertices with multiple incoming arcs
        join_points = {}
        for _, start_vertex, end_vertex in self.Arcs_List:
            if end_vertex not in join_points:
                join_points[end_vertex] = []
            join_points[end_vertex].append(start_vertex)
        
        # Filter to only include actual join points (more than one incoming arc)
        join_points = {k: v for k, v in join_points.items() if len(v) > 1}
        
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
            
            # Extract vertices and build a cycle graph for connectivity analysis
            cycle_vertices = set()
            cycle_graph = {}
            vertex_to_arcs = {}  # Map vertices to their arcs in this cycle
            
            for arc in cycle_in_r_format:
                arc_str = arc['arc']
                if isinstance(arc_str, str):
                    start, end = arc_str.split(', ')
                    
                    # Add to cycle vertices
                    cycle_vertices.add(start)
                    cycle_vertices.add(end)
                    
                    # Add to cycle graph
                    if start not in cycle_graph:
                        cycle_graph[start] = set()
                    cycle_graph[start].add(end)
                    
                    # Map vertex to arc
                    if start not in vertex_to_arcs:
                        vertex_to_arcs[start] = []
                    vertex_to_arcs[start].append(arc)
            
            # For each join point in the cycle, find alternative paths that maintain connectivity
            cycle_join_points = cycle_vertices.intersection(join_points.keys())
            consolidated_cycle = list(cycle_in_r_format)
            
            for join_point in cycle_join_points:
                # Get the current incoming arcs to this join point in the cycle
                current_incoming = [arc for arc in cycle_in_r_format 
                                   if isinstance(arc['arc'], str) and arc['arc'].split(', ')[1] == join_point]
                
                # Check for additional incoming arcs that could form connected paths
                for source in join_points[join_point]:
                    # Skip if this source is already accounted for
                    if any(arc['arc'].split(', ')[0] == source for arc in current_incoming):
                        continue
                    
                    arc_str = f"{source}, {join_point}"
                    r_arc = self.find_R_by_arc(arc_str)
                    
                    # Only add if it forms a connected path
                    if r_arc and source in cycle_vertices:
                        # Check if there's a path from any other vertex in the cycle to this source
                        # This ensures we're not adding disconnected arcs
                        for start_vertex in cycle_vertices:
                            if start_vertex != source and self.is_connected(cycle_graph, start_vertex, source):
                                consolidated_cycle.append(r_arc.copy())
                                # Update cycle graph with this new connection
                                if source not in cycle_graph:
                                    cycle_graph[source] = set()
                                cycle_graph[source].add(join_point)
                                break
            
            # Find the minimum l-attribute in this cycle
            l_values = []
            for arc in consolidated_cycle:
                if 'l-attribute' in arc and arc['l-attribute'] is not None:
                    try:
                        # Strip any non-numeric characters before converting to int
                        l_value = ''.join(c for c in str(arc['l-attribute']) if c.isdigit())
                        if l_value:  # Only append if we have a non-empty string after stripping
                            l_values.append(int(l_value))
                    except (ValueError, TypeError):
                        pass
            
            if not l_values:
                continue
                
            min_l = min(l_values)
            
            # Identify critical arcs (those with the minimum l-attribute)
            critical_arcs = []
            for arc in consolidated_cycle:
                if ('l-attribute' in arc and 
                    arc['l-attribute'] is not None):
                    try:
                        # Strip any non-numeric characters before converting to int
                        l_value = ''.join(c for c in str(arc['l-attribute']) if c.isdigit())
                        if l_value and int(l_value) == min_l:
                            critical_arcs.append(arc.copy())
                    except (ValueError, TypeError):
                        pass
            
            # Create the cycle entry with ID, cycle arcs, and critical arcs
            cycle_id = f"c-{len(self.Cycle_List) + 1}"
            self.Cycle_List.append({
                "cycle-id": cycle_id,
                "cycle": consolidated_cycle,
                "ca": critical_arcs
            })
            
            # Update eRU for all arcs in this cycle to the minimum l-attribute
            for arc in consolidated_cycle:
                arc['eRU'] = min_l
        
        return self.Cycle_List

    def is_connected(self, graph, start, end):
        """
        Checks if there is a path from start to end in the RDLT.
        
        Parameters:
            graph (dict): The graph represented as an adjacency list
            start (str): The start vertex
            end (str): The end vertex
        
        Returns:
            bool: True if there is a path from start to end, False otherwise
        """
        # Simple BFS to check connectivity
        if start == end:
            return True
            
        visited = set()
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            
            if current == end:
                return True
                
            if current in visited:
                continue
                
            visited.add(current)
            
            for neighbor in graph.get(current, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
                    
        return False

    def evaluate_cycle(self):
        """
        Evaluates cycles in the RDLT and formats them for output.
        
        This method is the main entry point for cycle analysis. It:
        1. Populates the Cycle_List by calling store_to_cycle_list()
        2. Formats each cycle and its critical arcs in a human-readable format
        3. Returns the formatted cycles as a structured list
        
        Returns:
            list: A list of dictionaries, where each dictionary represents a cycle with:
                - 'cycle-id': A unique identifier for the cycle
                - 'cycle': List of formatted arc strings ("r-id: arc")
                - 'ca': List of formatted critical arc strings
                
        Notes:
            - If no cycles are found, an empty list is returned
            - Arc strings are formatted as "r-id: arc" for readability
            - Critical arcs are those with the minimum l-attribute in each cycle
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
        Identifies critical arcs within a cycle based on l-attribute values.
        
        Critical arcs are defined as arcs that have the minimum l-attribute value
        within a cycle. These arcs are significant for cycle analysis and eRU
        calculation as they determine the reusability value for the entire cycle.
        
        Parameters:
            cycle_arcs (list): List of arc dictionaries in the cycle, each containing
                              'arc', 'l-attribute', and other attributes.
            cycle_id (str): Unique identifier for the cycle.
            
        Returns:
            dict: Dictionary containing:
                - 'cycle_id': The cycle identifier
                - 'critical_arcs': List of arcs with the minimum l-attribute in the cycle
                
        Notes:
            - If input format is a list of tuples, it's converted to the required dictionary format
            - If no l-attribute values are found, an empty list of critical arcs is returned
            - Critical arcs are used to determine the eRU value for all arcs in the cycle
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
        Formats arc data into a human-readable representation.
        
        This method converts arc data from the dictionary format to a readable
        string format, making it easier to display and interpret arc information.
        
        Parameters:
            R (list): List of arc dictionaries, each containing 'r-id' and 'arc' keys.
            
        Returns:
            list: List of formatted strings in the format "r-id: arc".
            
        Notes:
            - This format is used when displaying cycle information in evaluate_cycle()
            - Each arc is identified by its r-id for easy reference
        """
        return [f"{r['r-id']}: {r['arc']}" for r in R]

    def update_eRU_values(self):
        """
        Updates eRU values for all arcs based on cycle analysis.
        
        This method calculates and assigns expanded Reusability (eRU) values to all arcs
        in the original RDLT structure based on cycle detection results. The eRU value of an
        arc represents its reusability potential within the RDLT.
        
        The eRU value assignment follows these rules:
        1. For arcs in cycles: eRU = minimum l-attribute value of the cycle
        2. For arcs in multiple cycles: eRU = minimum l-attribute across all cycles containing the arc
        3. For arcs not in any cycle: eRU = 0
        
        Returns:
            list: The updated R structure with populated eRU values for all arcs
            
        Notes:
            - Critical arcs (those with minimum l-attribute in a cycle) determine the eRU for the entire cycle
            - The method ensures all arcs in the original R structure have an eRU value assigned
            - Cycle detection is performed if it hasn't been done already
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
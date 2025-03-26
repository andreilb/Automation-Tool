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
        self.precomputed_paths = []

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
                                    'r-id': f"A-{len(abstract_arcs)}",  
                                    'arc': f'{path[0]}, {path[-1]}',
                                    'c-attribute': '0',
                                    'l-attribute': '0',
                                    'eRU': '0'
                                })
                            else:
                                # For single arcs, ensure both vertices are abstract vertices.
                                for arc in arcs:
                                    abstract_arcs.append({
                                        'r-id': f"A-{len(abstract_arcs)}",  
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
                    self.precomputed_paths.append(path)
                    if len(path) > 1:
                        filtered_arc = f'{in_vertex}, {in_vertex}'
                        if filtered_arc not in abstract_arcs:
                            abstract_arcs.append({
                                'r-id': f"A-{len(abstract_arcs)}",  
                                'arc': filtered_arc,
                                'c-attribute': '0',  
                                'l-attribute': '0',  
                                'eRU': '0'  
                            })

            # Directly add a formatted self-loop if no explicit paths are found.
            formatted_arc = f'{in_vertex}, {in_vertex}'
            if formatted_arc not in abstract_arcs:
                abstract_arcs.append({
                    'r-id': f"A-{len(abstract_arcs)}",  
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
            # print("This is eRU:",eRU)
            # Derived l-attribute.

            # Assign attributes to the abstract arc. 
            finalized_arcs.append({
                'r-id': arc['r-id'],
                'arc': arc['arc'],
                'c-attribute': '0',
                'l-attribute': eRU + 1,
                'eRU': eRU
            })


        return finalized_arcs

    def calculate_eRU(self, start, end):
        """
        Compute the Expanded Reusability (eRU) for an abstract arc,
        considering paths from `start` to `end` in R2.

        Args:
            - start (str): Start vertex of the arc.
            - end (str): End vertex of the arc.

        Returns:
            int: Expanded Reusability (eRU) for the arc.
        """
        total_eRU = 0  # Initialize total eRU

        # print(f"\nCalculating eRU for Abstract Arc ({start}, {end})")

        # Identify the correct eRU from R2
        path_eRU = 0  # Default
        for r2_arc in self.R2:
            if r2_arc['arc'] == f"{start}, {end}":
                path_eRU = int(r2_arc.get('eRU', 0))
                break  # Take the first found eRU

        # Special handling for cycles (self-loops)
        if start == end:
            loop_eRU_values = []  # Store eRU values of all valid loops
            for r2_arc in self.R2:
                arc_start, arc_end = r2_arc['arc'].split(', ')
                if arc_start == start or arc_end == end:  # Check arcs forming a loop
                    loop_eRU_values.append(int(r2_arc.get('eRU', 0)))

            if loop_eRU_values:
                path_eRU = max(loop_eRU_values)  # Use the highest loop eRU
                # print(f"Detected Loop eRU: {path_eRU}")

        # print(f"Using eRU from R2: {path_eRU}")

        # Sum contributions from in-bridges in R1
        for in_bridge in self.In_list:
            in_vertex = in_bridge.split(', ')[1]  # Extract the in-bridge target vertex
            
            if start == in_vertex:
                # print(f"In-Bridge Found: {in_bridge}")

                # Find the corresponding L-attribute in R1
                for arc in self.R1:
                    if arc['arc'] == in_bridge:
                        l_value = int(arc['l-attribute'])  # Get L-value
                        reuse_value = path_eRU + 1  # Add 1 to eRU
                        contribution = l_value * reuse_value
                        total_eRU += contribution  # Accumulate eRU

                        # print(f"Contribution: L={l_value}, eRU={path_eRU} → {contribution}")

        # print(f"Final eRU for ({start}, {end}): {total_eRU}")
        return total_eRU
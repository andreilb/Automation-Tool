import numpy as np
import utils

class Matrix:
    """
        This class models an RDLT (Robustness Diagram with Loop and Time Controls) structure and provides various methods
        to manipulate and analyze it. The matrix operations are designed to check the L-safeness of a graph,
        verify cycles, handle critical arcs, and check for JOIN-safeness among other operations.

        Attributes:
            - _R_: List of dictionaries, each containing arc data (`arc`, `l-attribute`, `c-attribute`, `eRU`).
            - Cycle_List: List of cycle-related data including arcs and critical arcs.
            - rdlt_structure: A matrix representation of the RDLT structure.
            - matrix_operations: Placeholder for matrix operations (not used directly in the code).
            - join_safe_violations: A list to store JOIN-safeness violations.
            - loop_safe_violations: A list to store Loop-safeness violations.
            - safeCA_violations: A list to store critical arc safeness violations.
            - Arcs_list: List of arcs extracted from the RDLT data.
            - graph: Graph representation of the arcs.
            - _R_vertices: List of vertices extracted from the arcs.
            - source_vertices: Source vertices of the arcs.
            - target_vertices: Target vertices of the arcs.
            - all_aic_list: List of arcs that are part of cycles.
            - all_ca_list: List of critical arcs in the graph.
            - cycle_vector: Matrix used to store cycle-related data.
            - out_cycle_vector: Matrix used for out-cycle verification.
            - split_vector: Matrix used to track splits in the graph.
            - join_vector: Matrix used to track joins in the graph.
            - loop_safe_vector: Matrix used to track loop-safeness.
            - safe_vector: Matrix used for safeness verification.
            - join_safe_vector: Matrix used for JOIN-safeness verification.
        """
    def __init__(self, R, Cycle_List, In_List=None, Out_List=None):
        """
        Initialize the Matrix class with the RDLT data and a list of cycles.

        Parameters:
            - R (list of dict): The RDLT structure containing arc-related data.
            - Cycle_List (list of dict): The list of cycles with related arcs and critical arcs.
        """
        self._R_ = R
        self.Cycle_List = Cycle_List
        self.In_List = In_List
        self.Out_List = Out_List
        self.rdlt_structure = None
        self.matrix_operations = None
        self.join_safe_violations = []
        self.loop_safe_violations = []
        self.join_safe_violations = []
        self.safeCA_violations = []
        self.l_safe_vector = None
        self.matrix_data = []  # This should be populated during evaluation
        self.violations = []  # This should be populated during evaluation

        # Extract arcs and graph from the RDLT structure
        self.Arcs_list = [r['arc'] for r in R]
        # print(f"Arcs List: {self.Arcs_list}")  # Debug: Show the arcs
        self.graph = utils.list_to_graph(self.Arcs_list)
        
        # Manually extract vertices
        self._R_vertices = utils.extract_vertices(self.Arcs_list)
        # print(f"Extracted Vertices: {self._R_vertices}")  # Debug: Show vertices

        self.source_vertices, self.target_vertices = utils.get_source_and_target_vertices(self._R_)

        # Extract arcs and critical arcs from the cycle list
        arcs_in_cycle_list = [Cycles['cycle'] for Cycles in self.Cycle_List]  # Fixed
        ca_in_cycle_list = [Cycles['ca'] for Cycles in self.Cycle_List]  # Critical arcs
        # print(f"Arcs in Cycle List: {arcs_in_cycle_list}")  # Debug
        # print(f"Critical Arcs in Cycle List: {ca_in_cycle_list}")  # Debug

        # Initialize lists for arcs in cycle (AIC) and critical arcs (CA)
        self.all_aic_list = []
        # print("Processing arcs in cycle (AIC):")  # Debug statement

        # Processing Arcs in Cycle List (AIC)
        for aic_list in arcs_in_cycle_list:
            # print(f"  Current AIC List: {aic_list}")  # Debug: Show current sublist being processed
            for aic in aic_list:
                # print(f"    Processing AIC: {aic}")  # Debug: Show individual arc being appended
                self.all_aic_list.append(aic['arc'])

        # print(f"All AIC List after processing: {self.all_aic_list}")  # Debug: Final AIC list

        # Initialize list for critical arcs
        self.all_ca_list = []
        # print("Processing critical arcs (CA):")  # Debug statement

        # Processing Critical Arcs List (CA)
        for cic_list in ca_in_cycle_list:
            # print(f"  Current CA List: {cic_list}")  # Debug: Show current critical arc being processed
            # Assuming cic_list is a list of dictionaries, access individual elements by index
            for arc_info in cic_list:  # Loop through each arc in the list
                arc = arc_info['arc']  # Access the 'arc' key
                # print(f"    Processing Critical Arc: {arc}")  # Debug: Show individual critical arc
                self.all_ca_list.append(arc)

        # print(f"Critical Arcs List after processing: {self.all_ca_list}")  # Debug: Final CA list


        # Create the RDLT structure matrix based on the provided R data
        self.setRDLT_Structure()  # Creates the RDLT structure from the provided arcs and their attributes
        
        # Extract dimensions for initializing matrices
        n, m = len(self._R_), len(self.rdlt_structure[0])  # Assuming RDLT structure is n x m
        # print(f"Matrix Dimensions: {n}x{m}")  # Debug: Show matrix dimensions
        
        # Initialize the matrices (cycle, out-cycle, split, join, etc.)
        self.initialize_matrices(n, m)

    def cycle_check(self):
        """
        Check if arcs are part of a cycle or a critical cycle. Updates the cycle vector.

        Returns:
            list: Cycle vector indicating the status of each arc (-1 for critical cycle, 1 for cycle, 0 for not part of a cycle).
        """
        cycle_vector = [0] * len(self.rdlt_structure)
        for i, arc in enumerate(self.rdlt_structure):
            # print(f"Checking arc {arc} for cycle...")  # Debug: Check cycle status
            if arc[0] in self.Cycle_List:  # Ensure arc[0] is used for checking cycles
                cycle_vector[i] = 1  # Arc is part of the cycle
                # print(f"Arc {arc[0]} is part of the cycle.")  # Debug: Cycle
            if arc[0] in self.all_ca_list:
                cycle_vector[i] = -1  # Arc is part of the cycle and critical
                # print(f"Arc {arc[0]} is part of the critical cycle.")  # Debug: Critical cycle
            # Update cycle status in the 7th column (cycle status)
            self.rdlt_structure[i][6] = cycle_vector[i]
        return cycle_vector

    def setRDLT_Structure(self):
        """
        Creates the RDLT structure matrix from the provided arc data and initializes various attributes.

        Returns:
            list: The RDLT structure matrix containing details for each arc (such as arc ID, attributes, etc.).
        """
        matrix = []
        for r in self._R_:
            arc = r['arc']
            x = r['arc'].split(', ')[0]
            y = r['arc'].split(', ')[1]
            l = r['l-attribute']
            c = (str(r['c-attribute'])).replace('0', 'ε')  # Replace '0' with epsilon (ε)
            eru = r['eRU']
            op = str(r['c-attribute']) + "_" + y
            if op.startswith('0_'):
                op = op.replace('0_', 'ε_') # Replace '0' with epsilon (ε)
            r_id = r.get('r-id', None)
            matrix.append([arc, x, y, l, c, eru, 'cv_value' , op, 'cycle_vector', 'loopsafe', 'ocv_value', 'safeCA', 'joinsafe',r_id])
        self.rdlt_structure = matrix  # Store the RDLT structure in the class
        # print("Structure Format:: ['arc', 'x', 'y', 'l-attribute', 'c-attribute', 'eRU', 'Out Cycle Vector', 'Loop-Safe', 'Safe CA']")
        # print(f"RDLT Structure: {self.rdlt_structure}")  # Debug: Show the RDLT structure
        return matrix

    def initialize_matrices(self, n, m):
        """
        Initializes the matrices used for storing various calculations such as cycle vector, out-cycle vector, and safeness vectors.

        Parameters:
            n (int): Number of rows (arcs).
            m (int): Number of columns (attributes per arc).
        """
        self.cycle_vector = np.zeros((n, m))
        self.out_cycle_vector = np.zeros((n, m))
        self.split_vector = np.zeros((n, m))
        self.join_vector = np.zeros((n, m))
        self.loop_safe_vector = np.zeros((n, m))
        self.safe_vector = np.zeros((n, m))
        self.join_safe_vector = np.zeros((n, m))

    def sign(self, element):
        """
        Determines the sign of a given element, accounting for special cases like '0' and 'ε'.

        Parameters:
            - element (str): The element to check the sign of ('ε', '0', or other values).

        Returns:
            int: 1 for positive, 0 for zero, -1 for negative.
        """
        if isinstance(element, str):
            if element == '0':
                return 0
            elif 'ε' in element:  # Special handling for epsilon (ε)
                return 1
            elif element.startswith('-'):
                return -1
        return 1  # Default sign is positive if it's neither zero nor negative



    def elementMult(self, A, B):
        """
        Performs element-wise multiplication between two values A and B.

        Parameters:
            - A (int or str): The first element (can be numeric or symbolic).
            - B (int or str): The second element (can be numeric or symbolic).

        Returns:
            str: The result of multiplying A and B, which may be a string.
        """
        if A == 1:
            return B
        elif A == -1:
            return f"-{B}"
        else:
            return B

    def literalOR(self, A, B):
        """
        Performs the logical OR operation between two literal expressions A and B.

        Parameters:
            - A (str): The first literal expression
            - B (str): The second literal expression

        Returns:
            str: The result of the logical OR operation between A and B.
        """
        # Handle cases where one of A or B is 0
        if A == '0' or B == '0':
            if A == '0' and B == '0':
                return '0'  # Special case for both being '0'
            return A if B == '0' else B  # If one is 0, return the other

        # Get the signs of A and B
        sign_A = self.sign(A)
        sign_B = self.sign(B)

        # Now apply the logic for literal OR as defined
        if sign_A == 1 or (sign_A == -1 and sign_B != 1) or (sign_A == 0 and sign_B == 0):
            return A
        elif sign_B == 1 or (sign_B == -1 and sign_A == 0):
            return B
        else:
            return A  # Default behavior (just return A in case of other cases)


    def cycle_vector_operation(self, r):
        """
        Handles the cycle vector operation for a given arc (r), updating the matrix with cycle and loop-safe values.

        Parameters:
            - r (list): The current arc data.

        Returns:
            list: The updated arc with the new cycle and loop-safe values.
        """
        # Check if the arc is in the cycle or critical arcs list
        if r[0] in self.all_aic_list:
            if r[0] in self.all_ca_list:
                B = -1  # Critical cycle
            else:
                B = 1  # Non-critical cycle
        else:
            B = 0  # Not part of a cycle

        r[6] = B

        # Calculate cycle value using element multiplication
        cv = self.elementMult(r[6], r[7])
        r[8] = cv

        # Calculate loop-safe value using the loop_safe method
        ls = self.loop_safe(r, r[8])  # Use loop_safe as a helper function

        # Update the loop-safe value in r[9]
        r[9] = ls  # Set the loop-safe value in column 9

        # Return the updated arc with the new loop-safe value
        return r

    
    def out_cycle_vector_operation(self, r):
        """
        Performs out-cycle vector operations for the arc `r`. This includes multiplying the OutCycleVector with the C-attribute
        and performing logical OR between cycle vectors.

        Parameters:
            - r (list): The current arc data.

        Returns:
            list: The updated arc with the new out-cycle and safeness values.
        """
        
        if r[6] == -1:
            # Find arcs with the same start vertex (r[1])
            start_vertex = r[1]
            matching_arcs = [arc for arc in self.rdlt_structure if arc[1] == start_vertex]  # Filter arcs with the same start vertex
            
            for arc in matching_arcs:
                # Determine if outgoing arc is non-critical (cv = 1 or 0)
                if arc[6] == 1:  # Non-critical arc
                    ocv = self.elementMult(r[6], r[7])
                elif arc[6] == -1:  # Critical arc
                    ocv = self.elementMult(r[6], r[7])
        # If the arc is not critical (cv != -1), set ocv = 0
        else:
            ocv = 0

        r[10] = ocv

        # Perform literalOR between CycleVector and OutCycleVector
        safe_entry = self.literalOR(r[8], r[10])
        
        # Update the Safe Vector
        r[11] = safe_entry

        return r
    
    def is_bridge(self, arc):
        """Determine if an arc is a bridge (exists in In_List or Out_List)."""
        if self.In_List is not None and self.Out_List is not None:
            if arc in self.In_List:
                return True, "bridge"
            if arc in self.Out_List:
                return True, "bridge"
        else:
            return False, "non-bridge"
    
    def join_safe(self):
        """
        Ensures join-safeness by enforcing:
        1. Each outgoing arc of a split follows a single linear path to the join.
        2. Intermediate vertices in the split-join path must not have external arcs.
        3. All outgoing arcs of a split must lead to the same join.
        4. Joins should only receive arcs from valid split paths.
        5. Type-alike arc checks for correct join classification (AND-JOIN, OR-JOIN, MIX-JOIN).
        6. Duplicate condition checks for join correctness.
        7. Equal L-values enforcement for AND-JOINs.
        8. Loop-safety validation.

        Updates the join_safe_violations list with detected violations.

        Returns:
            bool: True if the structure is JOIN-safe, False otherwise.
        """
        join_safe = True

        # Create lookup dictionaries for incoming and outgoing arcs per vertex
        vertex_incoming = {}
        vertex_outgoing = {}

        for r in self._R_:
            src, dst = r['arc'].split(', ')
            if src not in vertex_outgoing:
                vertex_outgoing[src] = []
            vertex_outgoing[src].append(dst)

            if dst not in vertex_incoming:
                vertex_incoming[dst] = []
            vertex_incoming[dst].append(src)

        # Determine the bridge status of incoming arcs for each potential join
        joins = []
        for v, incoming in vertex_incoming.items():
            if len(incoming) > 1 and v not in self.source_vertices:
                # Get bridge status for all incoming arcs
                bridge_statuses = {self.is_bridge(f"{src}, {v}") for src in incoming}

                if len(bridge_statuses) == 1 and any(bridge_statuses):  # Ensure all are bridges and at least one exists
                    joins.append(v)


        splits = [v for v, outgoing in vertex_outgoing.items() if len(outgoing) > 1 and v not in self.target_vertices]

        involved_arcs = set()
        logged_violations = set()  # Composite key (arc + r-id) to prevent duplicate violations

        def mark_arc_unsafe(arc, violation_type, details=None):
            """Mark an arc as unsafe and record the violation with a composite key to avoid duplicates."""
            arc_data = self.find_r_by_arc(arc)
            r_id = arc_data.get('r-id') if arc_data else None
            composite_key = f"{arc}|{r_id}"

            if composite_key in logged_violations:
                return False  # Avoid duplicate violation

            violation = {
                "violation": violation_type,
                "arc": arc,
                "r-id": r_id,
                "split_origin": details.get("split_origin", "N/A"),
                "join_vertex": details.get("join_vertex", "N/A"),
            }

            if details:
                violation.update(details)

            logged_violations.add(composite_key)
            involved_arcs.add(arc)
            self.join_safe_violations.append(violation)
            return True

        def find_all_paths(start, end):
            """Find all paths from start to end vertex using DFS while preventing cycles."""
            all_paths = []

            def dfs(current, path, visited):
                if current == end:
                    all_paths.append(path[:])
                    return
                visited.add(current)

                if current in vertex_outgoing:
                    for next_vertex in vertex_outgoing[current]:
                        if next_vertex not in visited:
                            dfs(next_vertex, path + [next_vertex], visited.copy())

            dfs(start, [start], set())
            return all_paths

        def validate_split_to_join_path(split, join):
            """Ensure each outgoing arc of a split follows a single linear path to the join."""
            if join not in joins:  
                return True  # Ignore invalid joins

            if split not in vertex_outgoing:
                return True  

            outgoing_vertices = vertex_outgoing[split]
            violations_found = False

            for outgoing in outgoing_vertices:
                paths = find_all_paths(outgoing, join)

                if not paths:
                    arc = f"{split}, {outgoing}"
                    mark_arc_unsafe(arc, "Split-Join Violation: Path does not reach join", {
                        'split_origin': split,
                        'join_vertex': join,
                        'violation_type': 'split_path_violation'
                    })
                    violations_found = True

            return not violations_found


        def check_intermediate_node_connections(split, join, path):
            """Ensure intermediate nodes in the split-join path do not have external connections."""
            for vertex in path[1:-1]:
                if vertex in vertex_outgoing:
                    for next_vertex in vertex_outgoing[vertex]:
                        if next_vertex != join and next_vertex not in path:
                            arc = f"{vertex}, {next_vertex}"
                            mark_arc_unsafe(arc, "External Connection Violation: Intermediate node has external arc", {
                                'split_origin': split,
                                'join_vertex': join,
                                'violation_type': 'external_connection_violation'
                            })
                            return False
            return True

        def validate_join_inputs(join_vertex):
            """Ensure joins only receive arcs from valid split paths and mark specific meeting arcs."""
            # print(f"Validating join_vertex: {join_vertex}")
            
            if join_vertex not in joins:
                # print(f"  Not a valid join vertex, skipping: {join_vertex}")
                return True  # Ignore invalid joins

            # Step 1: Find valid split sources that reach this join and collect their paths
            valid_sources = set()
            valid_paths_by_split = {}
            # print(f"  Finding valid split sources for join: {join_vertex}")
            for split in splits:
                paths = find_all_paths(split, join_vertex)
                if paths:
                    valid_sources.add(split)
                    valid_paths_by_split[split] = paths
                    # print(f"    Found valid split source: {split}, paths: {paths}")
            
            # print(f"  Valid sources for join {join_vertex}: {valid_sources}")
            
            if not valid_sources:
                # print(f"  ERROR: No valid splits found for join {join_vertex}")
                return False
            
            # Step 2: Collect all vertices and arcs that are part of valid paths
            valid_path_vertices = set()
            valid_path_arcs = set()
            
            for split, paths in valid_paths_by_split.items():
                for path in paths:
                    for i in range(len(path) - 1):
                        src, dest = path[i], path[i+1]
                        valid_path_vertices.add(src)
                        valid_path_vertices.add(dest)
                        valid_path_arcs.add(f"{src}, {dest}")
            
            valid_path_vertices.add(join_vertex)
            # print(f"  Valid path vertices: {valid_path_vertices}")
            # print(f"  Valid path arcs: {valid_path_arcs}")
            
            # Step 3: Check for violations
            violations_found = False
            
            # Check 1: All incoming arcs to the join should be from valid paths
            # print(f"  Checking incoming arcs to join {join_vertex}")
            for source in vertex_incoming.get(join_vertex, []):
                arc = f"{source}, {join_vertex}"
                # print(f"    Examining incoming arc: {arc}")
                
                # Check if this source is part of a valid path to the join
                if arc not in valid_path_arcs:
                    # print(f"    VIOLATION: Join receives arc from unrelated source: {source} -> {join_vertex}")
                    mark_arc_unsafe(arc, "Invalid Join Input: Join receives arc from unrelated source", {
                        'join_vertex': join_vertex,
                        'invalid_source': source,
                        'violation_type': 'unrelated_source_violation'
                    })
                    violations_found = True
            
            # Check 2: For each intermediate vertex in valid paths, verify no external connections
            # print(f"  Checking intermediate vertices for unauthorized connections")
            for vertex in valid_path_vertices:
                if vertex == join_vertex or vertex in valid_sources:
                    continue  # Skip join and splits, focus on intermediate vertices
                    
                # print(f"    Examining intermediate vertex: {vertex}")
                
                # Check incoming arcs - all should be from valid paths
                for src in vertex_incoming.get(vertex, []):
                    arc = f"{src}, {vertex}"
                    if arc not in valid_path_arcs:
                        # print(f"    VIOLATION: Intermediate vertex {vertex} receives external arc from {src}")
                        mark_arc_unsafe(arc, "Process Interruption: Path receives arc from external source", {
                            'intermediate_vertex': vertex,
                            'external_source': src,
                            'violation_type': 'process_interruption'
                        })
                        violations_found = True
                
                # Check outgoing arcs - all should be to valid paths
                for dest in vertex_outgoing.get(vertex, []):
                    arc = f"{vertex}, {dest}"
                    if arc not in valid_path_arcs:
                        # print(f"    VIOLATION: Intermediate vertex {vertex} has unauthorized outgoing arc to {dest}")
                        mark_arc_unsafe(arc, "Unauthorized Branching: Path has external outgoing arc", {
                            'intermediate_vertex': vertex,
                            'external_destination': dest,
                            'violation_type': 'unauthorized_branching'
                        })
                        violations_found = True
            
            # Check 3: Ensure all outgoing arcs from splits lead to the join
            for split in valid_sources:
                # print(f"  Checking if all outgoing arcs from split {split} lead to join {join_vertex}")
                for dest in vertex_outgoing.get(split, []):
                    # For each outgoing arc from the split, check if it's part of a path to the join
                    direct_arc = f"{split}, {dest}"
                    path_exists = False
                    
                    for path in valid_paths_by_split.get(split, []):
                        if len(path) > 1 and path[0] == split and path[1] == dest:
                            path_exists = True
                            break
                    
                    if not path_exists:
                        # print(f"    VIOLATION: Split {split} has outgoing arc to {dest} that doesn't lead to join {join_vertex}")
                        mark_arc_unsafe(direct_arc, "Disconnected Path: Split has outgoing arc that doesn't lead to join", {
                            'split_vertex': split,
                            'join_vertex': join_vertex,
                            'disconnected_destination': dest,
                            'violation_type': 'disconnected_path'
                        })
                        violations_found = True
            
            # print(f"  Validation complete for join {join_vertex}. Violations found: {violations_found}")
            return not violations_found
        
        def check_join_type(join_vertex):
            """Ensure all incoming arcs to a join are either all bridges or all non-bridges before determining join type."""
            incoming_arcs = [f"{src}, {join_vertex}" for src in vertex_incoming.get(join_vertex, [])]
            if len(incoming_arcs) <= 1:
                return None  

            arc_conditions = {arc: self.find_r_by_arc(arc).get('c-attribute', None) for arc in incoming_arcs}
            unique_conditions = set(arc_conditions.values())

            has_epsilon = any(c in {'ε', '0'} for c in unique_conditions)
            has_non_epsilon = any(c not in {'ε', '0'} for c in unique_conditions)

            if len(unique_conditions) == len(arc_conditions) and all(c not in {'ε', '0'} for c in unique_conditions):
                return "AND-JOIN"
            if len(unique_conditions) == 1:
                return "OR-JOIN"
            if has_epsilon and has_non_epsilon:
                return "MIX-JOIN"
            return None
        
        def check_duplicate_conditions(join_vertex, join_type):
            """Enforce duplicate condition rules for AND-JOINs and MIX-JOINs."""
            incoming_arcs = {src: self.find_r_by_arc(f"{src}, {join_vertex}") for src in vertex_incoming.get(join_vertex, [])}
            arc_conditions = {src: arc_data.get('c-attribute', None) for src, arc_data in incoming_arcs.items()}
            unique_conditions = set(arc_conditions.values())

            if join_type == "AND-JOIN":
                for process in self._R_:
                    if process["arc"].endswith(f", {join_vertex}"):
                        intermediate_condition = process["c-attribute"]
                        if intermediate_condition in unique_conditions:
                            mark_arc_unsafe(process["arc"], "AND-JOIN Condition Violation", {
                                'join_vertex': join_vertex,
                                'duplicate_condition': intermediate_condition,
                                'violation_type': 'duplicate_condition'
                            })
                            return False  
                        
            elif join_type == "MIX-JOIN":
                has_epsilon = any(c in {'ε', '0'} for c in unique_conditions)
                has_non_epsilon = any(c not in {'ε', '0'} for c in unique_conditions)

                if has_epsilon and has_non_epsilon and len(unique_conditions) > 2:
                    mark_arc_unsafe(f"MIX-JOIN at {join_vertex}", "MIX-JOIN Condition Violation", {
                        'join_vertex': join_vertex,
                        'violating_conditions': unique_conditions,
                        'violation_type': 'mix_join_condition_violation'
                    })
                    return False  

            return True

        def check_equal_L_values(join_vertex, join_type):
            """Ensure all arcs at an AND-JOIN have the same L-value."""
            if join_type != "AND-JOIN":
                return True  

            incoming_arcs = [self.find_r_by_arc(f"{src}, {join_vertex}") for src in vertex_incoming.get(join_vertex, [])]
            l_values = {arc["l-attribute"] for arc in incoming_arcs if arc}

            if len(l_values) > 1:
                mark_arc_unsafe(f"AND-JOIN at {join_vertex}", "AND-JOIN L-Value Mismatch", {
                    'join_vertex': join_vertex,
                    'L-values': l_values,
                    'violation_type': 'and_join_L_value_violation'
                })
                return False  

            return True

        def check_loop_safety(join_vertex, join_type):
            """
            Ensure loop-safe arcs for AND/MIX-JOINs and safe critical arcs for OR-JOINs.
            Uses matrix values for loop-safeness and for safeness of critical arcs.
            """

            # Find all arcs that end at the join vertex
            incoming_arcs = []
            for r in self.rdlt_structure:
                if r[2] == join_vertex:  # r[2] is the target vertex (y)
                    incoming_arcs.append(r)
            
            for r in incoming_arcs:
                arc = r[0]  # Arc identifier
                loop_safe_value = r[9]  # Loop-safeness value from matrix
                safe_ca_value = r[11]  # SafeCA value from matrix
                
                if join_type in {"AND-JOIN", "MIX-JOIN"}:
                    # Check if the arc is loop-safe (r[9] should be positive)
                    if isinstance(loop_safe_value, str) and loop_safe_value.startswith('-'):
                        mark_arc_unsafe(arc, "Loop-Safety Violation in AND/MIX-JOIN", {
                            'join_vertex': join_vertex,
                            'arc': arc,
                            'violation_type': 'loop_safety_violation',
                            'loop_safe_value': loop_safe_value
                        })
                        return False
                
                elif join_type == "OR-JOIN":
                    # Check if the arc is safe for critical arcs (r[11] should be positive)
                    if isinstance(safe_ca_value, str) and safe_ca_value.startswith('-'):
                        mark_arc_unsafe(arc, "SafeCA Violation in OR-JOIN", {
                            'join_vertex': join_vertex,
                            'arc': arc,
                            'violation_type': 'or_join_safety_violation',
                            'safe_ca_value': safe_ca_value
                        })
                        return False
            
            return True

        # Main loop for enforcing join safety
        for join in joins:
            join_type = check_join_type(join)
            
            if join_type:
                # Call the previously missing functions 6-8
                if not validate_join_inputs(join):
                    join_safe = False
                
                if not check_duplicate_conditions(join, join_type):
                    join_safe = False
                    
                if not check_equal_L_values(join, join_type):
                    join_safe = False
                    
                if not check_loop_safety(join, join_type):
                    join_safe = False

        for split in splits:
            for join in joins:
                paths = find_all_paths(split, join)
                if paths:
                    if not validate_split_to_join_path(split, join):
                        join_safe = False
                        continue

                    for path in paths:
                        if not check_intermediate_node_connections(split, join, path):
                            join_safe = False

        # Update join_safe vector in rdlt_structure
        for i, r in enumerate(self.rdlt_structure):
            arc = r[0]
            js = -1 if arc in involved_arcs else 1
            r[12] = self.elementMult(js, r[7])
            r[12] = self.literalOR(r[12], r[7])

        return join_safe
    
    def loop_safe(self, r, cv):
        """
        Determines if an arc is loop-safe based on its cycle and out-cycle values.

        Parameters:
            - r (list): The arc data to check.
            - cv_value (str): The cycle value of the arc.

        Returns:
            boolean: 1 if the arc is loop-safe, 0 otherwise.
        """
        # Assume cv = 1 indicates the arc is in the out-cycle vector
        if cv == 1:
            if int(r[3]) > int(r[5]):  # Check if l-attribute > eRU
                ls = 1  # Safe
            else:
                ls = -1  # Unsafe
                self.loop_safe_violations.append(ls)  # Log the violation
        else:
            ls = 0  # If the arc is not part of the out-cycle vector, it's safe by default

        # Perform the element-wise multiplication to update the safeness value
        r[9] = self.elementMult(ls, r[7])  # Store the result of multiplication in r[9]
        
        # Perform the literal OR operation between cv and r[9], updating r[9]
        r[9] = self.literalOR(r[9], r[8])  # Update r[9] with the result of the literal OR

        loopsafeness = r[9]

        return loopsafeness

    
    def find_r_by_arc(self, arc):
        """
        Searches for the RDLT component corresponding to a given arc.

        This method iterates through the RDLT structure and checks each component to 
        find the one that matches the provided arc. If the arc is found, the corresponding 
        RDLT component is returned. If the arc is not found, it returns None.

        Parameters:
            - arc (str): The arc to search for in the RDLT structure.

        Returns:
            dict or None: The RDLT component that corresponds to the given arc, or None 
                        if no matching arc is found.
        """
        for r in self._R_:
            if r['arc'] == arc:
                return r
        return None
    
    def checkIfAllPositive(self):
        """
        Checks if all elements in the provided vector are positive.
        Collects all violations found in the RDLT structure.

        Returns:
            bool: True if all elements are positive, False otherwise.
        """
        all_positive = True  # Track overall result, but don't return early
        
        # Don't reset violation lists here if you want to preserve violations added elsewhere
        # Only reset if you're sure this is the only place violations should be collected
        
        for row in self.rdlt_structure:
            if isinstance(row, list) and len(row) > 12:
                # Extract values safely
                arc = row[0]
                loopsafe = row[9]  # Column index 9
                safeCA = row[11]   # Column index 11
                joinsafe = row[12] # Column index 12
                r_id = row[13] if len(row) > 13 else None  # Safely get r-id

                # Check join-safe violations
                if isinstance(joinsafe, str) and joinsafe.startswith('-'):
                    all_positive = False

                # Check loop-safeness violations
                if isinstance(loopsafe, str) and loopsafe.startswith('-'):
                    # Check if this violation is already recorded
                    if not any(v.get('arc') == arc for v in self.loop_safe_violations):
                        self.loop_safe_violations.append({
                            "arc": arc,
                            "r-id": r_id
                        })
                    all_positive = False

                # Check safeness violations
                if isinstance(safeCA, str) and safeCA.startswith('-'):
                    # Check if this violation is already recorded
                    if not any(v.get('arc') == arc for v in self.safeCA_violations):
                        self.safeCA_violations.append({
                            "arc": arc,
                            "r-id": r_id
                        })
                    all_positive = False

        return all_positive


    def evaluate(self):
        """
        Evaluates the RDLT structure to check if it satisfies L-safeness criteria 
        by verifying join-safeness, loop-safeness, and safeness.

        This method processes the RDLT structure to calculate cycle vectors, 
        loop safety, and out-cycle vectors for each arc. It then checks the 
        overall safeness of the system.

        Returns:
            tuple: A tuple containing:
                - l_safe (bool): True if the system is L-safe, False otherwise.
                - matrix (list): The matrix of operations applied to the RDLT structure.
        """
        matrix = []
        
        for r in self.rdlt_structure:
            cv = self.cycle_vector_operation(r)
            ls = self.loop_safe(r, cv)
            safe_vector = self.out_cycle_vector_operation(r)
            self.join_safe()
            matrix.append([ls, safe_vector])

        join_safe = self.checkIfAllPositive()
        loop_safe = self.checkIfAllPositive()
        safe = self.checkIfAllPositive()

        if join_safe and loop_safe and safe:
            self.l_safe_vector = True
        else:
            self.l_safe_vector = False
        

        print(f"\nJOIN-Safe: {'Satisfied.' if join_safe else 'Not Satisfied.'}")
        print(f"Loop-Safe NCAs: {'Satisfied.' if loop_safe else 'Not Satisfied.'}")
        print(f"Safe CAs: {'Satisfied.' if safe else 'Not Satisfied.'}\n")

        self.matrix_operations = matrix
        return self.l_safe_vector, matrix

    def get_violations(self):
        """
        Retrieves and formats the violations found during the L-safeness checks.
        """
        # Clear existing violations list
        self.violations = []
        seen_violations = set()
        
        # Process JOIN-Safeness Violations
        if self.join_safe_violations:
            for violation in self.join_safe_violations:
                # Create a composite key for deduplication
                composite_key = f"{violation.get('arc')}|{violation.get('r-id')}"
                
                if composite_key not in seen_violations:
                    seen_violations.add(composite_key)
                    
                    violation_details = {
                        "type": "JOIN-Safeness",
                        "split_origin": violation.get("split_origin", "Unknown"),
                        "join_vertex": violation.get("join_vertex", "Unknown"),
                        "problematic_arc": violation.get("problematic_arc", violation.get("arc", "Unknown")),
                        "r-id": violation.get("r-id", "Unknown"),
                        "arc": violation.get("arc", "Unknown"),
                        "violation": violation.get("violation", "JOIN-Safeness")
                    }
                    self.violations.append(violation_details)
                    
                    # Print each violation component separately for debugging
                    print(f"\nJOIN-Safeness Violation:")
                    print(f"  Type: {violation_details['type']}")
                    print(f"  r-id: {violation_details['r-id']}")
                    print(f"  arc: {violation_details['arc']}")
                    print(f"  Split Origin: {violation_details['split_origin']}")
                    print(f"  Join Vertex: {violation_details['join_vertex']}")
                    print(f"  Problematic Arc: {violation_details['problematic_arc']}")
                    print(f"  Violation: {violation_details['violation']}")

        # Process Loop-Safeness Violations
        if self.loop_safe_violations:
            for violation in self.loop_safe_violations:
                violation_details = {
                    "type": "Loop-Safeness",
                    "arc": violation.get("arc", "Unknown"),
                    "r-id": violation.get("r-id", "Unknown")
                }
                self.violations.append(violation_details)
                
                print(f"\nLoop-Safeness Violation:")
                print(f"  Arc: {violation_details['arc']}")
                print(f"  r-id: {violation_details['r-id']}")

        # Process Safeness of Critical Arcs (CAs) Violations
        if self.safeCA_violations:
            for violation in self.safeCA_violations:
                violation_details = {
                    "type": "Safeness of Critical Arcs",
                    "arc": violation.get("arc", "Unknown"),
                    "r-id": violation.get("r-id", "Unknown")
                }
                self.violations.append(violation_details)
                
                print(f"\nSafeness Violation:")
                print(f"  Arc: {violation_details['arc']}")
                print(f"  r-id: {violation_details['r-id']}")

        # If no violations were found, print a message
        if not self.violations:
            print("\nNo violations found. The RDLT structure is L-safe.")
        else:
            print(f"\nFound {len(self.violations)} violations in total.")

        return self.violations


    def print_matrix(self):
        """
        Prints the matrix (RDLT structure) with updated values.
        This method iterates through each row of the RDLT structure and prints it.
        """
        #print whoie matrix
        # for row in self.rdlt_structure:
        #     print(row)
        #print specific arcs (arc, c-attribute, l-attribute, loop-safe, safe, join-safe)
        columns_to_print = [0, 4, 3, 9, 11, 12]
        
        for row in self.rdlt_structure:
            # Create a new list containing only the specified columns
            filtered_row = [row[col] for col in columns_to_print if col < len(row)]
            print(filtered_row)

    def get_matrix_data(self):
        return self.matrix_data
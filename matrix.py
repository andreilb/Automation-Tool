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
    def __init__(self, R, Cycle_List):
        """
        Initialize the Matrix class with the RDLT data and a list of cycles.

        Parameters:
            - R (list of dict): The RDLT structure containing arc-related data.
            - Cycle_List (list of dict): The list of cycles with related arcs and critical arcs.
        """
        self._R_ = R
        self.Cycle_List = Cycle_List
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

        # self.source_vertices, self.target_vertices = utils.get_source_and_target_vertices(self._R_)

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

    def join_safe(self, r):
        """
        Checks if the RDLT structure is JOIN-safe according to specified criteria.
        
        This method verifies JOIN-safeness by:
        1. Identifying all splits and joins in the graph
        2. Finding paths from splits to joins
        3. Checking various conditions based on join types (AND-JOIN, OR-JOIN, MIX-JOIN)
        4. Using matrix values for loop-safe and critical arc safeness checks
        5. Updating the join_vector with values (-1 for unsafe)
        
        Returns:
            bool: True if the structure is JOIN-safe, False otherwise
        """
        join_safe = True
        
        # Create arc_attributes and arc_safety dictionaries from _R_
        arc_attributes = {}
        arc_safety = {}
        for r in self._R_:
            arc = r['arc']
            arc_attributes[arc] = (r['c-attribute'], r['l-attribute'], r.get('r-id'))
            
            # Find the corresponding row in rdlt_structure to get safety values
            for row in self.rdlt_structure:
                if row[0] == arc:
                    arc_safety[arc] = {
                        'loop_safe': row[9] not in [-1, '-1'] and not (isinstance(row[9], str) and row[9].startswith('-')),
                        'safe_ca': row[11] not in [-1, '-1'] and not (isinstance(row[11], str) and row[11].startswith('-')),
                        'row_index': self.rdlt_structure.index(row)  # Store row index for later update
                    }
                    break
        
        # Cache vertices with multiple incoming/outgoing arcs
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
        
        # Find source and sink vertices
        sources = set(v for v in self._R_vertices if not vertex_incoming.get(v, []))
        sinks = set(v for v in self._R_vertices if not vertex_outgoing.get(v, []))

        # Create tracking set for arcs involved in split/join paths
        involved_arcs = set()
        # Dictionary to store unique violations by composite key (arc|r-id)
        unique_violations = {}
        
        # Identify joins and splits, properly excluding source/sink vertices
        joins = []
        for v, incoming in vertex_incoming.items():
            if len(incoming) > 1 and v not in sources:
                # Additional check: vertex should not be the first vertex in any arc
                if not any(r['arc'].split(', ')[0] == v for r in self._R_):
                    joins.append(v)
        
        splits = [v for v, outgoing in vertex_outgoing.items() 
                if len(outgoing) > 1 and v not in sinks]
        
        logged_violations = set()
        
        def mark_arc_unsafe(arc, violation_type, details=None):
            """Mark an arc as unsafe and record the violation"""
            if arc in arc_safety:
                # Create violation record with all required keys
                r_id = arc_attributes[arc][2] if arc in arc_attributes else None
                # Create a composite key for deduplication based on arc and r-id
                composite_key = f"{arc}|{r_id}|{violation_type}"  # Added violation_type to make key more specific
                
                # Only add if this unique arc+r-id+violation hasn't been seen before
                if composite_key not in unique_violations:
                    violation = {
                        "violation": violation_type,
                        "problematic_arc": arc,
                        "r-id": r_id,
                        "arc": arc,
                        "split_origin": details.get("split_origin", "N/A"),
                        "join_vertex": details.get("join_vertex", "N/A")
                    }
                
                    # Add any additional details
                    if details:
                        for key, value in details.items():
                            if key not in violation:  # Only add keys that don't already exist
                                violation[key] = value
                    unique_violations[composite_key] = violation
                    involved_arcs.add(arc)
                    # Only append to join_safe_violations if it's not already there
                    if not any(v.get('arc') == arc and v.get('r-id') == r_id and v.get('violation') == violation_type 
                        for v in self.join_safe_violations):
                        self.join_safe_violations.append(violation)
                    return True
            return False
        
        def find_all_paths(start, end, max_depth=100):
            """Find all paths from start to end vertex using DFS with cycle detection"""
            all_paths = []
            def dfs(current, path, depth):
                if depth > max_depth:
                    return
                if current == end:
                    all_paths.append(path[:])
                    return
                if current in vertex_outgoing:
                    for next_vertex in vertex_outgoing[current]:
                        if next_vertex not in path:  # Avoid cycles
                            dfs(next_vertex, path + [next_vertex], depth + 1)
            dfs(start, [start], 0)
            return all_paths

        # FIXED: Improved method to identify valid incoming arcs for each join
        def validate_join_inputs(join_vertex):
            """Check all incoming arcs to ensure they're part of valid paths from splits"""
            # Find all splits that can reach this join
            reachable_splits = set()
            # Dictionary to track all valid paths from each vertex to the join
            valid_paths_to_join = {v: False for v in self._R_vertices}
            
            # Mark the join vertex itself as valid
            valid_paths_to_join[join_vertex] = True
            
            # For each split, find all paths to the join and mark all vertices in these paths as valid
            for split in splits:
                paths = find_all_paths(split, join_vertex)
                if paths:
                    reachable_splits.add(split)
                    # Mark all vertices in paths as having valid paths to join
                    for path in paths:
                        for vertex in path:
                            valid_paths_to_join[vertex] = True
            
            # If no paths from any split to this join, it's not a real join in our context
            if not reachable_splits:
                return True
                
            # Check all actual incoming arcs to the join for validity
            has_violations = False
            for source in vertex_incoming.get(join_vertex, []):
                arc = f"{source}, {join_vertex}"
                
                # Skip the check if source is a valid split itself (direct split to join)
                if source in reachable_splits:
                    continue
                    
                # If the source vertex is not marked as having a valid path to the join,
                # this is an interruption
                if not valid_paths_to_join[source]:
                    violation = f"Process interruption: Invalid incoming arc {arc} to join {join_vertex}"
                    if mark_arc_unsafe(arc, violation, {
                        'join_vertex': join_vertex,
                        'external_source': source,
                        'valid_sources': [v for v, valid in valid_paths_to_join.items() if valid]
                    }):
                        has_violations = True
            
            return not has_violations
        
        # Check all joins for process interruptions (using our fixed validation function)
        for join in joins:
            if not validate_join_inputs(join):
                join_safe = False
        
        # Remaining checks (split origin, no branching, etc.)
        def check_one_split_origin(paths, split, join):
            """Check that paths only intersect at endpoints"""
            for i, path1 in enumerate(paths):
                path1_interior = set(path1[1:-1])
                for j, path2 in enumerate(paths[i+1:], i+1):
                    path2_interior = set(path2[1:-1])
                    intersection = path1_interior & path2_interior
                    
                    if intersection:
                        for vertex in intersection:
                            violation = f"Multiple split origins: paths intersect at {vertex}"
                            # Find all arcs involving the intersection vertex
                            related_arcs = []
                            if vertex in vertex_incoming:
                                related_arcs.extend(f"{pred}, {vertex}" for pred in vertex_incoming[vertex])
                            if vertex in vertex_outgoing:
                                related_arcs.extend(f"{vertex}, {succ}" for succ in vertex_outgoing[vertex])
                                
                            for arc in related_arcs:
                                violation_key = f"intersection:{arc}"
                                
                                if violation_key not in logged_violations:
                                    logged_violations.add(violation_key)
                                    mark_arc_unsafe(arc, violation, {
                                        'join_vertex': join,
                                        'split_origin': split,
                                        'path1': path1,
                                        'path2': path2,
                                        'intersection_vertex': vertex
                                    })
                                    return False
            return True
            
        def check_unrelated_processes(split, join, path):
            """Check for vertices in path leading to external vertices"""
            for vertex in path[1:-1]:  # Exclude split and join vertices
                if vertex in vertex_outgoing:
                    for next_vertex in vertex_outgoing[vertex]:
                        if next_vertex != join and next_vertex not in path:
                            violation = f"Unrelated process: vertex {vertex} connects to external vertex {next_vertex}"
                            arc = f"{vertex}, {next_vertex}"
                            
                            violation_key = f"unrelated:{arc}"
                            if violation_key not in logged_violations:
                                logged_violations.add(violation_key)
                                mark_arc_unsafe(arc, violation, {
                                    'join_vertex': join,
                                    'split_origin': split
                                })
                                return False
            return True

        def check_no_branching(split, join, path):
            """Check for unauthorized branching in path"""
            for vertex in path[1:-1]:  # Exclude split and join vertices
                if vertex in vertex_outgoing:
                    outgoing = vertex_outgoing[vertex]
                    next_vertex_in_path = None
                    for i, v in enumerate(path):
                        if v == vertex and i+1 < len(path):
                            next_vertex_in_path = path[i+1]
                            break
                    
                    for next_vertex in outgoing:
                        if next_vertex != next_vertex_in_path and next_vertex not in path:
                            violation = f"Unauthorized branching: vertex {vertex} branches to {next_vertex}"
                            arc = f"{vertex}, {next_vertex}"
                            
                            violation_key = f"branching:{arc}"
                            if violation_key not in logged_violations:
                                logged_violations.add(violation_key)
                                mark_arc_unsafe(arc, violation, {
                                    'join_vertex': join,
                                    'split_origin': split
                                })
                                return False
            return True

        def determine_join_type(incoming_arcs):
            """Determine join type based on conditions of incoming arcs"""
            conditions = [get_arc_condition(arc) for arc in incoming_arcs if arc in arc_attributes]
            has_epsilon = any(c == 'ε' or c == '0' for c in conditions)
            has_non_epsilon = any(c != 'ε' and c != '0' and c is not None for c in conditions)
            unique_conditions = set(conditions)
            
            if len(unique_conditions) == 1:
                return "OR-JOIN"
            elif not has_epsilon and has_non_epsilon:
                return "AND-JOIN"
            elif has_epsilon and has_non_epsilon:
                return "MIX-JOIN"
            return None

        def get_arc_condition(arc):
            """Get condition (c-attribute) for an arc"""
            return arc_attributes.get(arc, (None, None, None))[0]
            
        def get_arc_l_value(arc):
            """Get L-value (l-attribute) for an arc"""
            return arc_attributes.get(arc, (None, None, None))[1]

        def check_duplicate_conditions(paths, join, incoming_arcs):
            """Check duplicate conditions requirements for AND-JOIN and MIX-JOIN"""
            join_type = determine_join_type(incoming_arcs)
            if not join_type:
                return True
                
            # Only apply duplicate condition checks when there are more than 2 incoming arcs
            if len(incoming_arcs) <= 2:
                return True
                
            conditions = {arc: get_arc_condition(arc) for arc in incoming_arcs if arc in arc_attributes}
            
            if join_type == "AND-JOIN":
                # For AND-JOIN: All conditions must be different when there are more than 2 arcs
                condition_values = list(conditions.values())
                # Check for duplicates in conditions
                for i, cond in enumerate(condition_values):
                    if cond in condition_values[i+1:]:
                        duplicate_arcs = [arc for arc, c in conditions.items() if c == cond]
                        violation = f"AND-JOIN duplicate condition violation: Multiple arcs with condition {cond}"
                        
                        for arc in duplicate_arcs:
                            violation_key = f"duplicate:{arc}"
                            if violation_key not in logged_violations:
                                logged_violations.add(violation_key)
                                mark_arc_unsafe(arc, violation, {
                                    'join_vertex': join,
                                    'duplicate_condition': cond
                                })
                                return False
                            
            elif join_type == "MIX-JOIN":
                # For MIX-JOIN: Check epsilon and non-epsilon conditions
                epsilon_arcs = [arc for arc, cond in conditions.items() if cond in ['ε', '0']]
                non_epsilon_arcs = [arc for arc, cond in conditions.items() if cond not in ['ε', '0', None]]
                
                if non_epsilon_arcs:
                    reference_condition = get_arc_condition(non_epsilon_arcs[0])
                    
                    # All non-epsilon conditions must be the same
                    for arc in non_epsilon_arcs:
                        if get_arc_condition(arc) != reference_condition:
                            violation = f"MIX-JOIN condition violation: Different non-epsilon conditions"
                            mark_arc_unsafe(arc, violation, {
                                'join_vertex': join,
                                'expected_condition': reference_condition,
                                'found_condition': get_arc_condition(arc)
                            })
                            return False
                    
                    # Additional check for paths ending at the join
                    for path in paths:
                        if len(path) < 2:
                            continue
                            
                        last_arc = f"{path[-2]}, {path[-1]}"
                        if last_arc not in arc_attributes:
                            continue
                            
                        last_condition = get_arc_condition(last_arc)
                        
                        if last_condition not in ['ε', '0', reference_condition]:
                            violation = f"MIX-JOIN path violation: Invalid end condition"
                            mark_arc_unsafe(last_arc, violation, {
                                'join_vertex': join
                            })
                            return False
            
            return True

        def check_equal_l_values_and_safety(paths, join, incoming_arcs):
            """Check L-value equality for AND-JOIN and loop-safety requirements"""
            join_type = determine_join_type(incoming_arcs)
            if not join_type:
                return True
                
            # Check L-value equality for AND-JOIN
            if join_type == "AND-JOIN":
                l_values = {arc: get_arc_l_value(arc) for arc in incoming_arcs if arc in arc_attributes}
                unique_l_values = set(l_values.values())
                if len(unique_l_values) > 1:
                    violation = f"Unequal L-values at AND-JOIN"
                    for arc, l_value in l_values.items():
                        mark_arc_unsafe(arc, violation, {
                            'join_vertex': join,
                            'l_value': l_value,
                            'expected': next(iter(l_values.values()))
                        })
                    return False
            
            # Check loop-safety requirements based on join type
            for path in paths:
                for i in range(len(path) - 1):
                    arc = f"{path[i]}, {path[i+1]}"
                    if arc not in arc_safety:
                        continue
                    
                    if join_type in ["AND-JOIN", "MIX-JOIN"]:
                        # All arcs must be loop-safe
                        if not arc_safety[arc]['loop_safe']:
                            violation = f"Non-loop-safe arc in {join_type} path"
                            mark_arc_unsafe(arc, violation, {
                                'join_vertex': join
                            })
                            return False
                            
                    elif join_type == "OR-JOIN":
                        # Arcs must be either loop-safe or safe CA
                        if not (arc_safety[arc]['loop_safe'] or arc_safety[arc]['safe_ca']):
                            violation = f"Arc neither loop-safe nor safe CA in OR-JOIN path"
                            mark_arc_unsafe(arc, violation, {
                                'join_vertex': join
                            })
                            return False
            
            return True

        # Main processing loop - first validate join inputs to catch interruptions like x9→x3
        for join in joins:
            # First check for interruptions - this is the key fix!
            if not validate_join_inputs(join):
                join_safe = False
        
        # Now do the remaining split-to-join path checks
        for split in splits:
            for join in joins:
                if split == join:
                    continue
                    
                paths = find_all_paths(split, join)
                if not paths:
                    continue
                
                # Get incoming arcs to join
                incoming_arcs = []
                for pred in vertex_incoming.get(join, []):
                    incoming_arcs.append(f"{pred}, {join}")
                    
                # Check One Split Origin
                if not check_one_split_origin(paths, split, join):
                    join_safe = False
                    continue

                # Check Duplicate Conditions
                if not check_duplicate_conditions(paths, join, incoming_arcs):
                    join_safe = False
                    continue
                
                # Check L-values and safety
                if not check_equal_l_values_and_safety(paths, join, incoming_arcs):
                    join_safe = False
                    continue
                
                # Check each path for all requirements
                for path in paths:
                    # Check No Unrelated Processes
                    if not check_unrelated_processes(split, join, path):
                        join_safe = False
                        continue
                    
                    # Check No Branching
                    if not check_no_branching(split, join, path):
                        join_safe = False
                        continue

        # After processing all splits and joins, update the join_safe value in the rdlt_structure
        for i, r in enumerate(self.rdlt_structure):
            arc = r[0]
            # Check if this arc is in any violation
            is_violating = False
            
            for violation in self.join_safe_violations:
                if violation.get('arc') == arc:
                    is_violating = True
                    # Perform the element-wise multiplication to update the join-safe value
                    js = -1
                    r[12] = self.elementMult(js, r[7])
                    
                    # Perform the literal OR operation between the result and the c-attribute_y
                    r[12] = self.literalOR(r[12], r[7])
                    break
                    
            if not is_violating:
                if arc in involved_arcs:
                    js = 1
                else:
                    js = 0
                r[12] = js
                
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
                            "r-id": r_id,
                            "violating_value": loopsafe
                        })
                    all_positive = False

                # Check safeness violations
                if isinstance(safeCA, str) and safeCA.startswith('-'):
                    # Check if this violation is already recorded
                    if not any(v.get('arc') == arc for v in self.safeCA_violations):
                        self.safeCA_violations.append({
                            "arc": arc,
                            "r-id": r_id,
                            "violating_value": safeCA
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
            join_vector = self.join_safe(r)
            matrix.append([ls, safe_vector, join_vector])

        join_safe = self.checkIfAllPositive()
        loop_safe = self.checkIfAllPositive()
        safe = self.checkIfAllPositive()

        if join_safe and loop_safe and safe:
            self.l_safe_vector = True
        else:
            self.l_safe_vector = False

        self.matrix_operations = matrix
        return self.l_safe_vector, matrix

    # Fix for get_violations method
    def get_violations(self):
        """
        Retrieves and formats the violations found during the L-safeness checks.
        This method processes violations in JOIN-safeness, loop-safeness, 
        and safeness of critical arcs.

        Returns:
            list: A list of violation details, including type, source, target, 
                problematic arcs, and violating values.
        """
        # Process JOIN-Safeness Violations
        if self.join_safe_violations:
            for violation in self.join_safe_violations:
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
                print(f"JOIN-Safeness Violation:")
                print(f"  Type: {violation_details['type']}")
                print(f"  r-id: {violation_details['r-id']}")
                print(f"  arc: {violation_details['arc']}")
                print(f"  Split Origin: {violation_details['split_origin']}")
                print(f"  Join Vertex: {violation_details['join_vertex']}")
                print(f"  Problematic Arc: {violation_details['problematic_arc']}")

        # Process Loop-Safeness Violations
        if self.loop_safe_violations:
            for violation in self.loop_safe_violations:
                violation_details = {
                    "type": "Loop-Safeness",
                    "arc": violation.get("arc", "Unknown"),
                    "r-id": violation.get("r-id", "Unknown"),
                    "violating_value": violation.get("violating_value", "Unknown"),
                }
                self.violations.append(violation_details)
                
                print(f"Loop-Safeness Violation:")
                print(f"  Arc: {violation_details['arc']}")
                print(f"  r-id: {violation_details['r-id']}")
                print(f"  Violating Value: {violation_details['violating_value']}")

        # Process Safeness of Critical Arcs (CAs) Violations
        if self.safeCA_violations:
            for violation in self.safeCA_violations:
                violation_details = {
                    "type": "Safeness of Critical Arcs",
                    "arc": violation.get("arc", "Unknown"),
                    "r-id": violation.get("r-id", "Unknown"),
                    "violating_value": violation.get("violating_value", "Unknown"),
                }
                self.violations.append(violation_details)
                
                print(f"Unsafe Critical Arc:")
                print(f"  Arc: {violation_details['arc']}")
                print(f"  r-id: {violation_details['r-id']}")
                print(f"  Violating Value: {violation_details['violating_value']}")

        # If no violations were found, print a message
        if not self.violations:
            print("No violations found. The RDLT structure is L-safe.")
        else:
            print(f"Found {len(self.violations)} violations in total.")

        return self.violations


    def print_matrix(self):
        """
        Prints the matrix (RDLT structure) with updated values.
        This method iterates through each row of the RDLT structure and prints it.
        """
        for row in self.rdlt_structure:
            print(row)

    def get_matrix_data(self):
        return self.matrix_data
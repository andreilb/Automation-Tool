import copy
from collections import defaultdict
import utils

class ModifiedActivityExtraction:
    def __init__(self, R, contraction_path=None, R2=None, out_list=None, cycle_list=None):
        """
        Initialize the advanced activity extraction with enhanced cycle and path handling.
        
        Args:
            R (list): Reduced Direct Labeled Transition system
            contraction_path (list): Sequence of contraction paths
            R2 (list): Secondary transition system
            out_list (list): List of out-bridges
            cycle_list (list): List of cycles with their L-attributes
        """
        self.R = R
        self.R2 = R2 or []
        self.contraction_path = contraction_path or []
        self.out_list = out_list or []
        self.cycle_list = cycle_list or []
        # Initialize activity_profiles as an empty dictionary
        self.activity_profiles = {}
        # Enhanced tracking for time vectors
        self.time_vectors = self._initialize_time_vectors()
        
        # Core tracking structures
        self.source, self.sink = utils.get_source_and_target_vertices(self.R)

    def _initialize_time_vectors(self):
        """
        Initialize time vectors for each arc based on L-attributes.
        
        Returns:
            dict: Time vectors for each arc with zero initialization
        """
        time_vectors = {}
        for arc_data in self.R:
            arc = arc_data['arc']

            l_attribute = int(arc_data.get('l-attribute', ))
            
            # Ensure l_attribute is a positive integer
            l_attribute = max(1, l_attribute)
            
            time_vectors[arc] = [0] * l_attribute
        return time_vectors
    
    
    def extract_activity_profile(self):
        """
        Extract activity profile based on the comprehensive mathematical model.
        
        Returns:
            dict: Detailed activity profile with rigorous traversal tracking
        """
        activity_profile = {
            'S': {},              # Timestep-grouped arcs
            'time_vectors': self.time_vectors,  # Track arc time vectors
            'deadlock': False,    # Deadlock flag
            'successful': False,  # Successful traversal flag
            'sink_timestep': None  # Timestep when sink is reached
        }
        
        R_copy = copy.deepcopy(self.R)
        current_vertex = self.source
        timestep = 1
        visited_stack = [self.source]
        
        # Tracking unconstrained arc selection
        def is_unconstrained_arc(current_arc, competing_arcs):
            """
            Formal unconstrained arc evaluation based on mathematical definition.
            
            Args:
                current_arc (str): Current arc being considered
                competing_arcs (list): Other arcs targeting the same vertex
            
            Returns:
                bool: Whether the arc is unconstrained
            """
            current_end = current_arc.split(', ')[1]
            current_arc_data = next(
                (a for a in R_copy if a['arc'] == current_arc), 
                None
            )
            
            if not current_arc_data:
                return False
            
            current_c_attr = current_arc_data.get('c-attribute', '0')
            
            for competing_arc in competing_arcs:
                # Condition 1: C-attribute compatibility
                competing_arc_data = next(
                    (a for a in R_copy if a['arc'] == competing_arc), 
                    None
                )
                
                if not competing_arc_data:
                    continue
                
                competing_c_attr = competing_arc_data.get('c-attribute', '0')
                
                # Condition 1: C-attribute matching
                if competing_c_attr not in {'0', current_c_attr}:
                    continue
                
                # Condition 2: Traversal Count Verification
                current_time_vector = self.time_vectors.get(current_arc, [])
                competing_time_vector = self.time_vectors.get(competing_arc, [])
                
                current_traversals = len([t for t in current_time_vector if t >= 1])
                competing_traversals = len([t for t in competing_time_vector if t >= 1])
                
                max_competing_l_attr = len(competing_time_vector)
                
                # Condition 2: Traversal count consistency
                if (current_traversals <= competing_traversals <= max_competing_l_attr):
                    return True
                
                # Condition 3: Epsilon handling
                if (
                    current_c_attr == '0' and 
                    competing_c_attr in self.R_sigma and 
                    any(competing_time_vector)
                ):
                    return True
            
            return False
        
        max_iterations = 500
        iteration = 0
        
        while current_vertex != self.sink and iteration < max_iterations:
            iteration += 1
            
            # Identify arcs starting from current vertex
            current_arcs = [
                arc_data['arc'] for arc_data in R_copy 
                if arc_data['arc'].startswith(f"{current_vertex}, ")
            ]
            
            # Identify competing arcs for each potential arc
            potential_arcs = []
            for current_arc in current_arcs:
                end_vertex = current_arc.split(', ')[1]
                competing_arcs = [
                    arc for arc in current_arcs 
                    if arc.split(', ')[1] == end_vertex
                ]
                
                # Check unconstrained arc conditions
                if is_unconstrained_arc(current_arc, competing_arcs):
                    potential_arcs.append(current_arc)
            
            # Deadlock handling
            if not potential_arcs:
                if visited_stack:
                    current_vertex = visited_stack.pop()
                    continue
                
                activity_profile['deadlock'] = True
                break
            
            # Select first potential arc
            current_arc = potential_arcs[0]
            _, end_vertex = current_arc.split(', ')
            
            # Update time vector
            time_vector = self.time_vectors.get(current_arc, [])
            max_time = max(
                [max(self.time_vectors.get(other_arc, [0])) for other_arc in 
                 [arc for arc in R_copy if arc['arc'].endswith(f", {end_vertex}")]
                ] or [0]
            )
            
            # Find first zero in time vector
            zero_index = time_vector.index(0) if 0 in time_vector else len(time_vector)
            time_vector[zero_index] = max_time + 1
            
            # Update activity profile
            if timestep not in activity_profile['S']:
                activity_profile['S'][timestep] = []
            activity_profile['S'][timestep].append(current_arc)
            
            # Update current state
            current_vertex = end_vertex
            visited_stack.append(current_vertex)
            
            # Increment timestep
            timestep += 1
        
        # Finalize activity profile
        if current_vertex == self.sink:
            activity_profile['successful'] = True
            activity_profile['sink_timestep'] = timestep - 1
        
        return activity_profile
    
    def _is_arc_traversable(self, arc, R, activity_profile, traversed_arcs, current_timestep):
        """
        Determine if an arc is traversable based on join type and current activity profile.
        
        Args:
            arc (str): The arc to check for traversability
            R (list): Reduced Direct Labeled Transition system
            activity_profile (dict): Current activity profile
            traversed_arcs (set): Set of already traversed arcs
            current_timestep (int): Current timestep
        
        Returns:
            bool: Whether the arc is traversable
        """
        # Prevent re-traversing an arc
        if arc in traversed_arcs:
            return False
        
        start, end = arc.split(', ')
        
        # Find all incoming arcs to the end vertex
        incoming_arcs = [a['arc'] for a in R if a['arc'].endswith(f", {end}")]
        
        # If no other incoming arcs, always traversable
        if len(incoming_arcs) <= 1:
            return True
        
        # Determine join type
        join_type = self._determine_join_type(end, R)
        
        # Get c-attributes for all incoming arcs
        c_attributes = {}
        for inc_arc in incoming_arcs:
            inc_arc_data = next((a for a in R if a['arc'] == inc_arc), None)
            c_attributes[inc_arc] = inc_arc_data.get('c-attribute', '0')
        
        # Current arc's c-attribute
        current_arc_data = next((a for a in R if a['arc'] == arc), None)
        current_c_attr = current_arc_data.get('c-attribute', '0')
        
        # OR-JOIN: Always traversable if first incoming arc or all attributes identical
        if join_type == "OR-JOIN":
            return True
        
        # AND-JOIN: All other non-epsilon arcs must be checked
        elif join_type == "AND-JOIN":
            # Ensure all non-epsilon arcs have been checked
            return all(
                inc_arc in activity_profile['checks'] 
                for inc_arc in incoming_arcs 
                if inc_arc != arc and c_attributes[inc_arc] != '0'
            )
        
        # MIX-JOIN: More complex traversability rules
        elif join_type == "MIX-JOIN":
            # If current arc is non-epsilon
            if current_c_attr != '0':
                # No need to check epsilon arcs
                return True
            
            # If current arc is epsilon, check non-epsilon arcs first
            return all(
                inc_arc in activity_profile['checks'] 
                for inc_arc in incoming_arcs 
                if inc_arc != arc and c_attributes[inc_arc] != '0'
            )
        
        return False
    
    def _determine_join_type(self, vertex, R):
        """
        Determine the join type for a vertex based on c-attributes.
        
        Args:
            vertex (str): The vertex to analyze
            R (list): Reduced Direct Labeled Transition system
        
        Returns:
            str: Join type - 'OR-JOIN', 'AND-JOIN', or 'MIX-JOIN'
        """
        # Get incoming arcs to the vertex
        incoming_arcs = [a for a in R if a['arc'].endswith(f", {vertex}")]
        
        # Extract c-attributes, treating '0' as epsilon
        c_attributes = [arc.get('c-attribute', '0') for arc in incoming_arcs]
        
        # Remove epsilon (zero) attributes to check core attributes
        non_epsilon_attrs = [attr for attr in c_attributes if attr != '0']
        
        # Case 1: All attributes are identical (including all epsilon)
        if len(set(c_attributes)) <= 1:
            return "OR-JOIN"
        
        # Case 2: All non-epsilon attributes are different
        if len(set(non_epsilon_attrs)) > 1:
            return "AND-JOIN"
        
        # Case 3: Mixed epsilon and non-epsilon
        return "MIX-JOIN"
    
    def _extract_out_bridge_arc(self, out_bridge):
        """
        Safely extract the arc from an out-bridge representation.
        
        Args:
            out_bridge (str or dict): Out-bridge representation
        
        Returns:
            str: Arc representation
        """
        # If it's already a string, return it
        if isinstance(out_bridge, str):
            return out_bridge
        
        # If it's a dictionary, try multiple ways to extract the arc
        if isinstance(out_bridge, dict):
            # Try getting 'arc' key
            if 'arc' in out_bridge:
                return out_bridge['arc']
            
            # If no 'arc' key, convert dictionary to string representation
            return str(out_bridge)
        
        # If it's neither string nor dict, convert to string
        return str(out_bridge)
    
    def print_activity_profile(self, activity_profile=None):
        """
        Print the activity profile in the specified Markdown format.
        
        Parameters:
            activity_profile (dict, optional): The activity profile to print. 
            If None, uses the most recently generated profile.
        """
        # If no activity profile provided, use the most recent one
        if activity_profile is None:
            # Get the most recent activity profile (last added to the dictionary)
            if not self.activity_profiles:
                print("No activity profiles available.")
                return
            activity_profile = list(self.activity_profiles.values())[-1]
        
        # Check if 'S' key exists in the activity profile
        if 'S' not in activity_profile or not activity_profile['S']:
            print("No timestep sets found in the activity profile.")
            return

        # Print individual timestep sets with Markdown bold formatting
        for timestep, arcs in sorted(activity_profile['S'].items()):
            print(f"S({timestep}) = {set(arcs)}")
        
        # Print summary set 
        summary_set = {f"S({n})" for n in sorted(activity_profile['S'].keys())}
        print(f"S = {summary_set}")
        
        # Print sink reaching information
        if activity_profile.get('successful', False):
            print(f"The sink was reached at timestep {activity_profile.get('sink_timestep', 'N/A')}.")
        else:
            print("The activity profile did not successfully reach the sink.")
    
    def get_activity_profiles(self):
        """
        Returns the activity profiles for each violation.
        
        Returns:
            dict: A dictionary with violations as keys and activity profiles as values.
        """
        return self.activity_profiles
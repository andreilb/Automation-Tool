import utils
import copy
from collections import defaultdict

class ModifiedActivityExtraction:
    def __init__(self, R, contraction_paths=None, violations=None, 
                 failed_contractions=None, Cycle_List=None, R2=None, 
                 In_List=None, Out_List=None):
        """
        Initialize the activity extraction with advanced cycle handling.
        
        Args:
            R (list): Reduced Direct Labeled Transition system
            contraction_paths (dict): Contraction paths per violating arc
            R2 (list): Secondary transition system
            Out_List (list): List of out-bridges
            Cycle_List (list): List of cycles with their L-attributes
        """
        self.R = R
        self.R2 = R2 or []
        
        # Cycle handling
        self.Cycle_List = Cycle_List or []
        self.violating_arcs = self.normalize_violations(violations or [])
        # Tracking structures
        self.timestep_var = 0
        self.check_var = defaultdict(list)
        self.traverse_var = defaultdict(list)
        self.activity_sequences = {}
        self.exhausted_cycles = set()
        self.backtrack_stack = []

        self.source, self.sink = utils.get_source_and_target_vertices(R)

    def normalize_violations(self, violations):
        """Normalize violation inputs to a consistent format."""
        normalized_violations = []
        for violation in violations or []:
            if isinstance(violation, dict):
                if 'arc' in violation:
                    normalized_violations.append(violation['arc'])
                elif 'arcs' in violation:
                    arcs = violation['arcs']
                    if isinstance(arcs, list):
                        normalized_violations.extend(arcs)
                    else:
                        normalized_violations.append(arcs)
            elif isinstance(violation, list):
                normalized_violations.extend(violation)
            elif isinstance(violation, str):
                normalized_violations.append(violation)
        return normalized_violations

    def extract_activity_profile(self, contracted_path):
        """
        Extracts an activity profile from a contraction path.
        
        Parameters:
            - contracted_path (list): List of contracted arcs.
            
        Returns:
            dict: Activity profile with timesteps, checks, and traversals.
        """
        # Initialize activity profile
        activity_profile = {
            'timesteps': {},
            'checks': {},
            'traversals': {},
            'deadlocks': []
        }
        
        # Copy R for working with
        R_copy = copy.deepcopy(self.R)
        
        # Get source and sink vertices
        source, sink = utils.get_source_and_target_vertices(R_copy)
        
        # Initialize timestep
        timestep = 1
        
        # Initialize current vertex (start at source)
        current_vertex = source
        
        # Track visited vertices
        visited_vertices = {source}
        
        # Track traversed arcs
        traversed_arcs = set()
        
        # Create a queue of arcs to check
        arc_queue = []
        
        # Add outgoing arcs from source to the queue
        for arc_data in R_copy:
            start, end = arc_data['arc'].split(', ')
            if start == source:
                arc_queue.append(arc_data['arc'])
        
        # Initialize backtracking stack
        backtrack_stack = []
        
        # Process until we reach the sink or no more arcs can be processed
        while current_vertex != sink and arc_queue:
            # Get next arc to check
            current_arc = arc_queue.pop(0)
            start, end = current_arc.split(', ')
            
            # Skip if not connected to current vertex
            if start != current_vertex:
                arc_queue.append(current_arc)
                continue
            
            # Record check of this arc
            if current_arc not in activity_profile['checks']:
                activity_profile['checks'][current_arc] = []
            activity_profile['checks'][current_arc].append(timestep)
            
            # Initialize timestep for this arc if not already done
            if current_arc not in activity_profile['timesteps']:
                activity_profile['timesteps'][current_arc] = []
            activity_profile['timesteps'][current_arc].append(timestep)
            
            # Determine if arc is unconstrained
            is_unconstrained = self.is_arc_unconstrained(current_arc, R_copy, activity_profile)
            
            if is_unconstrained:
                # Traverse the arc
                if current_arc not in activity_profile['traversals']:
                    activity_profile['traversals'][current_arc] = []
                activity_profile['traversals'][current_arc].append(timestep)
                
                # Mark arc as traversed
                traversed_arcs.add(current_arc)
                
                # Update current vertex
                current_vertex = end
                visited_vertices.add(current_vertex)
                
                # Push current vertex to backtrack stack
                backtrack_stack.append(start)
                
                # Add outgoing arcs from new vertex to the queue
                new_arcs = []
                for arc_data in R_copy:
                    arc_start, arc_end = arc_data['arc'].split(', ')
                    if arc_start == current_vertex and arc_data['arc'] not in traversed_arcs:
                        new_arcs.append(arc_data['arc'])
                
                # Add new arcs to the front of the queue
                arc_queue = new_arcs + arc_queue
            else:
                # Check if there are alternative arcs from current vertex
                alternative_found = False
                for i, arc in enumerate(arc_queue):
                    arc_start, arc_end = arc.split(', ')
                    if arc_start == current_vertex:
                        # Move this arc to the front of the queue
                        arc_queue.pop(i)
                        arc_queue.insert(0, arc)
                        alternative_found = True
                        break
                
                # If no alternative found, backtrack
                if not alternative_found:
                    if backtrack_stack:
                        # Backtrack to the previous vertex
                        prev_vertex = backtrack_stack.pop()
                        current_vertex = prev_vertex
                        
                        # Add outgoing arcs from backtracked vertex to the queue
                        new_arcs = []
                        for arc_data in R_copy:
                            arc_start, arc_end = arc_data['arc'].split(', ')
                            if arc_start == current_vertex and arc_data['arc'] not in traversed_arcs:
                                new_arcs.append(arc_data['arc'])
                        
                        # Add new arcs to the front of the queue
                        arc_queue = new_arcs + arc_queue
                        
                        # Record a deadlock
                        activity_profile['deadlocks'].append(timestep)
                    else:
                        # No backtracking possible, we're stuck
                        activity_profile['deadlocks'].append(timestep)
                        break
            
            # Increment timestep
            timestep += 1
        
        # If we reached the sink, the activity profile is successful
        activity_profile['successful'] = (current_vertex == sink)
        
        return activity_profile

    def is_arc_unconstrained(self, arc, R, activity_profile):
        """
        Determines if an arc is unconstrained according to the provided conditions.
        
        Parameters:
            - arc (str): The arc to check.
            - R (list): The RDLT structure.
            - activity_profile (dict): Current activity profile.
            
        Returns:
            bool: True if the arc is unconstrained, False otherwise.
        """
        start, end = arc.split(', ')
        
        # Get all incoming arcs to the end vertex
        incoming_arcs = [a['arc'] for a in R if a['arc'].endswith(f", {end}")]
        
        # Condition 1: If there is only one incoming arc, it is unconstrained
        if len(incoming_arcs) == 1 and incoming_arcs[0] == arc:
            return True
        
        # Determine the join type for this vertex
        join_type = self.determine_join_type(end, R)
        
        # Get the c-attribute of the current arc
        current_arc_data = next((a for a in R if a['arc'] == arc), None)
        if not current_arc_data:
            return False
        
        current_c_attribute = current_arc_data.get('c-attribute', '0')
        
        # Condition 2: For OR-JOINs, choose any arc
        if join_type == "OR-JOIN":
            return True
        
        # Condition 3: For AND-JOINs, all incoming arcs must be traversed at the same timestep
        elif join_type == "AND-JOIN":
            # Check if all other incoming arcs have been checked
            all_checked = True
            for incoming_arc in incoming_arcs:
                if incoming_arc != arc and (
                    incoming_arc not in activity_profile['checks'] or 
                    not activity_profile['checks'][incoming_arc]
                ):
                    all_checked = False
                    break
            
            # If all have been checked, allow traversal
            return all_checked
        
        # Condition 4: For MIX-JOINs
        elif join_type == "MIX-JOIN":
            # If current arc has non-epsilon c-attribute
            if current_c_attribute != '0':
                # Can traverse without checking epsilon arcs
                return True
            else:  # Current arc has epsilon c-attribute
                # Must check non-epsilon arcs first
                for incoming_arc in incoming_arcs:
                    if incoming_arc != arc:
                        incoming_arc_data = next((a for a in R if a['arc'] == incoming_arc), None)
                        if incoming_arc_data and incoming_arc_data.get('c-attribute', '0') != '0':
                            # If non-epsilon arc hasn't been checked, can't traverse
                            if (
                                incoming_arc not in activity_profile['checks'] or 
                                not activity_profile['checks'][incoming_arc]
                            ):
                                return False
                
                # All non-epsilon arcs have been checked
                return True
        
        # Default case
        return False

    def determine_join_type(self, vertex, R):
        """
        Determines the join type for a vertex based on its incoming arcs.
        
        Parameters:
            - vertex (str): The vertex to check.
            - R (list): The RDLT structure.
            
        Returns:
            str: "OR-JOIN", "AND-JOIN", or "MIX-JOIN".
        """
        # Get all incoming arcs to the vertex
        incoming_arcs = [a for a in R if a['arc'].endswith(f", {vertex}")]
        
        if len(incoming_arcs) <= 1:
            # No join if only one incoming arc
            return "OR-JOIN"
        
        # Check c-attributes of incoming arcs
        c_attributes = [arc.get('c-attribute', '0') for arc in incoming_arcs]
        
        # Check if all are identical
        if all(c == c_attributes[0] for c in c_attributes):
            return "OR-JOIN"
        
        # Check if all are non-epsilon
        if all(c != '0' for c in c_attributes):
            return "AND-JOIN"
        
        # Otherwise, it's a MIX-JOIN (mix of epsilon and non-epsilon)
        return "MIX-JOIN"
    
    def get_activity_profiles(self):
        """
        Returns the activity profiles for each violation.
        
        Returns:
            dict: A dictionary with violations as keys and activity profiles as values.
        """
        return self.activity_profiles
import copy
from collections import defaultdict, Counter
import utils

class ModifiedActivityExtraction:
    def __init__(self, R, violations=None, contraction_path=None, cycle_list=None):
        self.R = R
        self.contraction_path = contraction_path or []
        self.violations = violations or []
        self.cycle_list = cycle_list or []

        
        self.source, self.sink = utils.get_source_and_target_vertices(self.R)

        self.checked_arcs = set()
        self.traversed_arcs = set()
        self.arc_traversal_count = defaultdict(int)
        self.max_traversal_depth = len(self.R) * 3

        self.join_vertices = self._identify_join_vertices()
        self.join_classifications = self._classify_joins()

        self.activity_profiles = {}

    def _identify_join_vertices(self):
        """Identify vertices with multiple incoming arcs"""
        incoming_count = defaultdict(int)
        for arc in self.R:
            try:
                _, target = self._safe_get_arc(arc).split(', ')
                incoming_count[target] += 1
            except Exception:
                continue
        
        return {v for v, count in incoming_count.items() if count > 1}

    def _classify_joins(self):
        """Classify join vertices based on their incoming arcs' c-attributes"""
        join_classifications = {}
        
        for vertex in self.join_vertices:
            incoming_arcs = [
                arc for arc in self.R if self._safe_get_arc(arc).endswith(f", {vertex}")
            ]
            
            c_attrs = [self._get_c_attribute(arc) for arc in incoming_arcs]
            non_epsilon = [c for c in c_attrs if c != '0']

            if len(set(c_attrs)) <= 1:
                join_type = 'OR-JOIN'
            elif len(non_epsilon) == len(c_attrs):
                join_type = 'AND-JOIN'
            else:
                join_type = 'MIX-JOIN'

            join_classifications[vertex] = {
                'type': join_type, 
                'incoming_arcs': incoming_arcs, 
                'c_attributes': c_attrs
            }
        
        return join_classifications

    def _check_join_traversability(self, arc, current_vertex, traversed_counts=None):
        """
        Check if a join vertex can be traversed, enforcing AND-JOIN semantics.
        Returns tuple: (is_traversable, required_arcs)
        
        Args:
            arc: The arc being considered for traversal
            current_vertex: The target vertex (join vertex being evaluated)
            traversed_counts: Dictionary tracking how many times arcs have been traversed
        """
        arc_str = self._safe_get_arc(arc)
        current_c_attr = self._get_c_attribute(arc)

        # Non-join vertices are always traversable
        if current_vertex not in self.join_vertices:
            return True, []

        join_info = self.join_classifications[current_vertex]
        join_type = join_info['type']
        incoming_arcs = join_info['incoming_arcs']
        c_attributes = join_info['c_attributes']

        # OR-JOINs can always be traversed (at least one incoming path)
        if join_type == 'OR-JOIN':
            return True, []

        # AND-JOIN requires all non-epsilon incoming arcs to be traversable
        if join_type == 'AND-JOIN':
            if current_c_attr != '0':
                non_epsilon_arcs = [a for a,c in zip(incoming_arcs, c_attributes) if c != '0']
                
                # Check if all source vertices of non-epsilon arcs have been reached
                for a in non_epsilon_arcs:
                    source, _ = self._safe_get_arc(a).split(', ')
                    if not self._is_vertex_reachable(source):
                        return False, []
                
                # Check if all non-epsilon arcs are traversable (within l-attribute limits)
                traversable = all(
                    self._is_arc_traversable(a, traversed_counts)
                    for a in non_epsilon_arcs
                )
                return traversable, non_epsilon_arcs
            return False, []

        # MIX-JOIN handling (combination of AND/OR semantics)
        if join_type == 'MIX-JOIN':
            if current_c_attr != '0':
                return True, []
                
            non_epsilon_arcs = [a for a,c in zip(incoming_arcs, c_attributes) if c != '0']
            
            unique_non_epsilon = {c for c in c_attributes if c != '0'}
            if len(unique_non_epsilon) <= 1:
                return True, []
                
            for a in non_epsilon_arcs:
                source, _ = self._safe_get_arc(a).split(', ')
                if not self._is_vertex_reachable(source):
                    return False, []
                    
            return all(
                self._is_arc_traversable(a, traversed_counts)
                for a in non_epsilon_arcs
            ), non_epsilon_arcs

        return False, []

    def _is_vertex_reachable(self, vertex, depth=0):
        if depth > len(self.R) * 2:
            return False

        if vertex == self.source:
            return True
        
        for path in self.contraction_path.values():
            if vertex in [v.split(', ')[0] for v in path.get('contracted_path', [])]:
                return True
        
        checked_sources = set()
        
        for arc in self.R:
            arc_str = self._safe_get_arc(arc)
            source, target = arc_str.split(', ')
            
            if target == vertex:
                if arc_str in self.traversed_arcs:
                    return True
                
                if source not in checked_sources:
                    checked_sources.add(source)
                    if self._is_vertex_reachable(source, depth + 1):
                        return True
        
        return False

    def extract_activity_profiles(self):
        self.activity_profiles = {}
        
        for contract_arc, path_info in self.contraction_path.items():
            print(f"\nProcessing contract arc: {contract_arc}")
            print(f"Contracted Path: {path_info.get('contracted_path', [])}")
            
            # Reset traversal tracking for each profile
            self.traversed_arcs = set()
            self.arc_traversal_count = defaultdict(int)
            
            # Get successful contractions for this path
            successful_contractions = path_info.get('successful_contractions', [])
            print(f"Successful Contractions: {successful_contractions}")
            
            # Find the original arc from successful contractions that matches the contract_arc
            profile_arc = next(
                (c for c in successful_contractions 
                if self._safe_get_arc(c) == contract_arc),
                None
            )
            
            if not profile_arc:
                contracted_path = path_info.get('contracted_path', [])
                if contracted_path:
                    profile_arc = contracted_path[0]
                    print(f"Using first contracted path arc: {profile_arc}")
                else:
                    profile_arc = None
                    print("No profile arc found")
            else:
                print(f"Using successful contraction arc: {profile_arc}")
            
            print("Arcs in R:", [self._safe_get_arc(arc) for arc in self.R])
            
            # Modified to force include the violation and exhaust its l-attribute
            profile = self._extract_profile_with_joins(profile_arc, force_include=contract_arc)
            print(f"Generated profile: {profile}")
            
            self.activity_profiles[contract_arc] = profile

        return self.activity_profiles

    def _extract_profile_with_joins(self, contract_arc=None, force_include=None):
        activity_profile = {
            'S': defaultdict(set),
            'deadlock': False,
            'successful': False,
            'sink_timestep': None,
            'traversed_arcs': defaultdict(int),
            'visited_states': set(),
            'required_arcs': set(),
            'violation_cause': None
        }

        current_vertex = self.source
        timestep = 1
        iteration = 0
        # Track visited arcs to manage complex dependencies
        visited_arcs = set()

        def is_vertex_fully_explored(vertex, current_profile):
            """Check if a vertex has exhausted all its outgoing arcs within l-attribute limits"""
            return len([
                arc for arc in self.R 
                if self._safe_get_arc(arc).startswith(f"{vertex}, ") and
                current_profile['traversed_arcs'].get(self._safe_get_arc(arc), 0) < self._get_l_attribute(arc)
            ]) == 0

        while current_vertex != self.sink and iteration < self.max_traversal_depth:
            iteration += 1
            
            # Identify possible outgoing arcs
            current_arcs = [
                arc for arc in self.R 
                if self._safe_get_arc(arc).startswith(f"{current_vertex}, ") and
                activity_profile['traversed_arcs'].get(self._safe_get_arc(arc), 0) < self._get_l_attribute(arc)
            ]

            # Prioritize forced inclusion
            if force_include:
                force_arcs = [arc for arc in current_arcs if self._safe_get_arc(arc) == force_include]
                if force_arcs:
                    current_arcs = force_arcs

            # Prioritize sink arcs
            sink_arcs = [arc for arc in current_arcs if self._safe_get_arc(arc).endswith(f", {self.sink}")]
            if sink_arcs:
                current_arcs = sink_arcs

            # Validate join conditions
            traversable_arcs = []
            for arc in current_arcs:
                arc_str = self._safe_get_arc(arc)
                _, next_vertex = arc_str.split(', ')

                is_traversable, required_arcs = self._check_join_traversability(
                    arc, next_vertex, activity_profile['traversed_arcs']
                )
                
                if is_traversable:
                    traversable_arcs.append((arc, required_arcs))

            if not traversable_arcs:
                # If no arcs are traversable, mark deadlock
                activity_profile['deadlock'] = True
                break

            # Select first traversable arc
            selected_arc, required_arcs = traversable_arcs[0]
            arc_str = self._safe_get_arc(selected_arc)
            _, next_vertex = arc_str.split(', ')

            # Update profile
            activity_profile['traversed_arcs'][arc_str] += 1
            activity_profile['S'][timestep].add(arc_str)
            visited_arcs.add(arc_str)

            # Process any required arcs from join conditions
            for req_arc in required_arcs:
                req_arc_str = self._safe_get_arc(req_arc)
                activity_profile['traversed_arcs'][req_arc_str] += 1
                activity_profile['S'][timestep].add(req_arc_str)
                visited_arcs.add(req_arc_str)

            current_vertex = next_vertex
            
            # Handle sink reaching
            if current_vertex == self.sink:
                activity_profile['successful'] = True
                activity_profile['sink_timestep'] = timestep
                break

            timestep += 1

            # Prevent excessive iterations
            if iteration == len(self.R) * 4:
                activity_profile['deadlock'] = True
                break

        # Clean up empty timesteps
        activity_profile['S'] = {k: v for k, v in activity_profile['S'].items() if v}

        return activity_profile

    def _is_arc_traversable(self, arc, traversed_counts=None):
        arc_str = self._safe_get_arc(arc)
        l_attribute = self._get_l_attribute(arc)
        
        if traversed_counts is not None:
            current_count = traversed_counts.get(arc_str, 0)
        else:
            current_count = self.arc_traversal_count.get(arc_str, 0)
        
        return current_count < l_attribute

    def _get_l_attribute(self, arc):
        """Get l-attribute of an arc, defaulting to 1"""
        return int(arc.get('l-attribute', 1))

    def _safe_get_arc(self, arc_data):
        if isinstance(arc_data, str):
            return arc_data
        elif isinstance(arc_data, dict):
            return arc_data.get('arc', str(arc_data))
        return str(arc_data)

    def _get_c_attribute(self, arc):
        return arc.get('c-attribute', '0')

    def print_activity_profiles(self):
        for contract_arc, activity_profile in self.activity_profiles.items():
            print(f"\n--- Activity Profile for Contract Arc: {contract_arc} ---")
            self._print_activity_profile(activity_profile)

    def _print_activity_profile(self, activity_profile):
        if 'S' not in activity_profile:
            print("Invalid activity profile: Missing 'S' key")
            return

        for timestep, arcs in sorted(activity_profile['S'].items()):
            print(f"S({timestep}) = {set(arcs)}")

        if activity_profile['S']:
            print("\nS = {" + ", ".join(f"S({ts})" for ts in sorted(activity_profile['S'].keys())) + "}")
        if activity_profile.get('deadlock', False):
            last_timestep = max(activity_profile['S'].keys()) if activity_profile['S'] else 0
            print(f"\nSink was not reached (deadlock after timestep {last_timestep})")
            # if activity_profile.get('violation_cause'):
            #     print(f"Reason: {activity_profile['violation_cause']}")
        elif activity_profile.get('sink_timestep'):
            print(f"\nSink was reached at timestep {activity_profile['sink_timestep']}")
            

        # Display l-attribute usage using existing data
        # print("\nArc Usage (traversed/limit):")
        # all_arcs = {self._safe_get_arc(arc): self._get_l_attribute(arc) for arc in self.R}
        # for arc_str, limit in sorted(all_arcs.items()):
        #     used = activity_profile['traversed_arcs'].get(arc_str, 0)
        #     print(f"{arc_str}: {used}/{limit}")
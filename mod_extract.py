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

    def _check_join_traversability(self, arc, current_vertex):
        """
        Enhanced join traversability check with backtracking support
        """
        arc_str = self._safe_get_arc(arc)
        current_c_attr = self._get_c_attribute(arc)

        # If not a join vertex, always traversable
        if current_vertex not in self.join_vertices:
            return True, []

        join_info = self.join_classifications[current_vertex]
        join_type = join_info['type']
        incoming_arcs = join_info['incoming_arcs']
        c_attributes = join_info['c_attributes']

        # OR-JOIN: freely traversable if c-attributes are same
        if join_type == 'OR-JOIN':
            return True, []

        # Find non-epsilon arcs
        non_epsilon_arcs = [
            arc for arc, c_attr in zip(incoming_arcs, c_attributes) 
            if c_attr != '0'
        ]

        # AND-JOIN: all non-epsilon arcs must be traversable simultaneously
        if join_type == 'AND-JOIN':
            if current_c_attr != '0':
                # Must traverse all non-epsilon arcs together
                return all(
                    self._is_arc_traversable(other_arc) 
                    for other_arc in non_epsilon_arcs
                ), non_epsilon_arcs
            return False, []

        # MIX-JOIN: non-epsilon can be traversed alone, epsilon requires checking non-epsilon
        if join_type == 'MIX-JOIN':
            if current_c_attr != '0':
                return True, []
            else:
                return all(
                    self._is_arc_traversable(other_arc) 
                    for other_arc in non_epsilon_arcs
                ), non_epsilon_arcs

        return False, []

    def extract_activity_profiles(self):
        """Extract activity profiles with proper join handling"""
        self.activity_profiles = {}
        arcs_to_traverse = list(self.contraction_path.keys())
        arcs_to_traverse.insert(0, None)
        
        remaining_arcs = [
            arc for arc in self.R 
            if self._safe_get_arc(arc) not in arcs_to_traverse
        ]
        arcs_to_traverse.extend(remaining_arcs)

        for contract_arc in arcs_to_traverse:
            self.traversed_arcs = set()
            self.arc_traversal_count = defaultdict(int)
            
            if contract_arc is None:
                profile_key = None
                profile_arc = None
            else:
                profile_key = self._safe_get_arc(contract_arc)
                if profile_key in self.contraction_path:
                    contracted_path = self.contraction_path[profile_key].get('contracted_path', [])
                    profile_arc = contracted_path[0] if contracted_path else None
                else:
                    profile_arc = None
            
            profile = self._extract_profile_with_joins(profile_arc)
            self.activity_profiles[profile_key] = profile

        return self.activity_profiles

    def _extract_profile_with_joins(self, contract_arc=None):
        """Core traversal algorithm with proper join handling"""
        activity_profile = {
            'S': {},
            'deadlock': False,
            'successful': False,
            'sink_timestep': None
        }

        current_vertex = self.source
        timestep = 1
        iteration = 0

        while current_vertex != self.sink and iteration < self.max_traversal_depth:
            iteration += 1

            # Find available arcs from current vertex
            current_arcs = [
                arc for arc in self.R 
                if self._safe_get_arc(arc).startswith(f"{current_vertex}, ")
            ]

            if contract_arc:
                contract_arc_str = self._safe_get_arc(contract_arc)
                current_arcs = [
                    arc for arc in current_arcs 
                    if self._safe_get_arc(arc) != contract_arc_str
                ]

            # Find traversable arcs with join constraints
            traversable_arcs = []
            required_arcs_map = {}
            
            for arc in current_arcs:
                arc_str = self._safe_get_arc(arc)
                _, next_vertex = arc_str.split(', ')

                is_traversable, required_arcs = self._check_join_traversability(arc, next_vertex)
                
                if is_traversable and self._is_arc_traversable(arc):
                    # Check if required arcs are also traversable
                    if all(self._is_arc_traversable(req_arc) for req_arc in required_arcs):
                        traversable_arcs.append(arc)
                        required_arcs_map[arc_str] = required_arcs

            # Deadlock check
            if not traversable_arcs:
                activity_profile['deadlock'] = True
                break

            # Select first traversable arc and its required arcs
            selected_arc = traversable_arcs[0]
            arc_str = self._safe_get_arc(selected_arc)
            _, next_vertex = arc_str.split(', ')
            required_arcs = required_arcs_map.get(arc_str, [])

            # Update traversal tracking
            self.arc_traversal_count[arc_str] += 1
            self.traversed_arcs.add(arc_str)
            
            # Record main arc
            activity_profile['S'][timestep] = {arc_str}
            
            # Record required arcs at same timestep if any
            for req_arc in required_arcs:
                req_arc_str = self._safe_get_arc(req_arc)
                if req_arc_str not in self.traversed_arcs:
                    self.arc_traversal_count[req_arc_str] += 1
                    self.traversed_arcs.add(req_arc_str)
                    activity_profile['S'][timestep].add(req_arc_str)

            current_vertex = next_vertex

            # Check if sink is reached
            if current_vertex == self.sink:
                activity_profile['successful'] = True
                activity_profile['sink_timestep'] = timestep
                break

            timestep += 1

        if current_vertex != self.sink:
            activity_profile['deadlock'] = True

        return activity_profile

    def _is_arc_traversable(self, arc):
        """Check arc traversability with l-attribute constraint"""
        arc_str = self._safe_get_arc(arc)
        l_attribute = int(arc.get('l-attribute', 0))
        current_traversal_count = self.arc_traversal_count[arc_str]
        return current_traversal_count < l_attribute

    def _safe_get_arc(self, arc_data):
        """Safely get arc representation"""
        if isinstance(arc_data, str):
            return arc_data
        elif isinstance(arc_data, dict):
            return arc_data.get('arc', str(arc_data))
        return str(arc_data)

    def _get_c_attribute(self, arc):
        """Get c-attribute of an arc, defaulting to '0'"""
        return arc.get('c-attribute', '0')

    def print_activity_profiles(self):
        """Print detailed activity profiles"""
        for contract_arc, activity_profile in self.activity_profiles.items():
            print(f"\n--- Activity Profile for Contract Arc: {contract_arc} ---")
            self._print_activity_profile(activity_profile)

    def _print_activity_profile(self, activity_profile):
        """Print a single activity profile"""
        if 'S' not in activity_profile:
            print("Invalid activity profile: Missing 'S' key")
            return

        print("Timestep Sets:")
        for timestep, arcs in sorted(activity_profile['S'].items()):
            print(f"S({timestep}) = {set(arcs)}")
        
        print("\nSummary:")
        summary_set = {f"S({n})" for n in sorted(activity_profile['S'].keys())}
        print(f"S = {summary_set}")
        
        if activity_profile.get('successful', False):
            print(f"Sink reached at timestep: {activity_profile.get('sink_timestep', 'N/A')}")
        else:
            print("Sink not reached.")
        
        if activity_profile.get('deadlock', False):
            print("Deadlock occurred during traversal.")
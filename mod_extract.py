import utils
import logging
from collections import deque, defaultdict

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('extraction_debug.log')
#     ]
# )

# logger = logging.getLogger('ModifiedActivityExtraction')

class ModifiedActivityExtraction:
    def __init__(self, R, contraction_path, violating_arcs, failed_contractions, cycle_list, R2=None, in_list=None, out_list=None):
        self.R = R
        self.R2 = R2 if R2 is not None else []
        self.arcs_R2 = {}
        
        # Only process R2 if it's provided
        if R2 is not None:
            self.arcs_R2 = { rbs_arc["arc"]: {"r-id": rbs_arc["r-id"]} for rbs_arc in self.R2}
        
        self.contraction_path = {}
        self.contraction_path = {}
        for item in contraction_path:
            if isinstance(item, dict) and 'arc' in item:
                arc = item['arc']
                self.contraction_path[arc] = {
                    "r-id": item.get('r-id'),
                    "arc": arc
                }
        self.violating_arcs = violating_arcs
        self.failed_contractions = failed_contractions
        self.cycle_list = cycle_list
        
        # Initialize arc tracking dictionary
        self.T = {
            arc_data["arc"]: {
                "r-id": arc_data["r-id"],
                "check": 0,
                "traverse": 0,
                "count": 0,
                "l-attribute": int(arc_data["l-attribute"]),
                "c-attribute": arc_data["c-attribute"]
            }
            for arc_data in self.R
        }

        # Process in_list and out_list for reset functionality
        self.in_list = in_list if in_list else []
        self.out_list = out_list if out_list else []
        
        # Convert to list of arc strings if they contain dictionaries
        self.processed_in_list = []
        self.processed_out_list = []
        
        for arc in self.in_list:
            if isinstance(arc, dict) and 'arc' in arc:
                self.processed_in_list.append(arc['arc'])
            else:
                self.processed_in_list.append(arc)
                
        for arc in self.out_list:
            if isinstance(arc, dict) and 'arc' in arc:
                self.processed_out_list.append(arc['arc'])
            else:
                self.processed_out_list.append(arc)

        # Build graph and identify source and sink
        self.graph = utils.build_graph(R)
        self.source, self.sink = utils.get_source_and_target_vertices(self.R)
        
        # Store all generated activity profiles
        self.activity_profiles = []
        
        # Identify reachable nodes and valid arcs
        self.reachable_nodes = self.identify_reachable_nodes()
        self.valid_arcs = self.identify_valid_arcs()
        
        # logger.info(f"Initialized ModifiedActivityExtraction")
        # logger.info(f"Source: {self.source}, Sink: {self.sink}")
        # logger.info(f"Contraction Path: {self.contraction_path}")
        # logger.info(f"Violating Arcs: {self.violating_arcs}")
        # logger.info(f"Cycles: {self.cycle_list}")
        # logger.info(f"In List: {self.processed_in_list}")
        # logger.info(f"Out List: {self.processed_out_list}")
        # logger.info(f"Reachable Nodes: {self.reachable_nodes}")
        # logger.info(f"Valid Arcs: {self.valid_arcs}")

    def identify_reachable_nodes(self):
        """Identify nodes that are reachable from the source"""
        reachable = set([self.source])
        queue = deque([self.source])
        
        while queue:
            node = queue.popleft()
            for dst in self.graph.get(node, []):
                if dst not in reachable:
                    reachable.add(dst)
                    queue.append(dst)
        
        return reachable
    
    def identify_valid_arcs(self):
        """Identify arcs that can be validly traversed considering contraction results"""
        valid_arcs = set()
        
        # First, identify arcs with nodes that are reachable
        for arc_str in self.T:
            src, dst = arc_str.split(", ")
            if src in self.reachable_nodes and dst in self.reachable_nodes:
                valid_arcs.add(arc_str)
        
        # Process failed contractions
        failed_arc_strings = []
        for item in self.failed_contractions:
            if isinstance(item, dict) and 'arc' in item:
                failed_arc_strings.append(item['arc'])
            elif isinstance(item, str):
                failed_arc_strings.append(item)
        
        # Remove failed contraction arcs
        for arc in failed_arc_strings:
            if arc in valid_arcs:
                valid_arcs.remove(arc)
                # logger.info(f"Removed failed contraction arc: {arc}")
        
        # Now, check c-attribute constraints as in the original code
        c_attribute_map = defaultdict(set)
        
        # Map which c-attributes can be set for each node
        for arc_str in valid_arcs.copy():
            src, dst = arc_str.split(", ")
            c_attr = self.T[arc_str]["c-attribute"]
            if c_attr != "0":
                c_attribute_map[dst].add(c_attr)
        
        # Check for conflicts
        arcs_to_remove = set()
        for arc_str in valid_arcs:
            src, dst = arc_str.split(", ")
            c_attr = self.T[arc_str]["c-attribute"]
            
            # Special case for the source node
            if src == self.source and c_attr != "0":
                if len(c_attribute_map[src]) > 1:
                    arcs_to_remove.add(arc_str)
                    continue
                    
            # Check if this arc conflicts with possible c-attribute settings
            if c_attr != "0" and dst in c_attribute_map:
                possible_attrs = c_attribute_map[dst]
                # If node can have multiple c-attributes and this arc requires a specific one
                if len(possible_attrs) > 1 and c_attr not in possible_attrs:
                    arcs_to_remove.add(arc_str)
        
        # Remove arcs that violate c-attribute constraints
        for arc_str in arcs_to_remove:
            valid_arcs.remove(arc_str)
        
        return valid_arcs

    def reset_traversal_state(self):
        """Reset traversal state for a new path exploration"""
        for arc in self.T:
            self.T[arc]["check"] = 0
            self.T[arc]["traverse"] = 0
            self.T[arc]["count"] = 0
        
        self.visited_nodes = set()
        self.parent_nodes = {}
        self.current_timestep = 0
        self.activity_profile = []
        self.sink_reached_at_timestep = None

    def is_arc_in_cycle(self, arc):
        """Check if an arc is part of any cycle"""
        for cycle in self.cycle_list:
            cycle_arcs = []
            
            # Handle different cycle data formats
            if isinstance(cycle, dict) and 'cycle' in cycle:
                cycle_arcs = cycle['cycle']
            else:
                cycle_arcs = cycle
                
            # Check if arc is in this cycle (handling both string and dict formats)
            for cycle_arc in cycle_arcs:
                if isinstance(cycle_arc, dict) and 'arc' in cycle_arc and cycle_arc['arc'] == arc:
                    return True
                elif cycle_arc == arc:
                    return True
        return False

    def get_cycle_for_arc(self, arc):
        """Get the cycle that contains this arc"""
        for cycle in self.cycle_list:
            cycle_arcs = []
            
            # Handle different cycle data formats
            if isinstance(cycle, dict) and 'cycle' in cycle:
                cycle_arcs = cycle['cycle']
            else:
                cycle_arcs = cycle
                
            # Check if arc is in this cycle (handling both string and dict formats)
            for cycle_arc in cycle_arcs:
                if isinstance(cycle_arc, dict) and 'arc' in cycle_arc and cycle_arc['arc'] == arc:
                    return cycle
                elif cycle_arc == arc:
                    return cycle
        return None

    def reset_arcs_after_out_list_traversal(self, traversed_arcs):
        """Reset traversal counts for arcs when an out_list arc is traversed"""
        reset_arcs = traversed_arcs.copy()
        
        # Only reset arcs that aren't in the in_list
        for arc in list(reset_arcs.keys()):
            if arc in self.processed_in_list or arc in self.processed_out_list or arc in self.arcs_R2:
                continue
            reset_arcs[arc] = 0
                
        return reset_arcs

    def extract_all_activity_profiles(self, max_depth=15):
        """Generate all possible activity profiles from source to sink with loop prevention"""
        self.activity_profiles = []
        
        # Ensure reachable nodes and valid arcs are identified
        self.reachable_nodes = self.identify_reachable_nodes()
        self.valid_arcs = self.identify_valid_arcs()
        
        # Pre-calculate paths to sink
        paths_to_sink = self.calculate_paths_to_sink()
        
        # Track visited paths to prevent loops
        visited_paths = set()
        
        # Use a depth-first search approach to explore all possible paths
        def dfs_paths(current_node, path, activity_profile, timestep, traversed_arcs, 
                    node_c_attributes=None, has_traversed_out_list=False, depth=0):
            # Initialize node_c_attributes to track which c-attribute is active for each node
            if node_c_attributes is None:
                node_c_attributes = {}
                
            # Create a state signature to detect cycles in exploration
            # Include current node, traversed arcs counts, and node c-attributes
            state_signature = (
                current_node,
                tuple(sorted((arc, count) for arc, count in traversed_arcs.items())),
                tuple(sorted((node, attr) for node, attr in node_c_attributes.items()))
            )
        

            # Check if we've already visited this state
            if state_signature in visited_paths:
                return
            
            # Add this state to visited paths
            visited_paths.add(state_signature)
                
            # Limit depth to prevent infinite exploration
            if depth > max_depth:
                # Record this as a potential deadlock path since we hit max depth
                self.activity_profiles.append({
                    'path': path.copy(),
                    'activity_profile': [step.copy() for step in activity_profile],
                    'traversed_arcs': traversed_arcs.copy(),
                    'violating_arcs_status': self.check_violating_arcs_status(traversed_arcs),
                    'timesteps': timestep,
                    'reached_sink': False,
                    'reason': 'Deadlock'
                })
                return
            elif current_node == self.source and depth == 0:
                # Find the first contraction arc from the source if it exists
                for arc_str in self.contraction_path:
                    if isinstance(arc_str, dict):
                        arc = arc_str.get('arc', '')
                    else:
                        arc = arc_str
                        
                    if arc.startswith(f"{self.source}, "):
                        src, dest = arc.split(", ")
                        
                        # Create a new activity profile with just this first step
                        new_activity_profile = [[]]  # First timestep
                        new_activity_profile[0].append((src, dest))
                        
                        # Record that we traversed this arc
                        new_traversed = {arc: 1}
                        
                        # Record this as a timestep 1 activity even if it leads to deadlock
                        self.activity_profiles.append({
                            'path': [src, dest],
                            'activity_profile': new_activity_profile,
                            'traversed_arcs': new_traversed,
                            'violating_arcs_status': self.check_violating_arcs_status(new_traversed),
                            'timesteps': 1,
                            'reached_sink': False,
                            'reason': 'Deadlock'
                        })
                        break 
            
            # If we've reached the sink, record this path
            if current_node == self.sink:
                self.activity_profiles.append({
                    'path': path.copy(),
                    'activity_profile': [step.copy() for step in activity_profile],
                    'traversed_arcs': traversed_arcs.copy(),
                    'violating_arcs_status': self.check_violating_arcs_status(traversed_arcs),
                    'timesteps': timestep,
                    'reached_sink': True
                })
                return
                
            
            # Only consider nodes that are reachable
            if current_node not in self.reachable_nodes:
                return
            
            # Get all outgoing arcs from the current node that are part of paths to sink
            outgoing_arcs = []
            for dest in self.graph.get(current_node, []):
                arc = f"{current_node}, {dest}"
                # Only consider valid arcs that lead to the sink
                if arc in self.T and arc in self.valid_arcs and dest in paths_to_sink:
                    # Skip arcs that have reached their l-attribute limit
                    arc_count = traversed_arcs.get(arc, 0)
                    if arc_count >= self.T[arc]["l-attribute"]:
                        continue
                    outgoing_arcs.append((arc, dest))
            
            # If we have no outgoing arcs and haven't reached the sink, this is a deadlock
            if not outgoing_arcs:
                self.activity_profiles.append({
                    'path': path.copy(),
                    'activity_profile': [step.copy() for step in activity_profile],
                    'traversed_arcs': traversed_arcs.copy(),
                    'violating_arcs_status': self.check_violating_arcs_status(traversed_arcs),
                    'timesteps': timestep,
                    'reached_sink': False,
                    'reason': 'No valid outgoing arcs'
                })
                return
            
            # Sort outgoing arcs to prioritize contraction path arcs
            prioritized_outgoing_arcs = []
            contraction_path_arcs = []
            other_arcs = []
            
            for arc, dest in outgoing_arcs:
                if arc in self.contraction_path:
                    contraction_path_arcs.append((arc, dest))
                else:
                    other_arcs.append((arc, dest))
            
            # Put contraction path arcs first
            prioritized_outgoing_arcs = contraction_path_arcs + other_arcs
            outgoing_arcs = prioritized_outgoing_arcs
            
            # Process successor paths as in the original code
            successor_paths = self.group_by_successor_paths(outgoing_arcs, paths_to_sink)
            
            # For each successor path, traverse the arcs
            for successor_path_arcs in successor_paths:
                new_traversed = traversed_arcs.copy()
                new_node_c_attributes = node_c_attributes.copy()
                new_out_list_traversed = has_traversed_out_list
                
                # New timestep for this step
                new_timestep = timestep + 1
                new_activity_profile = activity_profile.copy()
                
                # Ensure we have enough timesteps in our activity profile
                while len(new_activity_profile) < new_timestep:
                    new_activity_profile.append([])
                
                # Add arcs for this successor path to the activity profile
                for arc, dest in successor_path_arcs:
                    src = arc.split(", ")[0]
                    new_activity_profile[new_timestep-1].append((src, dest))
                    new_traversed[arc] = new_traversed.get(arc, 0) + 1
                    
                    # Update node c-attribute state
                    arc_c_attribute = self.T[arc]["c-attribute"]
                    if arc_c_attribute != "0":
                        new_node_c_attributes[dest] = arc_c_attribute
                    
                    # Check if we're traversing an out_list arc
                    if arc in self.processed_out_list:
                        new_out_list_traversed = True
                
                # If an out_list arc was traversed, reset applicable arcs
                if new_out_list_traversed and not has_traversed_out_list:
                    new_traversed = self.reset_arcs_after_out_list_traversal(new_traversed)
                    # Also reset node_c_attributes
                    new_node_c_attributes = {}
                
                # Get the next node to explore
                next_node = successor_path_arcs[-1][1]  # Last arc's destination
                
                # Update the path
                new_path = path.copy()
                new_path.append(next_node)
                
                # Continue exploration with increased depth
                dfs_paths(next_node, new_path, new_activity_profile, new_timestep, 
                        new_traversed, new_node_c_attributes, new_out_list_traversed, depth + 1)
        
        # Start DFS from the source
        dfs_paths(self.source, [self.source], [], 0, {})
        
        # Post-process to group activities by target vertex within each timestep
        for profile_data in self.activity_profiles:
            profile_data['activity_profile'] = self.group_activities_by_target(profile_data['activity_profile'])
        
        return self.activity_profiles

    def calculate_paths_to_sink(self):
        """Calculate nodes that are part of paths to the sink"""
        nodes_to_sink = set([self.sink])
        queue = deque([self.sink])
        
        while queue:
            node = queue.popleft()
            for src in self.graph.keys():
                if src != node:  # Avoid self-loops
                    for dst in self.graph.get(src, []):
                        if dst == node:
                            arc = f"{src}, {dst}"
                            if arc in self.valid_arcs and src not in nodes_to_sink:
                                nodes_to_sink.add(src)
                                queue.append(src)
        
        return nodes_to_sink

    def group_by_successor_paths(self, traversable_arcs, paths_to_sink):
        """Group traversable arcs by their successor paths, prioritizing contraction path arcs"""
        # Process contraction path into a set for quick lookup
        contraction_path_set = set()
        for item in self.contraction_path:
            if isinstance(item, dict) and 'arc' in item:
                contraction_path_set.add(item['arc'])
            else:
                contraction_path_set.add(item)
        
        # Prioritize contraction path arcs
        contraction_arcs = []
        other_arcs = []
        
        for arc, dest in traversable_arcs:
            if arc in contraction_path_set:
                contraction_arcs.append((arc, dest))
            else:
                other_arcs.append((arc, dest))
        
        # Create paths starting with contraction arcs first
        successor_paths = []
        for arc, dest in contraction_arcs:
            successor_paths.append([(arc, dest)])
        
        # Then add other arcs
        for arc, dest in other_arcs:
            successor_paths.append([(arc, dest)])
        
        return successor_paths
    
    def explore_cycle(self, start_node, path, activity_profile, timestep, traversed_arcs, 
                  node_c_attributes, cycle, dfs_callback, has_traversed_out_list=False, depth=0):
        """Explore a cycle to exhaust l-attributes of its arcs"""
        # Extract the arcs in this cycle
        cycle_arcs = []
        
        # Handle different cycle data formats
        if isinstance(cycle, dict) and 'cycle' in cycle:
            for arc in cycle['cycle']:
                if isinstance(arc, dict) and 'arc' in arc:
                    cycle_arcs.append(arc['arc'])
                else:
                    cycle_arcs.append(arc)
        else:
            # If cycle is directly a list of arcs
            if isinstance(cycle, list):
                for arc in cycle:
                    if isinstance(arc, dict) and 'arc' in arc:
                        cycle_arcs.append(arc['arc'])
                    else:
                        cycle_arcs.append(arc)
            else:
                # If cycle is a single arc string
                cycle_arcs = [cycle]
        
        # Only consider valid arcs from the identified valid arcs
        cycle_arcs = [arc for arc in cycle_arcs if arc in self.valid_arcs]
        
        # Find the sequence of nodes in the cycle
        cycle_nodes = []
        current = start_node
        visited = set()
        
        while current not in visited:
            visited.add(current)
            cycle_nodes.append(current)
            
            # Find the next node in the cycle, prioritizing contraction path arcs
            next_node = None
            contraction_path_found = False
            
            # First try to find contraction path arcs
            for arc in cycle_arcs:
                src, dst = arc.split(", ")
                if src == current and f"{src}, {dst}" in cycle_arcs:
                    if arc in self.contraction_path:
                        next_node = dst
                        contraction_path_found = True
                        break
            
            # If no contraction path arc was found, use the first available arc
            if not contraction_path_found:
                for arc in cycle_arcs:
                    src, dst = arc.split(", ")
                    if src == current and f"{src}, {dst}" in cycle_arcs:
                        next_node = dst
                        break
            
            if next_node:
                current = next_node
            else:
                # If no next node found, break to avoid infinite loop
                break
                
            # If we've completed the cycle, break
            if current == start_node:
                break
        
        # Check if we need to continue exhausting l-attributes in this cycle
        needs_exhausting = False
        for arc in cycle_arcs:
            arc_count = traversed_arcs.get(arc, 0)
            if arc in self.T and arc_count < self.T[arc]["l-attribute"]:
                needs_exhausting = True
                break
        
        if needs_exhausting:
            # Group activities for cycle traversal by target
            target_groups = defaultdict(list)
            cycle_traversed = {}
            out_list_traversed = has_traversed_out_list
            
            # Mark all traversable arcs in the cycle
            for i in range(len(cycle_nodes)):
                src = cycle_nodes[i]
                dst = cycle_nodes[(i + 1) % len(cycle_nodes)]
                arc = f"{src}, {dst}"
                
                # Only consider valid arcs that are part of the cycle
                if arc in cycle_arcs and arc in self.T and arc in self.valid_arcs:
                    l_limit = self.T[arc]["l-attribute"]
                    current_count = traversed_arcs.get(arc, 0)
                    
                    if current_count < l_limit:
                        # Check if node is reachable
                        if dst in self.reachable_nodes:
                            target_groups[dst].append((arc, src, dst))
                            cycle_traversed[arc] = True
                            
                            # Check if we're traversing an out_list arc
                            if arc in self.processed_out_list:
                                out_list_traversed = True
            
            if cycle_traversed:
                # Traverse the cycle once
                new_traversed = traversed_arcs.copy()
                new_timestep = timestep + 1
                new_activity_profile = activity_profile.copy()
                new_node_c_attributes = node_c_attributes.copy()
                
                # Ensure we have enough timesteps
                while len(new_activity_profile) < new_timestep:
                    new_activity_profile.append([])
                
                # Add all arcs in this cycle iteration to the activity profile by target
                for dst, arc_group in target_groups.items():
                    for arc_tuple in arc_group:
                        arc, src, dst = arc_tuple
                        # Update the traversed count
                        new_traversed[arc] = new_traversed.get(arc, 0) + 1
                        
                        # Add to activity profile
                        new_activity_profile[new_timestep-1].append((src, dst))
                        
                        # Update node c-attribute state
                        arc_c_attribute = self.T[arc]["c-attribute"]
                        if arc_c_attribute != "0":
                            new_node_c_attributes[dst] = arc_c_attribute
                
                # If an out_list arc was traversed, reset applicable arcs
                if out_list_traversed and not has_traversed_out_list:
                    new_traversed = self.reset_arcs_after_out_list_traversal(new_traversed)
                    # Also reset node_c_attributes
                    new_node_c_attributes = {}
                
                # Update path with all nodes in the cycle
                new_path = path.copy()
                for node in cycle_nodes[1:]:  # Skip the start node which is already in the path
                    if node not in new_path and node in self.reachable_nodes:
                        new_path.append(node)
                
                # Call back to continue exploration from the last node in the cycle
                dfs_callback(cycle_nodes[-1], new_path, new_activity_profile, 
                            new_timestep, new_traversed, new_node_c_attributes, out_list_traversed, depth + 1)
        
        # Also explore paths that exit the cycle
        dfs_callback(start_node, path, activity_profile, timestep, traversed_arcs, 
                    node_c_attributes, has_traversed_out_list, depth)

    def group_activities_by_target(self, activity_profile):
        """Group activities within each timestep by target vertex"""
        grouped_profile = []
        
        for timestep_activities in activity_profile:
            # Group by target vertex
            target_groups = defaultdict(list)
            for src, dst in timestep_activities:
                target_groups[dst].append((src, dst))
            
            # Flatten the groups
            grouped_activities = []
            for dst, arcs in target_groups.items():
                grouped_activities.extend(arcs)
            
            grouped_profile.append(grouped_activities)
        
        return grouped_profile

    def can_traverse_in_path(self, arc, traversed_arcs, node_c_attributes):
        """Check if an arc can be traversed based on c-attributes in the current path"""
        x, y = arc.split(", ")
        
        # Check l-attribute limit
        arc_count = traversed_arcs.get(arc, 0)
        if arc in self.T and arc_count >= self.T[arc]["l-attribute"]:
            return False
            
        arc_c_attribute = self.T[arc]["c-attribute"]
        
        # Build a map of which c-attributes have been used for each node
        node_c_attributes = {}
        
        # Examine all traversed arcs to determine node c-attribute state
        for traversed_arc, count in traversed_arcs.items():
            if count > 0:  # If this arc has been traversed
                src, dst = traversed_arc.split(", ")
                arc_c = self.T[traversed_arc]["c-attribute"]
                
                if arc_c != "0":  # If this arc has a non-zero c-attribute
                    if dst not in node_c_attributes:
                        node_c_attributes[dst] = arc_c
                    elif node_c_attributes[dst] != arc_c:
                        # This should never happen if the algorithm is working correctly,
                        # as we shouldn't allow conflicting c-attributes to be traversed
                        print(f"Conflict in node c-attributes: node {dst} has both {node_c_attributes[dst]} and {arc_c}")
        
        # Check if there's a conflict with the current c-attribute state of the target node
        if y in node_c_attributes and arc_c_attribute != "0" and node_c_attributes[y] != arc_c_attribute:
            return False
        
        return True

    def check_violating_arcs_status(self, traversed_arcs):
        """Check the status of violating arcs in the current path"""
        status = {}
        
        # Convert violating_arcs to a list of arc strings if it contains dictionaries
        violating_arc_names = []
        violating_types = {}
        
        for arc in self.violating_arcs:
            if isinstance(arc, dict) and 'arc' in arc:
                arc_name = arc['arc']
                violating_arc_names.append(arc_name)
                violating_types[arc_name] = arc.get('type', 'Unknown')
            else:
                violating_arc_names.append(arc)
                violating_types[arc] = 'Unknown'
        
        for arc in violating_arc_names:
            if arc in traversed_arcs and traversed_arcs[arc] > 0:
                status[arc] = {
                    "status": "traversed",  # Traversed from source to sink
                    "type": violating_types.get(arc, 'Unknown')
                }
            elif arc in traversed_arcs:
                status[arc] = {
                    "status": "checked_not_traversed",  # Checked but not traversed (deadlock)
                    "type": violating_types.get(arc, 'Unknown')
                }
            else:
                status[arc] = {
                    "status": "unreached",  # Never checked/traversed
                    "type": violating_types.get(arc, 'Unknown')
                }
        
        return status

    def print_activity_profiles(self):
        """Print all generated activity profiles with detailed information"""
        if not self.activity_profiles:
            print("No activity profiles generated yet. Run extract_all_activity_profiles() first.")
            return
        
        profile_counter = 0
        
        for profile_data in self.activity_profiles:
            # Check if this profile has any non-empty timesteps
            has_activities = False
            for activities in profile_data['activity_profile']:
                if activities:  # If there are any activities in this timestep
                    has_activities = True
                    break
            
            # Skip this profile if it has no activities
            if not has_activities:
                continue
                
            profile_counter += 1
            print(f"\n=== ACTIVITY PROFILE {profile_counter} ===")
            
            # Print the sequence of activities
            for t, activities in enumerate(profile_data['activity_profile']):
                if not activities:
                    continue
                    
                formatted_step = ", ".join(f"({x}, {y})" for x, y in activities)
                print(f"S({t+1}) = {{{formatted_step}}}")
            
            # Check if the last activity actually reaches the sink
            # This ensures we correctly report if the sink was reached regardless of the flag
            sink_reached = False
            last_activities = None
            
            # Find the last non-empty timestep
            for activities in reversed(profile_data['activity_profile']):
                if activities:
                    last_activities = activities
                    break
            
            # Check if any activity in the last timestep reaches the sink
            if last_activities:
                for src, dst in last_activities:
                    if dst == self.sink:
                        sink_reached = True
                        break
            
            # Use both the flag and our check to determine if sink was reached
            # Priority to our check which examines the actual path
            reached_sink = sink_reached or profile_data.get('reached_sink', False)
            
            if reached_sink:
                timesteps = len([a for a in profile_data['activity_profile'] if a])
                summary_sets = ", ".join([f"S({i+1})" for i in range(timesteps)])
                print(f"\nS = {{{summary_sets}}}. Sink was reached at timestep {timesteps}.")
            else:
                print("\nSink was NOT reached. Path ended with deadlock.")
            
            # Print violating arc status
            violating_status = profile_data['violating_arcs_status']
            # if violating_status:
            #     print("\nViolating Arcs Status:")
            #     for arc, info in violating_status.items():
            #         status = info.get("status", "Unknown")
            #         violation_type = info.get("type", "Unknown")
            #         print(f"  - {arc}: {status}")
            #         print(f"    Violation Type: {violation_type}")
        
        # Recalculate the summary based only on non-empty profiles
        non_empty_profiles = [p for p in self.activity_profiles if any(activities for activities in p['activity_profile'])]
        
        # Update reached_sink flags in the profiles based on actual path
        for profile in non_empty_profiles:
            # Check if any activity in the last timestep reaches the sink
            sink_reached = False
            last_activities = None
            
            # Find the last non-empty timestep
            for activities in reversed(profile['activity_profile']):
                if activities:
                    last_activities = activities
                    break
            
            # Check if any activity in the last timestep reaches the sink
            if last_activities:
                for src, dst in last_activities:
                    if dst == self.sink:
                        sink_reached = True
                        profile['reached_sink'] = True
                        break
        
        # Now count based on updated flags
        total_profiles = len(non_empty_profiles)
        reached_sink = sum(1 for p in non_empty_profiles if p.get('reached_sink', False))
        deadlocks = total_profiles - reached_sink
        
        # Print summary statistics
        print(f"\n=========== SUMMARY ===========")
        print(f"Total Activity Profiles: {total_profiles}")
        print(f"Properly Terminated: {reached_sink}")
        print(f"Paths with Deadlock: {deadlocks}")
        
        # Analyze violating arcs across all paths (only non-empty ones)
        all_violating = set()
        for p in non_empty_profiles:
            for arc in p['violating_arcs_status'].keys():
                all_violating.add(arc)
        
        print(f"Total Violating Arcs: {len(all_violating)}")
        for arc in all_violating:
            traversed_in = sum(1 for p in non_empty_profiles 
                            if arc in p['violating_arcs_status'] 
                            and p['violating_arcs_status'][arc].get('status') == "traversed")
            
            checked_not_traversed = sum(1 for p in non_empty_profiles 
                                    if arc in p['violating_arcs_status'] 
                                    and p['violating_arcs_status'][arc].get('status') == "checked_not_traversed")
            
            unreached = sum(1 for p in non_empty_profiles 
                        if arc in p['violating_arcs_status'] 
                        and p['violating_arcs_status'][arc].get('status') == "unreached")
            
            # Get type of violating arc
            arc_type = "Unknown"
            for p in non_empty_profiles:
                if arc in p['violating_arcs_status']:
                    arc_type = p['violating_arcs_status'][arc].get('type', 'Unknown')
                    break
            
            print(f"  - {arc}:")
            print(f"    Traversed in {traversed_in} activities")
            print(f"    Checked but not traversed in {checked_not_traversed} activities")
            print(f"    Unreached in {unreached} activities")
            print(f"    Violation Type: {arc_type}")

    def print_violations_report(self):
        """
        Print a comprehensive report of violations, separating l-safe violations
        and identifying classical soundness violations.
        """
        if not self.activity_profiles:
            print("No activity profiles generated yet. Run extract_all_activity_profiles() first.")
            return
        
        print("\n=========== VIOLATIONS REPORT ===========")
        
        # First, analyze l-safe violations (already in violating_arcs)
        l_safe_violations = set()
        for arc in self.violating_arcs:
            if isinstance(arc, dict) and 'arc' in arc:
                l_safe_violations.add(arc['arc'])
            else:
                l_safe_violations.add(arc)
        
        # Get all valid profiles
        valid_profiles = [p for p in self.activity_profiles if any(activities for activities in p['activity_profile'])]
        
        # Analyze classical soundness properties
        is_sound= self.verify_classical_soundness()
        
        # Check proper termination
        reach_sink = [p for p in valid_profiles if p.get('reached_sink', False)]
        deadlocks = [p for p in valid_profiles if not p.get('reached_sink', False)]
        proper_termination = len(deadlocks) == 0
        
        # Check liveness
        traversed_arcs = set()
        for profile in valid_profiles:
            for arc, count in profile.get('traversed_arcs', {}).items():
                if count > 0:
                    traversed_arcs.add(arc)
        
        non_traversed_arcs = self.valid_arcs - traversed_arcs
        liveness = len(non_traversed_arcs) == 0
        
        print(f"\nVIOLATING ARCS ({len(l_safe_violations)}):")
        if l_safe_violations:
            for arc in l_safe_violations:
                # Count how many profiles this arc was traversed in
                traversed_in = sum(1 for p in valid_profiles 
                                if arc in p['violating_arcs_status'] 
                                and p['violating_arcs_status'][arc].get('status') == "traversed")
                
                checked_not_traversed = sum(1 for p in valid_profiles 
                                        if arc in p['violating_arcs_status'] 
                                        and p['violating_arcs_status'][arc].get('status') == "checked_not_traversed")
                
                unreached = sum(1 for p in valid_profiles 
                            if arc in p['violating_arcs_status'] 
                            and p['violating_arcs_status'][arc].get('status') == "unreached")
                
                # Get type of violating arc
                arc_type = "Unknown"
                for p in valid_profiles:
                    if arc in p['violating_arcs_status']:
                        arc_type = p['violating_arcs_status'][arc].get('type', 'Unknown')
                        break
                
                print(f"\n  - {arc}:")
                # print(f"    Violation Type: {arc_type}")
                print(f"    Traversed in {traversed_in} paths")
                print(f"    Checked but not traversed in {checked_not_traversed} paths")
                print(f"    Unreached in {unreached} paths")
                
                # Check if this arc also violated classical soundness
                classical_soundness_issues = []
                
                # Check if this arc caused deadlocks
                deadlock_profiles = [p for p in deadlocks if 
                                    arc in p['traversed_arcs'] and p['traversed_arcs'][arc] > 0]
                
                if deadlock_profiles:
                    classical_soundness_issues.append(f"Caused deadlock in {len(deadlock_profiles)} activities")
                
                # Check if this arc was never traversed
                if arc in non_traversed_arcs:
                    classical_soundness_issues.append("Violated liveness (never traversed)")
                
                if classical_soundness_issues:
                    print(f"    Classical Soundness Violation:")
                    for issue in classical_soundness_issues:
                        print(f"      - {issue}")
        else:
            print("  No l-safe violations found.")
        
        # Final summary
        print("\n=========== SUMMARY ===========")
        print(f"\n{'RDLT is L-Safe.' if not l_safe_violations else 'RDLT is NOT L-Safe.'}")
        print(f"\n{'RDLT is CLASSICAL SOUND.' if is_sound else 'RDLT is NOT CLASSICAL SOUND.'}")
        print(f"  - Proper Termination: {'Satisfied' if proper_termination else 'Not Satisfied'}")
        print(f"  - Liveness: {'Satisfied' if liveness else 'Not Satisfied'}\n")

    def analyze_model(self, max_depth=10):
        """Analyze the model and generate all possible activity profiles"""
        # Generate all possible activity profiles with a reasonable depth limit
        self.extract_all_activity_profiles(max_depth)
        
        # Print detailed results
        self.print_activity_profiles()

        # Print violations report
        self.print_violations_report()
        
        # Return the results for further processing
        return self.activity_profiles
    
    def analyze_deadlock_arcs(self):
        """
        Analyze arcs that were checked but not traversed in deadlock scenarios.
        This helps diagnose why certain paths ended in deadlock despite having potential next steps.
        """
        if not self.activity_profiles:
            print("No activity profiles generated yet. Run extract_all_activity_profiles() first.")
            return
        
        print("\n=== DEADLOCK ARC ANALYSIS ===")
        
        # Get all deadlock profiles
        deadlock_profiles = [p for p in self.activity_profiles 
                            if any(activities for activities in p['activity_profile']) and not p.get('reached_sink', False)]
        
        if not deadlock_profiles:
            print("No deadlocks found.")
            return
        
        print(f"Total deadlocks: {len(deadlock_profiles)}")
        
        # Collect all last nodes in deadlock paths
        deadlock_points = {}
        for profile in deadlock_profiles:
            # Find the last node in the path
            last_node = None
            for activities in reversed(profile['activity_profile']):
                if activities:
                    # Last activity's destination is where we got stuck
                    last_node = activities[-1][1]  
                    break
            
            if last_node:
                if last_node not in deadlock_points:
                    deadlock_points[last_node] = 0
                deadlock_points[last_node] += 1
        
        # Print deadlock distribution by node
        print("\nDeadlock distribution by node:")
        for node, count in sorted(deadlock_points.items(), key=lambda x: x[1], reverse=True):
            print(f"  Node {node}: {count} deadlocks")
        
        # Analyze potential outgoing arcs from deadlock nodes
        print("\nPotential outgoing arcs from deadlock nodes that were checked but not traversed:")
        
        for node in deadlock_points:
            print(f"\nFrom deadlock node: {node}")
            outgoing_arc_stats = {}
            
            # Find all possible outgoing arcs from this node
            potential_arcs = []
            for dst in self.graph.get(node, []):
                arc = f"{node}, {dst}"
                if arc in self.T:
                    potential_arcs.append(arc)
            
            if not potential_arcs:
                print("  No outgoing arcs defined for this node.")
                continue
            
            # Analyze why these arcs couldn't be traversed
            for arc in potential_arcs:
                print(f"  Arc: {arc}")
                print(f"    l-attribute limit: {self.T[arc]['l-attribute']}")
                
                # Count deadlock profiles where this arc was checked but not traversed
                checked_profiles = [p for p in deadlock_profiles if 
                                    any(a[0] == arc.split(", ")[0] for activities in p['activity_profile'] for a in activities)]
                
                traversed_count = sum(1 for p in checked_profiles if p['traversed_arcs'].get(arc, 0) > 0)
                not_traversed_count = len(checked_profiles) - traversed_count
                
                print(f"    Traversed in {traversed_count} activities with deadlock")
                print(f"    Checked but not traversed in {not_traversed_count} activities with deadlock")
                
                # For paths where the arc was checked but not traversed, analyze why
                if not_traversed_count > 0:
                    print("    Reasons for not traversing:")
                    
                    # Check if arc is valid
                    if arc not in self.valid_arcs:
                        print(f"      - Arc is not in valid_arcs")
                    
                    # Check if destination is in paths to sink
                    if arc.split(", ")[1] not in self.calculate_paths_to_sink():
                        print(f"      - Destination node is not in paths_to_sink")
                    
                    # Check l-attribute limits
                    l_limit_exceeded = sum(1 for p in checked_profiles if p['traversed_arcs'].get(arc, 0) >= self.T[arc]['l-attribute'])
                    if l_limit_exceeded > 0:
                        print(f"      - l-attribute limit exceeded in {l_limit_exceeded} paths")
                    
                    # Check c-attribute constraints
                    c_attr = self.T[arc]['c-attribute']
                    if c_attr != "0":
                        print(f"      - Has c-attribute constraint: {c_attr}")
                        # We'd need to check individual paths for c-attribute conflicts
                    
                    # Check if arc is in failed contractions
                    failed_arc_strings = []
                    for item in self.failed_contractions:
                        if isinstance(item, dict) and 'arc' in item:
                            failed_arc_strings.append(item['arc'])
                        elif isinstance(item, str):
                            failed_arc_strings.append(item)
                    
                    if arc in failed_arc_strings:
                        print(f"      - Arc is in failed_contractions")
                    
                print()

    def verify_classical_soundness(activity_extraction):
        """
        Verify if the given RDLT model satisfies classical soundness properties.
        
        Classical soundness has two main properties:
        1. Proper termination - ALL activity profiles reach the sink (no deadlocks)
        2. Liveness - ALL arcs are traversable in at least one activity profile
        
        Parameters:
        activity_extraction (ModifiedActivityExtraction): An instance of ModifiedActivityExtraction 
                                                        with already generated activity profiles
        
        Returns:
        tuple: (is_sound, report) where:
            - is_sound is a boolean indicating if the RDLT is classical sound
            - report is a detailed string explaining the verification results
        """
        # Ensure activity profiles are generated
        if not activity_extraction.activity_profiles:
            activity_extraction.analyze_model()
        
        # Filter out activity profiles with no activities
        valid_profiles = [p for p in activity_extraction.activity_profiles 
                        if any(activities for activities in p['activity_profile'])]
        
        if not valid_profiles:
            return False, "No valid activity profiles were generated."
        
        # Check proper termination (all profiles reach sink)
        reach_sink = [p for p in valid_profiles if p.get('reached_sink', False)]
        deadlocks = [p for p in valid_profiles if not p.get('reached_sink', False)]
        
        proper_termination = len(deadlocks) == 0
        
        # Check liveness (all arcs are traversed in at least one profile)
        # First, get all valid arcs that should be traversable
        all_arcs = activity_extraction.valid_arcs
        
        # Then, check which arcs are actually traversed
        traversed_arcs = set()
        for profile in valid_profiles:
            for arc, count in profile.get('traversed_arcs', {}).items():
                if count > 0:
                    traversed_arcs.add(arc)
        
        # Arcs that should be traversable but aren't
        non_traversed_arcs = all_arcs - traversed_arcs
        
        liveness = len(non_traversed_arcs) == 0
        
        # Determine if the RDLT is classical sound
        is_sound = proper_termination and liveness
        
        # # Generate detailed report
        # report = []
        # report.append('-' * 60)
        # # report.append(f"Total Activity Profiles Generated: {len(valid_profiles)}")
        # # report.append(f"Activities that Properly Terminated: {len(reach_sink)}")
        # # report.append(f"Activities Ending in Deadlock: {len(deadlocks)}")
        
        # report.append(f"\nProper Termination: {'SATISFIED' if proper_termination else 'NOT SATISFIED'}")
        # if not proper_termination:
        #     report.append(f"- {len(deadlocks)} activity profiles ended in deadlock")
            
        #     # # List some deadlock examples
        #     # if deadlocks:
        #     #     report.append("\nDeadlocks:")
        #     #     max_examples = min(3, len(deadlocks))
        #     #     for i in range(max_examples):
        #     #         # Find the last node in the deadlock path
        #     #         last_node = None
        #     #         for activities in reversed(deadlocks[i]['activity_profile']):
        #     #             if activities:
        #     #                 # Last activity's destination
        #     #                 last_node = activities[-1][1]
        #     #                 break
                    
        #     #         reason = deadlocks[i].get('reason', 'Unknown')
        #     #         report.append(f"  - Deadlock at node {last_node}.")
        
        # report.append(f"\nLiveness: {'SATISFIED' if liveness else 'NOT SATISFIED'}")
        # if not liveness:
        #     report.append(f"- {len(non_traversed_arcs)} arcs are not traversed in any activity profile")
            
        #     # List some non-traversed arcs
        #     if non_traversed_arcs:
        #         report.append("\nNon-traversed Arcs:") #Cannot fully verify classical soundness if non-empty
        #         max_examples = min(5, len(non_traversed_arcs))
        #         for i, arc in enumerate(list(non_traversed_arcs)[:max_examples]):
        #             report.append(f"  - {arc}")
        #         if len(non_traversed_arcs) > max_examples:
        #             report.append(f"  - And {len(non_traversed_arcs) - max_examples} more...")
        
        # # report.append(f"\nFINAL VERIFICATION: The RDLT is {'CLASSICAL SOUND' if is_sound else 'NOT Classical Sound'}")
        
        return is_sound #"\n".join(report)
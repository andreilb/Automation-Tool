import utils
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('extraction_debug.log')
    ]
)

logger = logging.getLogger('ModifiedActivityExtraction')

class ModifiedActivityExtraction:
    def __init__(self, R, contraction_path, violating_arcs, failed_contractions, in_list=None, out_list=None):
        self.R = R
        self.contraction_path = contraction_path
        self.violating_arcs = violating_arcs
        self.failed_contractions = failed_contractions
        self.activity_profile = []
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

        self.untraversed_violations = {}

        self.in_list = in_list if in_list else []
        self.out_list = out_list if out_list else []

        self.graph = utils.build_graph(R)
        self.source, self.sink = utils.get_source_and_target_vertices(self.R)
        self.visited_nodes = set()
        self.parent_nodes = {}
        self.current_timestep = 0
        
        logger.info(f"Initialized ModifiedActivityExtraction")
        logger.info(f"Source: {self.source}, Sink: {self.sink}")
        logger.info(f"Contraction Path: {self.contraction_path}")
        logger.info(f"Violating Arcs: {self.violating_arcs}")

    def traverse_and_update(self, x, y):
        arc_name = f"{x}, {y}"
        self.current_timestep += 1
        t_check = self.current_timestep

        logger.debug(f"Checking arc {arc_name} at timestep {t_check}...")

        if arc_name not in self.T:
            logger.warning(f"Arc {arc_name} not found in T dictionary")
            return None  # Ensure we only operate on valid arcs

        # Ensure `self.RBS` exists before using it
        if hasattr(self, "RBS") and arc_name in self.out_list:
            logger.debug(f"Resetting T-values for out-bridge arcs related to {arc_name}...")
            for reset_arc in self.T:
                if reset_arc in self.RBS:  # Ensure it's in the Restricted Bridge Set
                    self.T[reset_arc]["check"] = 0
                    self.T[reset_arc]["traverse"] = 0

        self.T[arc_name]['check'] = t_check

        arc_data = next((arc for arc in self.R if arc['arc'] == arc_name), None)
        if not arc_data:
            logger.warning(f"Warning: Arc {arc_name} not found in RDLT.")
            return None

        if self.T[arc_name]['count'] >= arc_data['l-attribute']:
            logger.warning(f"Arc {arc_name} has reached its L-value limit. Cannot traverse.")
            return None

        self.T[arc_name]['count'] += 1
        t_traverse = self.current_timestep
        self.T[arc_name]['traverse'] = t_traverse

        while len(self.activity_profile) < t_traverse:
            self.activity_profile.append([])

        self.activity_profile[t_traverse - 1].append((x, y))
        logger.info(f"Arc {arc_name} traversed at timestep {t_traverse}. Traversal count: {self.T[arc_name]['count']}")

        self.visited_nodes.add(y)
        self.parent_nodes[y] = x

        return y

    def extract_activity_profile(self):
        self.visited_nodes.add(self.source)
        current_nodes = {self.source}
        self.activity_profile = []
        
        logger.info(f"Starting extraction from source node: {self.source}")
        
        while current_nodes and not (len(current_nodes) == 1 and self.sink in current_nodes):
            logger.debug(f"Current nodes: {current_nodes}")
            
            # Step 1: Check outgoing arcs from current nodes
            checked_arcs = set()
            for node in current_nodes:
                outgoing_arcs = [f"{node}, {neighbor}" for neighbor in self.graph.get(node, [])]
                for arc in outgoing_arcs:
                    if arc in self.T and self.T[arc]['check'] == 0:
                        self.current_timestep += 1
                        self.T[arc]['check'] = self.current_timestep
                        checked_arcs.add(arc)
                        logger.debug(f"Checking arc {arc} at timestep {self.current_timestep}")

            # Step 2: Find immediately traversable arcs (can be traversed in same timestep as checked)
            immediate_traversable = {}
            for arc in checked_arcs:
                if self.is_immediately_traversable(arc):
                    x, y = arc.split(", ")
                    if y not in immediate_traversable:
                        immediate_traversable[y] = []
                    immediate_traversable[y].append(arc)
                    logger.debug(f"Arc {arc} can be traversed immediately in the same timestep")
            
            # Step 3: Traverse immediately traversable arcs
            if immediate_traversable:
                timestep_activities = []
                next_nodes = set()
                
                # Use same prioritization logic
                def prioritization_key(target):
                    has_contraction_arc = any(arc in self.contraction_path for arc in immediate_traversable[target])
                    return (
                        target == self.sink,
                        has_contraction_arc,
                        len(immediate_traversable[target])
                    )
                
                # Select highest priority target
                if immediate_traversable:  # Check if not empty
                    selected_target = max(immediate_traversable.keys(), key=prioritization_key)
                    selected_arcs = immediate_traversable[selected_target]
                    
                    # Further sort selected arcs to prioritize contraction path
                    selected_arcs.sort(key=lambda a: a not in self.contraction_path)
                    
                    logger.info(f"Selected target node for immediate traversal: {selected_target}")
                    logger.info(f"Selected arcs for immediate traversal: {selected_arcs}")
                    
                    # Traverse all selected arcs in the same timestep they were checked
                    for arc in selected_arcs:
                        x, y = arc.split(", ")
                        # Use the check timestep as the traverse timestep
                        traverse_timestep = self.T[arc]['check']
                        self.T[arc]['traverse'] = traverse_timestep
                        self.T[arc]['count'] += 1
                        
                        # Ensure activity_profile has enough elements
                        while len(self.activity_profile) < traverse_timestep:
                            self.activity_profile.append([])
                        
                        # Add to the activity profile at the appropriate timestep (index is timestep-1)
                        self.activity_profile[traverse_timestep-1].append((x, y))
                        
                        next_nodes.add(y)
                        self.visited_nodes.add(y)
                        logger.info(f"Immediately traversing arc {arc} at the same timestep {traverse_timestep}")
                        if arc in self.contraction_path:
                            logger.info(f"Traversed contraction path arc: {arc}")
                    
                    current_nodes = next_nodes
                    continue  # Skip to next iteration since we've already processed these nodes

            # Step 4: If no immediate traversal, find traversable arcs for next timestep
            traversable_arcs = []
            for arc in checked_arcs:
                if arc not in immediate_traversable.get(arc.split(", ")[1], []) and self.can_traverse(arc):
                    traversable_arcs.append(arc)
            
            # Group by target vertex
            traversable_groups = {}
            for arc in traversable_arcs:
                x, y = arc.split(", ")
                if y not in traversable_groups:
                    traversable_groups[y] = []
                traversable_groups[y].append(arc)
            
            # Step 5: Traverse grouped arcs in next timestep
            if traversable_groups:
                self.current_timestep += 1
                timestep_activities = []
                next_nodes = set()
                
                def prioritization_key(target):
                    has_contraction_arc = any(arc in self.contraction_path for arc in traversable_groups[target])
                    return (
                        target == self.sink,
                        has_contraction_arc,
                        len(traversable_groups[target])
                    )
                
                selected_target = max(traversable_groups.keys(), key=prioritization_key)
                selected_arcs = traversable_groups[selected_target]
                
                selected_arcs.sort(key=lambda a: a not in self.contraction_path)
                
                logger.info(f"Selected target node for next timestep: {selected_target}")
                logger.info(f"Selected arcs for next timestep: {selected_arcs}")
                
                for arc in selected_arcs:
                    x, y = arc.split(", ")
                    self.T[arc]['traverse'] = self.current_timestep
                    self.T[arc]['count'] += 1
                    timestep_activities.append((x, y))
                    next_nodes.add(y)
                    self.visited_nodes.add(y)
                    logger.info(f"Traversing arc {arc} at timestep {self.current_timestep}")
                    if arc in self.contraction_path:
                        logger.info(f"Traversed contraction path arc: {arc}")
                
                if timestep_activities:
                    self.activity_profile.append(timestep_activities)
                current_nodes = next_nodes
            else:
                # If no traversable arcs found, check for deadlock
                logger.warning("No traversable arcs found - potential deadlock")
                return self.detect_deadlock()
        
        logger.info(f"Extraction completed successfully! Sink {self.sink} has been reached.")
        return self.activity_profile

    def is_immediately_traversable(self, arc):
        """
        Check if an arc can be traversed in the same timestep it was checked.
        This is possible if the arc is unconstrained according to the definition.
        """
        if not self.can_traverse(arc):
            return False
            
        x, y = arc.split(", ")
        arc_data = self.T[arc]
        c_attribute = arc_data['c-attribute']
        
        # Get all incoming arcs to y
        incoming_arcs = [a for a in self.T if a.endswith(f", {y}")]
        
        # Check if arc is unconstrained based on the three conditions from Definition 21
        
        # Condition 1: All other incoming arcs have c-attribute of empty or same as current arc
        for other_arc in incoming_arcs:
            if other_arc != arc:
                other_c = self.T[other_arc]['c-attribute']
                # If other arc has different non-empty c-attribute, this arc isn't immediately traversable
                if other_c != "0" and other_c != c_attribute:
                    return False
        
        # Condition 2: Traversal count is within limits for all type-alike arcs
        for other_arc in incoming_arcs:
            if other_arc != arc:
                other_count = self.T[other_arc]['count']
                other_limit = self.T[other_arc]['l-attribute']
                # If other arc's traversal count exceeds current arc's, this arc isn't immediately traversable
                if other_count > arc_data['count'] and other_count < other_limit:
                    return False
        
        # Condition 3: Special case for empty c-attribute with previously traversed arcs
        if c_attribute == "0":
            for other_arc in incoming_arcs:
                if other_arc != arc:
                    other_c = self.T[other_arc]['c-attribute']
                    if other_c != "0" and self.T[other_arc]['traverse'] > 0:
                        return True
        
        # If all conditions pass, arc is immediately traversable
        logger.debug(f"Arc {arc} is immediately traversable (can be traversed in same timestep as checked)")
        return True

    def is_reachable(self, start, target):
        from collections import deque
        queue = deque([start])
        visited = set()

        while queue:
            node = queue.popleft()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    queue.append(neighbor)

        return False
    
    def is_required_for_connectivity(self, arc):
        x, y = arc.split(", ")

        # Check if multiple incoming arcs are necessary for y to be reached
        incoming_arcs = [f"{src}, {y}" for src in self.graph if f"{src}, {y}" in self.T]

        # If more than one incoming arc is needed for y to be reachable, return True
        if len(incoming_arcs) > 1 and all(self.T[a]['check'] > 0 for a in incoming_arcs):
            return True

        return False

    def can_traverse(self, arc):
        x, y = arc.split(", ")

        if x not in self.visited_nodes:
            logger.debug(f"Cannot traverse {arc} because {x} has not been reached.")
            return False  

        arc_data = self.T[arc]

        if arc_data["count"] >= arc_data["l-attribute"]:
            logger.debug(f"Arc {arc} exceeded l-attribute limit. Cannot traverse.")
            return False

        incoming_arcs = [a for a in self.T if a.endswith(f", {y}")]

        relevant_incoming_arcs = []
        for other_arc in incoming_arcs:
            if other_arc != arc:
                other_c = self.T[other_arc]['c-attribute']
                arc_c = arc_data['c-attribute']
                if other_c != "0" and other_c != arc_c:
                    relevant_incoming_arcs.append(other_arc)

        unchecked_incoming = [a for a in relevant_incoming_arcs if self.T[a]["check"] == 0]
        
        if unchecked_incoming:
            logger.debug(f"Cannot traverse {arc}. Not all relevant incoming arcs to {y} have been checked: {unchecked_incoming}")
            return False  

        traversed_incoming_arcs = [a for a in incoming_arcs if self.T[a]['traverse'] > 0]

        if traversed_incoming_arcs:
            logger.debug(f"Since {traversed_incoming_arcs} was traversed, {arc} must also traverse now.")
            return True  

        return True  

    def detect_deadlock(self):
        logger.error(f"\nDeadlock occurred. Sink {self.sink} was NOT reached.")

        # Find last checked timestep
        last_checked_timestep = max((T['check'] for T in self.T.values() if T['check'] > 0), default=0)
        deadlock_arcs = {arc: T for arc, T in self.T.items() if T['check'] == last_checked_timestep and T['traverse'] == 0}

        if deadlock_arcs:
            logger.error("\nThe following arcs caused the deadlock:")
            for arc, t_values in deadlock_arcs.items():
                logger.error(f"  - Arc {arc}: T[check={t_values['check']}, traverse={t_values['traverse']}]")
                
                # Check if the deadlock arc is in violating_arcs
                if arc in self.violating_arcs:
                    logger.error(f"Violating arc {arc} is preventing traversal.")
                    self.untraversed_violations[arc] = t_values

        # Try alternative paths before fully giving up
        alternative_found = False
        for arc, values in deadlock_arcs.items():
            x, y = arc.split(", ")
            alt_paths = [f"{src}, {y}" for src in self.graph if f"{src}, {y}" in self.T and src != x]

            for alt_arc in alt_paths:
                if self.T[alt_arc]['check'] == 0 and self.can_traverse(alt_arc):
                    logger.info(f"Trying alternative path {alt_arc} to avoid deadlock...")
                    self.T[alt_arc]['check'] = self.current_timestep
                    self.T[alt_arc]['traverse'] = self.current_timestep
                    alternative_found = True
                    break  

        # If an alternative path was found, retry traversal once
        if alternative_found:
            logger.info("Retrying traversal after alternative path was found.")
            return self.activity_profile  # Return current state instead of restarting traversal

        logger.error("\nNo alternative paths available. Deadlock confirmed.")
        
        # Report violating arcs that might be causing problems
        if self.untraversed_violations:
            logger.error("\nCRITICAL: The following violating arcs prevented traversal:")
            for arc, t_values in self.untraversed_violations.items():
                logger.error(f"  - Violating arc {arc}: T[check={t_values['check']}, traverse={t_values['traverse']}]")
        
        return self.activity_profile, self.T  # Final deadlock output

    def print_activity_profile(self):
        activity_sets = {}
        for arc_name, values in self.T.items():
            t_traverse = values['traverse']
            if t_traverse > 0:
                if t_traverse not in activity_sets:
                    activity_sets[t_traverse] = set()
                activity_sets[t_traverse].add(tuple(arc_name.split(", ")))

        # Get original timesteps in sorted order
        original_timesteps = sorted(activity_sets.keys())
        
        # Create a mapping from original to sequential timesteps
        timestep_mapping = {orig: seq+1 for seq, orig in enumerate(original_timesteps)}
        
        # Create new dictionary with sequential timesteps
        sequential_sets = {timestep_mapping[t]: activity_sets[t] for t in original_timesteps}
        
        logger.info("\nACTIVITY PROFILE:\n")
        for t in range(1, len(sequential_sets) + 1):
            formatted_step = ", ".join(f"({x}, {y})" for x, y in sequential_sets[t])
            logger.info(f"S({t}) = {{{formatted_step}}}")
        
        # Add summary line about reaching the sink
        max_timestep = len(sequential_sets)
        if self.sink in self.visited_nodes:
            logger.info(f"\nS = {{S(1), S(2), ..., S({max_timestep})}}. Sink was reached at timestep {max_timestep}.")
        else:
            logger.info("\nSink was not reached. Extraction terminated due to deadlock or other issues.")
        
        return sequential_sets

    def debug_state(self):
        """Debug method to print current state of extraction"""
        logger.debug("\n===== DEBUGGING CURRENT STATE =====")
        logger.debug(f"Current timestep: {self.current_timestep}")
        logger.debug(f"Visited nodes: {self.visited_nodes}")
        
        logger.debug("\nArc T-values:")
        for arc, values in self.T.items():
            if values['check'] > 0:  # Only show arcs that have been checked
                logger.debug(f"Arc {arc}: check={values['check']}, traverse={values['traverse']}, count={values['count']}/{values['l-attribute']}")
        
        logger.debug("\nContraction path progress:")
        for arc in self.contraction_path:
            if arc in self.T:
                status = "Traversed" if self.T[arc]['traverse'] > 0 else "Not traversed"
                logger.debug(f"Path arc {arc}: {status}")
        
        logger.debug("\nViolating arcs status:")
        for arc in self.violating_arcs:
            if arc in self.T:
                status = "Traversed" if self.T[arc]['traverse'] > 0 else "Not traversed"
                logger.debug(f"Violating arc {arc}: {status}")
        
        logger.debug("===================================\n")
import utils
import logging
from itertools import chain

# Set up logging configuration
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("contraction_debug.log"),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger('ContractionPath')

class ContractionPath:
    def __init__(self, R, violations):
        """
        Initializes the contraction path algorithm.

        Parameters:
            - R (list): The RDLT structure containing arcs.
        """
        self.R = R
        self.violations = violations
        self.graph = utils.build_graph(R)
        self.contracted_path = []  # Store the final contracted path
        self.successful_contractions_with_rid = []  # Store successful contractions with r-id
        self.failed_contractions_with_rid = []  # Store failed contractions with r-id
        self.successfully_contracted_arcs = set()
        self.failed_contractions = set()  # Track failed contractions as a set
        self.unreached_arcs = set(arc['arc'] for arc in R)
        
        # Keep track of arcs by their start and end vertices
        self.arc_pairs = {}
        
        for arc_data in R:
            arc = arc_data['arc']
            try:
                start, end = arc.split(', ')
                pair = (start, end)
                if pair not in self.arc_pairs:
                    self.arc_pairs[pair] = []
                self.arc_pairs[pair].append(arc)
            except ValueError:
                print(f"Invalid arc format: {arc}")

    def get_outgoing_arcs(self, vertex):
        """
        Gets all outgoing arcs and their c-attributes for a given vertex.
        """
        outgoing_arcs = []
        for arc_data in self.R:
            start, end = arc_data['arc'].split(', ')
            if start == vertex:
                outgoing_arcs.append(arc_data)
        return outgoing_arcs

    def can_contract(self, arc, superset):
        """
        Determines if an arc can be contracted by checking its incoming arcs.
        Returns a tuple (can_contract, reason) where reason is None if can_contract is True,
        otherwise it contains the reason for failure.
        """
        try:
            start, end = arc.split(', ')
        except ValueError:
            # logger.error(f"Invalid arc format: {arc}. Expected format: 'start, end'.")
            return False, "Invalid arc format"

        arc_data = next((a for a in self.R if a['arc'] == arc), None)
        if not arc_data:
            # logger.error(f"Arc {arc} not found in RDLT.")
            return False, "Arc not found in RDLT"

        # Get all incoming arcs to the end vertex
        incoming_arcs = [a for a in self.R if a['arc'].endswith(f", {end}")]

        # If there is only one incoming arc (the current arc), it can be contracted
        if len(incoming_arcs) == 1 and incoming_arcs[0]['arc'] == arc:
            return True, None

        # Collect conflicting c-attributes
        conflicting_c_attributes = set()
        conflicting_arcs = []
        for incoming_arc in incoming_arcs:
            incoming_c_attribute = incoming_arc.get('c-attribute', '0')
            
            if incoming_c_attribute != '0' and incoming_c_attribute not in superset:
                conflicting_c_attributes.add(incoming_c_attribute)
                conflicting_arcs.append(incoming_arc['arc'])

        if conflicting_c_attributes:
            # Find the violating arcs that are causing the conflict
            violating_arcs = []
            for c_attribute in conflicting_c_attributes:
                violating_arcs.extend([arc for arc in conflicting_arcs if 
                                      next((a for a in self.R if a['arc'] == arc), {}).get('c-attribute', '0') == c_attribute])
            
            return False, f"Conflicting with violating arc: {', '.join(violating_arcs)}"

        return True, None

    def get_rid_from_arc(self, arc_str):
        """
        Gets the r-id for a given arc string.
        """
        for arc_data in self.R:
            if arc_data['arc'] == arc_str:
                return arc_data.get('r-id')
        return None

    def contract_paths(self):
        """
        Contracts paths from source to sink sequentially, with improved handling of failed contractions.
        Also tracks r-id for successful and failed contractions, and reasons for failure.
        """
        source, sink = utils.get_source_and_target_vertices(self.R)
        # logger.info(f"Attempting contraction from {source} to {sink}")
        
        # Initialize superset with c-attributes of source's outgoing arcs
        current_superset = {'0'}
        source_outgoing_arcs = self.get_outgoing_arcs(source)
        for arc_data in source_outgoing_arcs:
            c_attribute = arc_data.get('c-attribute', '0')
            if c_attribute != '0':
                current_superset.add(c_attribute)
        
        # Track reached vertices (initially only the source)
        reached_vertices = {source}
        
        # Track the current dummy vertex (initially the source)
        dummy_vertex = source
        
        # Track whether the superset has been updated in the current iteration
        superset_updated = True
        
        # Track contracted arc pairs to avoid duplicates
        contracted_arc_pairs = set()
        
        # Iterate until all arcs are processed or no further contractions are possible
        while reached_vertices and superset_updated:
            contracted_in_iteration = set()
            
            # Reset the superset_updated flag at the start of each iteration
            superset_updated = False

            # Find all outgoing arcs of reached vertices
            candidate_arcs = []
            for vertex in reached_vertices:
                for arc_data in self.get_outgoing_arcs(vertex):
                    arc_str = arc_data['arc']
                    try:
                        start, end = arc_str.split(', ')
                        pair = (start, end)
                        # Only consider if not already contracted
                        if pair not in contracted_arc_pairs and arc_str in self.unreached_arcs:
                            candidate_arcs.append(arc_str)
                    except ValueError:
                        print(f"Invalid arc format: {arc_str}")
                    
            if not candidate_arcs:
                # logger.warning("No more candidate arcs to contract. Breaking loop.")
                break

            # Try to contract candidate arcs
            for arc in candidate_arcs:
                # Check if an identical arc has already been contracted
                try:
                    start, end = arc.split(', ')
                    pair = (start, end)
                    if pair in contracted_arc_pairs:
                        continue
                        
                    can_contract, failure_reason = self.can_contract(arc, current_superset)
                    if can_contract:
                        # Get r-id for the arc
                        r_id = self.get_rid_from_arc(arc)
                        
                        # Contract the arc
                        self.successfully_contracted_arcs.add(arc)
                        contracted_in_iteration.add(arc)
                        contracted_arc_pairs.add(pair)
                        
                        # Store the successful contraction with r-id
                        self.successful_contractions_with_rid.append({
                            'arc': arc,
                            'r-id': r_id
                        })
                        
                        # Remove all instances of this arc from unreached_arcs
                        for duplicate_arc in self.arc_pairs.get(pair, []):
                            self.unreached_arcs.discard(duplicate_arc)
                            # Also remove from failed contractions if present
                            self.failed_contractions.discard(duplicate_arc)
                        
                        # Update the dummy vertex
                        dummy_vertex += end
                        
                        # Add end vertex to reached vertices
                        reached_vertices.add(end)

                        # Update superset with c-attributes of outgoing arcs
                        for outgoing_arc in self.get_outgoing_arcs(end):
                            c_attr = outgoing_arc.get('c-attribute', '0')
                            if c_attr not in current_superset:
                                current_superset.add(c_attr)
                                superset_updated = True
                        
                        # Always mark that we've made progress
                        superset_updated = True
                        
                        # Add to the contracted path
                        self.contracted_path.append(arc)
                    else:
                        # Get r-id for the arc
                        r_id = self.get_rid_from_arc(arc)
                        
                        # Add to failed contractions
                        self.failed_contractions.add(arc)
                        
                        # Store the failed contraction with r-id and failure reason
                        self.failed_contractions_with_rid.append({
                            'arc': arc,
                            'r-id': r_id,
                            'failure_reason': failure_reason
                        })
                        
                        # logger.info(f"Failed to contract arc {arc} with r-id {r_id}. Reason: {failure_reason}")
                except ValueError:
                    print(f"Invalid arc format: {arc}")
            
            # If no contractions happened in this iteration but the superset was updated,
            # retry all failed contractions
            if not contracted_in_iteration and superset_updated:
                retry_candidates = list(self.failed_contractions)
                
                # Clear failed contractions before retrying
                self.failed_contractions = set()
                self.failed_contractions_with_rid = []
                
                retry_success = False
                for arc in retry_candidates:
                    try:
                        start, end = arc.split(', ')
                        pair = (start, end)
                        
                        # Skip if already contracted
                        if pair in contracted_arc_pairs:
                            continue
                            
                        can_contract, failure_reason = self.can_contract(arc, current_superset)
                        if can_contract:
                            # Get r-id for the arc
                            r_id = self.get_rid_from_arc(arc)
                            
                            # Contract the arc
                            self.successfully_contracted_arcs.add(arc)
                            contracted_in_iteration.add(arc)
                            contracted_arc_pairs.add(pair)
                            
                            # Store the successful contraction with r-id
                            self.successful_contractions_with_rid.append({
                                'arc': arc,
                                'r-id': r_id
                            })
                            
                            # Remove all instances of this arc
                            for duplicate_arc in self.arc_pairs.get(pair, []):
                                self.unreached_arcs.discard(duplicate_arc)
                            
                            # Update the dummy vertex
                            dummy_vertex += end
                            
                            # Add end vertex to reached vertices
                            reached_vertices.add(end)

                            # Update superset with c-attributes of outgoing arcs
                            for outgoing_arc in self.get_outgoing_arcs(end):
                                c_attr = outgoing_arc.get('c-attribute', '0')
                                if c_attr not in current_superset:
                                    current_superset.add(c_attr)
                                    superset_updated = True
                            
                            # Always mark that we've made progress
                            superset_updated = True
                            retry_success = True
                            
                            # Add to the contracted path
                            self.contracted_path.append(arc)
                            
                            # logger.info(f"Successfully contracted arc {arc} with r-id {r_id} after retry")
                        else:
                            # Get r-id for the arc
                            r_id = self.get_rid_from_arc(arc)
                            
                            # Add back to failed contractions
                            self.failed_contractions.add(arc)
                            
                            # Store the failed contraction with r-id and failure reason
                            self.failed_contractions_with_rid.append({
                                'arc': arc,
                                'r-id': r_id,
                                'failure_reason': failure_reason
                            })
                            
                            # logger.info(f"Failed to contract arc {arc} with r-id {r_id} after retry. Reason: {failure_reason}")
                    except ValueError:
                        print(f"Invalid arc format: {arc}")
                
                # If no retries were successful, break the loop
                if not retry_success:
                    # logger.warning("No successful contractions after retrying. Breaking loop.")
                    break
            
            # If no contractions happened and no superset update, break the loop
            if not contracted_in_iteration and not superset_updated:
                # logger.warning("No contractions and no superset update. Breaking loop.")
                break

        # Create a deduplicated contracted path (without r-id)
        unique_contracted_path = []
        seen_arc_pairs = set()
        for arc in self.contracted_path:
            start, end = arc.split(', ')
            pair = (start, end)
            if pair not in seen_arc_pairs:
                unique_contracted_path.append(arc)
                seen_arc_pairs.add(pair)
        
        # Replace the contracted path with the deduplicated version
        self.contracted_path = unique_contracted_path
        
        # Deduplicate successful and failed contractions with r-id by arc
        unique_successful = []
        unique_failed = []
        seen_success_arcs = set()
        seen_failed_arcs = set()
        
        for item in self.successful_contractions_with_rid:
            if item['arc'] not in seen_success_arcs:
                unique_successful.append(item)
                seen_success_arcs.add(item['arc'])
                
        for item in self.failed_contractions_with_rid:
            if item['arc'] not in seen_failed_arcs:
                unique_failed.append(item)
                seen_failed_arcs.add(item['arc'])
        
        self.successful_contractions_with_rid = unique_successful
        self.failed_contractions_with_rid = unique_failed
        
        # logger.info(f"Final contracted path: {len(self.contracted_path)} arcs")
        # logger.info(f"Successful contractions with r-id: {len(self.successful_contractions_with_rid)}")
        if self.failed_contractions:
            print(f"Failed contractions: {len(self.failed_contractions_with_rid)}")
            # Log detailed information about failed contractions
            for failed in self.failed_contractions_with_rid:
                print(f" - Arc: {failed['arc']}, R-ID: {failed['r-id']}, Reason: {failed.get('failure_reason', 'Unknown')}")
    
    def get_contractions_with_rid(self):
        """
        Returns the successful and failed contractions with their associated r-ids.
        
        Returns:
            tuple: A tuple containing two lists:
                - successful_contractions_with_rid: List of successful contractions with r-id
                - failed_contractions_with_rid: List of failed contractions with r-id
        """
        return self.successful_contractions_with_rid, self.failed_contractions_with_rid
    
    def get_list_contraction_arcs(self):
        """
        Returns just the 'arc' values from successful and failed contractions.
        
        Returns:
            tuple: A tuple containing two lists:
                - successful_arcs: List of arc strings from successful contractions
                - failed_arcs: List of arc strings from failed contractions
        """
        successful_arcs = [item['arc'] for item in self.successful_contractions_with_rid]
        failed_arcs = [item['arc'] for item in self.failed_contractions_with_rid]
        
        return successful_arcs, failed_arcs
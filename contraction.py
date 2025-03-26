import utils
import logging
import copy
from itertools import chain

class ContractionPath:
    def __init__(self, R, violations):
        """
        Initializes the contraction path algorithm.

        Parameters:
            - R (list): The RDLT structure containing arcs.
            - violations (list): List of violating arcs.
        """
        self.R = R
        
        # Convert violations to a list of arc strings if they are dictionaries
        self.violations = [v['arc'] if isinstance(v, dict) else v for v in violations]
        
        self.graph = utils.build_graph(R)
        self.contraction_paths = {}  # Store the contraction paths for each violation
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
                
        # Create contraction paths for each violation
        self.create_contraction_paths_for_violations()
        
        # Print detailed contraction paths
        self.print_contraction_paths()

    def get_outgoing_arcs(self, vertex, R):
        """
        Gets all outgoing arcs and their c-attributes for a given vertex.
        """
        outgoing_arcs = []
        for arc_data in R:
            start, end = arc_data['arc'].split(', ')
            if start == vertex:
                outgoing_arcs.append(arc_data)
        return outgoing_arcs

    def can_contract(self, arc, superset, R):
        """
        Determines if an arc can be contracted by checking its incoming arcs.
        Returns a tuple (can_contract, reason) where reason is None if can_contract is True,
        otherwise it contains the reason for failure.
        """
        try:
            start, end = arc.split(', ')
        except ValueError:
            return False, "Invalid arc format"

        arc_data = next((a for a in R if a['arc'] == arc), None)
        if not arc_data:
            return False, "Arc not found in RDLT"

        # Get all incoming arcs to the end vertex
        incoming_arcs = [a for a in R if a['arc'].endswith(f", {end}")]

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
                                      next((a for a in R if a['arc'] == arc), {}).get('c-attribute', '0') == c_attribute])
            
            return False, f"Conflicting with violating arc: {', '.join(violating_arcs)}"

        return True, None

    def get_rid_from_arc(self, arc_str, R):
        """
        Gets the r-id for a given arc string.
        """
        for arc_data in R:
            if arc_data['arc'] == arc_str:
                return arc_data.get('r-id')
        return None

    def contract_paths_for_violation(self, violation_arc, R_copy):
        """
        Contracts paths from source to sink for a specific violation.
        Returns a list of contracted arcs and a dictionary of unsuccessful contractions.
        """
        source, sink = utils.get_source_and_target_vertices(R_copy)
        
        # Initialize superset with c-attributes of source's outgoing arcs
        current_superset = {'0'}
        source_outgoing_arcs = self.get_outgoing_arcs(source, R_copy)
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
        
        # Track contracted arcs
        contracted_path = []
        successful_contractions = []
        failed_contractions = []
        
        # Unreached arcs
        unreached_arcs = set(arc['arc'] for arc in R_copy)
        
        # Iterate until all arcs are processed or no further contractions are possible
        while reached_vertices and superset_updated:
            contracted_in_iteration = set()
            
            # Reset the superset_updated flag at the start of each iteration
            superset_updated = False

            # Find all outgoing arcs of reached vertices
            candidate_arcs = []
            for vertex in reached_vertices:
                for arc_data in self.get_outgoing_arcs(vertex, R_copy):
                    arc_str = arc_data['arc']
                    try:
                        start, end = arc_str.split(', ')
                        pair = (start, end)
                        # Only consider if not already contracted
                        if pair not in contracted_arc_pairs and arc_str in unreached_arcs:
                            candidate_arcs.append(arc_str)
                    except ValueError:
                        print(f"Invalid arc format: {arc_str}")
                    
            if not candidate_arcs:
                break

            # Try to contract candidate arcs
            for arc in candidate_arcs:
                # Check if an identical arc has already been contracted
                try:
                    start, end = arc.split(', ')
                    pair = (start, end)
                    if pair in contracted_arc_pairs:
                        continue
                        
                    can_contract, failure_reason = self.can_contract(arc, current_superset, R_copy)
                    if can_contract:
                        # Get r-id for the arc
                        r_id = self.get_rid_from_arc(arc, R_copy)
                        
                        # Contract the arc
                        contracted_in_iteration.add(arc)
                        contracted_arc_pairs.add(pair)
                        
                        # Store the successful contraction with r-id
                        successful_contractions.append({
                            'arc': arc,
                            'r-id': r_id
                        })
                        
                        # Remove all instances of this arc from unreached_arcs
                        for duplicate_arc in self.arc_pairs.get(pair, []):
                            unreached_arcs.discard(duplicate_arc)
                        
                        # Update the dummy vertex
                        dummy_vertex += end
                        
                        # Add end vertex to reached vertices
                        reached_vertices.add(end)

                        # Update superset with c-attributes of outgoing arcs
                        for outgoing_arc in self.get_outgoing_arcs(end, R_copy):
                            c_attr = outgoing_arc.get('c-attribute', '0')
                            if c_attr not in current_superset:
                                current_superset.add(c_attr)
                                superset_updated = True
                        
                        # Always mark that we've made progress
                        superset_updated = True
                        
                        # Add to the contracted path
                        contracted_path.append(arc)
                    else:
                        # Get r-id for the arc
                        r_id = self.get_rid_from_arc(arc, R_copy)
                        
                        # Store the failed contraction with r-id and failure reason
                        failed_contractions.append({
                            'arc': arc,
                            'r-id': r_id,
                            'failure_reason': failure_reason
                        })
                except ValueError:
                    print(f"Invalid arc format: {arc}")
            
            # Retry failed contractions if superset was updated
            if not contracted_in_iteration and superset_updated:
                retry_candidates = [fc['arc'] for fc in failed_contractions]
                
                # Clear failed contractions before retrying
                failed_contractions = []
                
                retry_success = False
                for arc in retry_candidates:
                    try:
                        start, end = arc.split(', ')
                        pair = (start, end)
                        
                        # Skip if already contracted
                        if pair in contracted_arc_pairs:
                            continue
                            
                        can_contract, failure_reason = self.can_contract(arc, current_superset, R_copy)
                        if can_contract:
                            # Get r-id for the arc
                            r_id = self.get_rid_from_arc(arc, R_copy)
                            
                            # Contract the arc
                            contracted_in_iteration.add(arc)
                            contracted_arc_pairs.add(pair)
                            
                            # Store the successful contraction with r-id
                            successful_contractions.append({
                                'arc': arc,
                                'r-id': r_id
                            })
                            
                            # Remove all instances of this arc
                            for duplicate_arc in self.arc_pairs.get(pair, []):
                                unreached_arcs.discard(duplicate_arc)
                            
                            # Update the dummy vertex
                            dummy_vertex += end
                            
                            # Add end vertex to reached vertices
                            reached_vertices.add(end)

                            # Update superset with c-attributes of outgoing arcs
                            for outgoing_arc in self.get_outgoing_arcs(end, R_copy):
                                c_attr = outgoing_arc.get('c-attribute', '0')
                                if c_attr not in current_superset:
                                    current_superset.add(c_attr)
                                    superset_updated = True
                            
                            # Always mark that we've made progress
                            superset_updated = True
                            retry_success = True
                            
                            # Add to the contracted path
                            contracted_path.append(arc)
                        else:
                            # Get r-id for the arc
                            r_id = self.get_rid_from_arc(arc, R_copy)
                            
                            # Store the failed contraction with r-id and failure reason
                            failed_contractions.append({
                                'arc': arc,
                                'r-id': r_id,
                                'failure_reason': failure_reason
                            })
                    except ValueError:
                        print(f"Invalid arc format: {arc}")
                
                # If no retries were successful, break the loop
                if not retry_success:
                    break
            
            # If no contractions happened and no superset update, break the loop
            if not contracted_in_iteration and not superset_updated:
                break

        # Create a deduplicated contracted path
        unique_contracted_path = []
        seen_arc_pairs = set()
        for arc in contracted_path:
            start, end = arc.split(', ')
            pair = (start, end)
            if pair not in seen_arc_pairs:
                unique_contracted_path.append(arc)
                seen_arc_pairs.add(pair)
        
        # Deduplicate successful and failed contractions
        unique_successful = []
        unique_failed = []
        seen_success_arcs = set()
        seen_failed_arcs = set()
        
        for item in successful_contractions:
            if item['arc'] not in seen_success_arcs:
                unique_successful.append(item)
                seen_success_arcs.add(item['arc'])
                
        for item in failed_contractions:
            if item['arc'] not in seen_failed_arcs:
                unique_failed.append(item)
                seen_failed_arcs.add(item['arc'])
        
        return unique_contracted_path, unique_successful, unique_failed

    def print_contraction_paths(self):
        """
        Prints detailed information about contraction paths for each violating arc.
        """
        print("\n--- Contraction Paths for Violations ---")
        for violation_arc, path_data in self.contraction_paths.items():
            print(f"\nViolation Arc: {violation_arc}")
            
            # Determine unreached arcs
            all_arcs = {arc_data['arc'] for arc_data in self.R}
            contracted_arcs = set(path_data['contracted_path'])
            failed_arcs = {failed['arc'] for failed in path_data['failed_contractions']}
            
            unreached_arcs = all_arcs - contracted_arcs - failed_arcs
            
            # Conditionally print sections
            if path_data['contracted_path']:
                print("Contracted Path:")
                contracted_tuples = [tuple(arc.split(', ')) for arc in path_data['contracted_path']]
                print(contracted_tuples)
            
            if path_data['successful_contractions']:
                print("\nSuccessful Contractions:")
                successful_arcs = [contract['arc'] for contract in path_data['successful_contractions']]
                print(successful_arcs)
            
            if path_data['failed_contractions']:
                print("\nFailed Contractions:")
                failed_arcs = [failed['arc'] for failed in path_data['failed_contractions']]
                print(failed_arcs)
            
            if unreached_arcs:
                print("\nUnreached Arcs:")
                print(list(unreached_arcs))

    def create_contraction_paths_for_violations(self):
        """
        Creates contraction paths for each violation.
        """
        for violation_arc in self.violations:
            # Create a fresh copy of R for each violation to ensure independent processing
            R_copy = copy.deepcopy(self.R)
            
            contracted_path, successful_contractions, failed_contractions = self.contract_paths_for_violation(violation_arc, R_copy)
            
            self.contraction_paths[violation_arc] = {
                'contracted_path': contracted_path,
                'successful_contractions': successful_contractions,
                'failed_contractions': failed_contractions
            }
            
    def get_contraction_paths(self):
        """
        Returns the contraction paths for each violation and a consolidated list of failed contractions.
        
        Returns:
            tuple: A tuple containing:
            - dict: A dictionary with violations as keys and contraction paths as values
            - list: A consolidated list of all failed contractions across all violations
        """
        # Consolidate failed contractions into a single list
        all_failed_contractions = []
        for path_data in self.contraction_paths.values():
            all_failed_contractions.extend(path_data['failed_contractions'])
        
        return self.contraction_paths, all_failed_contractions
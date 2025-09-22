"""
Enhanced GXW Parser - for PLC Flowchart Project

Extends GXWParser to analyze control flow within PLC ladder logic.
Identifies jumps, calls, and program ends to build a structural representation
of the program, which is essential for generating a flowchart.
"""

from typing import Dict, List, Any, Optional
import logging

# Assuming gxw_parser is in the same directory
from .gxw_parser import GXWParser, LadderRung, LadderInstruction

logger = logging.getLogger(__name__)

class EnhancedGXWParser(GXWParser):
    """
    An enhanced parser for GX Works2 files that inherits from GXWParser
    and adds capabilities to analyze the program's control flow, such as
    conditional jumps (CJ), subroutine calls (CALL), and program ends.

    This class is designed to produce a structured analysis of the logic flow,
    making it suitable for visualization as a flowchart.
    """

    def __init__(self):
        """
        Initializes the EnhancedGXWParser.
        Extends the instruction map from the parent class with control flow instructions.
        """
        super().__init__()
        
        # New instructions for control flow analysis
        self.control_instructions = {
            'CJ': 'conditional_jump',
            'CALL': 'subroutine_call',
            'END': 'program_end',
            'FEND': 'main_end',
            # Pointer for CJ and CALL targets
            'P': 'pointer_destination',
            'I': 'interrupt_handler'
        }
        
        # Extend the original instruction map for a unified lookup
        # Note: Actual opcodes for these are typically different from the basic ones.
        # This is a conceptual extension. The parsing logic will need to handle them.
        # For now, we'll rely on string matching from the parsed output.
        
    def parse(self, filepath: str) -> Dict[str, Any]:
        """
        Parses a .gxw file, extracts ladder logic, and then analyzes
        the control flow and branches.

        Args:
            filepath: The absolute path to the .gxw file.

        Returns:
            A dictionary containing the parsed project data, including
            the newly added control flow analysis.
        """
        # First, get the basic parsed data from the parent parser
        parsed_data = super().parse(filepath)

        if 'ladder_rungs' in parsed_data and parsed_data['ladder_rungs']:
            logger.info("Performing enhanced analysis: control flow and branches.")
            
            # 1. Extract high-level control flow nodes
            control_flow_nodes = self.extract_control_flow(parsed_data['ladder_rungs'])
            parsed_data['control_flow'] = control_flow_nodes
            
            # 2. Analyze conditional branches (jumps)
            branches = self.analyze_branches(parsed_data['ladder_rungs'])
            parsed_data['branches'] = branches
        else:
            logger.warning("No ladder rungs found to analyze for control flow.")
            parsed_data['control_flow'] = []
            parsed_data['branches'] = []
            
        return parsed_data

    def extract_control_flow(self, ladder_rungs: List[Dict]) -> List[Dict]:
        """
        Extracts control flow nodes (like CJ, CALL, END) from a list of ladder rungs.

        This method iterates through the rungs and identifies instructions that
        dictate the program's execution path.

        Args:
            ladder_rungs: A list of dictionaries, where each represents a rung
                          of the ladder logic, as parsed by the parent class.

        Returns:
            A list of dictionaries, each representing a control flow node with
            details like type, target, and source line number.
        """
        flow_nodes = []
        for i, rung in enumerate(ladder_rungs):
            # The parent parser's output might be a dict or a dataclass, handle both
            instruction = rung.get('instruction', '').upper()
            device = rung.get('device', '')

            node = None
            if instruction in self.control_instructions:
                node = {
                    'rung_index': i,
                    'rung_number': rung.get('rung_number'),
                    'type': self.control_instructions[instruction],
                    'target': device,
                    'comment': rung.get('comment', '')
                }
            # Also check if the device itself is a pointer (destination)
            elif device.upper().startswith(tuple(self.control_instructions.keys())):
                 for prefix, type in self.control_instructions.items():
                     if device.upper().startswith(prefix):
                        node = {
                            'rung_index': i,
                            'rung_number': rung.get('rung_number'),
                            'type': type,
                            'target': device,
                            'comment': rung.get('comment', '')
                        }
                        break
            
            if node:
                flow_nodes.append(node)
                
        logger.info(f"Extracted {len(flow_nodes)} control flow nodes.")
        return flow_nodes

    def analyze_branches(self, rungs: List[Dict]) -> List[Dict]:
        """
        Analyzes conditional branches (jumps) within the ladder logic.

        It specifically looks for 'CJ' (Conditional Jump) instructions and maps
        them to their corresponding 'P' (Pointer) destinations.

        Args:
            rungs: A list of dictionaries representing the ladder rungs.

        Returns:
            A list of dictionaries, each detailing a branch with its source,
            target, and the conditions leading to the jump.
        """
        branches = []
        
        # Create a map of pointer names to their rung indices for quick lookup
        pointer_map = {
            rung.get('device'): rung.get('rung_number')
            for rung in rungs if rung.get('device', '').upper().startswith('P')
        }

        for i, rung in enumerate(rungs):
            instruction = rung.get('instruction', '').upper()
            if instruction == 'CJ':
                target_pointer = rung.get('device', '')
                branch_info = {
                    'source_rung': rung.get('rung_number'),
                    'target_pointer': target_pointer,
                    'target_rung': pointer_map.get(target_pointer, 'Unknown'),
                    'condition_rungs': self._get_conditions_for_rung(rungs, i),
                    'comment': rung.get('comment', '')
                }
                branches.append(branch_info)
        
        logger.info(f"Analyzed {len(branches)} conditional branches.")
        return branches

    def _get_conditions_for_rung(self, rungs: List[Dict], start_index: int) -> List[Dict]:
        """
        Helper function to trace back and find the logical conditions
        that lead to a specific instruction (like a CJ or OUT).
        
        This is a simplified implementation that collects rungs backwards until
        it hits an 'LD' (Load) or another output instruction.

        Args:
            rungs: The full list of ladder rungs.
            start_index: The index of the rung to start tracing back from.

        Returns:
            A list of rungs that form the condition for the instruction at start_index.
        """
        conditions = []
        # Include the instruction itself
        current_rung_num = rungs[start_index].get('rung_number')
        
        # Iterate backwards from the rung just before the start_index
        for i in range(start_index - 1, -1, -1):
            rung = rungs[i]
            # Stop if we hit a rung from a different network/rung number
            if rung.get('rung_number') != current_rung_num:
                break
            
            instruction = rung.get('instruction', '').upper()
            conditions.insert(0, rung) # Prepend to keep order
            
            # Stop tracing if we hit the start of a logic block (LD)
            if instruction.startswith('LD'):
                break
        
        return conditions


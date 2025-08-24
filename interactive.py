#!/usr/bin/env python3
"""
Interactive selection module.

This module provides interactive terminal-based selection
for regions and other options using rich library.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class Region:
    """Region data structure."""
    code: str
    name: str


class PresetManager:
    """Manage region presets from configuration."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize preset manager with configuration."""
        self.config = config
        self.presets = config.get('region_presets', {})
    
    def list_presets(self) -> List[str]:
        """Get list of available preset names."""
        return list(self.presets.keys())
    
    def get_preset_regions(self, preset_name: str) -> List[str]:
        """Get list of region codes for a specific preset."""
        if preset_name not in self.presets:
            raise ValueError(f"Preset '{preset_name}' not found. Available: {self.list_presets()}")
        return self.presets[preset_name]
    
    def validate_preset(self, preset_name: str, available_regions: List[str]) -> List[str]:
        """Validate preset and return only existing regions."""
        preset_regions = self.get_preset_regions(preset_name)
        valid_regions = [r for r in preset_regions if r in available_regions]
        invalid_regions = [r for r in preset_regions if r not in available_regions]
        
        if invalid_regions:
            print(f"Warning: Invalid regions in preset '{preset_name}': {invalid_regions}")
        
        return valid_regions


class RegionSelector:
    """Interactive region selection using terminal UI."""
    
    def __init__(self, regions: List[Dict[str, str]]):
        """Initialize selector with list of regions."""
        self.regions = [Region(r['code'], r['name']) for r in regions]
        self.selected_indices = set()
        self.cursor_position = 0
        self.console = Console() if RICH_AVAILABLE else None
    
    def _check_terminal_support(self) -> bool:
        """Check if terminal supports interactive mode."""
        if not RICH_AVAILABLE:
            return False
        
        # Check if we're in a terminal
        if not sys.stdin.isatty():
            return False
        
        # Check terminal type
        term = os.environ.get('TERM', '')
        if not term or term == 'dumb':
            return False
        
        return True
    
    def _draw_checkbox_list(self) -> str:
        """Draw the current state of checkbox list."""
        if not self.console:
            return "Interactive mode not available"
        
        # Create table for checkbox list
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Checkbox", width=3)
        table.add_column("Region", width=50)
        
        for i, region in enumerate(self.regions):
            # Checkbox symbol
            checkbox = "☒" if i in self.selected_indices else "☐"
            
            # Cursor indicator
            cursor = "▶" if i == self.cursor_position else " "
            
            # Region name with cursor
            region_text = f"{cursor} {region.name}"
            
            # Highlight selected regions
            if i in self.selected_indices:
                region_text = f"[bold green]{region_text}[/bold green]"
            
            table.add_row(checkbox, region_text)
        
        # Create panel with controls
        controls = "[Space] Toggle  [Enter] Confirm  [q] Quit  [a] Select All  [n] Select None"
        panel = Panel(table, title="Select Regions", subtitle=controls)
        
        return panel
    
    def _handle_key_input(self, key: str) -> Optional[List[str]]:
        """Handle keyboard input and return selected regions or None to continue."""
        if key.lower() == 'q':
            return []  # Exit without selection
        
        elif key == ' ':  # Space
            if self.cursor_position in self.selected_indices:
                self.selected_indices.remove(self.cursor_position)
            else:
                self.selected_indices.add(self.cursor_position)
        
        elif key.lower() == 'a':  # Select all
            self.selected_indices = set(range(len(self.regions)))
        
        elif key.lower() == 'n':  # Select none
            self.selected_indices.clear()
        
        elif key == '\x1b[A':  # Up arrow
            self.cursor_position = max(0, self.cursor_position - 1)
        
        elif key == '\x1b[B':  # Down arrow
            self.cursor_position = min(len(self.regions) - 1, self.cursor_position + 1)
        
        elif key == '\r':  # Enter
            return [self.regions[i].code for i in self.selected_indices]
        
        return None  # Continue selection
    
    def select_regions_interactive(self, pre_selected: List[str] = None) -> List[str]:
        """Show interactive checkbox list for region selection."""
        if not self._check_terminal_support():
            print("Interactive mode not available. Please use command line options.")
            return []
        
        # Pre-select regions if provided
        if pre_selected:
            for i, region in enumerate(self.regions):
                if region.code in pre_selected:
                    self.selected_indices.add(i)
        
        try:
            while True:
                # Clear screen and show current state
                self.console.clear()
                self.console.print(self._draw_checkbox_list())
                
                # Get user input
                key = self.console.input("")
                
                # Handle input
                result = self._handle_key_input(key)
                if result is not None:
                    return result
                    
        except KeyboardInterrupt:
            print("\nSelection cancelled.")
            return []
        except Exception as e:
            print(f"Error in interactive selection: {e}")
            return []
    
    def create_checkbox_list(self, selected: List[str] = None) -> List[str]:
        """Create checkbox list with pre-selected regions."""
        if selected is None:
            selected = []
        
        return self.select_regions_interactive(selected)


def select_regions_interactive(available_regions: List[Dict[str, str]], 
                             pre_selected: List[str] = None) -> List[str]:
    """Convenience function for interactive region selection."""
    selector = RegionSelector(available_regions)
    return selector.select_regions_interactive(pre_selected)


def create_checkbox_list(items: List[Dict[str, str]], selected: List[str] = None) -> List[str]:
    """Convenience function for creating checkbox list."""
    selector = RegionSelector(items)
    return selector.create_checkbox_list(selected)


def main():
    """Main function for interactive module."""
    print("Interactive Region Selection Module")
    
    # Test with sample data
    sample_regions = [
        {'code': 'moscow', 'name': 'Moscow'},
        {'code': 'spb', 'name': 'Saint Petersburg'},
        {'code': 'belgrade', 'name': 'Belgrade'},
        {'code': 'minsk', 'name': 'Minsk'}
    ]
    
    print("Available regions:")
    for region in sample_regions:
        print(f"  {region['code']}: {region['name']}")
    
    if RICH_AVAILABLE:
        print("\nRich library available - interactive mode supported")
    else:
        print("\nRich library not available - interactive mode disabled")


if __name__ == "__main__":
    main()


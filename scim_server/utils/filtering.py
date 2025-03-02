"""
Utilities for handling SCIM filtering operations.
"""

import re
from typing import Optional, Dict, Any, List, Union

class SCIMFilter:
    """
    Utility class for parsing and converting SCIM filters to Microsoft Graph API filters.
    """
    
    # SCIM filter operators and their Graph API equivalents
    operators = {
        'eq': 'eq',
        'ne': 'ne',
        'co': 'contains',
        'sw': 'startswith',
        'ew': 'endswith',
        'pr': 'ne null',
        'gt': 'gt',
        'ge': 'ge',
        'lt': 'lt',
        'le': 'le'
    }
    
    # SCIM to Graph API attribute mapping
    attribute_mapping = {
        'userName': 'userPrincipalName',
        'name.familyName': 'surname',
        'name.givenName': 'givenName',
        'displayName': 'displayName',
        'emails.value': 'mail',
        'active': 'accountEnabled',
        'id': 'id',
        'externalId': 'userPrincipalName',
        
        # Group mappings
        'displayName': 'displayName'
    }
    
    @staticmethod
    def parse_simple_filter(filter_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse a simple SCIM filter string (e.g., 'userName eq "john@example.com"')
        Returns a dictionary with attribute, operator, and value.
        """
        # Regex for SCIM filter format
        pattern = r'(\S+)\s+(\S+)\s+"?([^"]*)"?'
        match = re.match(pattern, filter_str)
        
        if not match:
            return None
            
        attribute, operator, value = match.groups()
        
        return {
            'attribute': attribute,
            'operator': operator,
            'value': value
        }
    
    @staticmethod
    def convert_to_graph_filter(scim_filter: Optional[str]) -> str:
        """
        Convert a SCIM filter string to a Microsoft Graph API filter string.
        """
        if not scim_filter:
            return ""
            
        # For now, we'll just handle simple filters
        parsed = SCIMFilter.parse_simple_filter(scim_filter)
        if not parsed:
            return ""
            
        attribute = parsed['attribute']
        operator = parsed['operator']
        value = parsed['value']
        
        # Map SCIM attribute to Graph API attribute
        graph_attribute = SCIMFilter.attribute_mapping.get(attribute, attribute)
        
        # Map SCIM operator to Graph API operator
        graph_operator = SCIMFilter.operators.get(operator)
        
        if not graph_operator:
            return ""
            
        # Special handling for 'pr' (present) operator
        if operator == 'pr':
            return f"{graph_attribute} ne null"
            
        # Handle Boolean values
        if value.lower() in ('true', 'false'):
            return f"{graph_attribute} {graph_operator} {value.lower()}"
            
        # Handle numeric values
        if value.isdigit():
            return f"{graph_attribute} {graph_operator} {value}"
            
        # Handle string values (needs single quotes in Graph API)
        return f"{graph_attribute} {graph_operator} '{value}'"

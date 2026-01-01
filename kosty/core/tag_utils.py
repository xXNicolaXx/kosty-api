"""Tag utilities for resource filtering"""

from typing import List, Dict, Any, Optional


def should_exclude_resource_by_tags(resource: Dict[str, Any], config_manager) -> bool:
    """Check if resource should be excluded based on tags
    
    Args:
        resource: Resource dict that may contain 'Tags' or 'tags' field
        config_manager: ConfigManager instance
    
    Returns:
        True if resource should be excluded, False otherwise
    """
    if not config_manager:
        return False
    
    tags = resource.get('Tags') or resource.get('tags') or []
    
    if not tags:
        return False
    
    return config_manager.should_exclude_by_tags(tags)


def get_resource_tags(resource: Dict[str, Any], resource_type: str = None) -> List[Dict[str, str]]:
    """Extract tags from resource in various formats
    
    Args:
        resource: Resource dict that may contain tags in various formats
        resource_type: Optional resource type (ec2, s3, rds, etc.) for type-specific handling
    
    Returns:
        List of tag dictionaries with 'Key' and 'Value' fields
    """
    tags = resource.get('Tags') or resource.get('tags') or resource.get('TagList') or []
    
    # Some services return tags as a list of dicts with different key names
    if tags and isinstance(tags, list) and len(tags) > 0:
        # Normalize tag format to have 'Key' and 'Value'
        normalized_tags = []
        for tag in tags:
            if isinstance(tag, dict):
                if 'Key' in tag and 'Value' in tag:
                    normalized_tags.append(tag)
                elif 'key' in tag and 'value' in tag:
                    normalized_tags.append({'Key': tag['key'], 'Value': tag['value']})
                elif 'Name' in tag and 'Value' in tag:
                    normalized_tags.append({'Key': tag['Name'], 'Value': tag['Value']})
        return normalized_tags if normalized_tags else tags
    
    return tags


def filter_resources_by_tag(resources: List[Dict[str, Any]], 
                            tag_key: str, 
                            tag_values: List[str] = None,
                            resource_type: str = None) -> List[Dict[str, Any]]:
    """Filter resources by specific tag key and optionally by tag values
    
    Args:
        resources: List of resources to filter
        tag_key: Tag key to filter by (e.g., 'Environment', 'Stage')
        tag_values: Optional list of tag values to match (e.g., ['prod', 'production'])
        resource_type: Optional resource type for type-specific tag extraction
    
    Returns:
        Filtered list of resources matching the tag criteria
    """
    filtered = []
    
    for resource in resources:
        tags = get_resource_tags(resource, resource_type)
        
        for tag in tags:
            if tag.get('Key') == tag_key:
                if tag_values is None:
                    # If no specific values provided, include any resource with this tag key
                    filtered.append(resource)
                    break
                elif tag.get('Value') in tag_values:
                    # Include resource if tag value matches
                    filtered.append(resource)
                    break
    
    return filtered


def get_tag_value(resource: Dict[str, Any], tag_key: str, resource_type: str = None) -> Optional[str]:
    """Get the value of a specific tag from a resource
    
    Args:
        resource: Resource dict
        tag_key: Tag key to look for
        resource_type: Optional resource type
    
    Returns:
        Tag value if found, None otherwise
    """
    tags = get_resource_tags(resource, resource_type)
    
    for tag in tags:
        if tag.get('Key') == tag_key:
            return tag.get('Value')
    
    return None


def has_environment_tag(resource: Dict[str, Any], 
                       environments: List[str] = None,
                       resource_type: str = None) -> bool:
    """Check if resource has an environment tag matching specified environments
    
    Common environment tag keys: Environment, Env, Stage, Tier
    Common values: prod, production, staging, stage, dev, development, test
    
    Args:
        resource: Resource dict
        environments: List of environment values to match (e.g., ['prod', 'production'])
        resource_type: Optional resource type
    
    Returns:
        True if resource has matching environment tag, False otherwise
    """
    if environments is None:
        environments = ['prod', 'production', 'staging', 'stage', 'dev', 'development', 'test']
    
    # Common environment tag keys
    env_keys = ['Environment', 'Env', 'Stage', 'Tier', 'environment', 'env', 'stage']
    
    tags = get_resource_tags(resource, resource_type)
    
    for tag in tags:
        tag_key = tag.get('Key', '')
        tag_value = tag.get('Value', '').lower()
        
        if tag_key in env_keys and tag_value in [e.lower() for e in environments]:
            return True
    
    return False

import json
import os
from typing import Dict, List, Set

def load_character_lists() -> Dict[str, Set[str]]:
    """Load saved character lists from file"""
    if os.path.exists('character_lists.json') and os.path.getsize('character_lists.json') > 0:
        with open('character_lists.json', 'r', encoding='utf-8') as f:
            lists_dict = json.load(f)
            # Convert lists to sets for efficient operations
            return {name: set(chars) for name, chars in lists_dict.items()}
    return {"Favorites": set()}  # Default empty favorites list

def save_character_lists(lists_dict: Dict[str, Set[str]]) -> None:
    """Save character lists to file"""
    # Convert sets to lists for JSON serialization
    json_dict = {name: list(chars) for name, chars in lists_dict.items()}
    with open('character_lists.json', 'w', encoding='utf-8') as f:
        json.dump(json_dict, f, ensure_ascii=False, indent=2)

def add_to_list(list_name: str, character: str) -> None:
    """Add a character to a specified list"""
    lists_dict = load_character_lists()
    if list_name not in lists_dict:
        lists_dict[list_name] = set()
    lists_dict[list_name].add(character)
    save_character_lists(lists_dict)

def remove_from_list(list_name: str, character: str) -> None:
    """Remove a character from a specified list"""
    lists_dict = load_character_lists()
    if list_name in lists_dict and character in lists_dict[list_name]:
        lists_dict[list_name].remove(character)
        save_character_lists(lists_dict)

def create_list(list_name: str) -> None:
    """Create a new character list"""
    lists_dict = load_character_lists()
    if list_name not in lists_dict:
        lists_dict[list_name] = set()
        save_character_lists(lists_dict)

def delete_list(list_name: str) -> None:
    """Delete a character list"""
    if list_name == "Favorites":  # Protect the Favorites list
        return
    lists_dict = load_character_lists()
    if list_name in lists_dict:
        del lists_dict[list_name]
        save_character_lists(lists_dict)

def get_characters_in_list(list_name: str) -> Set[str]:
    """Get all characters in a specified list"""
    lists_dict = load_character_lists()
    return lists_dict.get(list_name, set())

def get_all_lists() -> List[str]:
    """Get names of all available character lists"""
    lists_dict = load_character_lists()
    return list(lists_dict.keys()) 
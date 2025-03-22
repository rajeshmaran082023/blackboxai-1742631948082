"""
Module for handling data persistence of contacts using JSON storage.
"""
import json
import logging
from typing import List, Dict
from pathlib import Path

from config import CONTACTS_FILE
from contacts import Contact, ContactBook

logger = logging.getLogger(__name__)

def load_contacts() -> ContactBook:
    """
    Load contacts from the JSON storage file.
    
    Returns:
        ContactBook: A ContactBook instance containing the loaded contacts
    """
    try:
        file_path = Path(CONTACTS_FILE)
        if not file_path.exists():
            logger.info(f"Contacts file not found at {CONTACTS_FILE}. Starting with empty contact book.")
            return ContactBook()

        with open(file_path, 'r', encoding='utf-8') as f:
            contacts_data = json.load(f)
            
        if not isinstance(contacts_data, list):
            logger.error("Invalid contacts data format. Starting with empty contact book.")
            return ContactBook()
            
        contact_book = ContactBook.from_dict_list(contacts_data)
        logger.info(f"Successfully loaded {len(contact_book.contacts)} contacts from storage")
        return contact_book

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding contacts file: {e}")
        return ContactBook()
    except Exception as e:
        logger.error(f"Unexpected error loading contacts: {e}")
        return ContactBook()

def save_contacts(contact_book: ContactBook) -> bool:
    """
    Save contacts to the JSON storage file.
    
    Args:
        contact_book (ContactBook): The ContactBook instance to save
        
    Returns:
        bool: True if contacts were saved successfully, False otherwise
    """
    try:
        contacts_data = contact_book.to_dict_list()
        
        # Create directory if it doesn't exist
        file_path = Path(CONTACTS_FILE)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(contacts_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully saved {len(contacts_data)} contacts to storage")
        return True

    except Exception as e:
        logger.error(f"Error saving contacts: {e}")
        return False
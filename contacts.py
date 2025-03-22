"""
Module containing the Contact and ContactBook classes for managing contacts.
"""
import uuid
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class Contact:
    """Represents a single contact with personal information."""
    
    def __init__(self, name: str, phone: str, email: str, address: str, contact_id: str = None):
        """
        Initialize a new contact.
        
        Args:
            name (str): Contact's full name
            phone (str): Contact's phone number
            email (str): Contact's email address
            address (str): Contact's physical address
            contact_id (str, optional): Unique identifier for the contact
        """
        self.contact_id = contact_id or str(uuid.uuid4())
        self.name = name.strip()
        self.phone = phone.strip()
        self.email = email.strip()
        self.address = address.strip()

    def to_dict(self) -> Dict:
        """Convert contact to dictionary format for storage."""
        return {
            "contact_id": self.contact_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Contact':
        """Create a Contact instance from a dictionary."""
        return cls(
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            address=data["address"],
            contact_id=data["contact_id"]
        )

    def __repr__(self) -> str:
        return f"Contact(name='{self.name}', phone='{self.phone}', email='{self.email}')"

class ContactBook:
    """Manages a collection of contacts with CRUD operations."""

    def __init__(self):
        """Initialize an empty contact book."""
        self.contacts: List[Contact] = []

    def add_contact(self, contact: Contact) -> bool:
        """
        Add a new contact to the book.
        
        Args:
            contact (Contact): Contact instance to add
            
        Returns:
            bool: True if contact was added successfully, False otherwise
        """
        if not contact.name:
            logger.error("Cannot add contact: Name is required")
            return False
        
        self.contacts.append(contact)
        logger.info(f"Added new contact: {contact.name}")
        return True

    def update_contact(self, contact_id: str, updated_data: Dict) -> bool:
        """
        Update an existing contact's information.
        
        Args:
            contact_id (str): ID of the contact to update
            updated_data (Dict): Dictionary containing the updated fields
            
        Returns:
            bool: True if contact was updated successfully, False otherwise
        """
        for i, contact in enumerate(self.contacts):
            if contact.contact_id == contact_id:
                if not updated_data.get("name", contact.name).strip():
                    logger.error("Cannot update contact: Name is required")
                    return False
                
                updated_contact = Contact(
                    name=updated_data.get("name", contact.name),
                    phone=updated_data.get("phone", contact.phone),
                    email=updated_data.get("email", contact.email),
                    address=updated_data.get("address", contact.address),
                    contact_id=contact_id
                )
                self.contacts[i] = updated_contact
                logger.info(f"Updated contact: {updated_contact.name}")
                return True
        
        logger.error(f"Contact not found with ID: {contact_id}")
        return False

    def delete_contact(self, contact_id: str) -> bool:
        """
        Delete a contact from the book.
        
        Args:
            contact_id (str): ID of the contact to delete
            
        Returns:
            bool: True if contact was deleted successfully, False otherwise
        """
        for i, contact in enumerate(self.contacts):
            if contact.contact_id == contact_id:
                del self.contacts[i]
                logger.info(f"Deleted contact: {contact.name}")
                return True
        
        logger.error(f"Contact not found with ID: {contact_id}")
        return False

    def search_contacts(self, query: str) -> List[Contact]:
        """
        Search for contacts matching the query string.
        
        Args:
            query (str): Search query to match against contact fields
            
        Returns:
            List[Contact]: List of contacts matching the query
        """
        query = query.lower().strip()
        if not query:
            return self.contacts.copy()
        
        results = []
        for contact in self.contacts:
            if (query in contact.name.lower() or
                query in contact.phone.lower() or
                query in contact.email.lower() or
                query in contact.address.lower()):
                results.append(contact)
        
        return results

    def get_all_contacts(self) -> List[Contact]:
        """
        Get all contacts in the book.
        
        Returns:
            List[Contact]: List of all contacts
        """
        return self.contacts.copy()

    def to_dict_list(self) -> List[Dict]:
        """
        Convert all contacts to a list of dictionaries for storage.
        
        Returns:
            List[Dict]: List of contact dictionaries
        """
        return [contact.to_dict() for contact in self.contacts]

    @classmethod
    def from_dict_list(cls, data: List[Dict]) -> 'ContactBook':
        """
        Create a ContactBook instance from a list of contact dictionaries.
        
        Args:
            data (List[Dict]): List of contact dictionaries
            
        Returns:
            ContactBook: New ContactBook instance with loaded contacts
        """
        contact_book = cls()
        for contact_data in data:
            contact = Contact.from_dict(contact_data)
            contact_book.add_contact(contact)
        return contact_book
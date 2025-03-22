"""
Main entry point for the Contact Book application.
"""
import logging
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for

from config import LOG_LEVEL, LOG_FORMAT
from storage import load_contacts, save_contacts
from contacts import Contact

def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "contact_book.log")
        ]
    )

# Initialize Flask app
app = Flask(__name__)
contact_book = None

@app.route('/')
def index():
    """Render the main page."""
    contacts = contact_book.get_all_contacts()
    return render_template('index.html', contacts=contacts)

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """API endpoint to get contacts."""
    query = request.args.get('q', '').lower()
    contacts = contact_book.search_contacts(query)
    return jsonify([contact.to_dict() for contact in contacts])

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """API endpoint to add a new contact."""
    data = request.json
    contact = Contact(
        name=data.get('name', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        address=data.get('address', '')
    )
    
    if contact_book.add_contact(contact):
        save_contacts(contact_book)
        return jsonify({"success": True, "contact": contact.to_dict()})
    return jsonify({"success": False, "error": "Failed to add contact"}), 400

@app.route('/api/contacts/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """API endpoint to update a contact."""
    data = request.json
    if contact_book.update_contact(contact_id, data):
        save_contacts(contact_book)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Contact not found"}), 404

@app.route('/api/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """API endpoint to delete a contact."""
    if contact_book.delete_contact(contact_id):
        save_contacts(contact_book)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Contact not found"}), 404

def main():
    """Main application entry point."""
    global contact_book
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load contacts from storage
        logger.info("Starting Contact Book application")
        contact_book = load_contacts()
        
        # Create templates directory if it doesn't exist
        Path("templates").mkdir(exist_ok=True)
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=8000, debug=True)
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
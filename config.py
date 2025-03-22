"""
Configuration settings for the Contact Book application.
"""
import logging
import os

# File paths
CONTACTS_FILE = "contacts.json"

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# UI Configuration
WINDOW_TITLE = "Contact Book"
WINDOW_SIZE = "800x600"
PADDING = 10

# Colors and Styles
PRIMARY_COLOR = "#2196F3"  # Material Blue
SECONDARY_COLOR = "#757575"  # Material Gray
BG_COLOR = "#FFFFFF"  # White
TEXT_COLOR = "#212121"  # Dark Gray
ERROR_COLOR = "#F44336"  # Material Red

# Column settings for the contact list
COLUMNS = {
    "name": {"label": "Name", "width": 150},
    "phone": {"label": "Phone", "width": 120},
    "email": {"label": "Email", "width": 200},
    "address": {"label": "Address", "width": 250}
}
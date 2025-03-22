"""
Module for the graphical user interface of the Contact Book application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Optional, Dict, Callable

from contacts import Contact, ContactBook
from storage import save_contacts
from config import (
    WINDOW_TITLE, WINDOW_SIZE, PADDING,
    PRIMARY_COLOR, SECONDARY_COLOR, BG_COLOR, TEXT_COLOR,
    COLUMNS
)

logger = logging.getLogger(__name__)

class ContactForm(tk.Toplevel):
    """A form window for adding or editing contacts."""

    def __init__(
        self,
        parent: tk.Tk,
        contact: Optional[Contact] = None,
        on_submit: Callable = None
    ):
        """
        Initialize the contact form.

        Args:
            parent (tk.Tk): Parent window
            contact (Optional[Contact]): Contact to edit, or None for new contact
            on_submit (Callable): Callback function for form submission
        """
        super().__init__(parent)
        self.contact = contact
        self.on_submit = on_submit
        
        # Window setup
        self.title("Edit Contact" if contact else "Add Contact")
        self.geometry("400x350")
        self.resizable(False, False)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        self._load_contact_data()
        
        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """Create and arrange form widgets."""
        # Main frame
        main_frame = ttk.Frame(self, padding=PADDING)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Style
        style = ttk.Style()
        style.configure("Submit.TButton", background=PRIMARY_COLOR)

        # Form fields
        fields = [
            ("Name:", "name"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("Address:", "address")
        ]

        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            # Label
            ttk.Label(main_frame, text=label_text).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            
            # Entry field
            if field_name == "address":
                entry = tk.Text(main_frame, height=3, width=30)
                entry.grid(
                    row=i, column=1, sticky="ew", padx=5, pady=5
                )
            else:
                entry = ttk.Entry(main_frame, width=30)
                entry.grid(
                    row=i, column=1, sticky="ew", padx=5, pady=5
                )
            self.entries[field_name] = entry

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame,
            text="Submit",
            style="Submit.TButton",
            command=self._submit
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _load_contact_data(self):
        """Load existing contact data into the form if editing."""
        if self.contact:
            self.entries["name"].insert(0, self.contact.name)
            self.entries["phone"].insert(0, self.contact.phone)
            self.entries["email"].insert(0, self.contact.email)
            self.entries["address"].insert("1.0", self.contact.address)

    def _submit(self):
        """Handle form submission."""
        try:
            # Gather data
            data = {
                "name": self.entries["name"].get().strip(),
                "phone": self.entries["phone"].get().strip(),
                "email": self.entries["email"].get().strip(),
                "address": self.entries["address"].get("1.0", tk.END).strip()
            }

            # Validate
            if not data["name"]:
                messagebox.showerror("Error", "Name is required!")
                return

            # Create or update contact
            if self.contact:
                data["contact_id"] = self.contact.contact_id
                contact = Contact.from_dict(data)
            else:
                contact = Contact(**data)

            # Call submission callback
            if self.on_submit:
                self.on_submit(contact)
            
            self.destroy()

        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            messagebox.showerror("Error", "An error occurred while saving the contact.")

class ContactBookUI:
    """Main window of the Contact Book application."""

    def __init__(self, contact_book: ContactBook):
        """
        Initialize the main window.

        Args:
            contact_book (ContactBook): Instance of ContactBook to manage
        """
        self.contact_book = contact_book
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # Configure style
        self._setup_styles()
        
        # Create widgets
        self._create_widgets()
        
        # Populate contact list
        self._refresh_contacts()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=BG_COLOR,
            foreground=TEXT_COLOR,
            fieldbackground=BG_COLOR
        )
        style.configure(
            "Treeview.Heading",
            background=SECONDARY_COLOR,
            foreground=TEXT_COLOR
        )
        style.configure(
            "Action.TButton",
            background=PRIMARY_COLOR
        )

    def _create_widgets(self):
        """Create and arrange the main window widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=PADDING)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, PADDING))
        
        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._on_search())
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=40
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Action buttons
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(
            button_frame,
            text="Add Contact",
            style="Action.TButton",
            command=self._add_contact
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Edit Contact",
            command=self._edit_contact
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Delete Contact",
            command=self._delete_contact
        ).pack(side=tk.LEFT, padx=5)

        # Contact list
        self.tree = ttk.Treeview(
            main_frame,
            columns=list(COLUMNS.keys()),
            show="headings",
            selectmode="browse"
        )
        
        # Configure columns
        for key, config in COLUMNS.items():
            self.tree.heading(key, text=config["label"])
            self.tree.column(key, width=config["width"])

        # Add scrollbars
        vsb = ttk.Scrollbar(
            main_frame,
            orient="vertical",
            command=self.tree.yview
        )
        hsb = ttk.Scrollbar(
            main_frame,
            orient="horizontal",
            command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        # Grid scrollbars and tree
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        # Bind double-click to edit
        self.tree.bind("<Double-1>", lambda e: self._edit_contact())

    def _refresh_contacts(self, query: str = ""):
        """
        Refresh the contact list display.

        Args:
            query (str): Search query to filter contacts
        """
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get filtered contacts
        contacts = self.contact_book.search_contacts(query)

        # Add contacts to tree
        for contact in contacts:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    contact.name,
                    contact.phone,
                    contact.email,
                    contact.address
                ),
                tags=(contact.contact_id,)
            )

    def _on_search(self):
        """Handle search input changes."""
        query = self.search_var.get()
        self._refresh_contacts(query)

    def _get_selected_contact(self) -> Optional[Contact]:
        """Get the currently selected contact."""
        selection = self.tree.selection()
        if not selection:
            return None

        contact_id = self.tree.item(selection[0], "tags")[0]
        for contact in self.contact_book.contacts:
            if contact.contact_id == contact_id:
                return contact
        return None

    def _add_contact(self):
        """Open form to add a new contact."""
        ContactForm(self.root, on_submit=self._handle_contact_submit)

    def _edit_contact(self):
        """Open form to edit the selected contact."""
        contact = self._get_selected_contact()
        if not contact:
            messagebox.showwarning(
                "No Selection",
                "Please select a contact to edit."
            )
            return
        
        ContactForm(
            self.root,
            contact=contact,
            on_submit=self._handle_contact_submit
        )

    def _delete_contact(self):
        """Delete the selected contact."""
        contact = self._get_selected_contact()
        if not contact:
            messagebox.showwarning(
                "No Selection",
                "Please select a contact to delete."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {contact.name}?"
        ):
            self.contact_book.delete_contact(contact.contact_id)
            save_contacts(self.contact_book)
            self._refresh_contacts(self.search_var.get())

    def _handle_contact_submit(self, contact: Contact):
        """
        Handle contact form submission.

        Args:
            contact (Contact): The contact to add or update
        """
        # Add or update contact
        if any(c.contact_id == contact.contact_id for c in self.contact_book.contacts):
            self.contact_book.update_contact(
                contact.contact_id,
                contact.to_dict()
            )
        else:
            self.contact_book.add_contact(contact)

        # Save to storage
        save_contacts(self.contact_book)

        # Refresh display
        self._refresh_contacts(self.search_var.get())

    def _on_closing(self):
        """Handle window closing event."""
        save_contacts(self.contact_book)
        self.root.destroy()

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
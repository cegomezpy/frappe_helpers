"""
frappe_helpers.utils.constants
===============================
Constants used across the frappe_helpers app.
"""

FRAMEWORK_DOCTYPES = frozenset({
    # Schema
    "DocType", "DocField", "DocPerm", "DocType Link", "DocType Action",
    "DocType State", "Module Def", "Installed Applications",

    # Customization
    "Property Setter", "Custom Field", "Client Script", "Custom Script",
    "Server Script",

    # Users & Auth
    "User", "Role", "Has Role", "User Permission", "User Email",
    "User Social Login", "DefaultValue", "Session Default",

    # System config
    "System Settings", "Naming Series", "Global Defaults",

    # Desk / UI
    "Workspace", "Workspace Link", "Workspace Chart", "Workspace Shortcut",
    "Workspace Quick List", "Desktop Icon", "Number Card",
    "Dashboard", "Dashboard Chart", "Dashboard Chart Link",

    # Printing
    "Print Format", "Print Settings", "Letter Head",

    # Workflows
    "Workflow", "Workflow State", "Workflow Action Master", "Workflow Transition",

    # Email
    "Email Account", "Email Template", "Notification",
    "Email Unsubscribe", "Auto Email Report",

    # Logging / audit
    "Error Log", "Activity Log", "Access Log", "Patch Log",
    "Scheduled Job Log", "Scheduled Job Type",

    # Translation
    "Translation", "Language",

    # Attachments / tags
    "Tag", "Tag Link", "Document Share Key", "File",

    # Bulk ops
    "Bulk Update", "Data Import", "Data Export",

    # Communication
    "Comment", "Communication", "ToDo", "Note",
    "Communication Link", "Contact", "Address",

    # Reports
    "Report", "Prepared Report",

    # Web
    "Web Page", "Web Form", "Blog Post", "Blog Category",
})

SETUP_DOCTYPES = [
    # Core Company Setup
    "Company",
    "Currency",
    "Country",

    # Settings (Singles)
    "System Settings",
    "Website Settings",
    "Selling Settings",
    "Buying Settings",
    "Stock Settings",
    "Accounts Settings",
    "HR Settings",
    "Manufacturing Settings",
    "CRM Settings",

    # Basic Master Data
    "Fiscal Year",
    "Territory",
    "Customer Group",
    "Supplier Group",
    "Item Group",
    "Brand",
    "UOM",
    "Warehouse",

    # Chart of Accounts
    "Account",
    "Cost Center",
    "Mode of Payment",
    "Payment Terms Template",

    # Email & Communication
    "Email Domain",
    "Email Account",

    # User Configuration
    "User",
    "Role",
]

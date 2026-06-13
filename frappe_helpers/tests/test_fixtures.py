"""
frappe_helpers.tests.test_fixtures
===================================
Test fixtures and helpers for frappe_helpers tests.
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class FrappeHelpersTestCase(FrappeTestCase):
	"""Base test case with common setup for frappe_helpers tests."""

	@classmethod
	def setUpClass(cls):
		"""Set up test fixtures once for the entire test class."""
		super().setUpClass()
		cls.setup_test_doctypes()

	@classmethod
	def setup_test_doctypes(cls):
		"""Create test DocTypes if they don't exist."""
		if not frappe.db.exists("DocType", "Test Item Helper"):
			cls.create_test_item_doctype()

		if not frappe.db.exists("DocType", "Test Customer Helper"):
			cls.create_test_customer_doctype()

	@classmethod
	def create_test_item_doctype(cls):
		"""Create a test Item DocType with Link field."""
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Test Item Helper",
			"module": "Frappe Helpers",
			"custom": 1,
			"fields": [
				{
					"fieldname": "item_name",
					"fieldtype": "Data",
					"label": "Item Name",
					"reqd": 1,
				},
				{
					"fieldname": "item_group",
					"fieldtype": "Link",
					"label": "Item Group",
					"options": "Test Item Group Helper",
				},
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1}],
		})
		doc.insert(ignore_if_duplicate=True)
		frappe.db.commit()

	@classmethod
	def create_test_customer_doctype(cls):
		"""Create a test Customer DocType."""
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "Test Customer Helper",
			"module": "Frappe Helpers",
			"custom": 1,
			"fields": [
				{
					"fieldname": "customer_name",
					"fieldtype": "Data",
					"label": "Customer Name",
					"reqd": 1,
				},
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1}],
		})
		doc.insert(ignore_if_duplicate=True)
		frappe.db.commit()

	def create_test_record(self, doctype, data):
		"""Helper to create a test record."""
		data["doctype"] = doctype
		doc = frappe.get_doc(data)
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
		return doc

	def tearDown(self):
		"""Clean up after each test."""
		super().tearDown()
		frappe.db.rollback()

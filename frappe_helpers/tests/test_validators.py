"""
frappe_helpers.tests.test_validators
=====================================
Unit tests for validator utilities.
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from frappe_helpers.utils.constants import FRAMEWORK_DOCTYPES
from frappe_helpers.utils.validators import DocTypeValidator


class TestDocTypeValidator(FrappeTestCase):
	"""Test DocTypeValidator class."""

	def test_validate_existing_doctypes(self):
		"""Test validation of existing DocTypes."""
		validator = DocTypeValidator()
		doctypes = ["User", "DocType", "Role"]

		result = validator.validate_doctypes_exist(doctypes)

		self.assertEqual(len(result), 3)
		self.assertIn("User", result)
		self.assertIn("DocType", result)
		self.assertIn("Role", result)

	def test_validate_nonexistent_doctypes_raises_error(self):
		"""Test that nonexistent DocTypes raise ValidationError."""
		validator = DocTypeValidator()
		doctypes = ["NonExistentDocType123"]

		with self.assertRaises(frappe.ValidationError):
			validator.validate_doctypes_exist(doctypes)

	def test_validate_mixed_doctypes(self):
		"""Test validation with mix of existing and non-existing DocTypes."""
		validator = DocTypeValidator()
		doctypes = ["User", "NonExistentDocType456"]

		with self.assertRaises(frappe.ValidationError) as cm:
			validator.validate_doctypes_exist(doctypes)

		self.assertIn("NonExistentDocType456", str(cm.exception))

	def test_is_framework_doctype(self):
		"""Test framework DocType detection."""
		validator = DocTypeValidator()

		self.assertTrue(validator.is_framework_doctype("User"))
		self.assertTrue(validator.is_framework_doctype("Role"))
		self.assertTrue(validator.is_framework_doctype("DocType"))
		self.assertTrue(validator.is_framework_doctype("Error Log"))

		self.assertFalse(validator.is_framework_doctype("Item"))
		self.assertFalse(validator.is_framework_doctype("Customer"))

	def test_framework_doctypes_constant(self):
		"""Test that FRAMEWORK_DOCTYPES is a frozenset."""
		self.assertIsInstance(FRAMEWORK_DOCTYPES, frozenset)
		self.assertGreater(len(FRAMEWORK_DOCTYPES), 50)
		self.assertIn("User", FRAMEWORK_DOCTYPES)
		self.assertIn("Role", FRAMEWORK_DOCTYPES)
		self.assertIn("DocType", FRAMEWORK_DOCTYPES)

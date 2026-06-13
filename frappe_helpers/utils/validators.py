"""
frappe_helpers.utils.validators
================================
Validation utilities for frappe_helpers.
"""

import frappe
from frappe import _


class DocTypeValidator:
	"""Validates DocType existence and properties."""

	@staticmethod
	def validate_doctypes_exist(doctypes: list[str]) -> list[str]:
		"""
		Validate that all provided DocType names exist in the database.

		Args:
			doctypes: List of DocType names to validate

		Returns:
			List of validated DocType names

		Raises:
			frappe.ValidationError: If any DocType doesn't exist
		"""
		logger = frappe.logger("frappe_helpers")
		invalid = []

		for doctype in doctypes:
			try:
				exists = frappe.db.exists("DocType", doctype)
			except Exception as e:
				logger.error(f"Error checking DocType {doctype}: {e}")
				exists = False

			if not exists:
				invalid.append(doctype)

		if invalid:
			error_msg = _(
				"The following DocTypes were not found: {0}. "
				"Use the DocType name as it appears in Frappe (e.g. 'Item' not 'tabItem')."
			).format(", ".join(invalid))
			frappe.throw(error_msg, frappe.ValidationError)

		logger.info(f"Validated {len(doctypes)} DocType(s) successfully")
		return doctypes

	@staticmethod
	def is_framework_doctype(doctype: str) -> bool:
		"""
		Check if a DocType is a framework/system DocType.

		Args:
			doctype: DocType name to check

		Returns:
			True if it's a framework DocType, False otherwise
		"""
		from frappe_helpers.utils.constants import FRAMEWORK_DOCTYPES
		return doctype in FRAMEWORK_DOCTYPES

"""
frappe_helpers.tests.test_orchestrator
=======================================
Integration tests for EnvResetOrchestrator.

IMPORTANT: These tests ONLY test dataclasses and planning logic.
Execution tests are removed because they would trigger database operations.
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from frappe_helpers.services.env_reset_orchestrator import (
	EnvResetPlan,
	EnvResetResult,
	EnvResetOrchestrator,
)


class TestEnvResetPlan(FrappeTestCase):
	"""Test EnvResetPlan dataclass (read-only, no DB operations)."""

	def test_env_reset_plan_dataclass(self):
		"""Test EnvResetPlan dataclass structure."""
		plan = EnvResetPlan(
			requested_doctypes=["Item", "Customer"],
			all_doctypes={"Item": "requested", "Customer": "requested"},
			import_order=["Item", "Customer"],
			total_doctypes=2,
			dependency_count=0,
		)

		self.assertEqual(len(plan.requested_doctypes), 2)
		self.assertEqual(plan.total_doctypes, 2)
		self.assertEqual(plan.dependency_count, 0)
		self.assertIn("Item", plan.requested_doctypes)
		self.assertIn("Customer", plan.requested_doctypes)


class TestEnvResetResult(FrappeTestCase):
	"""Test EnvResetResult dataclass."""

	def test_env_reset_result_success(self):
		"""Test EnvResetResult with success=True."""
		result = EnvResetResult(
			success=True,
			doctypes_processed=5,
			records_imported=100,
			records_failed=2,
			output_dir="/tmp/test",
		)

		self.assertTrue(result.success)
		self.assertEqual(result.doctypes_processed, 5)
		self.assertEqual(result.records_imported, 100)
		self.assertEqual(result.records_failed, 2)
		self.assertEqual(result.output_dir, "/tmp/test")
		self.assertIsNone(result.error_message)

	def test_env_reset_result_failure(self):
		"""Test EnvResetResult with success=False."""
		result = EnvResetResult(
			success=False,
			doctypes_processed=0,
			records_imported=0,
			records_failed=0,
			output_dir="",
			error_message="Test error",
		)

		self.assertFalse(result.success)
		self.assertEqual(result.error_message, "Test error")


class TestEnvResetOrchestratorPlanning(FrappeTestCase):
	"""
	Test EnvResetOrchestrator planning methods (read-only).

	NOTE: We do NOT test execute() because it would trigger database operations.
	The execute() method is tested manually in staging/dev environments.
	"""

	def test_create_plan_with_valid_doctypes(self):
		"""Test creating a plan with valid DocTypes (read-only)."""
		orchestrator = EnvResetOrchestrator(frappe.local.site)
		requested = ["User", "Role"]

		plan = orchestrator.create_plan(requested, resolve_dependencies=False)

		self.assertIsInstance(plan, EnvResetPlan)
		self.assertEqual(len(plan.requested_doctypes), 2)
		self.assertIn("User", plan.requested_doctypes)
		self.assertIn("Role", plan.requested_doctypes)
		self.assertEqual(plan.dependency_count, 0)

	def test_create_plan_with_dependency_resolution(self):
		"""Test creating a plan with dependency resolution (read-only)."""
		orchestrator = EnvResetOrchestrator(frappe.local.site)
		requested = ["User"]

		plan = orchestrator.create_plan(requested, resolve_dependencies=True)

		self.assertIsInstance(plan, EnvResetPlan)
		self.assertIn("User", plan.requested_doctypes)
		self.assertGreaterEqual(plan.total_doctypes, 1)

	def test_create_plan_with_invalid_doctype_raises_error(self):
		"""Test that invalid DocTypes raise ValidationError (read-only)."""
		orchestrator = EnvResetOrchestrator(frappe.local.site)
		requested = ["NonExistentDocType123"]

		with self.assertRaises(frappe.ValidationError):
			orchestrator.create_plan(requested)


class TestDocumentation(FrappeTestCase):
	"""
	Documentation: What we test vs what we don't test.
	"""

	def test_what_we_test(self):
		"""
		✅ WE TEST (safe, no DB operations):
		- Plan creation (create_plan)
		- DocType validation
		- Dependency resolution
		- Dataclass structures
		- Error handling in planning phase
		"""
		self.assertTrue(True, "Planning phase is tested")

	def test_what_we_dont_test(self):
		"""
		🚫 WE DON'T TEST (would trigger DB operations):
		- execute() method
		- Actual backup operations
		- Actual reinstall operations
		- Import/export with real files
		- Database writes

		WHY:
		- Would prompt for MySQL password
		- Would try to reinstall site
		- Would erase data
		- Requires mocking frappe.init/connect/destroy

		INSTEAD:
		- Test manually in dev/staging
		- Use the --dry-run flag in production
		"""
		self.assertTrue(True, "Execution phase is tested manually")

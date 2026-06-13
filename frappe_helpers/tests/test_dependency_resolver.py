"""
frappe_helpers.tests.test_dependency_resolver
==============================================
Unit tests for dependency resolution.
"""

from frappe.tests.utils import FrappeTestCase

from frappe_helpers.services.dependency_resolver import DependencyResolver


class TestDependencyResolver(FrappeTestCase):
	"""Test DependencyResolver class."""

	def setUp(self):
		"""Set up test fixtures."""
		self.resolver = DependencyResolver()

	def test_get_schema_links_for_user(self):
		"""Test getting schema links for User DocType."""
		links = self.resolver.get_schema_links("User")

		self.assertIsInstance(links, set)

	def test_get_schema_links_excludes_framework_doctypes(self):
		"""Test that framework DocTypes are excluded from links."""
		links = self.resolver.get_schema_links("User")

		self.assertNotIn("Role", links)
		self.assertNotIn("User", links)

	def test_get_schema_links_for_nonexistent_doctype(self):
		"""Test that nonexistent DocTypes return empty set."""
		links = self.resolver.get_schema_links("NonExistentDocType999")

		self.assertEqual(links, set())

	def test_resolve_all_dependencies(self):
		"""Test resolving all dependencies from requested DocTypes."""
		requested = ["User"]

		result = self.resolver.resolve_all_dependencies(requested)

		self.assertIsInstance(result, dict)
		self.assertIn("User", result)
		self.assertEqual(result["User"], "requested")

		for doctype, dtype in result.items():
			self.assertIn(dtype, ["requested", "dependency"])

	def test_topological_sort_simple(self):
		"""Test topological sort with simple dependency chain."""
		doctypes_dict = {
			"User": "requested",
		}

		order = self.resolver.topological_sort(doctypes_dict)

		self.assertIsInstance(order, list)
		self.assertEqual(len(order), 1)
		self.assertIn("User", order)

	def test_topological_sort_preserves_all_doctypes(self):
		"""Test that topological sort includes all input DocTypes."""
		doctypes_dict = {
			"User": "requested",
			"Role": "dependency",
		}

		order = self.resolver.topological_sort(doctypes_dict)

		self.assertEqual(len(order), 2)
		self.assertIn("User", order)
		self.assertIn("Role", order)

	def test_get_dynamic_links_from_data_empty(self):
		"""Test dynamic link resolution with no dynamic links."""
		records = [{"name": "test", "doctype": "User"}]

		links = self.resolver.get_dynamic_links_from_data("User", records)

		self.assertIsInstance(links, dict)

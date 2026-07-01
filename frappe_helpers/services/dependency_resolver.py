"""
frappe_helpers.services.dependency_resolver
============================================
Service for resolving DocType dependencies.
"""

from collections import defaultdict, deque
from typing import Dict, List, Set

import frappe
from frappe_helpers.utils.constants import FRAMEWORK_DOCTYPES


class DependencyResolver:
	"""Resolves and manages DocType dependencies."""

	def __init__(self):
		self.logger = frappe.logger("frappe_helpers.dependency_resolver")

	def get_schema_links(self, doctype: str) -> Set[str]:
		"""
		Get all DocTypes that the given DocType references via schema.

		Scans Link, Table, and Table MultiSelect fields.
		Framework DocTypes are automatically excluded.

		Args:
			doctype: DocType name to analyze

		Returns:
			Set of linked DocType names
		"""
		try:
			meta = frappe.get_meta(doctype)
		except Exception as e:
			self.logger.error(f"Failed to get meta for {doctype}: {e}", exc_info=True)
			return set()

		linked = set()
		for field in meta.fields:
			if field.fieldtype in ("Link", "Table", "Table MultiSelect") and field.options:
				if field.options not in FRAMEWORK_DOCTYPES and field.options != doctype:
					linked.add(field.options)

		return linked

	def get_dynamic_links_from_data(self, doctype: str, records: List[dict]) -> Dict[str, Set[str]]:
		"""
		Scan record data to resolve Dynamic Link fields.

		Dynamic Links store a value whose DocType is specified in a sibling field.

		Args:
			doctype: DocType name
			records: List of record dictionaries

		Returns:
			Dictionary mapping linked_doctype to set of record names
		"""
		try:
			meta = frappe.get_meta(doctype)
		except Exception as e:
			self.logger.error(f"Failed to get meta for {doctype}: {e}", exc_info=True)
			return {}

		# Map: value_fieldname → fieldname_that_holds_the_doctype
		dyn_map = {
			field.fieldname: field.options
			for field in meta.fields
			if field.fieldtype == "Dynamic Link" and field.options
		}

		if not dyn_map:
			return {}

		found = defaultdict(set)
		for rec in records:
			for value_field, dt_field in dyn_map.items():
				linked_dt = rec.get(dt_field)
				linked_name = rec.get(value_field)
				if linked_dt and linked_name and linked_dt not in FRAMEWORK_DOCTYPES:
					found[linked_dt].add(linked_name)

		return dict(found)

	def resolve_all_dependencies(self, requested_doctypes: List[str]) -> Dict[str, str]:
		"""
		Perform BFS to resolve all dependencies from requested DocTypes.

		Args:
			requested_doctypes: List of initially requested DocTypes

		Returns:
			Dictionary mapping doctype_name to type ("requested" | "dependency")
		"""
		self.logger.info(f"Resolving dependencies for {len(requested_doctypes)} DocType(s)")

		result = {dt: "requested" for dt in requested_doctypes}
		queue = deque(requested_doctypes)

		while queue:
			doctype = queue.popleft()
			for linked_dt in self.get_schema_links(doctype):
				if linked_dt not in result:
					result[linked_dt] = "dependency"
					queue.append(linked_dt)

		n_deps = sum(1 for v in result.values() if v == "dependency")
		self.logger.info(f"Resolved {n_deps} additional dependencies")

		return result

	def topological_sort(self, doctypes_dict: Dict[str, str]) -> List[str]:
		"""
		Perform topological sort using Kahn's algorithm.

		Returns import order where dependencies come before dependents.
		Circular dependencies are detected and placed at the end.

		Args:
			doctypes_dict: Dictionary of doctypes with their types

		Returns:
			List of DocTypes in dependency order
		"""
		all_dts = set(doctypes_dict.keys())

		graph = defaultdict(set)
		in_degree = defaultdict(int)

		for dt in all_dts:
			if dt not in in_degree:
				in_degree[dt] = 0
			for dep in self.get_schema_links(dt):
				if dep in all_dts:
					graph[dep].add(dt)
					in_degree[dt] += 1

		queue = deque(dt for dt in all_dts if in_degree[dt] == 0)
		order = []

		while queue:
			dt = queue.popleft()
			order.append(dt)
			for dependent in graph[dt]:
				in_degree[dependent] -= 1
				if in_degree[dependent] == 0:
					queue.append(dependent)

		remaining = [dt for dt in all_dts if dt not in order]
		if remaining:
			self.logger.warning(
				f"Circular dependencies detected: {', '.join(remaining)}. "
				"These will be imported last."
			)
			order.extend(remaining)

		return order

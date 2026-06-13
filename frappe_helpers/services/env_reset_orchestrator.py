"""
frappe_helpers.services.env_reset_orchestrator
===============================================
Orchestrates the environment reset workflow.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frappe

from frappe_helpers.services.backup_service import BackupService
from frappe_helpers.services.dependency_resolver import DependencyResolver
from frappe_helpers.services.export_service import ExportService
from frappe_helpers.services.import_service import ImportService
from frappe_helpers.utils.validators import DocTypeValidator


@dataclass
class EnvResetResult:
	"""Result of environment reset operation."""
	success: bool
	doctypes_processed: int
	records_imported: int
	records_failed: int
	output_dir: str
	error_message: Optional[str] = None


@dataclass
class EnvResetPlan:
	"""Plan for environment reset showing what will be done."""
	requested_doctypes: List[str]
	all_doctypes: Dict[str, str]
	import_order: List[str]
	total_doctypes: int
	dependency_count: int


class EnvResetOrchestrator:
	"""
	Orchestrates the complete environment reset workflow.

	Responsibilities:
	- Coordinates service calls in correct order
	- Manages transaction-like behavior
	- Provides rollback information on failure
	"""

	def __init__(self, site: str):
		"""
		Initialize orchestrator for a specific site.

		Args:
			site: Site name
		"""
		self.site = site
		self.logger = frappe.logger("frappe_helpers.orchestrator")

		self.validator = DocTypeValidator()
		self.resolver = DependencyResolver()
		self.backup_service = BackupService()

	def create_plan(
		self,
		requested_doctypes: List[str],
		resolve_dependencies: bool = True
	) -> EnvResetPlan:
		"""
		Create an execution plan without making any changes.

		Args:
			requested_doctypes: List of DocTypes to preserve
			resolve_dependencies: Whether to resolve dependencies

		Returns:
			EnvResetPlan with all details
		"""
		self.logger.info(f"Creating reset plan for {len(requested_doctypes)} DocTypes")

		validated = self.validator.validate_doctypes_exist(requested_doctypes)

		if resolve_dependencies:
			doctypes_dict = self.resolver.resolve_all_dependencies(validated)
		else:
			doctypes_dict = {dt: "requested" for dt in validated}

		import_order = self.resolver.topological_sort(doctypes_dict)
		dep_count = sum(1 for v in doctypes_dict.values() if v == "dependency")

		return EnvResetPlan(
			requested_doctypes=validated,
			all_doctypes=doctypes_dict,
			import_order=import_order,
			total_doctypes=len(doctypes_dict),
			dependency_count=dep_count,
		)

	def execute(
		self,
		plan: EnvResetPlan,
		output_dir: Optional[str] = None,
		skip_backup: bool = False,
	) -> EnvResetResult:
		"""
		Execute the environment reset with the given plan.

		This is the main orchestration method that coordinates all services.

		Args:
			plan: Execution plan from create_plan()
			output_dir: Optional output directory for exports
			skip_backup: Whether to skip backup step

		Returns:
			EnvResetResult with operation outcome
		"""
		self.logger.info(f"Starting environment reset for site: {self.site}")

		try:
			output_dir = self._prepare_output_dir(output_dir)

			if not skip_backup:
				self._execute_backup()

			manifest = self._execute_export(plan, output_dir)

			frappe.destroy()

			self._execute_reinstall()

			stats = self._execute_import(manifest, output_dir)

			return EnvResetResult(
				success=True,
				doctypes_processed=len(manifest),
				records_imported=stats["success"],
				records_failed=stats["failed"],
				output_dir=output_dir,
			)

		except Exception as e:
			self.logger.error(f"Environment reset failed: {e}")
			return EnvResetResult(
				success=False,
				doctypes_processed=0,
				records_imported=0,
				records_failed=0,
				output_dir=output_dir or "",
				error_message=str(e),
			)

	def _prepare_output_dir(self, output_dir: Optional[str]) -> str:
		"""Prepare output directory for exports."""
		if not output_dir:
			ts = datetime.now().strftime("%Y%m%d_%H%M%S")
			safe_site = self.site.replace(".", "_")
			output_dir = str(
				Path(__file__).parent.parent / f"saved_fixtures_{safe_site}_{ts}"
			)

		os.makedirs(output_dir, exist_ok=True)
		self.logger.info(f"Output directory: {output_dir}")
		return output_dir

	def _execute_backup(self):
		"""Execute backup step."""
		self.logger.info("Executing backup")
		if not self.backup_service.backup_site(self.site):
			raise RuntimeError("Backup failed")

	def _execute_export(self, plan: EnvResetPlan, output_dir: str) -> List[Dict]:
		"""Execute export step."""
		self.logger.info("Executing export")
		export_service = ExportService(output_dir)
		return export_service.export_all(
			plan.all_doctypes,
			plan.import_order,
			self.site
		)

	def _execute_reinstall(self):
		"""Execute reinstall step."""
		self.logger.warning("Executing reinstall - all data will be erased")
		if not self.backup_service.reinstall_site(self.site):
			raise RuntimeError("Reinstall failed")

	def _execute_import(self, manifest: List[Dict], output_dir: str) -> Dict[str, int]:
		"""Execute import step."""
		self.logger.info("Executing import")
		import_service = ImportService(output_dir)
		return import_service.import_all(manifest, self.site)

"""
frappe_helpers.services.export_service
=======================================
Service for exporting DocType data to JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frappe


class ExportService:
	"""Handles exporting DocType records to JSON files."""

	def __init__(self, output_dir: str):
		"""
		Initialize the export service.

		Args:
			output_dir: Directory where JSON files will be saved
		"""
		self.output_dir = output_dir
		self.logger = frappe.logger("frappe_helpers.export_service")
		os.makedirs(output_dir, exist_ok=True)

	def _safe_filename(self, doctype: str) -> str:
		"""
		Convert DocType name to safe filename.

		Args:
			doctype: DocType name

		Returns:
			Safe filename with .json extension
		"""
		return doctype.replace(" ", "_").replace("/", "_") + ".json"

	def export_doctype(
		self,
		doctype: str,
		names_filter: Optional[List[str]] = None
	) -> Optional[str]:
		"""
		Export all records (or filtered subset) for a DocType to JSON.

		Args:
			doctype: DocType name to export
			names_filter: Optional list of specific record names to export

		Returns:
			Path to exported file, or None if nothing to export
		"""
		self.logger.info(f"Exporting {doctype}...")

		try:
			filters = [["name", "in", names_filter]] if names_filter else None

			rows = frappe.get_all(
				doctype,
				filters=filters,
				fields=["name"],
				ignore_permissions=True,
			)

			if not rows:
				self.logger.info(f"{doctype} is empty, skipped")
				return None

			full_records = []
			for row in rows:
				try:
					doc = frappe.get_doc(doctype, row.name)
					full_records.append(doc.as_dict())
				except Exception as exc:
					self.logger.error(f"Could not fetch {doctype} '{row.name}': {exc}", exc_info=True)

			if not full_records:
				return None

			filepath = os.path.join(self.output_dir, self._safe_filename(doctype))
			with open(filepath, "w", encoding="utf-8") as fh:
				json.dump(full_records, fh, indent=2, default=str, ensure_ascii=False)

			self.logger.info(f"Exported {len(full_records)} record(s) from {doctype}")
			return filepath

		except Exception as exc:
			self.logger.error(f"Failed to export {doctype}: {exc}", exc_info=True)
			frappe.log_error(title=f"Env Reset: Export {doctype} Failed")
			return None

	def export_all(
		self,
		doctypes_dict: Dict[str, str],
		import_order: List[str],
		site: str
	) -> List[Dict]:
		"""
		Export all DocTypes in dependency order and create manifest.

		Args:
			doctypes_dict: Dictionary mapping doctype to type (requested/dependency)
			import_order: List of doctypes in topological order
			site: Site name

		Returns:
			List of manifest entries (dicts with doctype/filepath/type)
		"""
		self.logger.info(f"Starting export of {len(doctypes_dict)} DocType(s)")
		manifest = []

		for doctype in import_order:
			if doctype not in doctypes_dict:
				continue

			filepath = self.export_doctype(doctype)
			if filepath:
				manifest.append({
					"doctype": doctype,
					"filepath": os.path.basename(filepath),
					"type": doctypes_dict[doctype],
				})

		self._create_manifest(manifest, site)
		self.logger.info(f"Export complete: {len(manifest)} DocType(s) exported")

		return manifest

	def _create_manifest(self, manifest: List[Dict], site: str):
		"""
		Create manifest.json file with export metadata.

		Args:
			manifest: List of exported DocType entries
			site: Site name
		"""
		manifest_path = os.path.join(self.output_dir, "manifest.json")
		manifest_data = {
			"site": site,
			"created_at": datetime.now().isoformat(),
			"import_order": [entry["doctype"] for entry in manifest],
			"files": manifest,
		}

		with open(manifest_path, "w", encoding="utf-8") as fh:
			json.dump(manifest_data, fh, indent=2)

		self.logger.info(f"Manifest created at {manifest_path}")

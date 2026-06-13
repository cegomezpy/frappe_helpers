"""
frappe_helpers.services.import_service
=======================================
Service for importing DocType data from JSON files.
"""

import json
import os
from typing import Dict, List, Tuple

import frappe


class ImportService:
	"""Handles importing DocType records from JSON files."""

	def __init__(self, output_dir: str):
		"""
		Initialize the import service.

		Args:
			output_dir: Directory containing JSON files to import
		"""
		self.output_dir = output_dir
		self.logger = frappe.logger("frappe_helpers.import_service")

	def import_records(self, doctype: str, records: List[dict]) -> Tuple[int, int]:
		"""
		Import (upsert) records for a DocType.

		If a record exists, it's updated. Otherwise, it's inserted.

		Args:
			doctype: DocType name
			records: List of record dictionaries

		Returns:
			Tuple of (success_count, fail_count)
		"""
		success = 0
		fail = 0

		for rec in records:
			name = rec.get("name", "<unknown>")
			try:
				if frappe.db.exists(doctype, name):
					doc = frappe.get_doc(doctype, name)
					doc.update(rec)
					doc.flags.ignore_permissions = True
					doc.flags.ignore_validate = True
					doc.save(ignore_permissions=True)
				else:
					doc = frappe.get_doc(rec)
					doc.flags.ignore_permissions = True
					doc.flags.ignore_validate = True
					doc.insert(
						ignore_permissions=True,
						ignore_if_duplicate=True,
						ignore_links=True,
					)
				success += 1

			except Exception as exc:
				self.logger.warning(f"Failed to import {doctype} '{name}': {exc}")
				fail += 1

		frappe.db.commit()
		return success, fail

	def import_all(self, manifest: List[Dict], site: str) -> Dict[str, int]:
		"""
		Re-initialize Frappe and import all records from manifest.

		Args:
			manifest: List of manifest entries with doctype/filepath info
			site: Site name

		Returns:
			Dictionary with import statistics
		"""
		self.logger.info("Re-initializing Frappe connection")
		frappe.destroy()
		frappe.init(site=site)
		frappe.connect()

		total_ok = 0
		total_fail = 0

		for entry in manifest:
			doctype = entry["doctype"]
			filepath = os.path.join(self.output_dir, entry["filepath"])

			if not os.path.exists(filepath):
				self.logger.warning(f"File missing for {doctype}, skipped")
				continue

			with open(filepath, "r", encoding="utf-8") as fh:
				records = json.load(fh)

			self.logger.info(f"Importing {doctype}...")
			ok, fail = self.import_records(doctype, records)

			total_ok += ok
			total_fail += fail

			if fail:
				self.logger.warning(f"{doctype}: {ok} imported, {fail} failed")
			else:
				self.logger.info(f"{doctype}: {ok} imported successfully")

		self.logger.info(f"Import complete: {total_ok} records imported, {total_fail} failed")

		return {
			"success": total_ok,
			"failed": total_fail,
		}

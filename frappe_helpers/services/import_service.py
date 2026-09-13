"""
frappe_helpers.services.import_service
=======================================
Service for importing DocType data from JSON files.
"""

import json
import os
from typing import Dict, List, Tuple

import click
import frappe

from frappe_helpers.utils.constants import NON_RESTORABLE_FIELDS


class ImportService:
	"""Handles importing DocType records from JSON files."""

	def __init__(self, output_dir: str, verbose: bool = False):
		"""
		Initialize the import service.

		Args:
			output_dir: Directory containing JSON files to import
			verbose: Enable verbose output
		"""
		self.output_dir = output_dir
		self.verbose = verbose
		self.logger = frappe.logger("frappe_helpers.import_service")

	def _restorable_fields(self, record: dict) -> dict:
		"""
		Strip framework-owned keys and unset values from an exported record.

		Replaying `modified` makes Frappe reject the save with
		TimestampMismatchError, and replaying `None` would overwrite the
		defaults a freshly reinstalled site already has.

		Args:
			record: Record dictionary as produced by doc.as_dict()

		Returns:
			Dictionary safe to apply onto an existing document
		"""
		return {
			key: value
			for key, value in record.items()
			if key not in NON_RESTORABLE_FIELDS and value is not None
		}

	def import_records(self, doctype: str, records: List[dict]) -> Tuple[int, int]:
		"""
		Import (upsert) records for a DocType.

		Single DocTypes are updated in-place. Regular DocTypes are upserted
		by name: updated if exists, inserted otherwise.

		Args:
			doctype: DocType name
			records: List of record dictionaries

		Returns:
			Tuple of (success_count, fail_count)
		"""
		meta = frappe.get_meta(doctype)

		if meta.issingle:
			return self._import_single(doctype, records[0] if records else {})

		success = 0
		fail = 0

		for rec in records:
			name = rec.get("name", "<unknown>")
			try:
				if frappe.db.exists(doctype, name):
					doc = frappe.get_doc(doctype, name)
					doc.update(self._restorable_fields(rec))
					doc.flags.ignore_permissions = True
					doc.flags.ignore_validate = True
					doc.flags.ignore_mandatory = True
					doc.flags.ignore_links = True
					doc.save(ignore_permissions=True)
					if self.verbose:
						click.echo(f"    • Updated {name}")
				else:
					doc = frappe.get_doc(rec)
					doc.flags.ignore_permissions = True
					doc.flags.ignore_validate = True
					doc.insert(
						ignore_permissions=True,
						ignore_if_duplicate=True,
						ignore_links=True,
					)
					if self.verbose:
						click.echo(f"    • Inserted {name}")
				success += 1

			except Exception as exc:
				self.logger.error(f"Failed to import {doctype} '{name}': {exc}", exc_info=True)
				if self.verbose:
					click.echo(click.style(f"    ✗ Failed to import {name}: {exc}", fg="red"))
				fail += 1

		frappe.db.commit()
		return success, fail

	def _import_single(self, doctype: str, record: dict) -> Tuple[int, int]:
		"""
		Import a Single DocType by updating its fields in-place.

		Singles cannot be inserted — they always exist as a single record
		that must be updated via get_doc/save.

		Args:
			doctype: Single DocType name
			record: Record dictionary from export

		Returns:
			Tuple of (success_count, fail_count)
		"""
		try:
			doc = frappe.get_doc(doctype)
			doc.update(self._restorable_fields(record))
			doc.flags.ignore_permissions = True
			doc.flags.ignore_validate = True
			doc.flags.ignore_mandatory = True
			doc.flags.ignore_links = True
			doc.save(ignore_permissions=True)
			frappe.db.commit()

			if self.verbose:
				click.echo(f"    • Updated Single {doctype}")
			return 1, 0

		except Exception as exc:
			self.logger.error(f"Failed to import Single {doctype}: {exc}", exc_info=True)
			if self.verbose:
				click.echo(click.style(f"    ✗ Failed to import Single {doctype}: {exc}", fg="red"))
			return 0, 1

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

		if self.verbose:
			click.echo(click.style(f"\n→ Re-initializing Frappe connection...", fg="cyan"))

		frappe.init(site=site)
		frappe.connect()
		self.logger = frappe.logger("frappe_helpers.import_service")

		if self.verbose:
			click.echo(click.style(f"  ✓ Connected to site: {site}", fg="green"))
			click.echo(click.style(f"\n→ Importing {len(manifest)} DocType(s)...", fg="cyan"))

		total_ok = 0
		total_fail = 0

		for entry in manifest:
			doctype = entry["doctype"]
			filepath = os.path.join(self.output_dir, entry["filepath"])

			if not os.path.exists(filepath):
				self.logger.error(f"File missing for {doctype}: {filepath}, skipped")
				if self.verbose:
					click.echo(click.style(f"  ✗ File missing for {doctype}, skipped", fg="red"))
				continue

			with open(filepath, "r", encoding="utf-8") as fh:
				records = json.load(fh)

			self.logger.info(f"Importing {doctype}...")
			if self.verbose:
				click.echo(click.style(f"  → Importing {doctype} ({len(records)} record(s))...", fg="cyan"))

			ok, fail = self.import_records(doctype, records)

			total_ok += ok
			total_fail += fail

			if fail:
				self.logger.error(f"{doctype}: {ok} imported, {fail} failed")
				if self.verbose:
					click.echo(click.style(f"    ⚠ {ok} imported, {fail} failed", fg="yellow"))
			else:
				self.logger.info(f"{doctype}: {ok} imported successfully")
				if self.verbose:
					click.echo(click.style(f"    ✓ {ok} imported successfully", fg="green"))

		self.logger.info(f"Import complete: {total_ok} records imported, {total_fail} failed")

		if self.verbose:
			click.echo(click.style(f"\n  ✓ Import complete: {total_ok} records imported, {total_fail} failed", fg="green"))

		return {
			"success": total_ok,
			"failed": total_fail,
		}

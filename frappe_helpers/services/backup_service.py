"""
frappe_helpers.services.backup_service
=======================================
Service for backup and reinstall operations.
"""

import os
import subprocess
from typing import List

import frappe


class BackupService:
	"""Handles site backup and reinstall operations."""

	def __init__(self):
		self.logger = frappe.logger("frappe_helpers.backup_service")

	def _get_bench_root(self) -> str:
		"""
		Get the bench root directory.

		Returns:
			Bench root path
		"""
		return os.getcwd()

	def _run_bench_command(self, args: List[str], description: str) -> bool:
		"""
		Execute a bench command.

		Args:
			args: Command arguments
			description: Human-readable description for logging

		Returns:
			True if successful, False otherwise
		"""
		cmd = ["bench"] + args
		self.logger.info(f"Running: {' '.join(cmd)}")

		try:
			result = subprocess.run(
				cmd,
				cwd=self._get_bench_root(),
				capture_output=True,
				text=True
			)

			if result.returncode != 0:
				self.logger.error(
					f"{description} failed with code {result.returncode}\n"
					f"STDOUT: {result.stdout}\n"
					f"STDERR: {result.stderr}"
				)
				return False

			self.logger.info(f"{description} completed successfully")
			return True

		except Exception as e:
			self.logger.error(f"{description} failed with exception: {e}")
			return False

	def get_backup_path(self, site: str) -> str:
		"""
		Get the backup directory path for a site.

		Args:
			site: Site name

		Returns:
			Full path to backup directory
		"""
		bench_root = self._get_bench_root()
		return os.path.join(bench_root, "sites", site, "private", "backups")

	def backup_site(self, site: str, with_files: bool = True) -> bool:
		"""
		Backup a Frappe site.

		Args:
			site: Site name
			with_files: Include files in backup

		Returns:
			True if backup successful, False otherwise
		"""
		backup_path = self.get_backup_path(site)
		self.logger.info(f"Starting backup for site: {site}")
		self.logger.info(f"Backup will be saved to: {backup_path}")

		args = ["--site", site, "backup"]

		if with_files:
			args.append("--with-files")

		success = self._run_bench_command(args, "Site backup")

		if success:
			self.logger.info(f"Backup completed. Files saved to: {backup_path}")

		return success

	def reinstall_site(self, site: str) -> bool:
		"""
		Reinstall a Frappe site (erases all data).

		Args:
			site: Site name

		Returns:
			True if reinstall successful, False otherwise
		"""
		self.logger.warning(f"Reinstalling site: {site} - ALL DATA WILL BE ERASED")
		args = ["--site", site, "reinstall", "--yes"]
		
		# Read MariaDB root password from environment variables to bypass interactive prompts
		db_root_password = os.environ.get("MARIADB_ROOT_PASSWORD") or os.environ.get("MYSQL_ROOT_PASSWORD")
		if db_root_password:
			args.extend(["--mariadb-root-password", db_root_password])

		# Read Administrator password from environment or fallback to 'admin'
		admin_password = os.environ.get("ADMIN_PASSWORD") or "admin"
		args.extend(["--admin-password", admin_password])

		return self._run_bench_command(args, "Site reinstall")

"""
frappe_helpers.services.backup_service
=======================================
Service for backup and reinstall operations.
"""

import os
import subprocess
from typing import List

import click
import frappe


class BackupService:
	"""Handles site backup and reinstall operations."""

	def __init__(self, verbose: bool = False):
		self.verbose = verbose
		self.logger = frappe.logger("frappe_helpers.backup_service")

	def _get_bench_root(self) -> str:
		"""
		Get the bench root directory.

		Returns:
			Bench root path
		"""
		return frappe.utils.get_bench_path()

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

		if self.verbose:
			click.echo(click.style(f"    $ {' '.join(cmd)}", fg="white", dim=True))

		try:
			result = subprocess.run(
				cmd,
				cwd=self._get_bench_root(),
				capture_output=True,
				text=True
			)

			if self.verbose and result.stdout:
				for line in result.stdout.strip().split('\n'):
					if line.strip():
						click.echo(f"      {line}")

			if result.returncode != 0:
				error_msg = (
					f"{description} failed with code {result.returncode}\n"
					f"STDOUT: {result.stdout}\n"
					f"STDERR: {result.stderr}"
				)
				self.logger.error(error_msg)
				if self.verbose:
					click.echo(click.style(f"    ✗ Command failed with code {result.returncode}", fg="red"))
					if result.stderr:
						click.echo(click.style(f"      {result.stderr}", fg="red"))
				return False

			self.logger.info(f"{description} completed successfully")
			return True

		except Exception as e:
			self.logger.error(f"{description} failed with exception: {e}", exc_info=True)
			if self.verbose:
				click.echo(click.style(f"    ✗ Exception: {e}", fg="red"))
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

		if self.verbose:
			click.echo(click.style(f"    Backup path: {backup_path}", fg="white", dim=True))

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

		if self.verbose:
			click.echo(click.style(f"    ⚠  ALL DATA WILL BE ERASED", fg="red", bold=True))

		args = ["--site", site, "reinstall", "--yes"]

		# Read MariaDB root password from environment variables to bypass interactive prompts
		db_root_password = os.environ.get("MARIADB_ROOT_PASSWORD") or os.environ.get("MYSQL_ROOT_PASSWORD")
		if db_root_password:
			args.extend(["--mariadb-root-password", db_root_password])
			if self.verbose:
				click.echo(click.style(f"    Using MariaDB root password from environment", fg="white", dim=True))

		# Read Administrator password from environment or fallback to 'admin'
		admin_password = os.environ.get("ADMIN_PASSWORD") or "admin"
		args.extend(["--admin-password", admin_password])
		if self.verbose:
			click.echo(click.style(f"    Using admin password from environment", fg="white", dim=True))

		return self._run_bench_command(args, "Site reinstall")

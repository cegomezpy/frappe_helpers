"""
frappe_helpers.commands.env_reset
==================================
CLI command to reset a Frappe site while preserving selected DocType data.

Usage:
    bench --site mysite.local env-reset -s "Item" -s "Customer" -s "Supplier"
"""

import traceback

import click
import frappe

from frappe_helpers.services.env_reset_orchestrator import EnvResetOrchestrator


def _print_banner():
	"""Print application banner."""
	click.echo(click.style("\n╔══════════════════════════════════════╗", fg="cyan"))
	click.echo(click.style("║       Frappe Env Reset Tool          ║", fg="cyan", bold=True))
	click.echo(click.style("╚══════════════════════════════════════╝", fg="cyan"))


def _print_plan(plan):
	"""Print the execution plan."""
	click.echo(click.style(f"\n✓ All {len(plan.requested_doctypes)} DocType(s) validated", fg="green"))

	if plan.dependency_count > 0:
		click.echo(
			click.style(
				f"✓ {len(plan.requested_doctypes)} requested  +  "
				f"{plan.dependency_count} auto-resolved dependencies",
				fg="green"
			)
		)

	click.echo(click.style("\n   Export plan (in import order):", fg="white", bold=True))
	for dt in plan.import_order:
		tag = (
			click.style("  [requested]  ", fg="cyan")
			if plan.all_doctypes.get(dt) == "requested"
			else click.style("  [dependency] ", fg="white", dim=True)
		)
		click.echo(f"  {tag}{dt}")


def _print_result(result):
	"""Print execution result."""
	if result.success:
		click.echo(
			click.style(
				"\n✅  All done!  Site has been reset and data restored.",
				fg="green", bold=True,
			)
		)
		click.echo(f"   Processed: {result.doctypes_processed} DocTypes")
		click.echo(f"   Imported: {result.records_imported} records")
		if result.records_failed > 0:
			click.echo(f"   Failed: {result.records_failed} records (check logs)")
		click.echo(f"   Fixtures kept at: {result.output_dir}\n")
	else:
		click.echo(click.style(f"\n✗ Operation failed: {result.error_message}", fg="red"))
		if result.output_dir:
			click.echo(f"   Exported data saved at: {result.output_dir}\n")


@click.command("env-reset")
@click.option(
	"--save-tables", "-s",
	multiple=True,
	required=True,
	help="DocType name to preserve. Repeat for multiple: -s 'Item' -s 'Customer'",
)
@click.option(
	"--output-dir", "-o",
	default=None,
	help="Directory to save exported JSON files (auto-named if omitted).",
)
@click.option(
	"--skip-backup",
	is_flag=True,
	default=False,
	help="Skip the site backup step.",
)
@click.option(
	"--no-deps",
	is_flag=True,
	default=False,
	help="Do NOT auto-resolve linked dependencies.",
)
@click.option(
	"--dry-run",
	is_flag=True,
	default=False,
	help="Show what would happen without making any changes.",
)
@click.option(
	"--yes", "-y",
	is_flag=True,
	default=False,
	help="Bypass confirmation prompt.",
)
@click.option(
	"--mariadb-root-password",
	default=None,
	help="MariaDB root password for reinstalling the site.",
)
@click.option(
	"--admin-password",
	default=None,
	help="New Administrator password for the reinstalled site.",
)
@click.pass_context
def env_reset(ctx, save_tables, output_dir, skip_backup, no_deps, dry_run, yes, mariadb_root_password, admin_password):
	"""
	Reset a Frappe site while preserving selected DocType data.

	\b
	What this does:
	  1. Validates that every given DocType name exists
	  2. Resolves linked dependencies automatically (disable with --no-deps)
	  3. Backs up the site
	  4. Exports all records from the selected DocTypes to JSON
	  5. Reinstalls the site  ← THIS ERASES ALL DATA
	  6. Re-imports the saved JSON records

	\b
	Example:
	  bench --site mysite.local env-reset \\
	        -s "Item" -s "Item Group" -s "UOM" \\
	        -s "Customer" -s "Customer Group"

	\b
	Dry run (see what would be exported):
	  bench --site mysite.local env-reset -s "Item" --dry-run
	"""
	site = ctx.obj["sites"][0]
	frappe.init(site=site)
	frappe.connect()

	try:
		_print_banner()

		orchestrator = EnvResetOrchestrator(site)

		plan = orchestrator.create_plan(
			requested_doctypes=list(save_tables),
			resolve_dependencies=not no_deps
		)

		_print_plan(plan)

		if dry_run:
			click.echo(click.style("\n── DRY RUN — no changes made ──────────\n", fg="yellow"))
			return

		if not yes:
			click.echo()
			click.confirm(
				click.style(
					"⚠  This will REINSTALL the site and erase ALL data. Proceed?",
					fg="red", bold=True,
				),
				abort=True,
			)

		if output_dir:
			click.echo(f"\n📁 Fixtures will be saved to: {output_dir}")

		result = orchestrator.execute(
			plan=plan,
			output_dir=output_dir,
			skip_backup=skip_backup,
			mariadb_root_password=mariadb_root_password,
			admin_password=admin_password,
		)

		_print_result(result)

		if not result.success:
			raise SystemExit(1)

	except click.exceptions.Abort:
		click.echo(click.style("\nAborted — no changes made.", fg="yellow"))
	except frappe.ValidationError as e:
		click.echo(click.style(f"\n✗ Validation error: {e}", fg="red"))
		raise SystemExit(1)
	except Exception as e:
		click.echo(click.style(f"\n✗ Unexpected error: {e}", fg="red"))
		click.echo(traceback.format_exc())
		raise SystemExit(1)
	finally:
		try:
			frappe.destroy()
		except Exception:
			pass

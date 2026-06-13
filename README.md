### Frappe Helpers

A Frappe app with utilities for staging and development environments. Currently includes tools for environment reset and data preservation.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench --site <your-site> install-app frappe_helpers
```

### Features

#### Environment Reset Command

Reset a Frappe site while preserving selected DocType data. Perfect for cleaning up development/staging environments while keeping master data intact.

**What it does:**
1. Validates that all specified DocTypes exist
2. Automatically resolves dependencies (Link, Table, Dynamic Link fields)
3. Backs up the site
4. Exports selected DocType records to JSON
5. Reinstalls the site (erases ALL data)
6. Re-imports the saved records in dependency order

**Usage:**

```bash
# Basic usage - save specific DocTypes
bench --site mysite.local env-reset \
  -s "Item" \
  -s "Item Group" \
  -s "Customer" \
  -s "Supplier"

# Dry run - see what would be exported without making changes
bench --site mysite.local env-reset -s "Item" -s "Customer" --dry-run

# Skip automatic dependency resolution
bench --site mysite.local env-reset -s "Item" --no-deps

# Skip backup step (faster, but less safe)
bench --site mysite.local env-reset -s "Item" --skip-backup

# Custom output directory
bench --site mysite.local env-reset -s "Item" -o /tmp/my_fixtures
```

**Options:**
- `-s, --save-tables`: DocType name to preserve (repeat for multiple)
- `-o, --output-dir`: Custom directory for exported files
- `--skip-backup`: Skip the site backup step
- `--no-deps`: Don't auto-resolve linked dependencies
- `--dry-run`: Show export plan without making changes

**Example Output:**
```
╔══════════════════════════════════════╗
║       Frappe Env Reset Tool          ║
╚══════════════════════════════════════╝

[1/6] Validating DocTypes
   ✓ All 2 DocType(s) found

[2/6] Resolving dependencies
   ✓ 2 requested  +  4 auto-resolved dependencies

   Export plan (in import order):
     [dependency]  UOM
     [dependency]  Item Group
     [dependency]  Brand
     [dependency]  Customer Group
     [requested]   Item
     [requested]   Customer
```

### Architecture

The app follows SOLID principles with a clean separation of concerns:

```
frappe_helpers/
├── commands/              # CLI layer (Click commands)
├── services/              # Business logic layer
│   ├── backup_service.py
│   ├── dependency_resolver.py
│   ├── export_service.py
│   └── import_service.py
└── utils/                 # Shared utilities
    ├── constants.py
    └── validators.py
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/frappe_helpers
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit

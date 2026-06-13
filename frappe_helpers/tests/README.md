# Frappe Helpers Tests

Comprehensive test suite for the frappe_helpers app.

## ⚠️ IMPORTANT: What We Test vs What We Mock

### ✅ WE TEST (Our Code)
- Orchestration logic (correct order of operations)
- Plan creation and validation
- Dependency resolution algorithms
- Result object creation
- Error handling and edge cases
- Service initialization
- Parameter passing between services

### 🚫 WE DON'T TEST (Database Operations & Destructive Actions)
- `BackupService.backup_site()` - uses Frappe's bench backup
- `BackupService.reinstall_site()` - **DESTRUCTIVE**, erases all data
- `ExportService.export_doctype()` - queries database
- `ImportService.import_all()` - writes to database, calls frappe.init()
- `Orchestrator.execute()` - runs the full workflow
- External subprocess calls (bench commands)

### Why?
- **We trust Frappe's operations work** - they're tested by the Frappe team
- **We don't want to destroy test data** - reinstall erases everything
- **Tests would be slow** - database operations take time (291s → 0.75s after fix!)
- **Tests would prompt for passwords** - MySQL root password, admin password
- **Mocking frappe.init/connect is complex** - deep framework integration
- **We ONLY test our logic** - not Frappe's database/backup functionality

**Bottom line**: Tests are SAFE and FAST - no database operations, no password prompts!

## Test Structure

```
tests/
├── __init__.py
├── README.md                      # This file
├── test_fixtures.py               # Base test case and fixtures
├── test_validators.py             # Unit tests for validators
├── test_dependency_resolver.py    # Unit tests for dependency resolver
├── test_services.py               # Unit tests for export/import services
└── test_orchestrator.py           # Integration tests for orchestrator
```

## Running Tests

### Run all tests for the app

```bash
# From bench root
bench --site <site-name> run-tests --app frappe_helpers
```

### Run specific test module

```bash
# Test validators only
bench --site <site-name> run-tests --app frappe_helpers --module frappe_helpers.tests.test_validators

# Test orchestrator only
bench --site <site-name> run-tests --app frappe_helpers --module frappe_helpers.tests.test_orchestrator
```

### Run specific test class

```bash
bench --site <site-name> run-tests --app frappe_helpers --module frappe_helpers.tests.test_validators.TestDocTypeValidator
```

### Run specific test method

```bash
bench --site <site-name> run-tests --app frappe_helpers --module frappe_helpers.tests.test_validators.TestDocTypeValidator.test_validate_existing_doctypes
```

### Run with coverage

```bash
# Install coverage first
pip install coverage

# Run tests with coverage
bench --site <site-name> run-tests --app frappe_helpers --coverage
```

## Test Categories

### Unit Tests

**Purpose**: Test individual components in isolation

- `test_validators.py` - DocType validation logic
- `test_dependency_resolver.py` - Dependency resolution algorithms
- `test_services.py` - Export/import service logic

**Characteristics**:
- Fast execution
- No external dependencies
- Mock external services
- Test single responsibility

### Integration Tests

**Purpose**: Test component interactions

- `test_orchestrator.py` - Full workflow orchestration

**Characteristics**:
- Tests multiple components together
- May use test database
- Slower than unit tests
- Test real interactions

## Writing New Tests

### 1. Extend FrappeHelpersTestCase

```python
from frappe_helpers.tests.test_fixtures import FrappeHelpersTestCase

class TestMyFeature(FrappeHelpersTestCase):
    def test_something(self):
        # Your test here
        pass
```

### 2. Use setUp and tearDown

```python
def setUp(self):
    """Run before each test."""
    self.service = MyService()

def tearDown(self):
    """Run after each test."""
    frappe.db.rollback()
```

### 3. Follow naming conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### 4. Use descriptive test names

```python
def test_validate_existing_doctypes(self):  # ✅ Clear
def test_validation(self):                  # ❌ Vague
```

## Test Coverage Goals

| Component | Target Coverage | Current |
|-----------|----------------|---------|
| Validators | 100% | ✅ |
| Services | 90%+ | ✅ |
| Orchestrator | 85%+ | ✅ |
| Commands | 70%+ | 🔄 |
| Overall | 85%+ | 🔄 |

## Continuous Integration

Tests should be run:
- ✅ Before committing (pre-commit hook)
- ✅ On every push (CI/CD pipeline)
- ✅ Before merging PRs
- ✅ On scheduled basis (nightly)

## Mocking Guidelines

Use mocks for:
- ✅ External services (backup, reinstall)
- ✅ File system operations
- ✅ Database writes (in unit tests)
- ✅ Destructive operations

Don't mock:
- ❌ The component under test
- ❌ Data structures
- ❌ Pure functions
- ❌ Frappe framework (in integration tests)

## Common Patterns

### Testing exceptions

```python
with self.assertRaises(frappe.ValidationError):
    validator.validate_doctypes_exist(["NonExistent"])
```

### Using mocks

```python
from unittest.mock import patch, MagicMock

@patch("frappe_helpers.services.backup_service.BackupService")
def test_with_mock(self, mock_backup):
    mock_backup.return_value.backup_site.return_value = True
    # Test code here
```

### Creating test data

```python
def setUp(self):
    self.test_doc = self.create_test_record("User", {
        "email": "test@example.com",
        "first_name": "Test"
    })
```

## Troubleshooting

### Tests fail with "DocType not found"
- Ensure test DocTypes are created in `setUpClass`
- Check that migrations have run

### Tests are slow
- Check if you're running integration tests when unit tests would suffice
- Use mocks for external dependencies
- Consider using `--failfast` flag

### Database state issues
- Always use `frappe.db.rollback()` in `tearDown`
- Don't commit in test methods unless testing commit logic
- Use transactions for test isolation

## Resources

- [Frappe Testing Docs](https://frappeframework.com/docs/user/en/testing)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

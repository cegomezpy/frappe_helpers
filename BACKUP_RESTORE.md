# Backup & Restore Guide

Critical safety information for the `env-reset` command.

## 📁 Where Backups Are Saved

When `bench backup` runs (default behavior unless `--skip-backup` is used), files are saved to:

```
{bench-root}/sites/{site-name}/private/backups/
```

### Example

```
frappe-bench/sites/mysite.local/private/backups/
├── 20260612_150422-mysite_local-database.sql.gz    # Database backup
├── 20260612_150422-mysite_local-files.tar          # Public files
└── 20260612_150422-mysite_local-private-files.tar  # Private files
```

### Check Backup Location

```bash
# List backups for your site
ls -lh sites/{site-name}/private/backups/

# Example
ls -lh sites/mysite.local/private/backups/

# Sort by date (newest first)
ls -lt sites/mysite.local/private/backups/ | head -10
```

---

## 🔄 Restore Commands

### 1. Restore Database Only

```bash
bench --site {site-name} restore \
  sites/{site-name}/private/backups/{timestamp}-{site}-database.sql.gz
```

**Example:**
```bash
bench --site mysite.local restore \
  sites/mysite.local/private/backups/20260612_150422-mysite_local-database.sql.gz
```

### 2. Restore Database + Files

```bash
# Restore database
bench --site {site-name} restore \
  sites/{site-name}/private/backups/{timestamp}-{site}-database.sql.gz

# Restore public files
bench --site {site-name} restore \
  --with-public-files sites/{site-name}/private/backups/{timestamp}-{site}-files.tar

# Restore private files
bench --site {site-name} restore \
  --with-private-files sites/{site-name}/private/backups/{timestamp}-{site}-private-files.tar
```

### 3. Full Restore (All-in-One)

```bash
bench --site {site-name} restore \
  sites/{site-name}/private/backups/{timestamp}-{site}-database.sql.gz \
  --with-public-files sites/{site-name}/private/backups/{timestamp}-{site}-files.tar \
  --with-private-files sites/{site-name}/private/backups/{timestamp}-{site}-private-files.tar
```

---

## 🚨 Emergency Recovery Procedure

If `env-reset` fails mid-execution and the site is broken:

### Step 1: Identify Latest Backup

```bash
# List backups sorted by date (newest first)
ls -lt sites/{site-name}/private/backups/ | head -10

# Example output:
# -rw-r--r-- 1 frappe frappe 12345678 Jun 12 15:04 20260612_150422-mysite_local-database.sql.gz
# -rw-r--r-- 1 frappe frappe 87654321 Jun 12 15:04 20260612_150422-mysite_local-files.tar
```

### Step 2: Drop Broken Site

```bash
bench drop-site {site-name} --force
```

### Step 3: Recreate Site

```bash
bench new-site {site-name} \
  --mariadb-root-password {your-mysql-root-password} \
  --admin-password {your-admin-password}
```

### Step 4: Restore from Backup

```bash
# Restore database
bench --site {site-name} restore \
  sites/{site-name}/private/backups/{latest-timestamp}-{site}-database.sql.gz

# If you need files too
bench --site {site-name} restore \
  --with-public-files sites/{site-name}/private/backups/{latest-timestamp}-{site}-files.tar \
  --with-private-files sites/{site-name}/private/backups/{latest-timestamp}-{site}-private-files.tar
```

### Step 5: Verify

```bash
# Run migrations
bench --site {site-name} migrate

# Test site
bench browse {site-name}
```

---

## 💡 Best Practices

### Before Running `env-reset`

1. **Check disk space:**
   ```bash
   df -h sites/{site-name}/private/backups/
   ```

2. **List existing backups:**
   ```bash
   ls -lh sites/{site-name}/private/backups/
   ```

3. **Test with --dry-run first:**
   ```bash
   bench --site {site-name} env-reset -s "Item" --dry-run
   ```

4. **Keep backup flag enabled:**
   ```bash
   # ✅ Good - backup created
   bench --site {site-name} env-reset -s "Item"

   # ⚠️ Risky - no backup
   bench --site {site-name} env-reset -s "Item" --skip-backup
   ```

### After Running `env-reset`

1. **Verify site works:**
   ```bash
   bench --site {site-name} migrate
   bench browse {site-name}
   ```

2. **Check imported data:**
   ```bash
   # Log into site and verify your preserved DocTypes are there
   ```

3. **Keep old backups** (don't delete immediately):
   ```bash
   # Backups are safe to keep - they're compressed
   # Only delete after confirming everything works
   ```

---

## 📊 Backup File Sizes

Typical backup sizes (compressed):

| Component | Typical Size | Example |
|-----------|--------------|---------|
| Database | 1-100 MB | `20260612_150422-mysite_local-database.sql.gz` |
| Public Files | 10-500 MB | `20260612_150422-mysite_local-files.tar` |
| Private Files | 5-200 MB | `20260612_150422-mysite_local-private-files.tar` |

**Note**: File sizes vary greatly depending on your data volume.

---

## ⚙️ Advanced Options

### Custom Backup Path

```bash
# env-reset automatically uses default Frappe backup location
# To manually backup to custom location:
bench --site {site-name} backup --backup-path /path/to/custom/backups
```

### Compress Database Backup

```bash
# Frappe automatically compresses (.sql.gz extension)
# To restore compressed backup:
bench --site {site-name} restore {backup-file}.sql.gz
```

### List All Backups for All Sites

```bash
find sites -name "*.sql.gz" -type f
```

---

## 🔗 Related Commands

```bash
# Manual backup (what env-reset uses)
bench --site {site-name} backup --with-files

# Check backup status
bench --site {site-name} backup --verbose

# Restore with force (overwrite existing)
bench --site {site-name} restore {backup-file} --force

# Restore specific database
bench --site {site-name} restore {backup-file} --db-name custom_db_name
```

---

## 📝 Summary

| Action | Command |
|--------|---------|
| **Create Backup** | `bench --site {site} backup --with-files` |
| **List Backups** | `ls -lt sites/{site}/private/backups/` |
| **Restore Database** | `bench --site {site} restore {backup}.sql.gz` |
| **Emergency Recovery** | Drop site → New site → Restore backup |
| **Verify Site** | `bench --site {site} migrate` |

**Remember**: Always keep backups until you've verified the new setup works! 🔒

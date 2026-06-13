# Frappe Helpers - Guía Rápida para DevOps

**Comando**: `bench env-reset` - Resetea un sitio preservando datos específicos

---

## 🚀 Inicio Rápido

### 1. Instalación
```bash
bench get-app https://github.com/cegomezpy/frappe_helpers
bench --site <sitio> install-app frappe_helpers
```

### 2. Uso Básico
```bash
# Ver qué se haría (SIN cambios)
bench --site <sitio> env-reset -s "Item" -s "Customer" --dry-run

# Ejecutar (CON cambios - DESTRUCTIVO)
bench --site <sitio> env-reset -s "Item" -s "Customer"
```

---

## ⚠️ IMPORTANTE

### ✅ SIEMPRE HACER
- ✅ Usar `--dry-run` primero
- ✅ Verificar espacio en disco
- ✅ Mantener backup habilitado (default)
- ✅ Usar nombres exactos de DocType

### ❌ NUNCA HACER
- ❌ Usar `--skip-backup` en producción
- ❌ Ejecutar sin `--dry-run` primero
- ❌ Usar en producción sin avisar al equipo
- ❌ Ejecutar si no hay espacio en disco

---

## 📍 Ubicaciones Clave

```bash
# Backups automáticos
sites/<sitio>/private/backups/

# Fixtures exportados
sites/<sitio>/private/env_reset_fixtures/

# Logs
logs/frappe_helpers.*.log
```

---

## 🔧 Comandos Esenciales

### Ver Backups
```bash
ls -lh sites/<sitio>/private/backups/
```

### Restaurar Backup
```bash
bench --site <sitio> restore \
  sites/<sitio>/private/backups/<archivo>.sql.gz
```

### Ver Fixtures
```bash
ls -lh sites/<sitio>/private/env_reset_fixtures/
```

### Ver Logs
```bash
tail -50 logs/frappe_helpers.import_service.log
```

---

## 📋 Ejemplo Completo: ERPNext

```bash
# 1. Dry run
bench --site prod.local env-reset \
  -s "Item" \
  -s "Item Group" \
  -s "Customer" \
  -s "Customer Group" \
  -s "Supplier" \
  -s "Supplier Group" \
  -s "Company" \
  -s "Warehouse" \
  --dry-run

# 2. Si todo OK, ejecutar sin --dry-run
bench --site prod.local env-reset \
  -s "Item" \
  -s "Item Group" \
  -s "Customer" \
  -s "Customer Group" \
  -s "Supplier" \
  -s "Supplier Group" \
  -s "Company" \
  -s "Warehouse"
```

---

## 🆘 Emergencia: Restaurar Todo

Si algo sale mal:

```bash
# 1. Ver backup más reciente
ls -lt sites/<sitio>/private/backups/ | head -1

# 2. Eliminar sitio
bench drop-site <sitio> --force

# 3. Recrear sitio
bench new-site <sitio> \
  --mariadb-root-password <pass> \
  --admin-password <pass>

# 4. Restaurar backup
bench --site <sitio> restore \
  sites/<sitio>/private/backups/<backup-mas-reciente>.sql.gz

# 5. Verificar
bench --site <sitio> migrate
```

---

## 💡 Tips

### Verificar DocTypes
```bash
# Entrar a consola de Frappe
bench --site <sitio> console

# Listar DocTypes
frappe.db.get_list("DocType", filters={"custom": 0}, fields=["name"])

# Contar registros
frappe.db.count("Item")
```

### Limpiar Espacio
```bash
# Ver espacio
df -h

# Eliminar backups antiguos (CUIDADO)
rm sites/<sitio>/private/backups/<backup-antiguo>*

# Eliminar fixtures antiguos
rm -rf sites/<sitio>/private/env_reset_fixtures/<dir-antiguo>
```

---

## 📊 Entender la Salida

```
✓ 7 solicitados  +  286 dependencias auto-resueltas
```
= 7 DocTypes que pediste + 286 que se necesitan (automático)

```
Importados: 5728 registros
Fallidos: 1606 registros
```
= 5728 OK, 1606 duplicados/opcionales (normal)

---

## 🔗 Más Info

- **Manual Completo**: [README.es.md](README.es.md)
- **Backup/Restore**: [BACKUP_RESTORE.md](BACKUP_RESTORE.md)
- **Issues**: https://github.com/cegomezpy/frappe_helpers/issues

---

**¿Dudas?** Lee el [README.es.md](README.es.md) completo primero.

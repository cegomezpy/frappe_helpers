# Frappe Helpers

Una aplicación de Frappe con utilidades para entornos de staging y desarrollo. Incluye herramientas para resetear entornos mientras se preservan datos maestros.

## 📋 Tabla de Contenidos

- [Instalación](#instalación)
- [¿Qué hace?](#qué-hace)
- [Uso](#uso)
- [Opciones](#opciones)
- [Seguridad](#seguridad)
- [Respaldo y Restauración](#respaldo-y-restauración)
- [Casos de Uso Comunes](#casos-de-uso-comunes)
- [Solución de Problemas](#solución-de-problemas)

---

## 🚀 Instalación

### Método 1: Desde GitHub

```bash
cd /path/to/your/frappe-bench
bench get-app https://github.com/cegomezpy/frappe_helpers
bench --site <nombre-del-sitio> install-app frappe_helpers
```

### Método 2: Instalación Local

```bash
cd /path/to/your/frappe-bench
bench get-app /path/to/frappe_helpers
bench --site <nombre-del-sitio> install-app frappe_helpers
```

### Verificar Instalación

```bash
bench --site <nombre-del-sitio> list-apps
# Debería aparecer frappe_helpers en la lista

bench --help | grep env-reset
# Debería mostrar el comando env-reset
```

---

## 🎯 ¿Qué hace?

El comando `env-reset` permite **limpiar un sitio de Frappe/ERPNext mientras preserva datos específicos**.

### Proceso paso a paso:

1. **Valida** que todos los DocTypes especificados existan
2. **Resuelve dependencias** automáticamente (campos Link, Table, Dynamic Link)
3. **Hace backup** del sitio completo (`sites/{sitio}/private/backups/`)
4. **Exporta** los registros seleccionados a JSON (`sites/{sitio}/private/env_reset_fixtures/`)
5. **Reinstala** el sitio (⚠️ **BORRA TODOS LOS DATOS**)
6. **Re-importa** los datos guardados en orden de dependencias

---

## 💻 Uso

### Uso Básico

```bash
bench --site misite.local env-reset \
  -s "Item" \
  -s "Item Group" \
  -s "Customer" \
  -s "Supplier"
```

### Dry Run (Ver qué se exportaría sin hacer cambios)

```bash
bench --site misite.local env-reset \
  -s "Item" \
  -s "Customer" \
  --dry-run
```

**Salida de ejemplo:**
```
╔══════════════════════════════════════╗
║       Frappe Env Reset Tool          ║
╚══════════════════════════════════════╝

✓ Todos los 2 DocType(s) validados
✓ 2 solicitados  +  4 dependencias auto-resueltas

   Plan de exportación (en orden de importación):
     [dependencia]  UOM
     [dependencia]  Item Group
     [dependencia]  Brand
     [dependencia]  Customer Group
     [solicitado]   Item
     [solicitado]   Customer

── DRY RUN — no se realizaron cambios ──────────
```

### Sin Resolver Dependencias

```bash
bench --site misite.local env-reset \
  -s "Item" \
  --no-deps
```

### Sin Backup (más rápido, pero arriesgado)

```bash
bench --site misite.local env-reset \
  -s "Item" \
  --skip-backup
```

⚠️ **NO recomendado en producción**

### Directorio Personalizado

```bash
bench --site misite.local env-reset \
  -s "Item" \
  -o /tmp/mis_fixtures
```

---

## ⚙️ Opciones

| Opción | Corto | Descripción |
|--------|-------|-------------|
| `--save-tables TEXT` | `-s` | Nombre del DocType a preservar. **Requerido.** Repetir para múltiples. |
| `--output-dir PATH` | `-o` | Directorio personalizado para exports. Auto-nombrado si se omite. |
| `--skip-backup` | | Omitir el paso de backup del sitio. |
| `--no-deps` | | NO auto-resolver dependencias vinculadas. |
| `--dry-run` | | Mostrar plan de exportación sin hacer cambios. |

---

## 🔒 Seguridad

### ⚠️ ADVERTENCIA IMPORTANTE

Este comando **REINSTALA EL SITIO** lo que significa:
- ✅ Se hace backup automático antes de proceder
- ⚠️ **SE BORRAN TODOS LOS DATOS** del sitio
- ✅ Solo se restauran los DocTypes que especifiques
- ⚠️ **OPERACIÓN DESTRUCTIVA E IRREVERSIBLE**

### Antes de Ejecutar

1. **SIEMPRE usa --dry-run primero**
   ```bash
   bench --site misite.local env-reset -s "Item" --dry-run
   ```

2. **Verifica que haya espacio en disco**
   ```bash
   df -h sites/<nombre-sitio>/private/backups/
   ```

3. **Lista los backups existentes**
   ```bash
   ls -lh sites/<nombre-sitio>/private/backups/
   ```

4. **NO uses --skip-backup en producción**

5. **Confirma los DocTypes correctos**
   - Usa nombres de DocType como aparecen en Frappe
   - Ejemplo: "Item" no "tabItem"
   - Ejemplo: "Customer" no "customer"

---

## 💾 Respaldo y Restauración

### 📁 Ubicaciones de Archivos

#### Backups (automáticos)
```
sites/<nombre-sitio>/private/backups/
├── 20260613_150422-misite_local-database.sql.gz      # Base de datos
├── 20260613_150422-misite_local-files.tar            # Archivos públicos
└── 20260613_150422-misite_local-private-files.tar    # Archivos privados
```

#### Fixtures Exportados
```
sites/<nombre-sitio>/private/env_reset_fixtures/
└── env_reset_20260613_151341/
    ├── manifest.json      # Metadatos y orden de importación
    ├── Item.json
    ├── Customer.json
    └── ...
```

### 🔄 Comandos de Restauración

#### Ver Backups Disponibles

```bash
# Listar todos los backups (más reciente primero)
ls -lt sites/<nombre-sitio>/private/backups/ | head -10
```

#### Restaurar Solo Base de Datos

```bash
bench --site <nombre-sitio> restore \
  sites/<nombre-sitio>/private/backups/20260613_150422-misite_local-database.sql.gz
```

#### Restauración Completa (Base de Datos + Archivos)

```bash
# Base de datos
bench --site <nombre-sitio> restore \
  sites/<nombre-sitio>/private/backups/20260613_150422-misite_local-database.sql.gz

# Archivos públicos
bench --site <nombre-sitio> restore \
  --with-public-files sites/<nombre-sitio>/private/backups/20260613_150422-misite_local-files.tar

# Archivos privados
bench --site <nombre-sitio> restore \
  --with-private-files sites/<nombre-sitio>/private/backups/20260613_150422-misite_local-private-files.tar
```

### 🚨 Procedimiento de Recuperación de Emergencia

Si `env-reset` falla a mitad de ejecución:

#### Paso 1: Identificar el Backup Más Reciente

```bash
ls -lt sites/<nombre-sitio>/private/backups/ | head -5
```

#### Paso 2: Eliminar Sitio Corrupto

```bash
bench drop-site <nombre-sitio> --force
```

#### Paso 3: Recrear Sitio

```bash
bench new-site <nombre-sitio> \
  --mariadb-root-password <contraseña-root-mysql> \
  --admin-password <contraseña-admin>
```

#### Paso 4: Restaurar desde Backup

```bash
bench --site <nombre-sitio> restore \
  sites/<nombre-sitio>/private/backups/<backup-mas-reciente>.sql.gz
```

#### Paso 5: Verificar

```bash
bench --site <nombre-sitio> migrate
bench browse <nombre-sitio>
```

---

## 📚 Casos de Uso Comunes

### Caso 1: Limpiar Staging con Datos Maestros

**Objetivo**: Resetear staging pero mantener Items, Customers, Suppliers

```bash
bench --site staging.local env-reset \
  -s "Item" \
  -s "Item Group" \
  -s "Customer" \
  -s "Customer Group" \
  -s "Supplier" \
  -s "Supplier Group"
```

### Caso 2: Resetear Dev sin Transacciones

**Objetivo**: Mantener configuración y maestros, eliminar transacciones

```bash
bench --site dev.local env-reset \
  -s "Company" \
  -s "Warehouse" \
  -s "Cost Center" \
  -s "Item" \
  -s "Customer" \
  -s "Supplier" \
  -s "Account"
```

### Caso 3: Reseteo Rápido de Pruebas

**Objetivo**: Reseteo rápido en ambiente de pruebas (sin archivos)

```bash
# Sin backup de archivos (más rápido)
bench --site test.local env-reset \
  -s "Item" \
  --skip-backup  # ⚠️ Solo en test
```

### Caso 4: ERPNext Completo

**Objetivo**: Preservar todos los maestros en ERPNext

```bash
bench --site prod.local env-reset \
  -s "Item" \
  -s "Item Group" \
  -s "Item Price" \
  -s "Price List" \
  -s "Customer" \
  -s "Customer Group" \
  -s "Supplier" \
  -s "Supplier Group" \
  -s "Warehouse" \
  -s "Cost Center" \
  -s "Company" \
  -s "Account" \
  -s "Mode of Payment" \
  -s "Terms and Conditions"
```

---

## 🔍 Solución de Problemas

### Problema: "DocType no encontrado"

**Error:**
```
✗ Los siguientes DocTypes no fueron encontrados:
      • Itemm
```

**Solución:**
- Verifica el nombre exacto del DocType en Frappe
- Usa mayúsculas/minúsculas correctas
- Ejemplo correcto: "Item" no "item" o "Itemm"

### Problema: "No se puede conectar a MySQL"

**Error:**
```
Could not connect to MySQL
```

**Solución:**
```bash
# Verifica que los contenedores estén corriendo
docker-compose ps

# Reinicia los servicios
docker-compose restart

# Verifica conectividad
bench --site <nombre-sitio> console
```

### Problema: "Registros fallaron al importar"

**Salida:**
```
✅ Completado
   Importados: 5728 registros
   Fallidos: 1606 registros (revisar logs)
```

**Solución:**
- Los fallos son normales (duplicados, dependencias opcionales)
- Verifica logs en: `logs/frappe_helpers.import_service.log`
- Verifica que tus datos principales se importaron:
  ```bash
  bench --site <sitio> console
  frappe.db.count("Item")      # Debe mostrar cantidad correcta
  frappe.db.count("Customer")  # Debe mostrar cantidad correcta
  ```

### Problema: "Disco lleno"

**Error:**
```
No space left on device
```

**Solución:**
```bash
# Ver espacio disponible
df -h

# Limpiar backups antiguos (CUIDADO)
ls -lt sites/<sitio>/private/backups/ | tail -10  # Ver antiguos
rm sites/<sitio>/private/backups/<backup-antiguo>*  # Eliminar

# Limpiar fixtures antiguos
rm -rf sites/<sitio>/private/env_reset_fixtures/<directorio-antiguo>
```

---

## 📖 Documentación Adicional

- [README.md](README.md) - Documentación en Inglés
- [BACKUP_RESTORE.md](BACKUP_RESTORE.md) - Guía detallada de backup/restore
- [tests/README.md](frappe_helpers/tests/README.md) - Documentación de tests

---

## ⚡ Comandos Rápidos

```bash
# Ver ayuda
bench --site <sitio> env-reset --help

# Dry run (siempre primero)
bench --site <sitio> env-reset -s "Item" --dry-run

# Ejecución normal
bench --site <sitio> env-reset -s "Item" -s "Customer"

# Ver backups
ls -lh sites/<sitio>/private/backups/

# Ver fixtures
ls -lh sites/<sitio>/private/env_reset_fixtures/

# Restaurar desde backup
bench --site <sitio> restore sites/<sitio>/private/backups/<archivo>.sql.gz

# Ver logs
tail -f logs/frappe_helpers.*.log
```

---

## ✅ Checklist Pre-Ejecución

Antes de ejecutar `env-reset` en **producción**:

- [ ] ✅ Ejecuté `--dry-run` primero
- [ ] ✅ Verifiqué espacio en disco disponible
- [ ] ✅ Confirmé los nombres de DocTypes correctos
- [ ] ✅ Verifiqué que existe backup reciente manualmente
- [ ] ✅ Notifiqué al equipo sobre el downtime
- [ ] ✅ Tengo tiempo para verificar después
- [ ] ✅ NO usé `--skip-backup`
- [ ] ✅ Documenté qué DocTypes estoy preservando
- [ ] ✅ Tengo plan de rollback si falla

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisa los logs**: `logs/frappe_helpers.*.log`
2. **Verifica backups**: `ls sites/<sitio>/private/backups/`
3. **Consulta documentación**: [README.md](README.md)
4. **Reporta issues**: https://github.com/cegomezpy/frappe_helpers/issues

---

## 📝 Notas Importantes

- ⚠️ **SIEMPRE** usa `--dry-run` primero en producción
- ⚠️ **NUNCA** uses `--skip-backup` en producción
- ✅ Los backups se guardan automáticamente
- ✅ Los fixtures se guardan en el sitio, no en la app
- ✅ Las dependencias se resuelven automáticamente
- ✅ El orden de importación es automático (topological sort)

---

**Versión**: 1.0.0
**Licencia**: MIT
**Autor**: César Gómez (cegomezpy@gmail.com)

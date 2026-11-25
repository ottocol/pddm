
> **No es necesario que sigas estos pasos** en el ejercicio, pero sí es interesante que los leas para poder entender mejor el funcionamiento interno de Core Data.

Podemos examinar el almacenamiento persistente, que, como hemos visto en el código del `PersistenceController`, se configura por defecto como una base de datos SQLite con el mismo nombre del proyecto (en nuestro caso `NotasCoreData.sqlite`). La base de datos se crea por defecto en el directorio `Library/Application Support` del *sandbox*.

Para localizar el archivo tenemos varias opciones:

- Emplear alguna utilidad como [SimSim](https://github.com/dsmelov/simsim), que ya hemos usado en otras sesiones para localizar el directorio con el *sandbox* de nuestra aplicación.
- Buscarlo desde la terminal entre los datos de los simuladores:

```bash
find ~/Library/Developer/CoreSimulator/Devices -name "NotasCoreData.sqlite"
```

- Imprimir la URL desde la propia app, por ejemplo en el `init` del `PersistenceController`, después de `loadPersistentStores`:

```swift
print(container.persistentStoreDescriptions.first?.url ?? "sin URL")
```

> Un truco muy útil para depurar es activar los mensajes de *log* de Core Data: en Xcode ve a `Product > Scheme > Edit Scheme...`, sección `Run`, pestaña `Arguments`, y en `Arguments Passed On Launch` añade `-com.apple.CoreData.SQLDebug 1`. Al ejecutar la app verás en la consola la ruta de la base de datos y todas las sentencias SQL que Core Data va ejecutando.

Si abrimos la base de datos usando alguna utilidad gráfica o bien desde la terminal (moviéndonos al directorio donde está el `NotasCoreData.sqlite` y tecleando):

```bash
sqlite3 NotasCoreData.sqlite
```

Debería aparecer el *prompt* de SQLite donde podemos por ejemplo ver la estructura de la BD, tecleando

```bash
sqlite> .schema
```

Aparecerá algo como 

```sql
CREATE TABLE ZNOTA ( Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER, Z_OPT INTEGER,
  ZFECHA TIMESTAMP, ZTEXTO VARCHAR );
CREATE TABLE Z_PRIMARYKEY (Z_ENT INTEGER PRIMARY KEY, Z_NAME VARCHAR, Z_SUPER
  INTEGER, Z_MAX INTEGER);
CREATE TABLE Z_METADATA (Z_VERSION INTEGER PRIMARY KEY, Z_UUID VARCHAR(255),
  Z_PLIST BLOB);
```

(y alguna tabla interna más, como `Z_MODELCACHE`, según la versión de iOS).

Como se ve, Core Data crea automáticamente una tabla para la entidad `Nota`, con el mismo nombre (aunque precedida de una curiosa `Z`, como los nombres de los campos). Crea también una columna por cada propiedad, asignándoles el tipo apropiado. Además automáticamente crea una clave primaria, aunque en la entidad no hemos definido ninguna.

Podemos comprobar también si se ha guardado la nota ejecutando una sentencia SQL

```sql
sqlite> select * from ZNOTA;
```

> Las fechas no se ven en un formato legible: Core Data las guarda como el número de segundos transcurridos desde el 1 de enero de 2001.

> Desde iOS 7 Core Data usa un modo de SQLite llamado *Write-Ahead Logging* (WAL). En este modo los cambios se escriben primero en un archivo aparte, `NotasCoreData.sqlite-wal`, y solo de vez en cuando se trasladan al archivo principal. Si abrimos la base de datos en su directorio original, `sqlite3` tiene en cuenta el `-wal` y veremos los datos actualizados. Pero si copiamos solo el archivo `.sqlite` a otro sitio, o lo abrimos con alguna herramienta que ignore el `-wal`, puede que no aparezcan los últimos cambios. Si queremos copiar la base de datos hay que copiar siempre los tres archivos (`.sqlite`, `.sqlite-wal` y `.sqlite-shm`).

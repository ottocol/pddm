
> **No es necesario que sigas estos pasos** en el ejercicio, pero sí es interesante que los leas para poder entender mejor el funcionamiento interno de Core Data.

Podemos examinar el almacenamiento persistente, que como ya hemos visto el código Swift del *delegate*, se configura por defecto como una base de datos SQLite con el mismo nombre del proyecto. Podemos localizar el archivo tecleando desde la terminal:

```bash
find . -name MisNotas.sqlite -print
```

o más sencillo, emplear alguna utilidad como [SimSim](https://github.com/dsmelov/simsim/releases), que ya hemos usado en otras sesiones para localizar el directorio con el *sandbox* de nuestra aplicación. La base de datos se crea por defecto en el directorio `Library/Application Support` del *sandbox*.

Si abrimos la base de datos usando alguna utilidad gráfica o bien desde la terminal (moviéndose al directorio donde está el `MisNotas.sqlite` y tecleando:)

```bash
sqlite3 MisNotas.sqlite
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

Como se ve, Core Data crea automáticamente una tabla para la entidad `Nota`, con el mismo nombre (aunque precedida de una curiosa `Z`, como los nombres de los campos). Crea también una columna por cada propiedad, asignándoles el tipo apropiado. Además automáticamente crea una clave primaria, aunque en la entidad no hemos definido ninguna.

Podemos comprobar también si se ha guardado la nota ejecutando una sentencia SQL

```sql
sqlite> select * from ZNOTA;
```

> Es posible que el `select` anterior no muestre los registros actualizados, ya que a partir de iOS7 se usa un modo de SQLite que se llama "Write Ahead Logging".  En este modo, las transacciones para las que no se ha hecho *commit* se almacenan en un archivo `.wal` aparte. 

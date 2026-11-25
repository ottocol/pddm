
Se conocen como migraciones *ligeras* aquellas en las que Core Data puede deducir por sí mismo cómo migrar los datos a la nueva versión del modelo. Típicamente comprenden estas operaciones:

- Añadir o eliminar un atributo o una relación
- Convertir en opcional un atributo obligatorio
- Convertir en obligatorio un atributo opcional, siempre que tenga un valor por defecto
- Cambiar una relación "a uno" por una "a muchos"
- Añadir o eliminar una entidad
- Renombrar un atributo, una relación o una entidad (como veremos, hay que ayudarle un poco)

Si usamos `NSPersistentContainer` para inicializar el *stack* de Core Data, como hace la plantilla de Xcode, las migraciones ligeras están activadas por defecto: al arrancar la app con una nueva versión del modelo, Core Data migra automáticamente los datos sin que tengamos que escribir código. Además, con SQLite se hacen directamente sobre la base de datos (más o menos como un `ALTER TABLE`), así que son muy rápidas aunque haya muchos datos.

## Un ejemplo

Supongamos que en la app de mensajería queremos hacer estos cambios:

1. Poder archivar conversaciones: añadimos a `Conversacion` un atributo `archivada` de tipo `Boolean`, no opcional, con valor por defecto `NO`.
2. Cambiar el nombre del atributo `titulo` de `Conversacion` por `asunto`, que nos parece más adecuado.

Los pasos serían:

1. Guardar un punto de restauración con los datos actuales, como se explica en la sección anterior.
2. Crear una nueva versión del modelo (`Editor > Add Model Version...`) y hacerla la versión actual.
3. En la **nueva** versión, hacer los cambios.
4. Ejecutar la app (con el punto de restauración activado, para poder repetir la prueba) y comprobar que los datos se han migrado correctamente.

### Añadir un atributo

Al añadir un atributo a una entidad, los objetos que ya existían quedarán sin valor (`nil`). Si el atributo no es opcional, debe tener un valor por defecto, que Core Data asignará a todos los objetos existentes. En el ejemplo, todas las conversaciones que ya existían quedarán como no archivadas. Normalmente es la mejor solución.

### Renombrar un atributo

Si simplemente cambiamos el nombre de `titulo` por `asunto` en la nueva versión del modelo, Core Data no sabe que es un renombrado: lo que ve es que en la versión antigua había un atributo `titulo` que ya no existe, y en la nueva hay un atributo `asunto` que antes no existía. Lo interpretará como la eliminación de un atributo y la creación de otro, así que **los títulos de todas las conversaciones se perderán**. Tiene sentido si pensamos que Core Data solo ve las dos versiones del modelo, no lo que hemos hecho en el editor para pasar de una a otra.

Para indicarle que es el mismo atributo con otro nombre, seleccionamos el atributo `asunto` en la nueva versión del modelo y, en el `Data Model Inspector`, escribimos el nombre antiguo (`titulo`) en el campo `Renaming ID`. Core Data usará esta información para deducir que tiene que conservar los valores.

![](img/renaming%20id.png)

### Actualizar el código

Al renombrar un atributo, las clases generadas por Xcode cambian, así que el código que usaba `titulo` dejará de compilar. Los errores del compilador nos indicarán dónde tenemos que cambiarlo.

!!! warning "Los nombres en cadenas no los detecta el compilador"
    Hay sitios donde el nombre del atributo aparece dentro de una cadena: predicados (`"titulo CONTAINS[cd] %@"`), *sort descriptors* creados con una cadena (`NSSortDescriptor(key: "titulo", ...)`)... El compilador no los revisa, así que la app compilará sin errores pero **se cerrará en tiempo de ejecución** al usarlos. Hay que buscarlos a mano en todo el proyecto (`Find > Find in Project...`, o `Shift+Cmd+F`). Este es un buen motivo para usar siempre que se pueda `#keyPath` y los *key paths* de Swift (como en `NSSortDescriptor(keyPath: \Conversacion.titulo, ascending: true)` o en el `sectionIdentifier` de `@SectionedFetchRequest`): con ellos, el compilador sí detecta el cambio.

## ¿Qué pasa si la migración ligera no es posible?

Si el cambio no es uno de los que Core Data puede deducir automáticamente (por ejemplo, si cambiamos el tipo de un atributo de `String` a `Integer 32`), al arrancar, `loadPersistentStores` devolverá un error y, con el código de la plantilla de Xcode, la app se cerrará en el `fatalError`. En ese caso tendremos que hacer una migración manual, que veremos en la siguiente sección.

> Para ver en la consola qué está haciendo Core Data durante la migración, podemos añadir el argumento de lanzamiento `-com.apple.CoreData.MigrationDebug 1` (en `Product > Scheme > Edit Scheme...`, igual que los del punto de restauración).

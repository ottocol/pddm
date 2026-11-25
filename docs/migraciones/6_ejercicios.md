
# Ejercicio de migraciones de datos (0.5 puntos)

Vamos a hacer dos migraciones sobre el modelo de datos de (¡cómo no!) la aplicación de notas: primero una ligera y después una manual.

> Antes de empezar, haz un `commit` con el mensaje `terminada presencial 2`, para poder volver al estado actual del código si lo necesitas.

## Preparar el punto de restauración (0.1 puntos)

- Añade al proyecto el archivo `PuntoRestauracion.swift` y el código del `PersistenceController` de la sección de probar migraciones, cambiando el nombre de la base de datos por el de tu proyecto.
- Añade en el esquema de ejecución los argumentos de lanzamiento `-guardarPunto` y `-restaurarPunto`, ambos desactivados.
- Ejecuta la app (sin argumentos) y asegúrate de tener datos de prueba variados: varias libretas, notas en distintas libretas, alguna nota sin libreta, notas de **varias líneas** y alguna nota con el texto **vacío**. Los necesitarás para comprobar bien las migraciones. Las 10.000 notas que importaste en la sesión de concurrencia ya incluyen notas de varias líneas y algunas vacías; si no las tienes, impórtalas ahora.
- Ejecuta la app una vez con `-guardarPunto` activado y comprueba en la consola que se ha guardado el punto de restauración. Desactiva el argumento.

## Migración ligera (0.15 puntos)

Vamos a hacer dos cambios en el modelo:

- Cambiar el nombre del atributo `texto` de `Nota` por `contenido`.
- Añadir a `Nota` un atributo `favorita` de tipo `Boolean`, no opcional, con valor por defecto `NO`.

Para ello:

1. Crea una nueva versión del modelo, hazla la versión actual y haz en ella los dos cambios. **No pongas todavía el *Renaming ID*.**
2. Actualiza el código para que compile: los errores del compilador te indicarán dónde. No olvides los sitios donde el nombre del atributo aparece en una cadena, como el predicado de la búsqueda, que el compilador no detecta.
3. Ejecuta con `-restaurarPunto` activado. ¿Qué ha pasado con el contenido de las notas?
4. Ahora pon el *Renaming ID* que corresponda y vuelve a ejecutar, también con `-restaurarPunto`. Comprueba que esta vez las notas conservan su contenido, siguen en sus libretas, y que la búsqueda funciona.
5. Cuando todo funcione, desactiva `-restaurarPunto`.

En la entrega, explica en un par de líneas qué ocurrió en el paso 3 y por qué. Comprueba también, abriendo la base de datos como se explica en el apéndice de la primera sesión de Core Data, qué valor tiene la columna de `favorita` en las notas que ya existían.

## Migración manual (0.25 puntos)

Queremos que cada nota tenga un **título**, que será la primera línea de su contenido. Así podremos mostrarlo en la lista en lugar del contenido completo.

> Podríamos pensar en calcular el título con una propiedad calculada en una extensión de `Nota`. Pero recuerda que en los predicados y en la ordenación de las consultas solo se pueden usar atributos del modelo, y queremos poder buscar y ordenar por título en el futuro. Por eso lo guardaremos como un atributo más.

Los requisitos son:

- Añadir a `Nota` un atributo `titulo` de tipo `String`.
- Al migrar, el título de cada nota existente debe ser la primera línea no vacía de su contenido, sin espacios al principio ni al final. Si el contenido está vacío, el título será "Sin título".
- Las notas nuevas que se creen en la app después de la migración (tanto desde la pantalla de nueva nota como al importarlas) también deben tener su título, calculado con el mismo criterio. Procura no repetir el código que lo calcula (por ejemplo, puedes escribirlo como una función en una extensión de `String`, que puedes usar tanto desde la *migration policy* como desde el resto de la app).
- En la lista de notas debe aparecer el título de cada nota.

Para ello:

1. Como vas a hacer un nuevo cambio en el modelo, **guarda un nuevo punto de restauración** con los datos ya migrados a la versión anterior.
2. Crea una nueva versión del modelo con el nuevo atributo y hazla la versión actual.
3. Crea un *mapping model* de la versión anterior a la nueva, y una *migration policy* que calcule el título. Recuerda configurar en el *mapping model* la *custom policy*.
4. Prueba la migración con `-restaurarPunto` tantas veces como necesites hasta que funcione correctamente. Con miles de notas, la migración manual tardará unos segundos en arrancar la app: es normal, y es una buena forma de comprobar que estas migraciones son mucho más costosas que las ligeras.

Comprueba que tras la migración:

- Las notas de varias líneas tienen como título su primera línea.
- Las notas vacías tienen como título "Sin título".
- Las notas siguen en sus libretas, y las secciones de la lista siguen funcionando.
- Las notas que creas después de la migración tienen título.

> Si al ejecutar la app Core Data no usa tu *mapping model* (por ejemplo, los títulos quedan vacíos), revisa la sección de migraciones manuales: probablemente has modificado el modelo después de crear el *mapping model*, o falta el nombre del módulo en la *custom policy*.

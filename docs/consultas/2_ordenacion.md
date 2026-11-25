
Hasta el momento hemos obtenido los resultados en el orden en que nos los da Core Data, que no asegura ningún orden específico (salvo en las relaciones ordenadas). Para indicar cómo queremos ordenar los resultados de una *fetch request* usaremos la clase `NSSortDescriptor`. Al igual que `NSPredicate`, esta clase no es propia de Core Data sino de Foundation.

Por ejemplo, para obtener los usuarios ordenados de más a menos créditos, y a igualdad de créditos, por orden alfabético de *login*:

```swift
let request: NSFetchRequest<Usuario> = Usuario.fetchRequest()
let credSort = NSSortDescriptor(key: "creditos", ascending: false)
let loginSort = NSSortDescriptor(key: "login", ascending: true)
request.sortDescriptors = [credSort, loginSort]
let usuarios = try miContexto.fetch(request)
```

Cada `NSSortDescriptor` indica el atributo por el que ordenar y si el orden es ascendente o descendente. Para usarlos, asignamos un array de ellos a la propiedad `sortDescriptors` de la *fetch request*. Son los mismos que le pasamos a `@FetchRequest` en el parámetro `sortDescriptors`, como hicimos en la lista de notas. El orden en el array especifica la prioridad: primero se ordena por el primer criterio, y solo se usa el segundo para "desempatar".

Como en los predicados, el nombre del atributo es una cadena y si nos equivocamos al escribirlo no nos enteraremos hasta ejecutar la consulta. Para evitarlo podemos usar un *key path* de Swift, que comprueba el compilador:

```swift
let credSort = NSSortDescriptor(keyPath: \Usuario.creditos, ascending: false)
```

## Ordenar cadenas correctamente

Por defecto las cadenas se ordenan distinguiendo mayúsculas y minúsculas y sin tener en cuenta el idioma, lo que puede dar resultados poco naturales: por ejemplo, las mayúsculas van antes que todas las minúsculas ("Zaragoza" antes que "alicante") y las letras acentuadas van al final ("Ávila" después de "Zamora"). Para ordenar como espera el usuario hay que indicar un método de comparación que tenga en cuenta el idioma:

```swift
let loginSort = NSSortDescriptor(key: "login", ascending: true,
                    selector: #selector(NSString.localizedCaseInsensitiveCompare(_:)))
```

> Como la consulta la ejecuta la base de datos, solo se pueden usar algunos métodos de comparación: `compare(_:)` (el de por defecto), `caseInsensitiveCompare(_:)`, `localizedCompare(_:)`, `localizedCaseInsensitiveCompare(_:)` y `localizedStandardCompare(_:)`.

## Ordenar y limitar

Combinando la ordenación con la propiedad `fetchLimit` que vimos en la sección anterior podemos obtener "los N primeros" según algún criterio. Por ejemplo, los 20 mensajes más recientes de un usuario `u`:

```swift
let request: NSFetchRequest<Mensaje> = Mensaje.fetchRequest()
request.predicate = NSPredicate(format: "usuario == %@", argumentArray: [u])
request.sortDescriptors = [NSSortDescriptor(key: "fecha", ascending: false)]
request.fetchLimit = 20
let recientes = try miContexto.fetch(request)
```

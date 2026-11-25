
!!! info "Material de ampliación"
    Esta sección es una lectura de ampliación, sin ejercicios. Su objetivo es que conozcas SwiftData y sepas relacionarlo con todo lo que has aprendido de Core Data.

## ¿Qué es SwiftData?

Desde iOS 17 (Xcode 15), Apple ofrece **SwiftData**, un *framework* de persistencia pensado para Swift y SwiftUI. Internamente se apoya en Core Data (de hecho, por defecto también guarda los datos en una base de datos SQLite), pero su API es muy distinto:

- **El modelo se define en código Swift**, con clases normales marcadas con `@Model`, en lugar de en el editor visual del `.xcdatamodeld`.
- No hay que inicializar el *stack*: basta con un modificador en la estructura principal de la app.
- Las consultas usan *key paths* y expresiones Swift comprobadas por el compilador, en lugar de cadenas.
- Los cambios se guardan automáticamente.

Lo importante es que **los conceptos son los mismos que en Core Data**: un modelo con entidades, atributos y relaciones, un contexto en el que se crean, modifican y borran los objetos, consultas con condiciones y ordenación, migraciones, y las mismas reglas de concurrencia. Si has entendido Core Data, aprender SwiftData es sobre todo aprender una sintaxis nueva.

## El modelo de mensajería en SwiftData

Así se definirían dos de las entidades del ejemplo de mensajería:

```swift
import SwiftData

@Model
final class Usuario {
    @Attribute(.unique) var login: String
    var creditos: Int
    var fechaAlta: Date
    @Relationship(deleteRule: .deny, inverse: \Mensaje.usuario)
    var mensajes: [Mensaje] = []

    init(login: String, creditos: Int = 0, fechaAlta: Date = .now) {
        self.login = login
        self.creditos = creditos
        self.fechaAlta = fechaAlta
    }
}

@Model
final class Mensaje {
    var texto: String
    var fecha: Date
    var usuario: Usuario?

    init(texto: String, fecha: Date = .now) {
        self.texto = texto
        self.fecha = fecha
    }
}
```

Fíjate en las diferencias con Core Data:

- Los atributos son propiedades Swift normales. Si no son opcionales en Swift, tampoco lo son en el modelo, y ya no hay que lidiar con los opcionales "artificiales" de las clases generadas por Core Data.
- Las relaciones "a muchos" son arrays de Swift, no `NSSet`, y se modifican como cualquier array: `usuario.mensajes.append(mensaje)`.
- Los objetos se crean con su inicializador, como cualquier otra clase. Al insertarlos en el contexto pasan a estar gestionados.
- Las *delete rules*, las restricciones de valores únicos y las relaciones inversas se indican con `@Relationship` y `@Attribute`.

## El contenedor y el contexto

En lugar del `PersistenceController`, basta con indicar en la estructura principal de la app qué clases forman el modelo:

```swift
@main
struct MensajeriaApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Usuario.self, Mensaje.self])
    }
}
```

Y en las vistas, el contexto se obtiene del entorno, como en Core Data:

```swift
@Environment(\.modelContext) private var contexto
```

Para crear un objeto, lo creamos con su inicializador y lo insertamos en el contexto. Para borrarlo, igual que en Core Data, se lo pedimos al contexto:

```swift
let mensaje = Mensaje(texto: "Hola")
mensaje.usuario = usuario
contexto.insert(mensaje)

contexto.delete(otroMensaje)
```

Por defecto, **SwiftData guarda automáticamente** los cambios del contexto principal cada cierto tiempo y cuando la app pasa a segundo plano. Podemos guardar en un momento concreto con `try contexto.save()`, como en Core Data.

Para las *previews*, el equivalente a la base de datos en memoria del `PersistenceController` es:

```swift
#Preview {
    MensajesView()
        .modelContainer(for: [Usuario.self, Mensaje.self], inMemory: true)
}
```

## Consultas

El equivalente a `@FetchRequest` es `@Query`, y en lugar de `NSPredicate` se usa la macro `#Predicate`, en la que la condición se escribe como una expresión Swift:

```swift
struct MensajesView: View {
    @Query(filter: #Predicate<Mensaje> { mensaje in
               mensaje.texto.localizedStandardContains("iOS")
           },
           sort: \Mensaje.fecha, order: .reverse)
    private var mensajes: [Mensaje]

    var body: some View {
        List(mensajes) { mensaje in
            Text(mensaje.texto)
        }
    }
}
```

Igual que con `@FetchRequest`, la vista se actualiza automáticamente cuando cambian los datos. Y como la condición es código Swift, **el compilador comprueba los nombres de los atributos**: si renombramos `texto`, la consulta dejará de compilar en lugar de cerrar la app en tiempo de ejecución. `localizedStandardContains` equivale al `CONTAINS[cd]` de los predicados de Core Data.

Las consultas que dependen de un parámetro se crean en el inicializador de la vista, exactamente igual que vimos con `@FetchRequest`:

```swift
init(usuario: Usuario) {
    let login = usuario.login
    _mensajes = Query(filter: #Predicate<Mensaje> { $0.usuario?.login == login },
                      sort: \Mensaje.fecha)
}
```

## Migraciones y concurrencia

**Migraciones.** Las migraciones ligeras son automáticas, como en Core Data. Para el resto, en lugar de versiones del `.xcdatamodeld`, *mapping models* y *migration policies*, cada versión del modelo se describe en código con un `VersionedSchema`, y las migraciones entre versiones con un `SchemaMigrationPlan`, en el que podemos escribir código que transforme los datos antes y después de migrar.

**Concurrencia.** Las reglas son las mismas que en Core Data: el contexto de las vistas (`mainContext`) pertenece al hilo principal, los objetos no se pueden pasar de un contexto a otro (se pasa su identificador, de tipo `PersistentIdentifier`, el equivalente al `objectID`), y el trabajo pesado se hace en otro contexto. Para esto último, SwiftData ofrece la macro `@ModelActor`, que crea un actor con su propio contexto, integrado con la concurrencia de Swift que vimos en la sesión anterior.

## Equivalencias

| Core Data | SwiftData |
|---|---|
| Archivo `.xcdatamodeld` y editor visual | Clases con `@Model` |
| Entidad | Clase `@Model` |
| `NSManagedObject` | Objeto de una clase `@Model` |
| `NSPersistentContainer` | `ModelContainer` |
| `NSManagedObjectContext` | `ModelContext` |
| `@FetchRequest` | `@Query` |
| `NSPredicate` (cadena) | `#Predicate` (código Swift) |
| `NSSortDescriptor` | `SortDescriptor` o *key path* en `@Query` |
| Restricción de valores únicos | `@Attribute(.unique)` |
| Relación "a muchos" (`NSSet`) | Array |
| `objectID` | `persistentModelID` |
| Contexto en segundo plano | Actor con `@ModelActor` |
| Versiones del modelo y *mapping model* | `VersionedSchema` y `SchemaMigrationPlan` |

## ¿Core Data o SwiftData?

SwiftData es claramente el futuro, y su código es mucho más sencillo y seguro. Pero conviene tener en cuenta algunas cosas antes de elegirlo:

- **Solo funciona a partir de iOS 17.** Una app que tenga que funcionar en versiones anteriores tiene que usar Core Data.
- **Es un *framework* joven.** La primera versión, la de iOS 17, tiene limitaciones y algunos errores conocidos, y varias funcionalidades importantes (como los índices) no llegaron hasta iOS 18. Por ejemplo, no tiene un equivalente a `@SectionedFetchRequest`: para mostrar una lista con secciones hay que agrupar los resultados nosotros.
- **Algunos comportamientos son distintos.** Por ejemplo, con `@Attribute(.unique)`, si insertamos un objeto con un valor que ya existe, SwiftData no da un error, sino que **actualiza** el objeto existente con los valores del nuevo (lo que en Core Data sería la *merge policy* `mergeByPropertyObjectTrump`). El ejercicio de nombres de libreta únicos funcionaría de forma muy distinta.
- **La inmensa mayoría de apps existentes usan Core Data**, y lo seguirán usando durante años. Si trabajáis en una de ellas, es lo que tendréis que mantener.

En cualquier caso, lo que habéis aprendido en estas sesiones sirve para ambos: el modelo de datos, el contexto, las consultas, las migraciones y las reglas de concurrencia son los mismos conceptos con distinta sintaxis.

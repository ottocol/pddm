
En las secciones anteriores hemos ejecutado las *fetch requests* con el método `fetch` del contexto, que nos devuelve un array con los resultados. Pero, como vimos en la primera sesión de Core Data, para mostrar los resultados de una consulta en una vista es mucho más cómodo usar `@FetchRequest`: SwiftUI ejecuta la consulta y redibuja la vista cada vez que cambian los datos. En esta sección veremos cómo usar con `@FetchRequest` todo lo que sabemos de consultas, y algunas posibilidades más.

Seguiremos con el ejemplo de la aplicación de mensajería.

## Consultas con predicado

Además de los criterios de ordenación, a `@FetchRequest` le podemos pasar un predicado:

```swift
struct MensajesRecientesView: View {
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \Mensaje.fecha, ascending: false)],
                  predicate: NSPredicate(format: "fecha > %@", argumentArray: [Date(timeIntervalSinceNow: -24*60*60)]),
                  animation: .default)
    private var mensajes: FetchedResults<Mensaje>

    var body: some View {
        List(mensajes) { mensaje in
            Text(mensaje.texto ?? "")
        }
    }
}
```

El parámetro `animation` es opcional: indica que cuando cambien los resultados (porque se crea, modifica o borra un mensaje), las filas aparezcan, desaparezcan o se muevan con una animación.

## Cambiar la consulta

Muchas veces la consulta no es fija: depende, por ejemplo, de lo que escriba el usuario en un buscador. No hace falta crear una nueva `@FetchRequest`: podemos cambiar el predicado o los criterios de ordenación de una ya existente a través de las propiedades `nsPredicate` y `nsSortDescriptors` de los resultados. SwiftUI volverá a ejecutar la consulta y redibujará la vista:

```swift
struct BuscarMensajesView: View {
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \Mensaje.fecha, ascending: false)])
    private var mensajes: FetchedResults<Mensaje>

    var body: some View {
        VStack {
            Button("Solo los que hablan de iOS") {
                mensajes.nsPredicate = NSPredicate(format: "texto CONTAINS[cd] %@", argumentArray: ["iOS"])
            }
            Button("Todos") {
                mensajes.nsPredicate = nil
            }
            List(mensajes) { mensaje in
                Text(mensaje.texto ?? "")
            }
        }
    }
}
```

Fíjate en que para mostrar todos los mensajes basta con poner el predicado a `nil`.

## Consultas que dependen de un parámetro

Otro caso habitual es una vista que muestra datos relacionados con un objeto que recibe como parámetro. Por ejemplo, una pantalla de detalle de una conversación con sus mensajes. Aquí la consulta depende de la conversación, así que no la podemos escribir en la declaración de la propiedad: la creamos en el inicializador de la vista.

```swift
struct ConversacionView: View {
    @FetchRequest private var mensajes: FetchedResults<Mensaje>

    init(conversacion: Conversacion) {
        _mensajes = FetchRequest(
            sortDescriptors: [NSSortDescriptor(keyPath: \Mensaje.fecha, ascending: true)],
            predicate: NSPredicate(format: "conversacion == %@", argumentArray: [conversacion]))
    }

    var body: some View {
        List(mensajes) { mensaje in
            Text(mensaje.texto ?? "")
        }
    }
}
```

> El guion bajo de `_mensajes` sirve para acceder al *property wrapper* en sí (la `FetchRequest`), y no a su valor (los resultados). Es la forma de inicializar un *property wrapper* en el inicializador de la vista.

En este ejemplo podríamos haber accedido a los mensajes directamente a través de la relación, con `conversacion.mensajes`. Pero entonces la vista no se actualizaría sola cuando llegara un mensaje nuevo, y tendríamos que hacer el *cast* de `NSOrderedSet` y ordenar nosotros.

## Secciones

Si queremos que una lista tenga secciones, usaremos `@SectionedFetchRequest` en lugar de `@FetchRequest`. Le indicamos, además de los criterios de ordenación, el atributo a partir del cual se forman las secciones (`sectionIdentifier`): todos los objetos con el mismo valor irán en la misma sección. Por ejemplo, para agrupar los mensajes por el título de la conversación a la que pertenecen:

```swift
struct MensajesPorConversacionView: View {
    @SectionedFetchRequest(
        sectionIdentifier: \Mensaje.conversacion?.titulo,
        sortDescriptors: [
            //primero por conversación, para que se formen bien las secciones
            NSSortDescriptor(key: "conversacion.titulo", ascending: true),
            //y dentro de cada conversación, por fecha
            NSSortDescriptor(keyPath: \Mensaje.fecha, ascending: false)
        ])
    private var secciones: SectionedFetchResults<String?, Mensaje>

    var body: some View {
        List {
            ForEach(secciones) { seccion in
                Section(seccion.id ?? "Sin conversación") {
                    ForEach(seccion) { mensaje in
                        Text(mensaje.texto ?? "")
                    }
                }
            }
        }
    }
}
```

Veamos los detalles:

- Como `conversacion` es opcional, el identificador de sección es de tipo `String?`, y así lo indicamos en el tipo de los resultados: `SectionedFetchResults<String?, Mensaje>`. Los mensajes que no pertenecen a ninguna conversación forman una sección cuyo identificador es `nil`, a la que en la vista le damos el título "Sin conversación".
- Los resultados son una colección de secciones. Cada sección tiene un identificador (`id`), que es el valor del atributo, y es a su vez una colección con los objetos de esa sección.
- Las secciones se van formando recorriendo los resultados **en el orden de la consulta**, empezando una nueva sección cada vez que cambia el valor del atributo. Si ordenáramos los mensajes solo por fecha, los de distintas conversaciones estarían mezclados y obtendríamos secciones repetidas y desordenadas. Por eso **el primer criterio de ordenación debe ser el mismo atributo que usamos para las secciones**. Dentro de cada sección, podemos ordenar por lo que queramos con los criterios siguientes.

> Si dos conversaciones distintas tuvieran el mismo título, sus mensajes acabarían en la misma sección. Las secciones se forman por el valor del atributo, no por el objeto relacionado.

!!! note "Nuevo en SwiftUI: `Section` y `ForEach` dentro de `List`"
    Hasta ahora hemos creado las listas pasándoles directamente los datos (`List(mensajes) { ... }`). Para listas más complejas, `List` también puede contener vistas, igual que un `VStack`. Dentro de ella, `ForEach` genera una fila por cada elemento de una colección, y `Section` agrupa filas bajo un título.

Las propiedades `nsPredicate` y `nsSortDescriptors` también existen en los resultados de `@SectionedFetchRequest`, así que podemos cambiar la consulta igual que antes.

## Borrar filas

Para que el usuario pueda borrar filas de una lista con el gesto de deslizar hacia la izquierda, se usa el modificador `.onDelete` sobre el `ForEach` de las filas. Recibe las posiciones de las filas a borrar:

```swift
struct MensajesView: View {
    @Environment(\.managedObjectContext) private var contexto
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \Mensaje.fecha, ascending: false)],
                  animation: .default)
    private var mensajes: FetchedResults<Mensaje>

    var body: some View {
        List {
            ForEach(mensajes) { mensaje in
                Text(mensaje.texto ?? "")
            }
            .onDelete { posiciones in
                for posicion in posiciones {
                    contexto.delete(mensajes[posicion])
                }
                try? contexto.save()
            }
        }
    }
}
```

Fíjate en que **no quitamos la fila de la lista**: borramos el objeto del contexto, y como la lista muestra los resultados de una `@FetchRequest`, se actualiza sola.

> `.onDelete` solo se puede usar sobre un `ForEach`, por eso aquí no podemos crear la lista con `List(mensajes) { ... }`. En una lista con secciones, el `.onDelete` va en el `ForEach` de las filas de cada sección, y las posiciones que recibe son las de las filas dentro de esa sección.

## Eficiencia

`@FetchRequest` no carga todos los objetos en memoria: Core Data los va recuperando de la base de datos según se necesitan, y SwiftUI solo crea las filas que se ven en pantalla. Si hay muchos datos, podemos además indicar que los objetos se carguen por lotes. Para eso necesitamos crear nosotros la `NSFetchRequest`, por ejemplo en el inicializador de la vista:

```swift
init() {
    let request: NSFetchRequest<Mensaje> = Mensaje.fetchRequest()
    request.sortDescriptors = [NSSortDescriptor(keyPath: \Mensaje.fecha, ascending: false)]
    //cargar los mensajes de 50 en 50 según se vayan necesitando
    request.fetchBatchSize = 50
    _mensajes = FetchRequest(fetchRequest: request)
}
```

> Internamente, `@FetchRequest` usa un `NSFetchedResultsController`, la clase que se usa en UIKit para mostrar en una tabla los resultados de una consulta de Core Data y mantenerlos actualizados. En UIKit hay que crearla y configurarla a mano y escribir el código que actualiza la tabla cada vez que cambian los datos; en SwiftUI todo esto lo hace `@FetchRequest` por nosotros.

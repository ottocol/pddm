
Core Data añade sus propias reglas a todo lo que hemos visto. Las ilustraremos con la aplicación de mensajería de sesiones anteriores, suponiendo que queremos importar en una conversación una gran cantidad de mensajes descargados de un servidor.

## La regla de oro

Cada contexto de Core Data tiene asociada una **cola**: un hilo (o una secuencia de hilos) en el que debe ejecutarse todo el código que lo usa. La regla de oro de la concurrencia en Core Data es:

> **Un contexto, y los objetos que pertenecen a él, solo se pueden usar desde la cola de ese contexto.**

El `viewContext`, el que hemos usado hasta ahora, está asociado a la cola principal, es decir, al hilo principal. Por eso lo usamos desde las vistas, y por eso todo lo que hagamos con él ocupará el hilo principal. Si insertamos miles de objetos en el `viewContext`, la interfaz se bloqueará mientras tanto.

Si no respetamos la regla, Core Data no siempre da un error inmediato: muchas veces la app funcionará en las pruebas y fallará de forma aparentemente aleatoria más adelante, con datos corruptos o cierres inesperados. Más adelante veremos cómo detectar estos problemas.

## Contextos en segundo plano

Para hacer trabajo pesado con Core Data sin bloquear la interfaz, usaremos un **contexto en segundo plano**, asociado a una cola propia distinta de la principal. Lo creamos a partir del contenedor:

```swift
let contextoFondo = PersistenceController.shared.container.newBackgroundContext()
```

Y todo el código que use este contexto o sus objetos debe ir dentro de una llamada a su método `perform`, que se encarga de ejecutarlo en la cola del contexto. Desde código asíncrono, `perform` se puede esperar con `await`:

```swift
try await contextoFondo.perform {
    //aquí podemos usar contextoFondo y sus objetos
    let mensaje = Mensaje(context: contextoFondo)
    mensaje.texto = "Hola"
    mensaje.fecha = Date()
    try contextoFondo.save()
}
```

> El código dentro de `perform` no es asíncrono: no podemos usar `await` dentro. Es un bloque de código normal que Core Data ejecuta en la cola del contexto, y que puede lanzar errores (de ahí el `try` delante de `await`). Si el bloque devuelve un valor, `perform` lo devuelve también.

> Fíjate en el papel de cada cosa en el ejemplo de lotes de más abajo: el bucle se ejecuta en el `MainActor`, pero cada `await contextoFondo.perform` envía el trabajo pesado a la cola del contexto en segundo plano y deja libre el hilo principal mientras tanto.

> Una alternativa es `PersistenceController.shared.container.performBackgroundTask { contexto in ... }`, que crea un contexto en segundo plano nuevo y ejecuta el bloque en él.

## Los objetos no viajan entre contextos

Supongamos que queremos importar los mensajes en una conversación determinada, que el usuario ha elegido en la interfaz. Esa conversación es un objeto del `viewContext`, y por la regla de oro **no la podemos usar dentro del `perform` del contexto en segundo plano**: ni leer sus propiedades ni relacionarla con los mensajes nuevos. Si lo intentamos con la relación, Core Data lanzará una excepción (*Illegal attempt to establish a relationship between objects in different contexts*).

Lo que sí podemos pasar de un contexto a otro es el **identificador** del objeto, su `objectID`, que es el mismo en todos los contextos. En el otro contexto, el método `object(with:)` nos da "su versión" del objeto:

```swift
//en el hilo principal, con la conversación del viewContext
let idConversacion = conversacion.objectID

try await contextoFondo.perform {
    //la conversación, pero en el contexto en segundo plano
    let conversacionFondo = contextoFondo.object(with: idConversacion) as! Conversacion
    let mensaje = Mensaje(context: contextoFondo)
    mensaje.texto = "Hola"
    mensaje.fecha = Date()
    mensaje.conversacion = conversacionFondo
    try contextoFondo.save()
}
```

Lo mismo en sentido contrario: si queremos usar en la interfaz un objeto creado en segundo plano, pasaremos su `objectID` y obtendremos el objeto del `viewContext` con `object(with:)`.

> Los datos "normales" (cadenas, números, fechas, arrays y `struct`s formados por ellos) sí se pueden pasar sin problemas de un contexto a otro, ya que se copian.

## Importar por lotes

Si vamos a importar una cantidad grande de datos, conviene hacerlo **por lotes**: insertar unos cientos de objetos, guardar, y pasar al siguiente lote. Así no acumulamos en memoria miles de objetos sin guardar. Además, si el bucle que recorre los lotes es asíncrono, entre lote y lote podemos actualizar la interfaz (por ejemplo, para mostrar el progreso) o comprobar si la tarea se ha cancelado.

```swift
struct MensajeJSON: Codable {
    let texto: String
    let fecha: Date
}

//en el MainActor: así, entre lote y lote, podemos actualizar la interfaz
@MainActor
func importar(_ datos: [MensajeJSON], en conversacion: Conversacion) async throws {
    let contextoFondo = PersistenceController.shared.container.newBackgroundContext()
    let idConversacion = conversacion.objectID
    let tamanoLote = 500

    for inicio in stride(from: 0, to: datos.count, by: tamanoLote) {
        let lote = datos[inicio..<min(inicio + tamanoLote, datos.count)]
        try await contextoFondo.perform {
            let conversacionFondo = contextoFondo.object(with: idConversacion) as! Conversacion
            for dato in lote {
                let mensaje = Mensaje(context: contextoFondo)
                mensaje.texto = dato.texto
                mensaje.fecha = dato.fecha
                mensaje.conversacion = conversacionFondo
            }
            try contextoFondo.save()
            //liberamos la memoria de los objetos ya guardados
            contextoFondo.reset()
        }
        //aquí, entre lote y lote, estamos de nuevo en el hilo principal:
        //podríamos actualizar la interfaz o comprobar si nos han cancelado
    }
}
```

> El método `reset()` hace que el contexto "olvide" todos sus objetos, liberando la memoria. Después de llamarlo, los objetos que tuviéramos de ese contexto dejan de ser válidos. Por eso obtenemos `conversacionFondo` de nuevo en cada lote.

## Cómo llegan los cambios a la interfaz

Cuando guardamos el contexto en segundo plano, los cambios se escriben en la base de datos. Pero el `viewContext` es otro contexto, con sus propios objetos en memoria: ¿cómo se entera de los cambios?

Aquí entra la línea del `PersistenceController` que dejamos pendiente en la primera sesión de Core Data:

```swift
container.viewContext.automaticallyMergesChangesFromParent = true
```

Con esta opción activada, cada vez que otro contexto del mismo contenedor guarda cambios, el `viewContext` los incorpora automáticamente. Y como las vistas con `@FetchRequest` se actualizan cuando cambian los datos del `viewContext`, **la interfaz reflejará los mensajes importados sin que tengamos que hacer nada**.

> El nombre de la propiedad es un poco engañoso: el "padre" del `viewContext` no es otro contexto, sino el almacenamiento persistente. Lo que hace es incorporar los cambios que cualquier contexto guarde en él.

### Conflictos

Si el mismo objeto se modifica a la vez en dos contextos distintos y ambos lo guardan, el segundo `save` encontrará que el objeto ha cambiado desde que lo leyó. Qué ocurre entonces lo decide la *merge policy* del contexto, que vimos con las restricciones de valores únicos: por defecto, el `save` dará un error. Si preferimos que prevalezcan los cambios del contexto que guarda, podemos cambiar la política del contexto en segundo plano:

```swift
contextoFondo.mergePolicy = NSMergePolicy.mergeByPropertyObjectTrump
```

## Detectar errores de concurrencia

Como hemos dicho, los errores de concurrencia en Core Data pueden pasar desapercibidos durante las pruebas. Para detectarlos, Core Data tiene un modo de depuración que hace que la app **se cierre inmediatamente** en cuanto se usa un contexto o uno de sus objetos desde una cola que no es la suya, indicando en qué línea.

Para activarlo, en `Product > Scheme > Edit Scheme...`, sección `Run`, pestaña `Arguments`, añade a `Arguments Passed On Launch`:

```
-com.apple.CoreData.ConcurrencyDebug 1
```

Es muy recomendable tenerlo activado siempre que se trabaje con varios contextos. Con él activado, verás en la consola el mensaje `CoreData: annotation: Core Data multi-threading assertions enabled.` al arrancar la app.

## Ampliación: inserciones masivas

!!! info "Nota"
    Este apartado es de ampliación. No lo necesitarás para los ejercicios.

Para importaciones realmente grandes (cientos de miles de objetos) existe `NSBatchInsertRequest`, que inserta los datos directamente en la base de datos, sin crear objetos en ningún contexto. Es muchísimo más rápido, pero tiene limitaciones: no ejecuta las validaciones, no permite establecer relaciones y, como no pasa por ningún contexto, el `viewContext` no se entera automáticamente de los cambios: hay que incorporárselos a mano.

```swift
//todo esto, dentro de un perform del contexto en segundo plano
let filas = datos.map { ["texto": $0.texto, "fecha": $0.fecha] as [String: Any] }
let request = NSBatchInsertRequest(entity: Mensaje.entity(), objects: filas)
request.resultType = .objectIDs
let resultado = try contextoFondo.execute(request) as? NSBatchInsertResult
if let ids = resultado?.result as? [NSManagedObjectID] {
    //avisamos al viewContext de los objetos insertados
    NSManagedObjectContext.mergeChanges(fromRemoteContextSave: [NSInsertedObjectsKey: ids],
                                        into: [PersistenceController.shared.container.viewContext])
}
```


Una **tarea** (`Task`) es una unidad de trabajo asíncrono. Ya hemos visto las dos formas habituales de crearlas desde SwiftUI: con `Task { ... }` y con el modificador `.task`. Todo código asíncrono se ejecuta dentro de alguna tarea.

## Cancelar tareas

Muchas veces nos interesa poder detener una operación larga, por ejemplo si el usuario pulsa un botón "Cancelar" o abandona la pantalla. Para ello, `Task { ... }` devuelve un valor que representa la tarea, y que podemos guardar para cancelarla después:

```swift
struct DescargaView: View {
    @State private var tarea: Task<Void, Never>?

    var body: some View {
        VStack {
            Button("Empezar") {
                tarea = Task {
                    //...operación larga
                }
            }
            Button("Cancelar") {
                tarea?.cancel()
            }
        }
    }
}
```

> `Task<Void, Never>` es el tipo de una tarea que no devuelve ningún resultado (`Void`) y no lanza errores (`Never`).

Pero cuidado: **la cancelación es cooperativa**. Llamar a `cancel()` no detiene la tarea a la fuerza: solo la marca como cancelada. Es el código de la tarea el que tiene que comprobar de vez en cuando si lo han cancelado, y en ese caso terminar. Para ello tenemos dos opciones:

- Consultar `Task.isCancelled`, que es `true` si la tarea actual está cancelada.
- Llamar a `try Task.checkCancellation()`, que lanza un error (`CancellationError`) si la tarea está cancelada.

```swift
func procesar(_ elementos: [Elemento]) async {
    for elemento in elementos {
        if Task.isCancelled {
            return
        }
        await procesarUno(elemento)
    }
}
```

Las funciones asíncronas del sistema ya hacen esta comprobación. Por ejemplo, si cancelamos una tarea mientras está esperando en `URLSession.shared.data(from:)`, la descarga se interrumpe y la función lanza un error.

## Tareas automáticas en SwiftUI

Las tareas creadas con el modificador `.task` tienen una ventaja: **SwiftUI las cancela automáticamente cuando la vista desaparece**. Así, si la vista estaba descargando datos y el usuario se va a otra pantalla, la descarga se cancela sin que tengamos que hacer nada.

La variante `.task(id:)` va más allá: la tarea se vuelve a lanzar cada vez que cambia el valor indicado en `id`, cancelando la anterior si todavía no había terminado. Es lo que usamos en la sesión de consultas para retardar las búsquedas:

```swift
.task(id: textoBusqueda) {
    do {
        try await Task.sleep(for: .milliseconds(500))
        actualizarBusqueda()
    } catch {
        //la espera se ha cancelado porque el texto ha vuelto a cambiar
    }
}
```

Ahora ya podemos entender cómo funciona: `Task.sleep` es una función asíncrona que espera el tiempo indicado sin bloquear el hilo. Si mientras espera cambia el texto, SwiftUI cancela la tarea, y `Task.sleep`, como todas las funciones asíncronas del sistema, comprueba la cancelación y lanza un error, así que no se llega a llamar a `actualizarBusqueda()`.


Vamos a añadir a la aplicación de notas la posibilidad de **importar notas** desde un servidor. Las notas están en un archivo JSON con 10.000 notas, publicado junto a estos apuntes. Lo usaremos para ver en la práctica la diferencia entre hacer el trabajo en el hilo principal y hacerlo en segundo plano.

> Antes de empezar, haz un `commit` con el mensaje `terminada no presencial 2`.

Además del código, en la entrega tendrás que responder a algunas preguntas, que se indican en cada apartado.

## Preparación

1. **Activa la depuración de concurrencia de Core Data**: añade el argumento de lanzamiento `-com.apple.CoreData.ConcurrencyDebug 1`, como se explica en la sección de Core Data, y déjalo activado durante todo el ejercicio. Comprueba que al arrancar la app aparece en la consola el mensaje `Core Data multi-threading assertions enabled`.
2. **Crea una vista `ImportarView`** con el siguiente esqueleto, y añádela como tercera pestaña del `TabView` de `ContentView`, con el título "Importar" y el icono `square.and.arrow.down`.

```swift
import SwiftUI
import CoreData

//cómo viene cada nota en el JSON
struct NotaJSON: Codable {
    let texto: String
    let fecha: Date
}

@MainActor
struct ImportarView: View {
    @Environment(\.managedObjectContext) private var contexto
    @FetchRequest(sortDescriptors: [NSSortDescriptor(keyPath: \Libreta.nombre, ascending: true)])
    private var libretas: FetchedResults<Libreta>

    @State private var libretaSeleccionada: Libreta?
    @State private var importando = false
    @State private var mensaje = ""

    let urlNotas = URL(string: "https://URL-DE-LOS-APUNTES/datos/notas.json")!

    var body: some View {
        VStack(spacing: 20) {
            Picker("Importar en la libreta", selection: $libretaSeleccionada) {
                Text("Sin libreta").tag(nil as Libreta?)
                ForEach(libretas) { libreta in
                    Text(libreta.nombre ?? "").tag(libreta as Libreta?)
                }
            }

            Button("Descargar") {
                //apartado 1
            }

            Button("Importar en el hilo principal") {
                //apartado 2
            }

            Button("Importar en segundo plano") {
                //apartado 3
            }

            //se ve mientras se importa: si deja de girar, el hilo principal está bloqueado
            if importando {
                ProgressView()
            }

            Text(mensaje)
        }
        .padding()
    }
}
```

> Durante el ejercicio vas a importar varias veces 10.000 notas. Si quieres volver a empezar con la base de datos vacía, borra la app del simulador (mantener pulsado el icono > `Eliminar app`). Tendrás que volver a crear las libretas.

## Descargar las notas (0.2 puntos)

Escribe en `ImportarView` una función que descargue el JSON de una URL y lo decodifique a un array de `NotaJSON`:

```swift
nonisolated func descargarNotas(de url: URL) async throws -> [NotaJSON] {
    //FALTA el código
}
```

- Las fechas del JSON están en formato ISO 8601. Recuerda configurar el *decoder* para que las decodifique correctamente (lo vimos en la sesión de persistencia básica).
- Fíjate en que la función es `nonisolated`. Decodificar 10.000 notas lleva su tiempo, y así no se hace en el hilo principal.

En la acción del botón "Descargar", llama a la función con la URL `urlNotas` dentro de una tarea, y muestra en `mensaje` cuántas notas se han descargado o, si se produce un error, un mensaje que lo indique. Pon `importando` a `true` antes de descargar y a `false` al terminar.

Comprueba que se descargan 10.000 notas. Después cambia provisionalmente la URL por una incorrecta y comprueba que se muestra el error y la app no se cierra.

## Importar en el hilo principal (0.15 puntos)

Escribe una función `importarEnPrincipal(_ notas: [NotaJSON])` que cree en el contexto de la vista (el `viewContext`) una `Nota` por cada nota del array, en la libreta seleccionada en el `Picker`, y al final guarde el contexto.

En la acción del botón "Importar en el hilo principal", dentro de una tarea: descarga las notas, impórtalas con esta función, y muestra en `mensaje` cuántas notas se han importado y cuánto tiempo ha tardado la importación (sin contar la descarga). Para medir el tiempo:

```swift
let inicio = Date()
//...lo que queremos medir
let segundos = Date().timeIntervalSince(inicio)
mensaje = "Importadas en \(segundos.formatted(.number.precision(.fractionLength(1)))) segundos"
```

Importa las notas mientras observas el indicador de actividad, e intenta cambiar de pestaña mientras se importan. Comprueba en la lista que las notas se han importado.

**Para la entrega:** indica cuánto ha tardado la importación, describe qué le pasa a la interfaz mientras tanto y explica por qué ocurre.

## Importar en segundo plano (0.3 puntos)

Escribe una función `importarEnSegundoPlano(_ notas: [NotaJSON]) async throws` que haga la importación en un contexto en segundo plano, por lotes de 500 notas. Después de cada lote, actualiza `mensaje` para indicar el progreso ("Importadas 1500 de 10000", por ejemplo).

**De momento, importa las notas sin libreta**: lo resolveremos en el siguiente apartado.

En la acción del botón "Importar en segundo plano", descarga las notas e impórtalas con esta función, midiendo también el tiempo de importación.

Comprueba que:

- El indicador de actividad sigue girando durante toda la importación, y se puede cambiar de pestaña.
- Si cambias a la pestaña de la lista durante la importación, las notas van apareciendo según se importan.
- La app no se cierra por ningún error de concurrencia de Core Data (recuerda que tienes activada la depuración).

**Para la entrega:** compara el tiempo con el del apartado anterior. Explica también por qué las notas aparecen en la lista sin que hayas escrito ningún código para actualizarla.

## Importar en la libreta seleccionada (0.15 puntos)

Ahora haz que las notas importadas en segundo plano se guarden en la libreta seleccionada en el `Picker` (o sin libreta, si está seleccionado "Sin libreta").

Primero hazlo de la forma "intuitiva": dentro del `perform`, asigna directamente `libretaSeleccionada` a la libreta de cada nota. Ejecuta la app, selecciona una libreta e importa. Lee el mensaje de error de la consola. Después corrígelo como se explica en la sección de Core Data.

**Para la entrega:** copia el mensaje de error que obtuviste y explica en dos o tres líneas por qué se produce y cómo lo has resuelto.

## Cancelar la importación (0.2 puntos)

Añade un botón "Cancelar" que se vea solo mientras se está importando, y que cancele la importación en segundo plano.

- Guarda la tarea de la importación en segundo plano en una variable de estado, para poder cancelarla.
- La función `importarEnSegundoPlano` debe comprobar entre lote y lote si se ha cancelado la tarea y, en ese caso, terminar sin importar más notas.
- Al cancelar, `mensaje` debe indicar cuántas notas se habían importado.

Comprueba que si pulsas "Cancelar" a mitad de la importación, se detiene y que el indicador de actividad desaparece.

**Para la entrega:** las notas importadas antes de cancelar se quedan en la base de datos. ¿Te parece un comportamiento correcto? Si quisieras que la importación fuera "todo o nada" (o se importan todas las notas o ninguna), ¿cómo lo harías? No hace falta que lo implementes.

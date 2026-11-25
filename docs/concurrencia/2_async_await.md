
## Funciones asíncronas

Una **función asíncrona** es una función que puede quedarse esperando sin bloquear el hilo en el que se ejecuta. Se declara con la palabra clave `async`:

```swift
struct Usuario: Codable, Identifiable {
    let id: Int
    let nombre: String
}

func descargarUsuarios() async throws -> [Usuario] {
    let url = URL(string: "https://ejemplo.com/usuarios.json")!
    //esperamos a que lleguen los datos, sin bloquear el hilo
    let (datos, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([Usuario].self, from: datos)
}
```

El método `data(from:)` de `URLSession` es a su vez una función asíncrona: descarga el contenido de una URL. Para llamar a una función asíncrona hay que poner delante `await` (y `try` si además puede lanzar errores, como en este caso). El `await` marca un **punto de suspensión**: la función se "aparta" mientras espera la respuesta del servidor, el hilo queda libre para hacer otras cosas (por ejemplo, seguir dibujando la interfaz) y, cuando llegan los datos, la función continúa desde ese punto.

Lo importante es que el código **se lee de arriba abajo**, como si fuera síncrono, aunque entre una línea y la siguiente puedan pasar varios segundos.

> Una función asíncrona solo se puede llamar desde otra función asíncrona (o desde una tarea, como veremos ahora). Es lo mismo que pasa con `throws`: una función que lanza errores solo se puede llamar con `try` desde un sitio que pueda tratarlos.

## Llamar a funciones asíncronas desde SwiftUI

El código de las vistas (el `body`, las acciones de los botones) no es asíncrono. Para llamar desde él a una función asíncrona tenemos dos opciones.

Si queremos que se ejecute **al aparecer la vista**, usamos el modificador `.task`, que es la versión asíncrona de `.onAppear`:

```swift
struct UsuariosView: View {
    @State private var usuarios: [Usuario] = []
    @State private var error = ""

    var body: some View {
        List(usuarios) { usuario in
            Text(usuario.nombre)
        }
        .overlay {
            if !error.isEmpty {
                Text(error)
            }
        }
        .task {
            do {
                usuarios = try await descargarUsuarios()
            } catch {
                self.error = "No se han podido descargar los usuarios"
            }
        }
    }
}
```

Si queremos que se ejecute **al pulsar un botón** (o en respuesta a cualquier otra acción del usuario), creamos una **tarea** con `Task`:

```swift
Button("Recargar") {
    Task {
        usuarios = try await descargarUsuarios()
    }
}
```

`Task { ... }` pone en marcha el código asíncrono que contiene y la acción del botón termina inmediatamente, sin esperar. Veremos las tareas con más detalle en la siguiente sección.

## Varias operaciones en paralelo

Si hacemos dos `await` seguidos, la segunda operación no empieza hasta que termina la primera:

```swift
let usuarios = try await descargarUsuarios()
let conversaciones = try await descargarConversaciones()
```

Si las dos operaciones son independientes, es más eficiente hacerlas a la vez. Para ello se usa `async let`, que pone en marcha la operación sin esperar a que termine. Esperamos después, cuando necesitamos los resultados:

```swift
async let usuarios = descargarUsuarios()
async let conversaciones = descargarConversaciones()
//aquí las dos descargas se están haciendo a la vez
let (listaUsuarios, listaConversaciones) = try await (usuarios, conversaciones)
```

!!! warning "`async` no significa "en otro hilo""
    Es muy habitual pensar que marcar una función como `async` hace que se ejecute en segundo plano. No es así: `async` solo significa que la función **puede esperar sin bloquear**. Si dentro de una función asíncrona hacemos un cálculo largo sin ningún `await`, ese cálculo ocupará el hilo en el que se esté ejecutando la función igual que si no fuera asíncrona. En qué hilo se ejecuta cada cosa lo veremos en la sección sobre el hilo principal.

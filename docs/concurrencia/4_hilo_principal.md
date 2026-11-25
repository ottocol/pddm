
Hemos visto que las funciones asíncronas pueden esperar sin bloquear, pero no hemos dicho **en qué hilo** se ejecutan. Es lo que vamos a ver ahora, y es lo que nos permitirá hacer cálculos largos sin bloquear la interfaz.

## Actores

Cuando varias tareas se ejecutan a la vez en distintos hilos, aparece un problema clásico de la programación concurrente: si dos de ellas modifican la misma variable al mismo tiempo, el resultado puede ser incorrecto, o incluso hacer que la app se cierre. Es lo que se llama una ***data race***.

Swift resuelve esto con los **actores**. Un actor es como una clase, pero que garantiza que su código se ejecuta **de uno en uno**: aunque varias tareas lo llamen a la vez, cada llamada espera su turno. Así, sus propiedades nunca se modifican desde dos sitios a la vez.

```swift
actor Contador {
    var valor = 0

    func incrementar() {
        valor += 1
    }
}
```

Como una llamada puede tener que esperar su turno, desde fuera del actor hay que usar `await` para llamar a sus métodos: `await contador.incrementar()`.

## El `MainActor`

El caso más importante de actor es el **`MainActor`**, que representa el hilo principal. Todo el código "aislado" en el `MainActor` se ejecuta en el hilo principal. Para indicar que una función, una clase o una estructura debe ejecutarse en el hilo principal se marca con `@MainActor`:

```swift
@MainActor
func actualizarInterfaz() {
    //esto siempre se ejecutará en el hilo principal
}
```

**Todo lo que modifica la interfaz debe ejecutarse en el `MainActor`**, y en SwiftUI eso incluye modificar las variables `@State`. Si se modifica una variable de estado desde otro hilo, Xcode mostrará un aviso en tiempo de ejecución y el comportamiento puede ser incorrecto.

!!! warning "Particularidad de Xcode 15: marca las vistas con `@MainActor`"
    En SwiftUI, el `body` de las vistas está marcado con `@MainActor`, y por tanto también el código de las acciones de los botones y las tareas creadas dentro de él. Pero en Xcode 15 **el resto de métodos de una vista no lo están**. Si escribimos en la vista un método `async` que modifica variables de estado y lo llamamos desde una tarea, ese método se ejecutará fuera del hilo principal.

    Para evitar sorpresas, en este curso marcaremos con `@MainActor` las vistas que tengan métodos asíncronos:

    ```swift
    @MainActor
    struct MiVista: View {
        //...
    }
    ```

    A partir de Xcode 16, el protocolo `View` ya está marcado con `@MainActor` y esto no es necesario.

## Hacer cálculos fuera del hilo principal

¿En qué hilo se ejecuta entonces el código asíncrono? La regla, en Swift 5.9/5.10 (Xcode 15), es:

- Una función o tarea **aislada en un actor** se ejecuta en ese actor. En particular, si está aislada en el `MainActor`, en el hilo principal.
- Una tarea creada con `Task { ... }` hereda el actor del sitio donde se crea. Una tarea creada en la acción de un botón se ejecuta, por tanto, en el `MainActor`.
- Una función asíncrona **no aislada** (que no pertenece a ningún actor) se ejecuta en un conjunto de hilos que el sistema gestiona para la concurrencia, **fuera del hilo principal**.

Volvamos al ejemplo de los números primos. Un intento habitual de arreglarlo es meter el cálculo en una tarea:

```swift
Button("Contar primos") {
    Task {
        let cuenta = contarPrimos(hasta: 2_000_000)   //¡sigue bloqueando!
        resultado = "Hay \(cuenta) primos"
    }
}
```

Pero **la interfaz se sigue bloqueando**: la tarea hereda el `MainActor` del botón, y `contarPrimos` es una función síncrona que no tiene ningún punto de suspensión, así que el cálculo ocupa el hilo principal igual que antes.

La solución es hacer el cálculo en una función asíncrona no aislada. Si la escribimos dentro de una vista marcada con `@MainActor`, hay que indicar que no queremos que esté aislada con `nonisolated`:

```swift
@MainActor
struct PrimosView: View {
    @State private var resultado = ""

    var body: some View {
        VStack(spacing: 20) {
            ProgressView()
            Button("Contar primos") {
                Task {
                    let cuenta = await contarPrimosEnSegundoPlano(hasta: 2_000_000)
                    resultado = "Hay \(cuenta) primos"
                }
            }
            Text(resultado)
        }
    }

    //no aislada: se ejecuta fuera del hilo principal
    nonisolated func contarPrimosEnSegundoPlano(hasta limite: Int) async -> Int {
        return contarPrimos(hasta: limite)
    }
}
```

Ahora el indicador sigue girando mientras se calcula. Fíjate en lo que ocurre:

1. La tarea se ejecuta en el hilo principal. Al llegar al `await`, llama a `contarPrimosEnSegundoPlano`, que al no estar aislada se ejecuta en otro hilo. Mientras tanto, el hilo principal queda libre.
2. Cuando el cálculo termina, la tarea continúa en el hilo principal, ya que pertenece al `MainActor`, y puede modificar `resultado` sin problemas.

Es decir: Swift se encarga de pasar de un hilo a otro en cada `await`, según a qué actor pertenezca cada código. Nosotros solo tenemos que indicar qué código debe ejecutarse dónde.

> Las reglas sobre en qué hilo se ejecuta el código asíncrono no aislado han cambiado en las versiones más recientes de Swift (6.2 y posteriores) si se activan ciertas opciones del compilador. Lo explicado aquí es el comportamiento de Xcode 15, y es también el de las versiones posteriores con la configuración por defecto de Swift 5.

## Comprobar el código con el compilador

Swift puede comprobar al compilar muchos de los posibles problemas de concurrencia (por ejemplo, que pasemos de un hilo a otro datos que no son seguros). En Xcode 15 estas comprobaciones están desactivadas por defecto, y en Swift 6 son obligatorias. Si quieres verlas, en los *Build Settings* del proyecto busca `Strict Concurrency Checking` y ponlo a `Complete`: Xcode mostrará *warnings* en el código que podría tener problemas. No lo necesitarás para los ejercicios, pero es interesante probarlo.

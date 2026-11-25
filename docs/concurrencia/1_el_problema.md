
## El hilo principal

En una app iOS, todo lo relacionado con la interfaz de usuario ocurre en un único hilo de ejecución, el **hilo principal** (*main thread*). Es el que dibuja la pantalla, responde a los toques del usuario y ejecuta el código de nuestras vistas: el `body`, las acciones de los botones, los `.onAppear`...

La pantalla se redibuja 60 veces por segundo (120 en los dispositivos más recientes), así que el hilo principal tiene unos 16 milisegundos para preparar cada fotograma. Si alguna operación lo mantiene ocupado más tiempo, la app deja de dibujar y de responder: las animaciones se paran, los botones no hacen caso y, si el bloqueo dura varios segundos, el sistema puede llegar a cerrar la aplicación.

Vamos a verlo con un ejemplo. Esta vista cuenta los números primos hasta dos millones con un algoritmo muy poco eficiente, para que tarde unos segundos:

```swift
func contarPrimos(hasta limite: Int) -> Int {
    var cuenta = 0
    for n in 2...limite {
        var esPrimo = true
        var divisor = 2
        while divisor * divisor <= n {
            if n % divisor == 0 {
                esPrimo = false
                break
            }
            divisor += 1
        }
        if esPrimo {
            cuenta += 1
        }
    }
    return cuenta
}

struct PrimosView: View {
    @State private var resultado = ""

    var body: some View {
        VStack(spacing: 20) {
            //un indicador de actividad que gira continuamente
            ProgressView()
            Button("Contar primos") {
                let cuenta = contarPrimos(hasta: 2_000_000)
                resultado = "Hay \(cuenta) primos"
            }
            Text(resultado)
        }
    }
}
```

Si lo ejecutas y pulsas el botón, verás que el indicador de actividad **deja de girar** hasta que termina el cálculo, y que mientras tanto la app no responde. La acción del botón se ejecuta en el hilo principal, y mientras está calculando no puede hacer nada más.

> El `ProgressView` girando es un truco muy útil para detectar bloqueos del hilo principal: si se para, aunque sea un instante, es que el hilo principal está ocupado.

## Esperar y calcular

Hay dos tipos de operaciones "lentas", y es importante distinguirlas porque se resuelven de forma distinta:

- Las operaciones en las que **esperamos**: descargar datos de un servidor, leer un archivo grande... El procesador no está haciendo nada, simplemente espera a que lleguen los datos. Bloquear el hilo principal mientras tanto es un desperdicio: podría seguir dibujando la interfaz mientras esperamos.
- Las operaciones en las que **calculamos**: procesar muchos datos, aplicar un filtro a una imagen, contar primos... Aquí el procesador está realmente ocupado, y la única solución es hacer el trabajo en **otro hilo**, dejando libre el principal.

Swift tiene, desde la versión 5.5, un sistema de concurrencia integrado en el lenguaje que resuelve los dos casos: las funciones asíncronas (`async`/`await`) para las esperas, y una serie de reglas sobre en qué hilo se ejecuta cada cosa para los cálculos. Es lo que veremos en esta sesión.

> En código anterior (y en mucha documentación que encontraréis por internet) veréis otra forma de hacer esto: con colas de GCD (`DispatchQueue.main.async { ... }`, `DispatchQueue.global().async { ... }`) y funciones que reciben como parámetro una clausura a la que llaman cuando terminan (*completion handlers*). El sistema de `async`/`await` sustituye a todo esto con un código mucho más legible y más seguro.

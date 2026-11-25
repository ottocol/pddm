
Vamos a mejorar la lista de la aplicación de notas: añadiremos una búsqueda por texto, la posibilidad de borrar notas y secciones por libreta.

> Antes de ponerte a hacer las modificaciones de esta sesión asegúrate de que has hecho un `commit` con el mensaje `terminada presencial 1`. Así cuando se evalúe el ejercicio el profesor podrá consultar el estado que tenía la aplicación antes de estos ejercicios.

## Búsqueda por texto (0.3 puntos)

Vamos a añadir a la lista de notas un campo de búsqueda.

!!! note "Nuevo en SwiftUI: `.searchable` y `.onChange`"
    El modificador `.searchable` añade un campo de búsqueda a la barra de navegación, y lo conecta mediante un *binding* a una variable de estado con el texto buscado. Como el campo va en la barra de navegación, la vista tiene que estar dentro de un `NavigationStack`.

    El modificador `.onChange(of:)` ejecuta un código cada vez que cambia un valor, por ejemplo una variable de estado.

    ```swift
    NavigationStack {
        List { ... }
            .navigationTitle("Notas")
            .searchable(text: $textoBusqueda)
            .onChange(of: textoBusqueda) {
                //esto se ejecuta cada vez que cambia el texto buscado
            }
    }
    ```

En `ListaNotasView`:

1. Mete la lista en un `NavigationStack`, con el título "Notas".
2. Añade una variable de estado `textoBusqueda`, de tipo `String`, y conéctala con `.searchable`.
3. Escribe una función `actualizarBusqueda()` que cambie el predicado de la `@FetchRequest` de las notas para que solo muestre las notas cuyo texto contenga el texto buscado, sin distinguir mayúsculas/minúsculas ni caracteres diacríticos. Si el texto de búsqueda está vacío deben mostrarse **todas** las notas.
4. Llama a `actualizarBusqueda()` con `.onChange` cada vez que cambie el texto buscado.

Las notas deben seguir apareciendo en orden inverso por fecha, de más reciente a más antigua.

Para comprobar que funciona correctamente prueba al menos estas búsquedas:

- Una palabra con acento escrita sin él (por ejemplo, si tienes una nota con "canción", busca "CANCION").
- Un texto con una comilla, por ejemplo `l'Alcúdia`. **La app no debe cerrarse.** Si se cierra, repasa la sección de predicados.
- Borrar el texto del buscador: deben volver a aparecer todas las notas.
- Con una búsqueda activa, cambia a la pestaña "Nueva", crea una nota que cumpla la búsqueda y vuelve a la lista: debe aparecer.

## Buscar también por libreta (0.2 puntos)

Amplía la búsqueda para que encuentre las notas cuyo texto contenga el texto buscado **o** que estén en una libreta cuyo nombre lo contenga. Por ejemplo, si buscamos "trabajo", deben aparecer las notas que contengan esa palabra y también todas las notas de la libreta "Trabajo", aunque su texto no la contenga.

Las notas que no tienen libreta deben seguir funcionando con normalidad: se encontrarán (o no) solo por su texto.

## Borrar notas (0.15 puntos)

Haz que se puedan borrar notas de la lista con el gesto de deslizar hacia la izquierda.

Comprueba que al borrar una nota desaparece de la lista con animación, que sigue borrada al detener la app y volver a ejecutarla, y que también se pueden borrar notas mientras hay una búsqueda activa.

## Secciones por libreta (0.2 puntos)

Haz que la lista tenga una sección por cada libreta, con el nombre de la libreta como título, y que dentro de cada sección las notas sigan ordenadas por fecha, de más reciente a más antigua.

- Las notas que no tienen libreta deben aparecer en una sección titulada "Sin libreta".
- La búsqueda y el borrado deben seguir funcionando con las secciones.

Para comprobar que funciona correctamente:

- Crea una nota en una libreta que todavía no tenga ninguna: al volver a la lista debe aparecer la nueva sección.
- Borra la única nota de una libreta: su sección debe desaparecer.
- Haz una búsqueda: solo deben aparecer las secciones que tengan alguna nota que la cumpla.

## Retardar las búsquedas (0.15 puntos)

Ahora mismo, cada vez que se teclea un carácter en el buscador se lanza una nueva consulta. Con pocas notas no se nota, pero con muchos datos, o si la búsqueda fuera costosa (por ejemplo, una petición a un servidor), estaríamos haciendo mucho trabajo inútil: si el usuario escribe "reunión" rápidamente, se buscarían "r", "re", "reu"... y no le daría tiempo ni a ver esos resultados intermedios.

Hay dos técnicas habituales para limitar la frecuencia con la que se ejecuta una operación:

- ***Throttling***: la operación se ejecuta como mucho una vez cada cierto intervalo de tiempo, aunque se solicite más veces.
- ***Debouncing***: la operación se ejecuta solo cuando ha pasado un cierto tiempo **sin** que se vuelva a solicitar. Es decir, cada nueva solicitud "reinicia el reloj".

Para una búsqueda mientras se escribe, lo más adecuado es el *debouncing*: buscaremos cuando el usuario haga una pausa al escribir. En SwiftUI se puede conseguir de forma muy sencilla con el modificador `.task(id:)`. **Sustituye el `.onChange` por el siguiente código**:

```swift
.task(id: textoBusqueda) {
    do {
        try await Task.sleep(for: .milliseconds(500))
        actualizarBusqueda()
    } catch {
        //la espera se ha cancelado porque el texto ha vuelto a cambiar:
        //no hacemos nada
    }
}
```

El modificador `.task(id:)` ejecuta su código al aparecer la vista y cada vez que cambia el valor indicado en `id`. Además, si el valor cambia mientras el código anterior todavía se está ejecutando, lo cancela. Así:

1. Cada vez que el usuario teclea un carácter, cambia `textoBusqueda` y empieza una espera de medio segundo.
2. Si antes de que termine se teclea otro carácter, la espera se cancela (`Task.sleep` lanza un error, y no se busca nada) y empieza otra.
3. Solo cuando pasa medio segundo sin teclear se llega a ejecutar `actualizarBusqueda()`.

> El `await` y el `Task` tienen que ver con la concurrencia en Swift, que veremos en la próxima sesión presencial. Por ahora basta con entender el efecto que tiene este código.

Para comprobar que funciona, pon un `print` en `actualizarBusqueda()` y escribe una palabra rápidamente en el buscador: el `print` debería aparecer **una sola vez**, medio segundo después de dejar de escribir.

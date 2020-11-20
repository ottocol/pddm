
Vamos a implementar una búsqueda por texto en la aplicación de notas sobre la que estáis trabajando en estas sesiones.

> Antes de ponerte a hacer las modificaciones de esta sesión asegúrate de que has hecho un `commit` con el mensaje `terminada sesión 2`. También puedes hacer un `.zip` con el proyecto, llamarlo `notas_sesion_2.zip` y adjuntarlo en las entregas de la asignatura. Así cuando se evalúe el ejercicio el profesor podrá consultar el estado que tenía la aplicación antes de estos ejercicios.

### Preparación de la interfaz (0.25 puntos)

Necesitamos una barra de búsqueda para poder introducir la cadena de texto a buscar. Usaremos un `UISearchController`. Este componente incluye la *search bar*. 

En `ListaNotasController`:

1. Define una propiedad que será el `UISearchController`

```swift
//esto debe ser una variable miembro de ListaNotasController
let searchController = UISearchController(searchResultsController: nil)
```

2. En el `viewDidLoad` introduce el siguiente código, que configura e inicializa el `UISearchController`

```swift
//iOS intentará pintar la tabla, hay que inicializarla aunque sea vacía
self.listaNotas = []
//ListaNotasController recibirá lo que se está escribiendo en la barra de búsqueda 
searchController.searchResultsUpdater = self
//Configuramos el search controller
searchController.obscuresBackgroundDuringPresentation = false
searchController.searchBar.placeholder = "Buscar texto"
//Lo añadimos a la tabla
searchController.searchBar.sizeToFit()
self.tableView.tableHeaderView = searchController.searchBar
```

3. La propiedad `searchResultsUpdater` indica quién es el *delegate* del `UISearchController`, en este caso `ListaNotasViewController`. El *delegate* debe ser conforme al protocolo `UISearchResultsUpdating`, que requiere que se implemente un método llamado `updateSearchResults(for:)`.

Cambia la cabecera de `ListaNotasViewController` para declarar que es conforme al protocolo `UISearchResultsUpdating`:

```swift
class ListaViewController: UITableViewController, UISearchResultsUpdating {
  ...
}  
```
Define en la clase el método `updateSearchResults(for:)`

```swift
func updateSearchResults(for searchController: UISearchController) {
    let texto = searchController.searchBar.text!
    print("Buscando \(texto)")
}
```

**Prueba la aplicación** para comprobar que todo está correcto, y deberías ver que cada vez que se escribe en la barra de búsqueda se llama a este método y se imprime en la consola la cadena buscada.

### Implementación del código de búsqueda (0.5 puntos)

> `updateSearchResults` se llama por cada nuevo carácter escrito en la barra de búsquedas, lo que permite actualizar los datos en "tiempo real" pero es muy ineficiente. Veremos cómo solucionarlo en el siguiente apartado, de momento dispararemos una nueva búsqueda por cada pulsación

Hecha la preparación de la interfaz, falta implementar la búsqueda en sí. En el método `updateSearchResults` **debes crear una fetch request que busque las notas cuyo texto contenga el texto escrito** en la barra de búsqueda, sin distinguir mayúsculas/minúsculas o caracteres diacríticos. 

Recuerda que para que se actualicen los datos visibles debes llamar a `tableView.reloadData()`

Una vez comprobado que funciona, **mejora la fetch request para que las notas aparezcan en orden inverso por fecha**, de más reciente a más antigua.

### *Throttling* de las búsquedas (0.25 puntos) 

Lanzar una nueva *fetch request* por cada carácter tecleado es muy ineficiente, sobre todo si el usuario teclea rápido y ni siquiera da tiempo a ver los resultados intermedios. Una implementación mejor haría *throttling* de la búsqueda, es decir, impediría que se repita la operación si todavía no ha pasado un mínimo de tiempo desde la anterior.

La idea es que si se intenta repetir la operación y todavía no ha pasado un tiempo prefijado por nosotros, la nueva operación se retrase hasta que pase el intervalo de tiempo. Esto no está implementado en los APIs de iOS pero en Internet vpodéis encontrar diversas implementaciones. La siguiente clase, tomada de [este tutorial](https://www.craftappco.com/blog/2018/5/30/simple-throttling-in-swift), implementa esta funcionalidad.

```swift
import Foundation

//De https://www.craftappco.com/blog/2018/5/30/simple-throttling-in-swift
class Throttler {
    private var workItem: DispatchWorkItem = DispatchWorkItem(block: {})
    private var previousRun: Date = Date.distantPast
    private let queue: DispatchQueue
    private let minimumDelay: TimeInterval
    
    init(minimumDelay: TimeInterval, queue: DispatchQueue = DispatchQueue.main) {
        self.minimumDelay = minimumDelay
        self.queue = queue
    }
    
    func throttle(_ block: @escaping () -> Void) {
        // Cancel any existing work item if it has not yet executed
        workItem.cancel()
        
        // Re-assign workItem with the new block task, resetting the previousRun time when it executes
        workItem = DispatchWorkItem() {
            [weak self] in
            self?.previousRun = Date()
            block()
        }
        
        // If the time since the previous run is more than the required minimum delay
        // => execute the workItem immediately
        // else
        // => delay the workItem execution by the minimum delay time
        let delay = previousRun.timeIntervalSinceNow > minimumDelay ? 0 : minimumDelay
        queue.asyncAfter(deadline: .now() + Double(delay), execute: workItem)
    }
}
```

Crea un nuevo fichero Swift en tu proyecto con esta clase. Para usarlo en `ListaNotasViewController`:

1. Define una variable miembro de tipo `Throttler` con el intervalo de tiempo deseado, por ejemplo 0.5 segundos (no queremos repetir búsquedas con más frecuencia)

```swift
let throttler = Throttler(minimumDelay: 0.5)
```

2. En el `updateSearchResults` "envuelve" tu código de búsqueda en un `throttle`. Automáticamente la clase `Throttler` se encargará de que el código no se ejecute más de 1 vez por cada 0.5 segundos (o el intervalo que hayas elegido)

```swift
func updateSearchResults(for searchController: UISearchController) {
    throttler.throttle {
        let texto = searchController.searchBar.text!
        //Aquí iría tu código de búsqueda
    }
}
```

## Ejercicio: contextos múltiples para operaciones en *background* *(1 punto)*


En el moodle de la sesión hay un proyecto llamado `PruebaContextosMultiples` que servirá como base para los ejercicios de la sesión. La aplicación solo tiene una pantalla con un listado de notas (no se pueden crear ni modificar). Hay dos operaciones costosas: exportar las notas y refrescar el listado con datos que vengan del servidor. En ambos casos el coste es simulado ya que ni se exportan de verdad ni se actualizan desde ningún servidor (ejem). El coste se simula "durmiendo" al hilo actual con la instrucción `usleep`.

Cuando la aplicación se carga, si no hay datos automáticamente inserta 500 objetos en la base de datos.

Pulsa sobre el botón de "exportar". Verás que la operación tarda 2-3 segundos. Si intentas hacer *scroll* de la pantalla durante este tiempo no podrás, ya que se queda bloqueada. Hay que solucionar esto.

Verás que en el método `botonExportarPulsado` del *view controller* se llama a un método que (de modo simulado) exporta las notas y que es el "culpable" del bloqueo. El método admite como parámetro el contexto de persistencia. **Cambia el código para que esta operación se haga en un nuevo contexto en background**. Recuerda que las operaciones de interfaz (como mostrar el alert tras la exportación) deben hacerse en el *thread* principal y que este se puede obtener con `OperationQueue.main`.




# Miniproyecto: *app* restaurante. Parte 2: Las pantallas de la *app*

En esta segunda parte implementaremos las pantallas de la *app*. La mayor parte de la interfaz ya está creada, tú tienes que implementar las funcionalidades en Core Data.

## La Carta (3 puntos)

Esta parte de la *app* es la que muestra los platos y nos permite añadirlos al pedido.

### La pantalla de Carta (`PlatosViewController`)

En esta pantalla se deben mostrar los datos de los platos. Está controlada por el `PlatosViewController`. Iremos primero con que salgan los platos listados y luego con la funcionalidad del botón de "Añadir" al pedido.

#### Listado de platos

- Usa un `NSFetchedResultsController` para **listar los platos** en la tabla. Haz que los platos se agrupen en secciones según su tipo.
    + Las celdas de la tabla son de la clase `PlatoTableViewCell`, aquí ya están definidos los *outlets* para poder rellenar los datos.

- Implementa una **búsqueda/filtrado de platos** como hiciste en la aplicación de notas, que busque texto en el nombre o en la descripción del plato. Para aplicar el "filtro" puedes:
    - Crear un predicado (`NSPredicate`) con la condición de búsqueda y asignárselo a la propiedad `fetchRequest.predicate` del `NSFetchedResultsController`. 
    - Para que se actualicen los datos tendrás que hacer un `performFetch` del `NSFetchedResultsController`

#### Añadir al pedido actual

Las celdas de la tabla tienen un *delegate* al que  avisarán de que se ha pulsado el botón "Añadir". Cada celda almacena su `IndexPath` (su número de fila y de sección) y tiene como *delegate* al *controller* de la pantalla.

Para avisar al *controller* de que se ha pulsado sobre "Añadir" se llama al **método `platoAñadido`. En este método tienes que obtener la entidad `Plato` elegida (la que está en la fila y sección seleccionadas)** para que el código restante (ya implementado) se lo pase al controller de la pantalla siguiente.

## El pedido actual (`PedidoActualViewController`) (3 puntos)


**A partir de aquí necesitarás tener también las entidades `Pedido` y `LineaPedido`. Recuerda también añadir la relación `lineasPedido` a la entidad plato (puedes ver el modelo completo en el apéndice)**

Esta parte de la *app* muestra los datos del pedido actual, añade los platos seleccionados al pedido y permite hacer el pedido o cancelarlo.

El *controller* recibe el plato elegido desde el controller anterior en la propiedad `platoElegido`, hay que añadir una entidad `LineaPedido` que vincule este plato con el pedido actual.

El pedido actual no se puede guardar en el propio *controller* ya que por la navegación entre pantallas este se destruiría al salir de ella. Por eso se debe guardar aparte, en la variable `pedidoActual` del *singleton* `StateSingleton.shared`. **Esta variable estaba comentada para que no diera error** ya que hasta ahora no existía la entidad `Pedido`, **descoméntala**. 

### Añadir el plato elegido al pedido

En el `viewDidLoad` de `PedidoActualViewController` nos tenemos que ocupar de añadir el plato elegido al pedido actual

- Primero **comprueba si ya existe un `Pedido` actual (`StateSingleton.shared.pedidoActual!=nil`), y si no existe créalo en Core Data, guárdalo en el `StateSingleton` y haz save() del contexto de persistencia**
- **Crea un nuevo `LineaPedido`**
    - Asígnale cantidad 1
    - Asócialo con el plato elegido. Recuerda que el plato elegido debería estar en la propiedad `platoElegido` del controller.
    - Asócialo con el pedido. Xcode debería haber generado un método de `Pedido` llamado `addToLineasPedido` para añadir una línea de pedido a un pedido.

### Cambiar la cantidad de un plato

En esta pantalla también se puede cambiar el número de unidades que queremos pedir de un plato. 

> Para simplificar solo podemos movernos entre 1 y 100, no podemos bajar las unidades a 0 y eliminar el plato

Al igual que en la pantalla anterior se usa la idea de *delegate* para saber qué celda se está seleccionando. Las celdas son de la clase `LineaPedidoTableviewCell`, y cada vez que se pulsa en un `+` o un `-` se avisa al *delegate* (en este caso el controller), pasándole el número de la fila.

El método `cantidadCambiada` del controller se llamará cada vez que el usuario cambie la cantidad de un plato. **Añade código que obtenga la línea de pedido correspondiente, cambie la cantidad y guarde los cambios**

### Realizar y cancelar pedido

En la pantalla tienes dos botones para realizar y cancelar el pedido. 

- Si se pulsa a "realizar" bastará con que le asignes la fecha actual al pedido, crees un nuevo pedido en `StateSingleton.shared.pedidoActual` y muestres un mensaje al usuario indicando que "su pedido está en camino" o algo similar
- Si se pulsa a "cancelar" deberías borrar en Core Data el pedido actual. Si la regla de borrado en cascada está puesta correctamente, al borrar un pedido deberían borrarse automáticamente todas sus líneas.

## Tu historial (`PedidosViewController`) (hasta 4 puntos)

En esta pantalla se deberían mostrar todos los pedidos realizados por el usuario actual. Está en blanco y puedes crear la interfaz del modo que desees.

- (1 punto) Si en el `viewWillAppear` muestras los datos de todos los pedidos en la consola con `print`, solo para ver que efectivamente se han almacenado correctamente
- (2 puntos) Si muestras en una tabla una línea con el resumen de cada pedido (fecha, total y número de platos pedidos)
- (4 puntos) Si muestras una pantalla con el listado de pedidos y otra con los detalles de cada uno   
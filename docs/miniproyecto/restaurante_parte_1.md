
# Miniproyecto: *app* restaurante. Parte 1: El modelo de datos

El objetivo es desarrollar una pequeña aplicación para gestionar pedidos *online* a un restaurante. Para ello almacenaremos los datos de la carta y de los pedidos realizados por el usuario en Core Data.

Descárgate la plantilla de la aplicación desde moodle, aquí está ya implementada la mayor parte de la interfaz.

En esta primera sesión nos ocuparemos del modelo de datos.

Nuestro modelo de datos debe tener tres entidades, `Plato`, `Pedido` y `LineaPedido`. Esta última es la que relaciona los platos con los pedidos,  guardando cuántas unidades de un plato se han incluido en un pedido. 

![](modelo_datos.png)

Cada entidad debe tener las siguientes propiedades y relaciones

- `Plato`:
    + Propiedades:
        * `nombre` de tipo `String`
        * `descripcion` de tipo `String`
        * `precio` de tipo `Double`
        * `tipo` de tipo `String`
    + Relaciones:
        * `lineasPedido`, relación "a muchos" con destino `LineaPedido`. La inversa es la relación `plato`
- `Pedido`:
    + Propiedades:
        *  `direccion` de tipo `String`
        *  `telefono` de tipo `String`
        *  `fecha` de tipo `Date`
        *  `total` de tipo `Double
    +  Relaciones:
        *  `lineasPedido`, relación "a muchos" con destino `LineaPedido`. La relación **debe ser ordenada**, para poder mostrar las lineas de un pedido siempre en el mismo orden. La inversa es la relación `pedido`. En la regla de borrado (`delete rule`) pon `Cascade` para que al eliminar un pedido se eliminen automáticamente sus líneas.
-  `LineaPedido`:
    +  Propiedades
        *  `cantidad` de tipo `Integer 16`
    +  Relaciones
        *  `pedido`, relación "a uno" con destino `Pedido`. La inversa es la relación `lineasPedido`
        *  `plato`, relación "a uno" con destino `Plato`. La inversa es la relación `lineasPedido`

> **Simplificaciones**: en realidad se deberían usar tipos `Decimal` en los precios para evitar errores de redondeo, pero usaremos `Double` por simplicidad de uso. Además, el tipo del plato debería ser un enumerado, pero estos no se pueden almacenar directamente en Core Data. Tendríamos que generar manualmente el código de las entidades para poder representar los datos externamente como *enums* e internamente como otro tipo.


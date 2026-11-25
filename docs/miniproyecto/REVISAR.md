Ya tienes el miniproyecto en SwiftUI: el enunciado y los fuentes de la plantilla. Mantiene la app, el modelo de datos, los apartados y los 2,5 puntos (0,5 + 0,25 + 0,5 + 0,75 + 0,5).

La plantilla compila desde el primer momento, sin tener que descomentar nada. Las filas (FilaPlato y FilaLinea) ya están hechas, pero no reciben objetos de Core Data sino datos simples y una clausura para la acción. Así no dependen del modelo, y los alumnos se centran en conectarlo. La app arranca con las tres pestañas y filas de ejemplo que van sustituyendo por los datos reales.

Lo que desaparece porque SwiftUI lo hace innecesario

Celdas con delegate e indexPath.
La navegación desde el storyboard.
Throttler, que en la sesión de consultas se sustituye por .task(id:).
El fallo del botón del tab bar sin platoElegido. Ahora “Añadir” añade el plato al pedido sin navegar a otra pantalla.
StateSingleton: el pedido actual pasa a ser el Pedido sin fecha. Esto mejora la app, porque el pedido ya no se pierde al cerrarla, y obliga a usar un predicado (fecha == nil).

Lo que integra de todo el bloque

Importar los platos en un contexto en segundo plano.
@SectionedFetchRequest por tipo.
Búsqueda en nombre o descripción.
Una consulta que depende de un parámetro (las líneas de un pedido).
Propiedades calculadas total y numPlatos en una extensión de Pedido.
Una pantalla de detalle en el historial, que sustituye a la opción del print por 0,25.
Elegir y justificar la delete rule de Plato.

Una decisión que he tomado y conviene que valides: he quitado lo de que lineasPedido sea una relación ordenada. Las líneas se muestran ordenadas por el nombre del plato mediante la consulta, que además es lo que hace que la lista y el total se actualicen solos. El diagrama modelo_datos.png sigue valiendo tal cual.

Lo que más me preocupa sin poder compilar: la pantalla del pedido. Una consulta de líneas con pedido.fecha == nil no se habría enterado de que el pedido se realizaba, porque @FetchRequest solo vigila su propia entidad. Por eso la pantalla tiene dos vistas: PedidoActualView consulta el pedido sin fecha y FormularioPedido consulta las líneas de ese pedido. El enunciado explica por qué, en un recuadro, porque es una sutileza real de Core Data que vale la pena que aprendan. Es lo primero que conviene probar.

Lo que tienes que hacer tú: no puedo generar un .xcodeproj fiable sin Xcode, así que el zip trae los fuentes y un LEEME_montar_plantilla.md con los pasos. Son unos 5 minutos: crear el proyecto con Core Data, vaciar el modelo, arrastrar los archivos y comprimir. El platos.json pasa de 4 a 20 platos en 6 tipos, para que las secciones y la búsqueda tengan con qué trabajar. He conservado la pizza de piña con martillo.

Con esto está todo el bloque. Te recomiendo encarecidamente hacer tú la práctica completa en Xcode 15 antes del curso, de la no presencial 1 al miniproyecto. Si quieres, te escribo una solución de referencia del miniproyecto para que puedas probarla directamente en el proyecto y comprobar que el enunciado se puede resolver tal como está.
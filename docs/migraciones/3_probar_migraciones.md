
Antes de ver cómo se hacen las migraciones, vamos a resolver un problema práctico: **¿cómo las probamos?**

Una migración se ejecuta una sola vez: la primera vez que la app arranca con el nuevo modelo, Core Data transforma la base de datos y, a partir de ahí, la base de datos ya está en el nuevo formato. Si la migración no ha salido como esperábamos (o simplemente queremos volver a probarla tras cambiar algo), ya no tenemos los datos antiguos para repetirla. Borrar la app y empezar de cero no sirve, porque lo que queremos probar es precisamente qué pasa con los datos que ya existían.

Lo que necesitamos es un **punto de restauración**: una copia de la base de datos tal como estaba *antes* de migrar, que podamos recuperar tantas veces como queramos.

## La base de datos son tres archivos

Como vimos en la primera sesión de Core Data, la base de datos SQLite está en el directorio `Library/Application Support` del *sandbox* de la app, y no es un único archivo sino tres: `NombreProyecto.sqlite`, `NombreProyecto.sqlite-wal` y `NombreProyecto.sqlite-shm`. Para hacer una copia válida **hay que copiar siempre los tres juntos**, y hacerlo cuando la app no tiene la base de datos abierta. Si copiamos solo el `.sqlite`, podemos perder los últimos cambios, que todavía estén en el `-wal`.

## Guardar y restaurar desde la propia app

Podríamos hacer la copia a mano desde el Finder o la terminal, pero es mucho más cómodo que lo haga la propia app al arrancar, según los **argumentos de lanzamiento** que le pasemos desde Xcode. Para ello añadimos al proyecto este archivo:

```swift
//  PuntoRestauracion.swift
//  Utilidad SOLO PARA DESARROLLO: guarda y restaura una copia de la base de datos
import Foundation
import CoreData

enum PuntoRestauracion {
    //CAMBIAR por el nombre del proyecto (el mismo que el del .xcdatamodeld)
    static let nombreBD = "Mensajeria"

    static let sufijos = [".sqlite", ".sqlite-wal", ".sqlite-shm"]
    //directorio donde NSPersistentContainer guarda la BD (Library/Application Support)
    static var dirBD: URL { NSPersistentContainer.defaultDirectoryURL() }
    static var dirCopia: URL { URL.documentsDirectory.appending(path: "punto_restauracion") }

    //Copia los archivos de la base de datos al directorio de la copia
    static func guardar() throws {
        let fm = FileManager.default
        try? fm.removeItem(at: dirCopia)
        try fm.createDirectory(at: dirCopia, withIntermediateDirectories: true)
        for sufijo in sufijos {
            let original = dirBD.appending(path: nombreBD + sufijo)
            if fm.fileExists(atPath: original.path) {
                try fm.copyItem(at: original, to: dirCopia.appending(path: nombreBD + sufijo))
            }
        }
        print("💾 Punto de restauración guardado")
    }

    //Sustituye la base de datos actual por la copia
    static func restaurar() throws {
        let fm = FileManager.default
        guard fm.fileExists(atPath: dirCopia.appending(path: nombreBD + ".sqlite").path) else {
            print("⚠️ No hay ningún punto de restauración guardado")
            return
        }
        for sufijo in sufijos {
            let actual = dirBD.appending(path: nombreBD + sufijo)
            let copia = dirCopia.appending(path: nombreBD + sufijo)
            try? fm.removeItem(at: actual)
            if fm.fileExists(atPath: copia.path) {
                try fm.copyItem(at: copia, to: actual)
            }
        }
        print("⏪ Base de datos restaurada desde el punto de restauración")
    }
}
```

Y en el inicializador del `PersistenceController` (archivo `Persistence.swift`) añadimos estas líneas **justo antes** de `loadPersistentStores`, que es cuando la base de datos todavía no está abierta:

```swift
init(inMemory: Bool = false) {
    container = NSPersistentContainer(name: "Mensajeria")
    if inMemory {
        container.persistentStoreDescriptions.first!.url = URL(fileURLWithPath: "/dev/null")
    }
    //AÑADIDO: punto de restauración, solo en las versiones de desarrollo
    //y nunca con la base de datos en memoria de las previews
    #if DEBUG
    if !inMemory {
        let argumentos = ProcessInfo.processInfo.arguments
        if argumentos.contains("-guardarPunto") {
            try? PuntoRestauracion.guardar()
        }
        if argumentos.contains("-restaurarPunto") {
            try? PuntoRestauracion.restaurar()
        }
    }
    #endif
    container.loadPersistentStores(completionHandler: { (storeDescription, error) in
        //...código generado por Xcode
    })
    container.viewContext.automaticallyMergesChangesFromParent = true
}
```

> El `#if DEBUG` hace que este código solo se compile en las versiones de desarrollo, y nunca llegue a una versión publicada en la App Store.

Los argumentos se configuran en `Product > Scheme > Edit Scheme...`, sección `Run`, pestaña `Arguments`, apartado `Arguments Passed On Launch`. Añadimos los dos, `-guardarPunto` y `-restaurarPunto`, y los activamos o desactivamos con su casilla según lo que queramos hacer en cada ejecución.

![](img/argumentos_lanzamiento.png)

## Cómo se usa

1. **Antes de tocar el modelo**, con la versión actual y algunos datos de prueba en la app, ejecutamos una vez con `-guardarPunto` activado. Después lo desactivamos.
2. Creamos la nueva versión del modelo y hacemos los cambios (lo veremos en las siguientes secciones).
3. Ejecutamos con `-restaurarPunto` activado. En cada ejecución, la app recupera la base de datos antigua y Core Data la vuelve a migrar. Podemos corregir el modelo o el código y repetir tantas veces como haga falta.
4. Cuando la migración funciona como queremos, desactivamos `-restaurarPunto`.

Si después vamos a hacer otro cambio en el modelo, repetimos el proceso desde el paso 1, guardando un nuevo punto de restauración con los datos ya migrados.

> La copia se guarda en el directorio `Documents` de la app, así que se conserva entre ejecuciones, pero **se pierde si borramos la app del simulador**.

> Esto resuelve la vuelta atrás de los **datos**. Para volver atrás en el **código** y en el modelo (por ejemplo, si queremos descartar una versión del modelo que hemos creado), usaremos el control de versiones del proyecto (`git`), como con cualquier otro cambio.

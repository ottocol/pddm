
# Ejercicio: Creación de App de Notas con Core Data

Aquí tienes el mismo ejercicio que está en los apuntes de la sesión pero sin la parte de teoría, si ya tienes claros los conceptos será más rápido seguir esta versión.

El objetivo es crear una pequeña aplicación para guardar y listar notas de texto persistentes.

## Parte 1: Configuración del Proyecto

1. Crea un nuevo proyecto en Xcode.
2. Selecciona la plantilla **App**.
3. Nombra el proyecto como **`NotasCoreData`**.
4. **Importante:** En el tercer desplegable, `Storage`, por defecto pone `None`. Cambia la opción a **Core Data**.

## Parte 2: Crear las Entidades (0,25 puntos)

Vamos a definir el modelo de datos editar el archivo `.xcdatamodeld` que se ha generado automáticamente.

1. Abre el archivo `NotasCoreData.xcdatamodeld` (o el nombre que tenga tu proyecto).
2. Pulsa el botón **Add Entity** (parte inferior).
3. Renombra la entidad creada a **`Nota`** (Doble clic sobre el nombre "Entity").
4. En la sección **Attributes**, añade los siguientes atributos pulsando el `+`:
* **Nombre:** `fecha` | **Tipo:** `Date`
* **Nombre:** `texto` | **Tipo:** `String`

5. **Guarda el archivo** (`File > Save`) para asegurar que Xcode genere las clases.

## Parte 3: Crear Datos Persistentes (0,25 puntos)

### 3.1. Interfaz de Usuario (Creación)

En el `Main.storyboard`, en la pantalla principal, añade los siguientes componentes y crea sus **Outlets** en `ViewController.swift`:

1. **Text View:** Para escribir el texto de la nota.
2. **Label (Fecha):** Para mostrar la fecha/hora.
3. **Label (Mensajes):** Para mostrar feedback al usuario (ej. "Nota guardada").
4. **Botón "Crear":** Crea un **Action** (Touch Up Inside).
5. **Botón "Guardar":** Crea un **Action** (Touch Up Inside).

### 3.2. Implementación del Código

En `ViewController.swift`:

**A. Importar Core Data**
Añade esto al principio del archivo:

```swift
import CoreData

```

**B. Acción del botón "Crear"**
Implementa el método para limpiar los campos:

```swift
@IBAction func crearNota(_ sender: Any) {
    // Asigna cadenas vacías a tus outlets del text view y los labels
    tuTextView.text = ""
    tuLabelFecha.text = ""
    tuLabelMensaje.text = ""
}

```

**C. Acción del botón "Guardar"**
Implementa la lógica de persistencia:

```swift
@IBAction func guardarNota(_ sender: Any) {
    // 1. Obtener referencia al AppDelegate y al Contexto
    guard let miDelegate = UIApplication.shared.delegate as? AppDelegate else {
        return
    }
    let miContexto = miDelegate.persistentContainer.viewContext

    // 2. Crear el objeto persistente
    let nuevaNota = Nota(context: miContexto)
    nuevaNota.fecha = Date()
    nuevaNota.texto = tuTextView.text // Asigna el contenido de tu outlet

    // 3. Guardar el contexto
    do {
        try miContexto.save()
        // Actualizar UI para feedback al usuario
        tuLabelMensaje.text = "Nota guardada correctamente"
        tuLabelFecha.text = "\(nuevaNota.fecha!)" // Formatea la fecha si lo deseas
    } catch {
        print("Error al guardar el contexto: \(error)")
        tuLabelMensaje.text = "Error al guardar"
    }
}

```

> *Nota: Si Xcode no reconoce la clase `Nota`, compila (`Cmd+B`) o guarda el `.xcdatamodeld`.*

## Parte 4: Listar las Notas (0,5 puntos)

Vamos a crear una segunda pantalla para ver las notas guardadas.

### 4.1. Configuración de la Navegación y UI

1. **Tab Bar Controller:** Selecciona el View Controller actual en el Storyboard, ve al menú `Editor > Embed In > Tab Bar Controller`.
2. Configura el título del item del tab inferior de la pantalla de creación como "Nueva".
3. **Nueva Pantalla:** Arrastra un **Table View Controller** al storyboard.
4. **Conexión:** Haz `Ctrl+Arrastrar` desde el *Tab Bar Controller* hacia el nuevo *Table View Controller*. Selecciona `view controllers` en "Relationship Segue".
5. Nombra el item del tab de la nueva pantalla como "Lista".

### 4.2. Configuración de la Tabla

1. Selecciona la celda prototipo de la tabla.
2. En el inspector de atributos, cambia el **Style** a `Basic`.
3. Establece el **Identifier** de la celda como `MiCelda`.

### 4.3. Crear el Controlador

1. Crea un nuevo archivo: `File > New > File...` -> **Cocoa Touch Class**.
2. Nombre: `ListaNotasController`.
3. Subclase de: `UITableViewController`.
4. **Asignación:** En el Storyboard, selecciona la nueva pantalla de tabla, ve al **Identity Inspector** y en `Class` selecciona `ListaNotasController`.

### 4.4. Implementación del Código de la Lista

En `ListaNotasController.swift`:

**A. Propiedades y Setup**

```swift
import UIKit
import CoreData // Importante

class ListaNotasController: UITableViewController {
    var listaNotas: [Nota]! // Array para almacenar los datos

    // ... resto de la clase
}

```

**B. Recuperar datos (Fetch)**
Sobrescribe `viewWillAppear` para cargar los datos cada vez que aparezca la pantalla:

```swift
override func viewWillAppear(_ animated: Bool) {
    super.viewWillAppear(animated)
    
    // 1. Obtener contexto (mismo código que en el paso anterior)
    guard let miDelegate = UIApplication.shared.delegate as? AppDelegate else { return }
    let miContexto = miDelegate.persistentContainer.viewContext
    
    // 2. Crear Request
    let request: NSFetchRequest<Nota> = Nota.fetchRequest()
    
    // 3. Ejecutar Query
    do {
        listaNotas = try miContexto.fetch(request)
        // 4. Refrescar la tabla
        self.tableView.reloadData()
    } catch {
        print("Error al recuperar notas: \(error)")
    }
}

```

**C. Métodos del Data Source**
Implementa/modifica los métodos de la tabla:

```swift
override func numberOfSections(in tableView: UITableView) -> Int {
    return 1
}

override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
    // Devolver el número de elementos en el array, o 0 si es nil
    return listaNotas?.count ?? 0
}

override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    // Usar el identificador que pusiste en el Storyboard
    let cell = tableView.dequeueReusableCell(withIdentifier: "MiCelda", for: indexPath)

    // Configurar la celda
    let nota = listaNotas[indexPath.row]
    cell.textLabel?.text = nota.texto
    
    return cell
}

```


# Proyecto_Numero_Dos

## DESCRIPCION DEL PROBLEMA

El problema es gestionar una colección de tareas pendientes, donde cada tarea tiene una prioridad asignada y un momento de llegada (cuando fue añadida). Se necesita una forma eficiente de determinar cuál es la próxima tarea a ejecutar, siguiendo la regla de: seleccionar la tarea con la máxima prioridad y, en caso de empate en prioridad, la que llegó primero (la más antigua). Además, se requiere poder visualizar las tareas pendientes en el orden en que fueron agregadas y poder cancelar tareas específicas antes de que se ejecuten.


## LENGUAJE DE PROGRAMACION Y FRAMEWORKS

El lenguaje de programacion utilizado es python y no utiliza frameworks pero si modulos de la biblioteca de python como:
heapq: Para implementar la cola de prioridad (montículo o heap).

time: Para obtener las marcas de tiempo (timestamps) necesarias para registrar el momento de llegada de las tareas.

typing: Para las anotaciones de tipo (ej. Optional, List, Any), que ayudan a la claridad y al análisis estático del código.

dataclasses (específicamente dataclass y field): Para crear clases de datos (Tarea y _Nodo) de forma más concisa y con generación automática de métodos como _init_, _repr_, y métodos de comparación.


## REQUISITOS PARA LA INSTALACION DEL CODIGO

Los requisitos para la instalacion del codigo son muy sencillos porque utiliza las bibliotecas estandar de python.

Se necesita tener instalado python en su version 3.7 o superior 

El codigo no requiere importar modulos externos ya que utiliza los propios de python (heap, time, typing, dataclases)


## REQUISITOS E INSTRUCCIONES PARA LA EJECUCION DEL CODIGO

# 1--> Guardar el código:
Descargar el archivo compartido con el Tag de version que esta alojado en el repositorio remoto llamado "Proyecto_final"

Debes guardar la carpeta completa con cada uno de los archivos para que se puedan ejecutar 

# 2--> Ejecutar el código:
Puedes ejecutar el codigo en un editor de texto como VS Code.

Puedes utlizar la terminal del propio VS Code o ejecutarlo a travez del cmd navegando a la ruta donde esta alojado el archivo. Ejm: python proyecti_Dos_Español.py 


## DESCRIPCION DE LAS FUNCIONALIDADES

# Agregar Tarea: 
Permitir añadir una nueva tarea al sistema proporcionando un identificador único (id_tarea) y un nivel de prioridad. El sistema debe registrar automaticamente el momento de llegada (marca_tiempo). Debe impedir que se añadan tareas con identificadores duplicados.

# Ejecutar Siguiente Tarea: 
Obtener y eliminar del sistema la tarea pendiente que tiene la máxima prioridad. Si hay varias con la misma máxima prioridad, debe seleccionar la que tenga la marca de tiempo más antigua (la que llegó primero). Debe devolver la tarea seleccionada o indicar que no hay tareas pendientes.

# Listar Tareas por Llegada: 
Proporcionar una forma de ver todas las tareas actualmente pendientes, ordenadas estrictamente por su momento de llegada, desde la mas antigua a la más reciente.

# Cancelar Tarea:
Permitir la eliminación de una tarea específica del sistema, identificada por su id_tarea, siempre que aún esté pendiente (no haya sido ejecutada).


## PRUEBA DEL CODIGO

El codigo tiene las siguientes clases principales:

"Tarea": Representa una tarea individual con su ID, prioridad y marca de tiempo.

"ListaDobleEnlazadaOrdenada": Mantiene las tareas ordenadas por su momento de llegada.

"ColaPrioridadTareas": Gestiona las tareas para obtener rápidamente la de mayor prioridad.

"GestorTareas": Coordina las estructuras de datos y las operaciones principales.

# A continuacion se muestra la ejecucion del codigo con una salida de ejemplo como prueba de funcionalidad

========================================
  INICIO DEMO GESTOR DE TAREAS
========================================
Añadiendo: Tarea(ID='Limpiar Casa', Prioridad=5, Llegada=1748092907.10)
Tarea 'Limpiar Casa' añadida correctamente.
Añadiendo: Tarea(ID='Estudiar Estructuras de Datos', Prioridad=10, Llegada=1748092907.13)
Tarea 'Estudiar Estructuras de Datos' añadida correctamente.
Añadiendo: Tarea(ID='Comprar Leche', Prioridad=5, Llegada=1748092907.17)
Tarea 'Comprar Leche' añadida correctamente.
Añadiendo: Tarea(ID='Llamar a Mamá', Prioridad=15, Llegada=1748092907.19)
Tarea 'Llamar a Mamá' añadida correctamente.
Añadiendo: Tarea(ID='Pasear al Perro', Prioridad=10, Llegada=1748092907.23)
Tarea 'Pasear al Perro' añadida correctamente.       

----------------------------------------

---> Listando tareas pendientes por orden de llegada:
   1. Tarea(ID='Limpiar Casa', Prioridad=5, Llegada=1748092907.10)
   2. Tarea(ID='Estudiar Estructuras de Datos', Prioridad=10, Llegada=1748092907.13)
   3. Tarea(ID='Comprar Leche', Prioridad=5, Llegada=1748092907.17)
   4. Tarea(ID='Llamar a Mamá', Prioridad=15, Llegada=1748092907.19)
   5. Tarea(ID='Pasear al Perro', Prioridad=10, Llegada=1748092907.23)

----------------------------------------
Ejecutando tareas...

---> Obteniendo la siguiente tarea a ejecutar...
*** Ejecutando: Tarea(ID='Llamar a Mamá', Prioridad=15, Llegada=1748092907.19) ***

---> Obteniendo la siguiente tarea a ejecutar...
*** Ejecutando: Tarea(ID='Estudiar Estructuras de Datos', Prioridad=10, Llegada=1748092907.13) ***

----------------------------------------

---> Listando tareas pendientes por orden de llegada:
   1. Tarea(ID='Limpiar Casa', Prioridad=5, Llegada=1748092907.10)
   2. Tarea(ID='Comprar Leche', Prioridad=5, Llegada=1748092907.17)
   3. Tarea(ID='Pasear al Perro', Prioridad=10, Llegada=1748092907.23)

----------------------------------------

---> Intentando cancelar la tarea con ID: 'Limpiar Casa'...
--- Encontrada: Tarea(ID='Limpiar Casa', Prioridad=5, Llegada=1748092907.10)     
--- Tarea 'Limpiar Casa' cancelada correctamente.

----------------------------------------

---> Listando tareas pendientes por orden de llegada:
   1. Tarea(ID='Comprar Leche', Prioridad=5, Llegada=1748092907.17)
   2. Tarea(ID='Pasear al Perro', Prioridad=10, Llegada=1748092907.23)

----------------------------------------
Ejecutando tareas restantes...

---> Obteniendo la siguiente tarea a ejecutar...
*** Ejecutando: Tarea(ID='Pasear al Perro', Prioridad=10, Llegada=1748092907.23) ***

---> Obteniendo la siguiente tarea a ejecutar...
*** Ejecutando: Tarea(ID='Comprar Leche', Prioridad=5, Llegada=1748092907.17) ***
---> Obteniendo la siguiente tarea a ejecutar...
--- No hay tareas pendientes para ejecutar.

----------------------------------------

---> Listando tareas pendientes por orden de llegada:
--- No hay tareas pendientes.

========================================
     FIN DEMO GESTOR DE TAREAS
========================================


## EXPLICACION

En la ejecucion del codigo podemos ver como se pueden adicionar varias tareas con diferentes prioridades; la lista de  tareas por orden de llegada; la ejecución de tareas según su prioridad (la más alta primero) y, en caso de empate, por orden de llegada (la más antigua primero); la cancelación de una tarea y el estado final del sistema despues de procesar y cancelar tareas.


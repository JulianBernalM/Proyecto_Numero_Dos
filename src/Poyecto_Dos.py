#Sistema de Gestión de Tareas con Prioridad y Orden de Llegada


import heapq  # Importamos la librería para usar colas de prioridad (heaps)
import time   # Para obtener la hora actual (timestamp)
from typing import Any, Optional, List # Para anotaciones de tipo (ayuda a entender qué tipo de dato se espera)

#-----------------------------------------------------
# PASO 1: Definir cómo es una Tarea (Nuestro Dato)
#-----------------------------------------------------
# Usamos 'dataclass' como una forma rápida de crear una clase que principalmente guarda datos.
# 'order=True' le dice a Python que genere automáticamente métodos de comparación (<, <=, >, >=)
# que son necesarios para que el heap (heapq) sepa cómo ordenar las tareas.
from dataclasses import dataclass, field 

@dataclass(order=True) 
class Task:
    """
    Representa una tarea individual en nuestro sistema.
    Contiene información sobre su prioridad, cuándo llegó y su ID único.
    También guarda una referencia a su lugar en la lista enlazada (explicado más abajo).
    """
    # --- Información principal de la tarea ---
    # Estos campos NO se usan directamente para ordenar en el HEAP, por eso 'compare=False'.
    priority: int = field(compare=False)      # Prioridad dada por el usuario (más alto = más importante)
    timestamp: float = field(compare=False)   # Momento exacto en que se creó (número decimal)
    task_id: Any = field(compare=False)       # Identificador único (puede ser string, número, etc.)

    # --- Campos auxiliares y ocultos SÓLO para ordenar en el HEAP ---
    # El heap (heapq) necesita saber qué tarea es "menor" que otra.
    # Queremos que la tarea con MAYOR prioridad salga primero. Como heapq es un MIN-heap
    # (siempre saca el elemento más pequeño), usamos un truco: guardamos la prioridad como
    # un número NEGATIVO. Así, la prioridad más alta (ej: 15) se vuelve el número más pequeño (-15)
    # y el min-heap la sacará primero.
    # Si dos tareas tienen la misma prioridad (ej: -10 y -10), queremos que la que llegó ANTES
    # (menor timestamp) salga primero. El timestamp ya funciona bien con el min-heap (menor es mejor).
    # Estos campos SÍ se usan para comparar (compare=True, que es el valor por defecto).
    # Los ponemos con un guion bajo '_' para indicar que son para uso interno de ordenación.
    _sort_priority: int = field(init=False, repr=False) 
    _sort_timestamp: float = field(init=False, repr=False)

    # --- Referencia para la Lista Enlazada ---
    # Esta variable guardará una "conexión" directa al nodo que contiene esta tarea
    # dentro de la lista doblemente enlazada (la estructura lineal).
    # Esto nos permite ELIMINAR la tarea de esa lista MUY RÁPIDO (en O(1))
    # una vez que la hemos sacado del heap, sin tener que buscarla.
    # 'None' significa que al principio no apunta a nada.
    # 'compare=False' porque no debe afectar al orden en el heap.
    # 'repr=False' para que no aparezca al imprimir el objeto Task (lo hace más limpio).
    list_node: Optional['SortedDoublyLinkedList._Node'] = field(default=None, compare=False, repr=False)

    # Esta función especial '__post_init__' se ejecuta justo después de crear una Tarea.
    # La usamos para calcular los valores de ordenación a partir de la prioridad y timestamp.        
    def __post_init__(self):
        # Hacemos negativa la prioridad para que el min-heap funcione como max-heap.
        self._sort_priority = -self.priority 
        # El timestamp se usa tal cual (menor timestamp sale antes en caso de empate de prioridad).
        self._sort_timestamp = self.timestamp

    # Define cómo se verá la Tarea si la imprimimos (print).
    def __str__(self):
        # formateamos el timestamp para que no muestre tantos decimales
        ts_formatted = f"{self.timestamp:.2f}" 
        return f"Tarea(ID='{self.task_id}', Prioridad={self.priority}, Llegada={ts_formatted})"
    
    # Define cómo se verá la Tarea en representaciones internas (como dentro de una lista).
    def __repr__(self):
        return str(self) # Hacemos que se vea igual que al imprimirla.

#-----------------------------------------------------------------------
# PASO 2: Implementar la Lista Doblemente Enlazada Ordenada (Lineal)
#-----------------------------------------------------------------------
# Esta estructura mantiene las tareas ordenadas por su 'timestamp' (orden de llegada).
# Es "lineal" porque conceptualmente los elementos van uno detrás de otro.
# Es "doblemente enlazada" porque cada elemento (nodo) sabe cuál es el siguiente Y el anterior.
# NO es un array/lista de Python normal.

class SortedDoublyLinkedList:
    """
    Guarda las tareas ordenadas por el momento en que llegaron (timestamp).
    Permite añadir tareas en orden y listarlas fácilmente en ese orden.
    También permite eliminar una tarea rápidamente si sabemos exactamente dónde está (su nodo).
    """

    # Clase interna para representar cada 'eslabón' o 'caja' en la lista.
    # Cada nodo contiene una Tarea y referencias (punteros) al nodo anterior y siguiente.
    @dataclass
    class _Node:
        task: Optional[Task]  # La tarea guardada en este nodo (puede ser None para los centinelas)
        prev: Optional['_Node'] = None # Referencia al nodo anterior
        next: Optional['_Node'] = None # Referencia al nodo siguiente

    def __init__(self):
        """Inicializa una lista vacía."""
        # Creamos dos nodos especiales llamados 'centinelas'. No guardan tareas reales.
        # self.head: Marca el inicio absoluto de la lista.
        # self.tail: Marca el final absoluto de la lista.
        # Esto simplifica mucho la lógica de añadir/quitar elementos en los bordes,
        # porque siempre hay un nodo 'prev' y 'next' (los centinelas).
        self.head = self._Node(task=None) # Nodo cabeza (ficticio)
        self.tail = self._Node(task=None) # Nodo cola (ficticio)
        
        # Conectamos los centinelas entre sí para representar una lista vacía.
        self.head.next = self.tail
        self.tail.prev = self.head
        
        self.size = 0 # Contador para saber cuántas tareas reales hay.

    def insert_task_ordered(self, task_to_insert: Task) -> _Node:
        """
        Añade una nueva tarea a la lista, asegurándose de que quede en el lugar
        correcto según su 'timestamp' (de más antiguo a más nuevo).
        Devuelve el nodo que se creó para esta tarea.
        """
        # 1. Crear el nuevo nodo que contendrá la tarea.
        new_node = self._Node(task=task_to_insert)
        
        # 2. Encontrar dónde insertar el nuevo nodo.
        # Empezamos a buscar desde el primer nodo real (el siguiente a 'head').
        current_node = self.head.next
        
        # Avanzamos mientras no lleguemos al final (tail) Y
        # el timestamp del nodo actual sea MENOR que el de la nueva tarea.
        while current_node != self.tail and current_node.task.timestamp < task_to_insert.timestamp:
            current_node = current_node.next
            
        # Cuando el bucle termina, 'current_node' es el primer nodo cuyo timestamp es
        # MAYOR O IGUAL que el de la nueva tarea (o es el nodo 'tail' si la nueva tarea
        # es la más reciente de todas).
        # Debemos insertar 'new_node' JUSTO ANTES de 'current_node'.
        
        # 3. Conectar el nuevo nodo en la lista.
        node_before = current_node.prev # El nodo que estaba antes de 'current_node'.
        
        # Actualizamos las conexiones:
        # a) El nodo anterior ahora apunta a 'new_node' como su siguiente.
        node_before.next = new_node
        # b) 'new_node' apunta al nodo anterior como su previo.
        new_node.prev = node_before
        # c) 'new_node' apunta a 'current_node' como su siguiente.
        new_node.next = current_node
        # d) 'current_node' apunta a 'new_node' como su previo.
        current_node.prev = new_node
        
        # 4. Incrementar el tamaño de la lista.
        self.size += 1
        
        # 5. ¡Importante! Guardamos la referencia a este 'new_node' dentro de la
        #    propia tarea. Esto nos permitirá encontrar y borrar este nodo
        #    muy rápido más tarde si es necesario (ver 'remove_node').
        task_to_insert.list_node = new_node 
        
        # 6. Devolvemos el nodo recién creado (por si se necesita fuera).
        return new_node

    def remove_node(self, node_to_remove: _Node):
        """
        Elimina un nodo específico de la lista. Esto es muy rápido (O(1))
        porque ya sabemos exactamente qué nodo quitar (no hay que buscarlo).
        Requiere que 'node_to_remove' sea un nodo válido de la lista.
        """
        # Comprobación básica: no intentar quitar nodos nulos o los centinelas.
        if node_to_remove is None or node_to_remove == self.head or node_to_remove == self.tail:
            print("Advertencia: Intento de eliminar nodo inválido.")
            return

        # Obtenemos los nodos vecinos al que vamos a eliminar.
        prev_node = node_to_remove.prev
        next_node = node_to_remove.next
        
        # Hacemos que los vecinos se "salten" al nodo a eliminar, apuntándose entre sí.
        if prev_node: # Siempre debería haber un nodo previo (al menos 'head')
            prev_node.next = next_node
        if next_node: # Siempre debería haber un nodo siguiente (al menos 'tail')
            next_node.prev = prev_node
            
        # Decrementamos el tamaño.
        self.size -= 1
        
        # Buena práctica: limpiar las referencias del nodo eliminado para evitar problemas.
        node_to_remove.prev = None
        node_to_remove.next = None
        
        # Crucial: Si la tarea dentro del nodo eliminado aún tiene una referencia
        # a este nodo, la quitamos (ponemos a None). Esto evita que la tarea
        # intente usar un nodo que ya no está en la lista.
        if node_to_remove.task and node_to_remove.task.list_node == node_to_remove:
             node_to_remove.task.list_node = None
             
    def get_tasks_in_arrival_order(self) -> List[Task]:
        """
        Recorre la lista desde el principio hasta el final y devuelve una lista
        normal de Python con todas las tareas en orden de llegada (timestamp).
        Esto es O(N) porque tiene que visitar cada nodo.
        """
        tasks_list = []
        current_node = self.head.next # Empezamos desde el primer nodo real.
        while current_node != self.tail: # Continuamos hasta llegar al final.
            tasks_list.append(current_node.task) # Añadimos la tarea a nuestra lista resultado.
            current_node = current_node.next # Pasamos al siguiente nodo.
        return tasks_list

    def __len__(self):
        """Permite usar len(lista_enlazada) para obtener el número de tareas."""
        return self.size

    def is_empty(self):
        """Comprueba si la lista no tiene tareas."""
        return self.size == 0

#-----------------------------------------------------------------------
# PASO 3: Implementar la Cola de Prioridad (No Lineal - Heap)
#-----------------------------------------------------------------------
# Esta estructura usa el módulo 'heapq' de Python, que implementa un montículo binario (heap).
# Un heap es eficiente para:
#   1. Añadir elementos (O(log N)).
#   2. Encontrar y sacar el elemento "más pequeño" (O(log N)).
# Como queremos sacar la tarea con MAYOR prioridad, usamos el truco de la prioridad negativa
# explicado en la clase Task. Así, el heap nos dará la tarea correcta.
# Es "no lineal" porque un heap se organiza como un árbol binario, no una secuencia simple.

class PriorityTaskQueue:
    """
    Gestiona las tareas para poder obtener rápidamente la que tiene
    mayor prioridad (y, en caso de empate, la que llegó antes).
    Usa un min-heap internamente.
    """
    def __init__(self):
        # El heap se almacena como una lista de Python, pero heapq la manipula
        # para mantener la propiedad del heap (el padre siempre es "menor" que sus hijos).
        self._heap: List[Task] = [] 
        
        # --- Manejo de Eliminaciones (Borrado Perezoso) ---
        # El problema con 'heapq' es que NO ofrece una forma eficiente de
        # ELIMINAR un elemento cualquiera que esté en medio del heap. Buscarlo
        # y reorganizar el heap sería lento (O(N)).
        # Para solucionar esto, usamos "borrado perezoso":
        # Cuando una tarea se "cancela" o se saca por otro motivo (como desde
        # la lista enlazada), no la borramos físicamente del heap de inmediato.
        # En lugar de eso, la marcamos como "inactiva" o "ya no válida".
        # Usamos un 'set' (conjunto) para guardar los IDs de las tareas que SÍ están activas.
        # Los sets son muy rápidos para añadir, quitar y comprobar si un elemento existe (O(1)).
        self._active_task_ids = set() 

    def add_task(self, task: Task):
        """Añade una tarea a la cola de prioridad."""
        # heapq.heappush añade la tarea y reorganiza el heap para mantener el orden.
        # Usa la comparación definida en la clase Task (<) para saber dónde ponerla.
        heapq.heappush(self._heap, task)
        # Marcamos la tarea como activa añadiendo su ID al set.
        self._active_task_ids.add(task.task_id)

    def get_highest_priority_task(self) -> Optional[Task]:
        """
        Obtiene y elimina la tarea con la mayor prioridad (y menor timestamp
        en caso de empate). Devuelve la tarea o None si la cola está vacía.
        """
        # Usamos un bucle por si las tareas en la cima del heap ya no son válidas.
        while self._heap:
            # heapq.heappop saca y devuelve el elemento "más pequeño" del heap
            # (que será nuestra tarea con mayor prioridad real gracias al truco).
            # Esto también reorganiza el heap (O(log N)).
            potential_task = heapq.heappop(self._heap)
            
            # --- Comprobación del Borrado Perezoso ---
            # Antes de devolver la tarea, verificamos si su ID está en nuestro
            # conjunto de tareas activas.
            if potential_task.task_id in self._active_task_ids:
                # ¡Sí está activa! Esta es la tarea que buscamos.
                # La quitamos del conjunto de activas porque ya la estamos sacando.
                self._active_task_ids.remove(potential_task.task_id)
                # La devolvemos.
                return potential_task
            # else:
            #   Si no está en el set, significa que esta tarea fue "cancelada"
            #   o eliminada previamente. Simplemente la ignoramos y el bucle
            #   `while` continuará para sacar la siguiente tarea del heap.
            
        # Si el bucle termina, significa que el heap se quedó vacío.
        return None 

    def mark_task_as_removed(self, task_id: Any):
        """
        Marca una tarea como inactiva (para el borrado perezoso).
        Esto se llama cuando una tarea se elimina por otro medio (ej: cancelada).
        Simplemente quitamos su ID del set de tareas activas.
        """
        # El método discard es seguro: si el ID no está en el set, no hace nada (no da error).
        self._active_task_ids.discard(task_id)

    def __len__(self):
        """Devuelve el número de tareas *activas* en la cola."""
        # Es importante devolver el tamaño del set, no del heap,
        # porque el heap puede contener tareas "inactivas".
        return len(self._active_task_ids)

    def is_empty(self):
        """Comprueba si no hay tareas activas."""
        return len(self._active_task_ids) == 0

#-----------------------------------------------------
# PASO 4: El Gestor Principal que une todo
#-----------------------------------------------------

class TaskManager:
    """
    Clase principal que coordina las dos estructuras de datos:
    - La Cola de Prioridad (Heap) para obtener la siguiente tarea a ejecutar.
    - La Lista Doblemente Enlazada Ordenada para listar tareas por llegada.
    """
    def __init__(self):
        # Creamos una instancia de nuestra cola de prioridad.
        self.priority_queue = PriorityTaskQueue() # Estructura No Lineal (Heap)
        # Creamos una instancia de nuestra lista ordenada por llegada.
        self.arrival_list = SortedDoublyLinkedList() # Estructura Lineal (Lista Enlazada)
        
        # Opcional pero útil: un diccionario para acceder rápidamente a una tarea
        # si solo conocemos su ID. Facilita operaciones como 'cancelar_tarea'.
        # Clave: task_id, Valor: objeto Task completo.
        self._tasks_by_id_lookup = {} 

    def add_task(self, task_id: Any, priority: int):
        """
        Añade una nueva tarea al sistema.
        La tarea se añade a AMBAS estructuras de datos.
        """
        # Comprobamos si ya existe una tarea con ese ID.
        if task_id in self._tasks_by_id_lookup:
            print(f"Error: El ID de tarea '{task_id}' ya existe. No se añadió.")
            return
            
        # Obtenemos el timestamp actual.
        current_timestamp = time.time() 
        
        # Creamos el objeto Tarea.
        new_task = Task(priority=priority, timestamp=current_timestamp, task_id=task_id)
        
        print(f"Añadiendo: {new_task}")
        
        # 1. Añadir a la lista ordenada por timestamp.
        #    Recordemos que `insert_task_ordered` también guarda la referencia
        #    del nodo de la lista dentro de `new_task.list_node`.
        self.arrival_list.insert_task_ordered(new_task) 
        
        # 2. Añadir a la cola de prioridad (heap).
        self.priority_queue.add_task(new_task)
        
        # 3. Guardar en nuestro diccionario de búsqueda por ID.
        self._tasks_by_id_lookup[task_id] = new_task
        
        print(f"Tarea '{task_id}' añadida correctamente.")

    def execute_next_task(self) -> Optional[Task]:
        """
        Obtiene la tarea con mayor prioridad (y más antigua en caso de empate),
        la elimina de ambas estructuras y la devuelve.
        """
        print("\n---> Obteniendo la siguiente tarea a ejecutar...")
        
        # 1. Sacar la tarea de la cola de prioridad (heap).
        #    Esto ya maneja el borrado perezoso internamente.
        task_to_execute = self.priority_queue.get_highest_priority_task()
        
        # 2. Si encontramos una tarea válida:
        if task_to_execute:
            print(f"*** Ejecutando: {task_to_execute} ***")
            
            # 3. Eliminarla de la lista doblemente enlazada.
            #    Usamos la referencia directa al nodo guardada en la tarea.
            #    Esto es O(1), ¡muy rápido!
            if task_to_execute.list_node:
                self.arrival_list.remove_node(task_to_execute.list_node)
            else:
                 # Esto sería inesperado si todo funciona bien.
                 print(f"Advertencia: La tarea {task_to_execute.task_id} no tenía referencia a su nodo en la lista.")

            # 4. Eliminarla del diccionario de búsqueda por ID.
            if task_to_execute.task_id in self._tasks_by_id_lookup:
                del self._tasks_by_id_lookup[task_to_execute.task_id]
                
            # 5. Devolver la tarea ejecutada.
            return task_to_execute
        else:
            # Si no había tareas activas en la cola de prioridad.
            print("--- No hay tareas pendientes para ejecutar.")
            return None

    def list_tasks_by_arrival(self):
        """Muestra todas las tareas pendientes, ordenadas por su hora de llegada."""
        print("\n---> Listando tareas pendientes por orden de llegada:")
        
        # Obtenemos la lista ordenada desde nuestra estructura lineal.
        ordered_tasks = self.arrival_list.get_tasks_in_arrival_order()
        
        if not ordered_tasks:
            print("--- No hay tareas pendientes.")
        else:
            # Imprimimos cada tarea.
            for i, task in enumerate(ordered_tasks):
                print(f"   {i+1}. {task}")
        # Podríamos devolver la lista si quisiéramos usarla fuera:
        # return ordered_tasks

    def cancel_task(self, task_id: Any):
        """
        Elimina una tarea específica del sistema usando su ID.
        Debe quitarla de ambas estructuras.
        """
        print(f"\n---> Intentando cancelar la tarea con ID: '{task_id}'...")
        
        # 1. Buscar la tarea en nuestro diccionario por ID.
        if task_id in self._tasks_by_id_lookup:
            task_to_cancel = self._tasks_by_id_lookup[task_id]
            print(f"--- Encontrada: {task_to_cancel}")
            
            # 2. "Eliminarla" de la cola de prioridad (usando borrado perezoso).
            #    Marcamos su ID como inactivo.
            self.priority_queue.mark_task_as_removed(task_id)
            
            # 3. Eliminarla físicamente de la lista doblemente enlazada.
            #    Usamos la referencia al nodo guardada en la tarea.
            if task_to_cancel.list_node:
                self.arrival_list.remove_node(task_to_cancel.list_node)
            else:
                 print(f"Advertencia: La tarea a cancelar {task_id} no tenía referencia a su nodo en la lista.")

            
            # 4. Eliminarla del diccionario de búsqueda por ID.
            del self._tasks_by_id_lookup[task_id]
            
            print(f"--- Tarea '{task_id}' cancelada correctamente.")
        else:
            # Si el ID no se encontró en el diccionario.
            print(f"--- Error: No se encontró ninguna tarea con el ID '{task_id}'.")


#-----------------------------------------------------
# PASO 5: Ejemplo de Uso
#-----------------------------------------------------
# Este bloque solo se ejecuta si corres este archivo directamente.
if __name__ == "__main__":
    
    print("========================================")
    print("  INICIO DEL GESTOR DE TAREAS DEMO")
    print("========================================")

    # Creamos nuestro gestor
    manager = TaskManager()

    # Añadimos algunas tareas de ejemplo (ID, Prioridad)
    # Damos pequeñas pausas para asegurarnos de que los timestamps sean distintos.
    manager.add_task("Limpiar", 5)
    time.sleep(0.02) 
    manager.add_task("Estudiar Estructuras", 10)
    time.sleep(0.02)
    manager.add_task("Comprar Leche", 5) # Misma prioridad que Limpiar, pero llegó después
    time.sleep(0.02)
    manager.add_task("Llamar a Mamá", 15) 
    time.sleep(0.02)
    manager.add_task("Pasear al Perro", 10) # Misma prioridad que Estudiar, pero llegó después

    print("\n----------------------------------------")
    # Veamos las tareas ordenadas por llegada
    manager.list_tasks_by_arrival()
    # Salida esperada (en orden): Limpiar, Estudiar, Comprar Leche, Llamar a Mamá, Pasear al Perro

    print("\n----------------------------------------")

    # Ejecutemos algunas tareas (deben salir por prioridad)
    print("Ejecutando tareas...")
    manager.execute_next_task() # Debería ser "Llamar a Mamá" (prioridad 15)
    manager.execute_next_task() # Debería ser "Estudiar Estructuras" (prioridad 10, llegó antes)
    
    print("\n----------------------------------------")

    # Veamos qué tareas quedan, ordenadas por llegada
    manager.list_tasks_by_arrival() 
    # Salida esperada (en orden): Limpiar, Comprar Leche, Pasear al Perro

    print("\n----------------------------------------")
    
    # Vamos a cancelar una tarea que aún no se ha ejecutado
    manager.cancel_task("Limpiar") 

    print("\n----------------------------------------")

    # Veamos qué tareas quedan ahora
    manager.list_tasks_by_arrival() 
    # Salida esperada (en orden): Comprar Leche, Pasear al Perro

    print("\n----------------------------------------")

    # Ejecutemos las tareas restantes
    print("Ejecutando tareas restantes...")
    manager.execute_next_task() # Debería ser "Pasear al Perro" (prioridad 10)
    manager.execute_next_task() # Debería ser "Comprar Leche" (prioridad 5)
    
    # Intentamos ejecutar una más (ya no debería haber)
    manager.execute_next_task() # Debería decir que no hay tareas

    print("\n----------------------------------------")
    # Verifiquemos que la lista está vacía
    manager.list_tasks_by_arrival() 
    
    print("\n========================================")
    print("     FIN DEL GESTOR DE TAREAS DEMO")
    print("========================================")

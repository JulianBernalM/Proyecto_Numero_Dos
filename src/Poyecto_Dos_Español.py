# -*- coding: utf-8 -*- # Para asegurar compatibilidad con caracteres españoles

import heapq  # Para usar colas de prioridad (montículos o heaps)
import time   # Para obtener la marca de tiempo actual
from typing import Any, Optional, List # Para anotaciones de tipo (clarifican qué tipo de dato se espera)
from dataclasses import dataclass, field # Para crear clases de datos de forma concisa

#-----------------------------------------------------
# PASO 1: Definir la estructura de una Tarea
#-----------------------------------------------------
# Usamos 'dataclass' para definir la clase 'Tarea' fácilmente.
# 'order=True' genera automáticamente métodos de comparación (<, <=, >, >=)
# que necesita el montículo (heapq) para ordenar las tareas.
@dataclass(order=True)
class Tarea:
    """
    Representa una tarea individual en nuestro sistema.
    Contiene su prioridad, momento de llegada (marca de tiempo) e ID único.
    También guarda una referencia a su nodo en la lista enlazada.
    """
    # --- Información principal de la tarea (no usada para ordenar directamente en el heap) ---
    prioridad: int = field(compare=False)       # Prioridad dada (número mayor = más importante)
    marca_tiempo: float = field(compare=False)  # Momento exacto de creación (número decimal)
    id_tarea: Any = field(compare=False)        # Identificador único (texto, número, etc.)

    # --- Campos auxiliares SÓLO para ordenar en el HEAP (montículo) ---
    # El montículo necesita saber qué tarea es "menor" que otra.
    # Queremos procesar primero la tarea con MAYOR prioridad. Como heapq es un MIN-heap
    # (siempre extrae el elemento más pequeño), usamos un truco: guardamos la prioridad
    # como un número NEGATIVO. Así, la prioridad más alta (ej: 15) se vuelve -15 (el número "más pequeño")
    # y el min-heap la extraerá primero.
    # Si hay empate en prioridad (ej: -10 y -10), queremos procesar la que llegó ANTES
    # (menor marca_tiempo). La marca_tiempo ya funciona bien con el min-heap.
    # Estos campos SÍ se usan para comparar (compare=True es el valor por defecto).
    # El guion bajo '_' indica que son para uso interno de ordenación.
    _prioridad_ordenacion: int = field(init=False, repr=False)
    _marca_tiempo_ordenacion: float = field(init=False, repr=False)

    # --- Referencia al Nodo en la Lista Doblemente Enlazada ---
    # Guarda una referencia directa al nodo que contiene esta tarea dentro de la
    # lista doblemente enlazada (la estructura lineal).
    # Permite ELIMINAR la tarea de esa lista MUY RÁPIDO (en O(1))
    # una vez extraída del heap, sin necesidad de buscarla.
    # 'Optional[...] indica que puede ser un Nodo o None (al inicio).
    # 'compare=False' para que no afecte al orden en el heap.
    # 'repr=False' para que no aparezca al imprimir el objeto Tarea (más limpio).
    nodo_lista: Optional['ListaDobleEnlazadaOrdenada._Nodo'] = field(default=None, compare=False, repr=False)

    # Esta función especial se ejecuta justo después de crear una Tarea.
    # La usamos para calcular los valores de ordenación (_prioridad_ordenacion, _marca_tiempo_ordenacion).
    def __post_init__(self):
        # Hacemos negativa la prioridad para que el min-heap funcione como max-heap.
        self._prioridad_ordenacion = -self.prioridad
        # La marca de tiempo se usa tal cual (menor es procesada antes en caso de empate).
        self._marca_tiempo_ordenacion = self.marca_tiempo

    # Define cómo se mostrará la Tarea al usar print().
    def __str__(self):
        # Formatea la marca de tiempo para legibilidad.
        ts_formateado = f"{self.marca_tiempo:.2f}"
        return f"Tarea(ID='{self.id_tarea}', Prioridad={self.prioridad}, Llegada={ts_formateado})"

    # Define cómo se representará la Tarea internamente (ej: dentro de una lista).
    def __repr__(self):
        # Hacemos que se vea igual que al imprimirla.
        return str(self)

#-----------------------------------------------------------------------
# PASO 2: Implementar la Lista Doblemente Enlazada Ordenada (Lineal)
#-----------------------------------------------------------------------
# Mantiene las tareas ordenadas por 'marca_tiempo' (orden de llegada).
# Es "lineal": los elementos van uno detrás de otro conceptualmente.
# Es "doblemente enlazada": cada nodo conoce al siguiente Y al anterior.
# NO es una lista estándar de Python.

class ListaDobleEnlazadaOrdenada:
    """
    Almacena tareas ordenadas por su momento de llegada (marca_tiempo).
    Permite añadir tareas manteniendo el orden y listarlas fácilmente.
    Permite eliminar una tarea rápidamente si se conoce su nodo (O(1)).
    """

    # Clase interna (_Nodo) para representar cada elemento (eslabón) de la lista.
    @dataclass
    class _Nodo:
        tarea: Optional[Tarea]          # La tarea almacenada (None para nodos centinela)
        anterior: Optional['_Nodo'] = None # Referencia al nodo previo
        siguiente: Optional['_Nodo'] = None # Referencia al nodo siguiente

    def __init__(self):
        """Inicializa una lista vacía con nodos centinela."""
        # Nodos 'centinela' (ficticios) para marcar inicio y fin.
        # Simplifican la lógica de inserción/eliminación en los extremos,
        # ya que siempre hay un nodo 'anterior' y 'siguiente'.
        self.cabeza = self._Nodo(tarea=None) # Nodo cabeza (ficticio)
        self.cola = self._Nodo(tarea=None)   # Nodo cola (ficticio)

        # Conectar centinelas para representar lista vacía.
        self.cabeza.siguiente = self.cola
        self.cola.anterior = self.cabeza

        self.tamano = 0 # Contador de tareas reales en la lista.

    def insertar_tarea_ordenada(self, tarea_a_insertar: Tarea) -> _Nodo:
        """
        Añade una tarea a la lista manteniendo el orden por 'marca_tiempo'
        (de más antiguo a más nuevo). Devuelve el nodo creado.
        """
        # 1. Crear el nuevo nodo para la tarea.
        nuevo_nodo = self._Nodo(tarea = tarea_a_insertar)

        # 2. Encontrar la posición correcta para insertar.
        # Empezamos desde el primer nodo real (después de la cabeza).
        nodo_actual = self.cabeza.siguiente

        # Avanzamos mientras no lleguemos al final (cola) Y
        # la marca de tiempo del nodo actual sea MENOR que la de la nueva tarea.
        while nodo_actual != self.cola and nodo_actual.tarea.marca_tiempo < tarea_a_insertar.marca_tiempo:
            nodo_actual = nodo_actual.siguiente

        # Al salir del bucle, 'nodo_actual' es el nodo ANTE el cual debemos insertar
        # 'nuevo_nodo' (o es la cola si la nueva tarea es la más reciente).

        # 3. Conectar el nuevo nodo en la lista.
        nodo_anterior = nodo_actual.anterior # Nodo que estaba antes de 'nodo_actual'.

        # Actualizar enlaces:
        nodo_anterior.siguiente = nuevo_nodo
        nuevo_nodo.anterior = nodo_anterior
        nuevo_nodo.siguiente = nodo_actual
        nodo_actual.anterior = nuevo_nodo

        # 4. Incrementar el tamaño.
        self.tamano += 1

        # 5. ¡IMPORTANTE! Guardar la referencia a 'nuevo_nodo' dentro de la tarea.
        #    Esto permite la eliminación rápida (O(1)) más tarde (ver 'eliminar_nodo').
        tarea_a_insertar.nodo_lista = nuevo_nodo

        # 6. Devolver el nodo recién creado.
        return nuevo_nodo

    def eliminar_nodo(self, nodo_a_eliminar: _Nodo):
        """
        Elimina un nodo específico de la lista. Es O(1) porque recibe el nodo directamente.
        Requiere que 'nodo_a_eliminar' sea un nodo válido de esta lista.
        """
        # Comprobación básica: no eliminar nodos nulos o centinelas.
        if nodo_a_eliminar is None or nodo_a_eliminar == self.cabeza or nodo_a_eliminar == self.cola:
            print("Advertencia: Intento de eliminar nodo inválido.")
            return

        # Obtener los nodos vecinos.
        nodo_previo = nodo_a_eliminar.anterior
        nodo_siguiente = nodo_a_eliminar.siguiente

        # Hacer que los vecinos se "salten" al nodo a eliminar, enlazándose entre sí.
        if nodo_previo:
            nodo_previo.siguiente = nodo_siguiente
        if nodo_siguiente:
            nodo_siguiente.anterior = nodo_previo

        # Decrementar el tamaño.
        self.tamano -= 1

        # Buena práctica: limpiar referencias del nodo eliminado.
        nodo_a_eliminar.anterior = None
        nodo_a_eliminar.siguiente = None

        # Crucial: Si la tarea aún apuntaba a este nodo, quitar esa referencia.
        if nodo_a_eliminar.tarea and nodo_a_eliminar.tarea.nodo_lista == nodo_a_eliminar:
             nodo_a_eliminar.tarea.nodo_lista = None

    def obtener_tareas_por_llegada(self) -> List[Tarea]:
        """
        Devuelve una lista estándar de Python con las tareas ordenadas
        por momento de llegada (recorriendo la lista enlazada). O(N).
        """
        lista_tareas = []
        nodo_actual = self.cabeza.siguiente # Empezar desde el primer nodo real.
        while nodo_actual != self.cola:     # Continuar hasta llegar a la cola.
            lista_tareas.append(nodo_actual.tarea)
            nodo_actual = nodo_actual.siguiente
        return lista_tareas

    def __len__(self):
        """Permite usar len() para obtener el número de tareas."""
        return self.tamano

    def esta_vacia(self):
        """Comprueba si la lista no tiene tareas."""
        return self.tamano == 0

#-----------------------------------------------------------------------
# PASO 3: Implementar la Cola de Prioridad (No Lineal - Heap/Montículo)
#-----------------------------------------------------------------------
# Usa 'heapq' de Python (implementación de montículo binario).
# Eficiente para:
#   1. Añadir elementos (O(log N)).
#   2. Encontrar y extraer el elemento "más pequeño" (O(log N)).
# Usamos el truco de la prioridad negativa para que actúe como cola de máxima prioridad.
# Es "no lineal" porque se organiza como un árbol.

class ColaPrioridadTareas:
    """
    Gestiona tareas para obtener rápidamente la de mayor prioridad
    (y más antigua en caso de empate). Usa un min-heap internamente.
    Implementa borrado perezoso para eficiencia.
    """
    def __init__(self):
        # El montículo se guarda como una lista, pero 'heapq' mantiene la propiedad del heap.
        self._monticulo: List[Tarea] = []

        # --- Manejo de Eliminaciones Eficiente (Borrado Perezoso) ---
        # 'heapq' NO permite eliminar eficientemente un elemento arbitrario (sería O(N)).
        # Solución: "Borrado Perezoso" (Lazy Deletion).
        # Cuando una tarea se cancela, no la borramos físicamente del montículo al instante.
        # En su lugar, la marcamos como "inactiva".
        # Usamos un 'set' (conjunto) para guardar los IDs de las tareas que SÍ están activas.
        # Los sets son muy rápidos para añadir, quitar y comprobar pertenencia (O(1)).
        self._ids_tareas_activas = set()

    def agregar_tarea(self, tarea: Tarea):
        """Añade una tarea a la cola de prioridad (montículo)."""
        # heapq.heappush añade y reorganiza el montículo (O(log N)).
        # Usa la comparación definida en la clase Tarea (<).
        heapq.heappush(self._monticulo, tarea)
        # Marcar la tarea como activa en el conjunto.
        self._ids_tareas_activas.add(tarea.id_tarea)

    def obtener_tarea_max_prioridad(self) -> Optional[Tarea]:
        """
        Obtiene y elimina la tarea con mayor prioridad (y más antigua en empate).
        Devuelve la tarea o None si la cola está vacía. Usa borrado perezoso.
        """
        # Bucle por si la cima del montículo contiene tareas ya "eliminadas".
        while self._monticulo:
            # heapq.heappop extrae y devuelve el elemento "más pequeño" (mayor prioridad real).
            # Reorganiza el montículo (O(log N)).
            posible_tarea = heapq.heappop(self._monticulo)

            # --- Comprobación del Borrado Perezoso ---
            # ¿Está el ID de esta tarea en nuestro conjunto de activas?
            if posible_tarea.id_tarea in self._ids_tareas_activas:
                # ¡Sí! Esta es la tarea válida que buscamos.
                # La quitamos del conjunto de activas porque la estamos extrayendo.
                self._ids_tareas_activas.remove(posible_tarea.id_tarea)
                # La devolvemos.
                return posible_tarea
            # else:
            #   Si no está en el set, fue marcada como eliminada previamente.
            #   La ignoramos y el bucle `while` continúa para sacar la siguiente.

        # Si el bucle termina, el montículo (de tareas activas) estaba vacío.
        return None

    def marcar_tarea_como_eliminada(self, id_tarea: Any):
        """
        Marca una tarea como inactiva (borrado perezoso). Se usa al cancelar.
        Simplemente quita su ID del conjunto de tareas activas.
        """
        # discard() es seguro: si el ID no está, no hace nada (no da error).
        self._ids_tareas_activas.discard(id_tarea)

    def __len__(self):
        """Devuelve el número de tareas *activas*."""
        # Importante: devolver el tamaño del set, no del montículo físico.
        return len(self._ids_tareas_activas)

    def esta_vacia(self):
        """Comprueba si no hay tareas activas."""
        return len(self._ids_tareas_activas) == 0

#-----------------------------------------------------
# PASO 4: El Gestor Principal que coordina todo
#-----------------------------------------------------

class GestorTareas:
    """
    Clase principal que utiliza y coordina las dos estructuras:
    - ColaPrioridadTareas (Heap) para obtener la siguiente tarea a ejecutar.
    - ListaDobleEnlazadaOrdenada para listar tareas por orden de llegada.
    """
    def __init__(self):
        # Instancia de la cola de prioridad (no lineal).
        self.cola_prioridad = ColaPrioridadTareas()
        # Instancia de la lista ordenada por llegada (lineal).
        self.lista_llegada = ListaDobleEnlazadaOrdenada()

        # Diccionario para acceso rápido a tareas por ID (facilita cancelación).
        # Clave: id_tarea, Valor: objeto Tarea completo.
        self._tareas_por_id = {}

    def agregar_tarea(self, id_tarea: Any, prioridad: int):
        """
        Añade una nueva tarea al sistema (a ambas estructuras).
        """
        # Evitar IDs duplicados.
        if id_tarea in self._tareas_por_id:
            print(f"Error: El ID de tarea '{id_tarea}' ya existe. No se añadió.")
            return

        # Obtener marca de tiempo actual.
        marca_tiempo_actual = time.time()

        # Crear el objeto Tarea.
        nueva_tarea = Tarea(prioridad=prioridad, marca_tiempo=marca_tiempo_actual, id_tarea=id_tarea)

        print(f"Añadiendo: {nueva_tarea}")

        # 1. Añadir a la lista ordenada por llegada.
        #    (Recordar que esto también guarda el nodo en nueva_tarea.nodo_lista).
        self.lista_llegada.insertar_tarea_ordenada(nueva_tarea)

        # 2. Añadir a la cola de prioridad (heap).
        self.cola_prioridad.agregar_tarea(nueva_tarea)

        # 3. Guardar en el diccionario de búsqueda por ID.
        self._tareas_por_id[id_tarea] = nueva_tarea

        print(f"Tarea '{id_tarea}' añadida correctamente.")

    def ejecutar_siguiente_tarea(self) -> Optional[Tarea]:
        """
        Obtiene la tarea de mayor prioridad, la elimina de ambas estructuras
        y la devuelve.
        """
        print("\n---> Obteniendo la siguiente tarea a ejecutar...")

        # 1. Sacar tarea de la cola de prioridad (maneja borrado perezoso).
        tarea_a_ejecutar = self.cola_prioridad.obtener_tarea_max_prioridad()

        # 2. Si se obtuvo una tarea válida:
        if tarea_a_ejecutar:
            print(f"*** Ejecutando: {tarea_a_ejecutar} ***")

            # 3. Eliminarla de la lista doblemente enlazada (O(1)).
            #    Usamos la referencia directa guardada en tarea_a_ejecutar.nodo_lista.
            if tarea_a_ejecutar.nodo_lista:
                self.lista_llegada.eliminar_nodo(tarea_a_ejecutar.nodo_lista)
            else:
                 # Esto no debería pasar si la lógica es correcta.
                 print(f"Advertencia: La tarea {tarea_a_ejecutar.id_tarea} no tenía referencia a su nodo en la lista.")

            # 4. Eliminarla del diccionario de búsqueda por ID.
            if tarea_a_ejecutar.id_tarea in self._tareas_por_id:
                del self._tareas_por_id[tarea_a_ejecutar.id_tarea]

            # 5. Devolver la tarea ejecutada.
            return tarea_a_ejecutar
        else:
            # No había tareas activas.
            print("--- No hay tareas pendientes para ejecutar.")
            return None

    def listar_tareas_por_llegada(self):
        """Muestra todas las tareas pendientes, ordenadas por llegada."""
        print("\n---> Listando tareas pendientes por orden de llegada:")

        # Obtener la lista ordenada desde la estructura lineal.
        tareas_ordenadas = self.lista_llegada.obtener_tareas_por_llegada()

        if not tareas_ordenadas:
            print("--- No hay tareas pendientes.")
        else:
            # Imprimir cada tarea.
            for i, tarea in enumerate(tareas_ordenadas):
                print(f"   {i+1}. {tarea}")
        # Podríamos devolver la lista si fuera necesario:
        # return tareas_ordenadas

    def cancelar_tarea(self, id_tarea: Any):
        """
        Elimina una tarea específica del sistema usando su ID.
        La quita de ambas estructuras (usando borrado perezoso para el heap).
        """
        print(f"\n---> Intentando cancelar la tarea con ID: '{id_tarea}'...")

        # 1. Buscar la tarea por ID en el diccionario.
        if id_tarea in self._tareas_por_id:
            tarea_a_cancelar = self._tareas_por_id[id_tarea]
            print(f"--- Encontrada: {tarea_a_cancelar}")

            # 2. "Eliminarla" de la cola de prioridad (borrado perezoso).
            #    Simplemente se marca como inactiva en el set.
            self.cola_prioridad.marcar_tarea_como_eliminada(id_tarea)

            # 3. Eliminarla físicamente de la lista doblemente enlazada (O(1)).
            if tarea_a_cancelar.nodo_lista:
                self.lista_llegada.eliminar_nodo(tarea_a_cancelar.nodo_lista)
            else:
                 print(f"Advertencia: La tarea a cancelar {id_tarea} no tenía referencia a su nodo en la lista.")

            # 4. Eliminarla del diccionario de búsqueda por ID.
            del self._tareas_por_id[id_tarea]

            print(f"--- Tarea '{id_tarea}' cancelada correctamente.")
        else:
            # El ID no se encontró.
            print(f"--- Error: No se encontró ninguna tarea con el ID '{id_tarea}'.")

#-----------------------------------------------------
# PASO 5: Ejemplo de Uso
#-----------------------------------------------------
# Este bloque solo se ejecuta si corres este archivo directamente.
if __name__ == "__main__":

    print("========================================")
    print("  INICIO DEMO GESTOR DE TAREAS")
    print("========================================")

    # Crear instancia del gestor.
    gestor = GestorTareas()

    # Añadir tareas de ejemplo (ID, Prioridad).
    # Pausas pequeñas para asegurar marcas de tiempo distintas.
    gestor.agregar_tarea("Limpiar Casa", 5)
    time.sleep(0.02)
    gestor.agregar_tarea("Estudiar Estructuras de Datos", 10)
    time.sleep(0.02)
    gestor.agregar_tarea("Comprar Leche", 5) # Misma prioridad que Limpiar, pero llegó después.
    time.sleep(0.02)
    gestor.agregar_tarea("Llamar a Mamá", 15)
    time.sleep(0.02)
    gestor.agregar_tarea("Pasear al Perro", 10) # Misma prioridad que Estudiar, pero llegó después.

    print("\n----------------------------------------")
    # Ver tareas ordenadas por llegada.
    gestor.listar_tareas_por_llegada()

    print("\n----------------------------------------")

    # Ejecutar tareas (deben salir por prioridad y luego por llegada).
    print("Ejecutando tareas...")
    gestor.ejecutar_siguiente_tarea() # Debería ser "Llamar a Mamá" (Prioridad 15)
    gestor.ejecutar_siguiente_tarea() # Debería ser "Estudiar Estructuras" (Prioridad 10, llegó antes)

    print("\n----------------------------------------")

    # Ver tareas restantes, ordenadas por llegada.
    gestor.listar_tareas_por_llegada()

    print("\n----------------------------------------")

    # Cancelar una tarea pendiente.
    gestor.cancelar_tarea("Limpiar Casa")

    print("\n----------------------------------------")

    # Ver qué tareas quedan ahora.
    gestor.listar_tareas_por_llegada()

    print("\n----------------------------------------")

    # Ejecutar las tareas restantes.
    print("Ejecutando tareas restantes...")
    gestor.ejecutar_siguiente_tarea() # Debería ser "Pasear al Perro" (Prioridad 10)
    gestor.ejecutar_siguiente_tarea() # Debería ser "Comprar Leche" (Prioridad 5)

    # Intentar ejecutar una más (ya no debería haber).
    gestor.ejecutar_siguiente_tarea()

    print("\n----------------------------------------")
    # Verificar que la lista de tareas pendientes está vacía.
    gestor.listar_tareas_por_llegada()

    print("\n========================================")
    print("     FIN DEMO GESTOR DE TAREAS")
    print("========================================")
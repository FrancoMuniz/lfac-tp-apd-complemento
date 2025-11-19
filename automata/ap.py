from abc import ABC, abstractmethod
from tabulate import tabulate
from typing import Hashable, Union


__all__ = ["AP", "SpecialStackSymbol"]


class SpecialStackSymbol:
    """Símbolos especiales para la pila."""
    EMPTY = "⊥"  # Símbolo de pila vacía/inicial
    LAMBDA = "λ"  # No leer/escribir en pila


class AP(ABC):
    """Clase abstracta que representa un autómata de pila."""

    def __init__(self):
        self.states = set()
        self.initial_state = None
        self.final_states = set()
        # Formato: {(estado, símbolo_entrada, símbolo_pila): [(nuevo_estado, cadena_pila)]}
        self.transitions = {}
        self.input_alphabet = set()  # Alfabeto de entrada
        self.stack_alphabet = set()  # Alfabeto de pila
        self.initial_stack_symbol = SpecialStackSymbol.EMPTY  # Símbolo inicial de pila

    def size(self):
        """Devuelve la cantidad de estados del autómata."""
        return len(self.states)

    def add_state(self, state: Hashable, final: bool = False):
        """
        Agrega un estado al autómata de pila.
        El estado puede ser cualquier cosa, siempre y cuando sea hashable.
        """
        if state in self.states:
            raise ValueError(f"El estado {state} ya pertenece al autómata.")
        self.states.add(state)
        if final:
            self.final_states.add(state)

    def mark_initial_state(self, state: Hashable):
        """Marca un estado del autómata como inicial."""
        if state not in self.states:
            raise ValueError(f"El estado {state} no pertenece al autómata.")
        self.initial_state = state

    def set_initial_stack_symbol(self, symbol: str):
        """Define el símbolo inicial de la pila."""
        self.initial_stack_symbol = symbol
        self.stack_alphabet.add(symbol)

    def normalize_states(self):
        """
        Normaliza los nombres de los estados según la convención q0, q1, q2, ...

        Modifica el autómata (no crea una copia) y devuelve el autómata modificado.
        """
        new_names = {}
        if self.initial_state is not None:
            new_names[self.initial_state] = "q0"
        for i, state in enumerate(self.states - {self.initial_state}):
            if state not in new_names:
                new_names[state] = f"q{i + 1}"

        # Ordenamos los estados para hacer el renombre sin pisar ninguno
        ordered_new_names = []
        while len(new_names) > 0:
            for old_name, new_name in new_names.items():
                if old_name == new_name or new_name not in new_names.keys():
                    ordered_new_names.append([old_name, new_name, False])
                    del new_names[old_name]
                    break
            else:
                # Detectamos un loop entre las operaciones de renombre
                # Hay que usar un nombre temporal
                old_name, new_name = next(iter(new_names.items()))
                ordered_new_names.append([old_name, new_name, True])
                del new_names[old_name]

        # Realizamos el renombre
        for old_name, new_name, use_temp in ordered_new_names:
            if use_temp:
                while new_name in self.states:
                    new_name = f"temp:{new_name}"
            self._rename_state(old_name, new_name)

        # Eliminamos los nombres temporales
        for state in list(self.states):
            if isinstance(state, str) and state.startswith("temp:"):
                self._rename_state(state, state.split(":")[-1])

        return self

    def transitions_table(self):
        """
        Genera una tabla con las transiciones del autómata de pila.
        
        La idea es simple: agrupa todas las transiciones por estado origen y las muestra
        en formato legible. Cada transición muestra (símbolo_entrada, símbolo_pila) → (estado_destino, cadena_pila).
        Los estados iniciales se marcan con ^ y los finales con *.
        """
        if not self.transitions:
            return "No hay transiciones definidas."

        # Agrupar transiciones por estado origen
        state_transitions = {}
        for (state, input_sym, stack_sym), targets in self.transitions.items():
            if state not in state_transitions:
                state_transitions[state] = []
            
            # Separamos en dos casos:
            # - APD: guarda targets como tupla directa (estado, pila)
            # - APND: guarda targets como lista/conjunto de tuplas [(estado, pila), ...]
            # igual creo no necesito el APND
            if isinstance(targets, tuple) and len(targets) == 2 and isinstance(targets[1], str):
                # Caso 1: APD - targets es directamente (new_state, stack_string)
                new_state, stack_string = targets
                stack_str = stack_string if stack_string else SpecialStackSymbol.LAMBDA
                input_str = input_sym if input_sym else SpecialStackSymbol.LAMBDA
                stack_sym_str = stack_sym if stack_sym else SpecialStackSymbol.LAMBDA
                state_transitions[state].append(
                    f"({input_str}, {stack_sym_str}) → ({new_state}, {stack_str})"
                )
            else:
                # Caso 2: APND - targets es una colección de tuplas
                for new_state, stack_string in targets:
                    stack_str = stack_string if stack_string else SpecialStackSymbol.LAMBDA
                    input_str = input_sym if input_sym else SpecialStackSymbol.LAMBDA
                    stack_sym_str = stack_sym if stack_sym else SpecialStackSymbol.LAMBDA
                    state_transitions[state].append(
                        f"({input_str}, {stack_sym_str}) → ({new_state}, {stack_str})"
                    )

        # Crear tabla con los estados y sus transiciones
        table = []
        for state in sorted(self.states, key=str):
            # Marcar estado inicial (^) y finales (*)
            state_marker = ""
            if state == self.initial_state:
                state_marker = "^"
            if state in self.final_states:
                state_marker += "*"
            
            transitions_str = "\n".join(state_transitions.get(state, ["-"]))
            table.append([f"{state}{state_marker}", transitions_str])

        return tabulate(table, headers=["Estado", "Transiciones δ(q, a, X)"], tablefmt="fancy_grid")

    def __str__(self):
        """Imprimirr el autómata."""
        return (f"{self.__class__.__name__}"
                f"<Q={len(self.states)} estados, "
                f"Σ={self.input_alphabet}, "
                f"Γ={self.stack_alphabet}, "
                f"q0={self.initial_state}, "
                f"Z0={self.initial_stack_symbol}, "
                f"F={len(self.final_states)} finales>")

    def _rename_state(self, old_name: Hashable, new_name: Hashable):
        """Renombrar un estado del autómata."""
        if old_name != new_name:
            self.states.remove(old_name)
            self.states.add(new_name)
            if old_name == self.initial_state:
                self.initial_state = new_name
            if old_name in self.final_states:
                self.final_states.remove(old_name)
                self.final_states.add(new_name)
            #  hay que renombrar también en las transiciones
            self._rename_state_in_transitions(old_name, new_name)

    @abstractmethod
    def _rename_state_in_transitions(self, old_name: Hashable, new_name: Hashable):
        """Renombra un estado dentro de las transiciones del autómata."""
        pass

    @abstractmethod
    def accepts(self, word: str) -> bool:
        """
        Determina si el autómata acepta la cadena dada.
        Debe ser implementado por las clases derivadas.
        """
        pass


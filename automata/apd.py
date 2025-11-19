from typing import Hashable, Union, Optional
from automata.ap import AP, SpecialStackSymbol


__all__ = ["APD"]
SIMBOLO_LAMBDA = None

class APD(AP):
    """
    Autómata de Pila Determinístico
    """

    def __init__(self):
        super().__init__()
        self.transitions = {}  # {(estado, input, stack_top): (new_state, stack_string)}

    def add_transition(self, state: Hashable, new_state: Hashable,
                      input_symbol: Optional[str], stack_top: str,
                      stack_push: str = ""):
        """
        Agrega una transición determinística al autómata de pila.
        
        Args:
            state: Estado actual
            new_state: Estado destino
            input_symbol: Símbolo a leer del input (None para transiciones lambda)
            stack_top: Símbolo que debe estar en el tope de la pila
            stack_push: Cadena a poner en la pila (vacío para pop, mismo símbolo para no cambiar)
                       Se apila de derecha a izquierda (el primer símbolo queda al tope)
        
        Raises:
            ValueError: Si viola el determinismo o los estados no existen
        """
        if state not in self.states:
            raise ValueError(f"El estado {state} no pertenece al autómata.")
        if new_state not in self.states:
            raise ValueError(f"El estado {new_state} no pertenece al autómata.")

        # Verificar determinismo
        key = (state, input_symbol, stack_top)
        
        # Verificar que no existe ya una transición para esta clave
        if key in self.transitions:
            raise ValueError(
                f"Ya existe una transición para ({state}, {input_symbol or SIMBOLO_LAMBDA}, {stack_top}). "
                f"El autómata no sería determinístico."
            )
        
        # Verificar que no hay conflicto con transiciones lambda para no romper el determinismo
        if input_symbol is not None:
            epsilon_key = (state, None, stack_top)
            if epsilon_key in self.transitions:
                raise ValueError(
                    f"Ya existe una transicion lambda desde ({state}, {SIMBOLO_LAMBDA}, {stack_top}). "
                    f"No se puede agregar transición con símbolo de entrada."
                )
        else:
            # Si agregamos transicion lambda, verificar que no hay transiciones con simbolos para no romper el determinismo
            for symbol in self.input_alphabet:
                symbol_key = (state, symbol, stack_top)
                if symbol_key in self.transitions:
                    raise ValueError(
                        f"Ya existe transición con símbolo desde ({state}, {symbol}, {stack_top}). "
                        f"No se puede agregar transicion lambda."
                    )
        
        # Agregar transición
        self.transitions[key] = (new_state, stack_push)
        # Actualizar alfabetos
        if input_symbol is not None:
            self.input_alphabet.add(input_symbol)
        self.stack_alphabet.add(stack_top)
        if stack_push:
            for symbol in stack_push:
                self.stack_alphabet.add(symbol)

    def get_transition(self, state: Hashable, input_symbol: Optional[str], 
                      stack_top: str) -> Optional[tuple]:
        """
        Obtiene la transición para una configuración dada.
        
        Returns:
            Tupla (nuevo_estado, cadena_pila) o None si no existe transición
        """
        key = (state, input_symbol, stack_top)
        return self.transitions.get(key)

    def step(self, state: Hashable, remaining_input: str, stack: list) -> Optional[tuple]:
        """
        Ejecuta un paso de cómputo del autómata.
        
        Args:
            state: Estado actual
            remaining_input: Cadena restante por leer
            stack: Pila actual (lista donde el último elemento es el tope)
        
        Returns:
            Tupla (nuevo_estado, nueva_cadena, nueva_pila) o None si no hay transición
        """
        if not stack:
            return None
        
        stack_top = stack[-1]
        
        # Intentar transición con símbolo de entrada
        if remaining_input:
            input_symbol = remaining_input[0]
            transition = self.get_transition(state, input_symbol, stack_top)
            if transition:
                new_state, stack_string = transition
                new_stack = stack[:-1]  # pop del tope
                # Push de la cadena (de derecha a izquierda para que el primero quede arriba)
                for symbol in reversed(stack_string):
                    new_stack.append(symbol)
                return (new_state, remaining_input[1:], new_stack)
        
        # Intentar transicion lambda
        transition = self.get_transition(state, None, stack_top)
        if transition:
            new_state, stack_string = transition
            new_stack = stack[:-1]  # pop del tope
            for symbol in reversed(stack_string):
                new_stack.append(symbol)
            return (new_state, remaining_input, new_stack)
        
        return None

    def accepts(self, word: str, acceptance_mode: str = "final_state") -> bool:
        """
        Determina si el autómata acepta la cadena dada.
        
        Args:
            word: Cadena a verificar
            acceptance_mode: "final_state" (aceptación por estado final) o 
                           "empty_stack" (aceptación por pila vacía)
        
        Returns:
            True si la cadena es aceptada, False en caso contrario
        """
        state = self.initial_state
        remaining_input = word
        stack = [self.initial_stack_symbol]
        
        # Ejecutar el autómata
        max_steps = len(word) * 100 + 1000  # para evitar loops infinitos
        steps = 0
        
        while steps < max_steps:
            steps += 1
            
            # Verificar condiciones de aceptación
            if not remaining_input:  # Input consumido
                if acceptance_mode == "final_state":
                    if state in self.final_states:
                        return True
                elif acceptance_mode == "empty_stack":
                    if not stack:
                        return True
            
            # Intentar dar un paso
            result = self.step(state, remaining_input, stack)
            if result is None:
                # No hay transición posible
                break
            
            state, remaining_input, stack = result
        
        # Verificar condiciones finales
        if not remaining_input:
            if acceptance_mode == "final_state":
                return state in self.final_states
            elif acceptance_mode == "empty_stack":
                return not stack
        
        return False

    def is_deterministic(self) -> bool:
        """
        Verifica que el autómata sea realmente determinístico.
        
        Returns:
            True si cumple con las propiedades de determinismo
        """
        # Verificar que no hay conflictos entre transiciones
        for (state, input_sym, stack_sym) in self.transitions.keys():
            # Si hay transicion lambda, no debe haber transición con simbolo
            if input_sym is None:
                for symbol in self.input_alphabet:
                    if (state, symbol, stack_sym) in self.transitions:
                        return False
        
        return True

    def _rename_state_in_transitions(self, old_name: Hashable, new_name: Hashable):
        """Renombra un estado dentro de las transiciones del autómata."""
        new_transitions = {}
        
        for (state, input_sym, stack_sym), (target_state, stack_string) in self.transitions.items():
            new_state = new_name if state == old_name else state
            new_target = new_name if target_state == old_name else target_state
            new_transitions[(new_state, input_sym, stack_sym)] = (new_target, stack_string)
        
        self.transitions = new_transitions


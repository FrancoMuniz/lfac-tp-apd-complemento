from typing import Hashable
from automata.apd import APD


__all__ = ["APDC"]
SIMBOLO_LAMBDA = None


class APDC(APD):

    def __init__(self):
        super().__init__()
        

    def crear_automata_complemento(self):
        """
        Construir el automata que reconoce el complemento del lenguaje reconocido por el automata actual.
        Basado en el Teorema 2.23 del libro The Theory of Parsing Volumen 1.

        La precondicion es que el automata actual sea un APD continuo, como se define en el libro.
        
        idea principal:
        El automata complemento C simula P paso a paso, con un marcador de 3 indices:
        - 0: Desde la ultima lectura de simbolo (no transicion lambda), P no estuvo en estado final
        - 1: Desde la ultima lectura de simbolo (no transicion lambda), P estuvo en estado final  
        - 2: Sabemos que P no va a aceptar la palabra, entonces C la acepta (complemento)
        
        Returns:
            Nuevo APDC que reconoce el complemento del lenguaje
        """
        C = APDC()
        
        # Empezamos con las 3 definiciones que da el teorema, definiendo Q', q0', y F'.
        # Para cada estado de P creamos 3 estados, uno con cada indice (0,1,2)
        for q in self.states:
            C.add_state((q, 0), final=False)
            C.add_state((q, 1), final=False)
            C.add_state((q, 2), final=True)
        
        # si q0 no es final, entonces el estado inicial de C es [q0, 0], 
        # pero si q0 es final, entonces el estado inicial de C es [q0, 1]
        if self.initial_state in self.final_states:
            C.mark_initial_state((self.initial_state, 1))
        else:
            C.mark_initial_state((self.initial_state, 0))
        
        # los alfabetos y el simbolo inicial de pila son los mismos que los de P, los copiamos:
        C.input_alphabet = self.input_alphabet.copy()
        C.stack_alphabet = self.stack_alphabet.copy()
        C.set_initial_stack_symbol(self.initial_stack_symbol)
        
        # Ahora empezamos con las 3 reglas que da el teorema
        
        # Regla (i): Transiciones que leen un simbolo (no miramos transiciones lambda)
        # Si el estado q lee un simbolo a y pasa a p, entonces:
        # - [q, 1] lee a y pasa a [p, i]
        # - [q, 2] lee a y pasa a [p, i] 
        # Se usa i = 0 si p no es final, i = 1 si p es final
        
        for (q, input_symbol, stack_symbol), (p, stack_push) in self.transitions.items():
            if input_symbol is SIMBOLO_LAMBDA:
                continue
            i = 1 if p in self.final_states else 0
            C.add_transition((q, 1), (p, i), input_symbol, stack_symbol, stack_push)
            C.add_transition((q, 2), (p, i), input_symbol, stack_symbol, stack_push)
        
        # Regla (ii): Transiciones lambda
        # Si el estado q no lee simbolo y solo cambia estado y pila, entonces:
        # - [q, 1] no lee simbolo y pasa a [p, 1], con el cambio de estado y pila
        # - [q, 0] no lee simbolo y pasa a [p, i], con el cambio de estado y pila
        # Se usa i = 0 si p no es final, i = 1 si p es final
        for (q, input_symbol, stack_symbol), (p, stack_push) in self.transitions.items():
            if input_symbol is not SIMBOLO_LAMBDA:
                continue
            i = 1 if p in self.final_states else 0
            C.add_transition((q, 1), (p, 1), SIMBOLO_LAMBDA, stack_symbol, stack_push)
            C.add_transition((q, 0), (p, i), SIMBOLO_LAMBDA, stack_symbol, stack_push)
        
        # Regla (iii): saltamos a indice 2 cuando ya no quedan transiciones lambda disponibles
        # Si no hay transiciones lambda desde q, entonces:
        # - [q, 0] no lee simbolo y pasa a [q, 2], con el cambio de estado
        for q in self.states:
            for stack_symbol in self.stack_alphabet:
                has_lambda_transition = (q, SIMBOLO_LAMBDA, stack_symbol) in self.transitions
                if not has_lambda_transition:
                    C.add_transition((q, 0), (q, 2), SIMBOLO_LAMBDA, stack_symbol, stack_symbol)
        
        return C

    def __str__(self):
        base_str = super().__str__()
        return base_str


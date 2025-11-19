#!/usr/bin/env python3
"""
Prueba simple para verificar que los autómatas de pila funcionan correctamente.
"""

from automata import APD, APDC

def test_anbn():
    """Prueba simple del lenguaje a^n b^n (n >= 1)"""
    print("Test: Lenguaje a^n b^n (n >= 1)")
    print("-" * 40)
    
    apd = APD()
    
    # Crear autómata
    apd.add_state("q0")
    apd.add_state("q1")
    apd.add_state("qf", final=True)
    apd.mark_initial_state("q0")
    apd.set_initial_stack_symbol("Z")
    
    # Transiciones
    apd.add_transition("q0", "q0", "a", "Z", "AZ")
    apd.add_transition("q0", "q0", "a", "A", "AA")
    apd.add_transition("q0", "q1", "b", "A", "")
    apd.add_transition("q1", "q1", "b", "A", "")
    apd.add_transition("q1", "qf", None, "Z", "Z")
    
    # Pruebas (cadena vacía ya NO es aceptada)
    tests = [
        ("", False),
        ("ab", True),
        ("aabb", True),
        ("aaabbb", True),
        ("a", False),
        ("b", False),
        ("abb", False),
        ("aab", False),
    ]
    
    all_passed = True
    for word, expected in tests:
        result = apd.accepts(word)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} '{word}' -> {result} (esperado: {expected})")
    
    return all_passed


def test_parentesis():
    """Prueba de lenguaje simple (aba o bab)"""
    print("\nTest: Lenguaje simple (aba o bab)")
    print("-" * 40)
    
    apd = APD()
    
    apd.add_state("q0")
    apd.add_state("q1")
    apd.add_state("q2")
    apd.add_state("q3")
    apd.add_state("q4")
    apd.add_state("qf", final=True)
    
    apd.mark_initial_state("q0")
    apd.set_initial_stack_symbol("Z")
    
    # Reconocer "aba"
    apd.add_transition("q0", "q1", "a", "Z", "Z")
    apd.add_transition("q1", "q2", "b", "Z", "Z")
    apd.add_transition("q2", "qf", "a", "Z", "Z")
    
    # Reconocer "bab"
    apd.add_transition("q0", "q3", "b", "Z", "Z")
    apd.add_transition("q3", "q4", "a", "Z", "Z")
    apd.add_transition("q4", "qf", "b", "Z", "Z")
    
    tests = [
        ("", False),
        ("aba", True),
        ("bab", True),
        ("ab", False),
        ("ba", False),
        ("a", False),
        ("b", False),
        ("abab", False),
    ]
    
    all_passed = True
    for word, expected in tests:
        result = apd.accepts(word)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} '{word}' -> {result} (esperado: {expected})")
    
    return all_passed


def test_apdc():
    """Prueba de APDC"""
    print("\nTest: APDC (Autómata Continuo)")
    print("-" * 40)
    
    apdc = APDC()
    
    apdc.add_state("q0")
    apdc.add_state("q1")
    apdc.add_state("qf", final=True)
    apdc.mark_initial_state("q0")
    apdc.set_initial_stack_symbol("Z")
    
    apdc.add_transition("q0", "q0", "a", "Z", "AZ")
    apdc.add_transition("q0", "q0", "a", "A", "AA")
    apdc.add_transition("q0", "q1", "b", "A", "")
    apdc.add_transition("q1", "q1", "b", "A", "")
    apdc.add_transition("q1", "qf", None, "Z", "Z")
    
    print(f"  ¿Es determinístico? {apdc.is_deterministic()}")
    print(f"  Número de estados: {apdc.size()}")
    print(f"  Alfabeto de entrada: {apdc.input_alphabet}")
    print(f"  Alfabeto de pila: {apdc.stack_alphabet}")
    
    return True


def main():
    print("\n" + "=" * 50)
    print("PRUEBAS DE AUTÓMATAS DE PILA")
    print("=" * 50 + "\n")
    
    results = []
    results.append(("a^n b^n (n>=1)", test_anbn()))
    results.append(("aba o bab", test_parentesis()))
    results.append(("APDC", test_apdc()))
    
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    for name, passed in results:
        status = "✓ PASÓ" if passed else "✗ FALLÓ"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n¡Todos los tests pasaron! ✓")
    else:
        print("\n¡Algunos tests fallaron! ✗")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


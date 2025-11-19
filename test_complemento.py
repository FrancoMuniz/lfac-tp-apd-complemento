#!/usr/bin/env python3
"""
Test de la implementación del complemento (Teorema 2.23)

Prueba que el algoritmo crear_automata_complemento() funciona correctamente.

Generados con IA y verificados manualmente
"""

from automata import APDC


def test_complemento_lenguaje_simple():
    """
    Test con el lenguaje L = {a^n b | n >= 1}
    Es decir: una o más a's seguidas de exactamente una b
    
    Acepta: "ab", "aab", "aaab", etc.
    Rechaza: "", "a", "b", "ba", "abb", "aabb", etc.
    
    IMPORTANTE: Construimos un APDC CONTINUO (con estado trampa)
    como requiere el Teorema 2.23.
    
    El complemento L^c debe aceptar exactamente lo que L rechaza.
    """
    print("=" * 70)
    print("TEST: Complemento del lenguaje {a^n b | n >= 1}")
    print("(Autómata continuo con estado trampa)")
    print("=" * 70)
    
    # Construir APDC CONTINUO para L = {a^n b | n >= 1}
    P = APDC()
    
    # Estados
    P.add_state("q0")              # Estado inicial
    P.add_state("q1")              # Leyendo a's
    P.add_state("q2", final=True)  # Leyó la b final (ACEPTA)
    P.add_state("trap")            # Estado trampa (para ser continuo)
    
    P.mark_initial_state("q0")
    P.set_initial_stack_symbol("Z")
    
    # Transiciones principales de P
    P.add_transition("q0", "q1", "a", "Z", "AZ")   # Primera 'a'
    P.add_transition("q1", "q1", "a", "Z", "AZ")   # Más a's
    P.add_transition("q1", "q1", "a", "A", "AA")   # Más a's
    P.add_transition("q1", "q2", "b", "Z", "Z")    # b final -> ACEPTA
    P.add_transition("q1", "q2", "b", "A", "A")    # b final -> ACEPTA
    
    # Transiciones para hacer el autómata CONTINUO (no se traba en loops)
    # Errores van al trap que consume todo el resto
    P.add_transition("q0", "trap", "b", "Z", "Z")  # Error: b al inicio
    P.add_transition("q2", "trap", "a", "Z", "Z")  # Error: símbolo después de aceptar
    P.add_transition("q2", "trap", "b", "Z", "Z")
    P.add_transition("q2", "trap", "a", "A", "A")
    P.add_transition("q2", "trap", "b", "A", "A")
    
    # Estado trampa consume todo (mantiene continuidad)
    P.add_transition("trap", "trap", "a", "Z", "Z")
    P.add_transition("trap", "trap", "b", "Z", "Z")
    P.add_transition("trap", "trap", "a", "A", "A")
    P.add_transition("trap", "trap", "b", "A", "A")
    
    print("\nAutómata original P:")
    print(P)
    print("\nEstados finales de P:", P.final_states)
    
    # Construir el complemento
    print("\n" + "-" * 70)
    print("Construyendo complemento C = P.crear_automata_complemento()...")
    print("-" * 70)
    
    C = P.crear_automata_complemento()
    
    print("\nAutómata complemento C:")
    print(C)
    print("\nEstados finales de C:", C.final_states)
    print(f"Cantidad de estados de C: {C.size()}")
    
    # Probar cadenas
    test_cases = [
        # (cadena, debe_aceptar_P, debe_aceptar_C)
        ("", False, True),      # Vacía no está en L → está en L^c
        ("a", False, True),     # Solo 'a' no está en L → está en L^c
        ("b", False, True),     # Solo 'b' no está en L → está en L^c
        ("ab", True, False),    # "ab" está en L → NO está en L^c
        ("aab", True, False),   # "aab" está en L → NO está en L^c
        ("aaab", True, False),  # "aaab" está en L → NO está en L^c
        ("ba", False, True),    # "ba" no está en L → está en L^c
        ("abb", False, True),   # "abb" no está en L → está en L^c
        ("aabb", False, True),  # "aabb" no está en L → está en L^c
        ("aa", False, True),    # "aa" no está en L → está en L^c
        ("bb", False, True),    # "bb" no está en L → está en L^c
    ]
    
    print("\n" + "=" * 70)
    print("PRUEBAS:")
    print("=" * 70)
    
    all_passed = True
    for word, expected_P, expected_C in test_cases:
        result_P = P.accepts(word)
        result_C = C.accepts(word)
        
        # Verificar que P funciona como esperado
        status_P = "✓" if result_P == expected_P else "✗"
        if result_P != expected_P:
            all_passed = False
        
        # Verificar que C es el complemento de P
        status_C = "✓" if result_C == expected_C else "✗"
        if result_C != expected_C:
            all_passed = False
        
        # Verificar la propiedad fundamental: C acepta ⟺ P rechaza
        complemento_ok = result_C == (not result_P)
        status_comp = "✓" if complemento_ok else "✗"
        if not complemento_ok:
            all_passed = False
        
        word_display = f"'{word}'" if word else "'ε'"
        print(f"  {word_display:8} | P: {result_P:5} {status_P} | C: {result_C:5} {status_C} | "
              f"C=¬P: {status_comp}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ TODOS LOS TESTS PASARON")
        print("\nCONCLUSIÓN: El algoritmo crear_automata_complemento() funciona correctamente.")
        print("L(C) = L(P)^c  ✓")
    else:
        print("✗ ALGUNOS TESTS FALLARON")
    print("=" * 70)
    
    return all_passed


def test_complemento_anbn():
    """
    Test con el lenguaje L = {aa, bb}
    
    Lenguaje simple: solo acepta "aa" o "bb"
    Rechaza: "", "a", "b", "ab", "ba", "aaa", etc.
    
    Este ejemplo es más simple y fácil de hacer continuo.
    """
    print("\n\n" + "=" * 70)
    print("TEST 2: Complemento del lenguaje {aa, bb}")
    print("(Lenguaje simple para demostrar el algoritmo)")
    print("=" * 70)
    
    # Construir APDC CONTINUO para L = {aa, bb}
    P = APDC()
    
    # Estados
    P.add_state("q0")              # Estado inicial
    P.add_state("q1")              # Leyó primera 'a'
    P.add_state("q2", final=True)  # Leyó "aa" - ACEPTA
    P.add_state("q3")              # Leyó primera 'b'
    P.add_state("q4", final=True)  # Leyó "bb" - ACEPTA
    P.add_state("trap")            # Estado trampa
    
    P.mark_initial_state("q0")
    P.set_initial_stack_symbol("Z")
    
    # Transiciones para "aa"
    P.add_transition("q0", "q1", "a", "Z", "Z")    # Primera 'a'
    P.add_transition("q1", "q2", "a", "Z", "Z")    # Segunda 'a' → ACEPTA
    
    # Transiciones para "bb"
    P.add_transition("q0", "q3", "b", "Z", "Z")    # Primera 'b'
    P.add_transition("q3", "q4", "b", "Z", "Z")    # Segunda 'b' → ACEPTA
    
    # Transiciones de error (hacer continuo)
    P.add_transition("q1", "trap", "b", "Z", "Z")  # Error: ab
    P.add_transition("q3", "trap", "a", "Z", "Z")  # Error: ba
    P.add_transition("q2", "trap", "a", "Z", "Z")  # Error: símbolos extra después de aa
    P.add_transition("q2", "trap", "b", "Z", "Z")
    P.add_transition("q4", "trap", "a", "Z", "Z")  # Error: símbolos extra después de bb
    P.add_transition("q4", "trap", "b", "Z", "Z")
    
    # Estado trampa consume todo
    P.add_transition("trap", "trap", "a", "Z", "Z")
    P.add_transition("trap", "trap", "b", "Z", "Z")
    
    print("\nAutómata original P para {aa, bb}:")
    print(P)
    
    # Construir complemento
    C = P.crear_automata_complemento()
    
    print("\nAutómata complemento C:")
    print(C)
    print(f"Estados de C: {C.size()}")
    
    # Probar cadenas
    test_cases = [
        ("", False, True),      # Vacía no está en L
        ("aa", True, False),    # "aa" está en L
        ("bb", True, False),    # "bb" está en L
        ("a", False, True),     # "a" no está en L
        ("b", False, True),     # "b" no está en L
        ("ab", False, True),    # "ab" no está en L
        ("ba", False, True),    # "ba" no está en L
        ("aaa", False, True),   # "aaa" no está en L
        ("bbb", False, True),   # "bbb" no está en L
        ("aabb", False, True),  # "aabb" no está en L
    ]
    
    print("\nPRUEBAS:")
    all_passed = True
    for word, expected_P, expected_C in test_cases:
        result_P = P.accepts(word)
        result_C = C.accepts(word)
        
        complemento_ok = result_C == (not result_P)
        status = "✓" if complemento_ok else "✗"
        
        if not complemento_ok or result_P != expected_P or result_C != expected_C:
            all_passed = False
        
        word_display = f"'{word}'" if word else "'ε'"
        print(f"  {word_display:10} | P: {result_P:5} | C: {result_C:5} | C=¬P: {status}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ TEST 2 PASÓ")
    else:
        print("✗ TEST 2 FALLÓ")
    print("=" * 70)
    
    return all_passed


def main():
    """Ejecuta todos los tests"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  TEST DEL ALGORITMO DE COMPLEMENTO (Teorema 2.23)".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70 + "\n")
    
    results = []
    results.append(("Test 1: {a^n b | n >= 1}", test_complemento_lenguaje_simple()))
    results.append(("Test 2: {aa, bb}", test_complemento_anbn()))
    
    print("\n\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    for name, passed in results:
        status = "✓ PASÓ" if passed else "✗ FALLÓ"
        print(f"  {status}: {name}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("\nEl algoritmo crear_automata_complemento() está correctamente implementado.")
        print("Cumple con el Teorema 2.23 de Aho & Ullman.")
    else:
        print("\n⚠️  Algunos tests fallaron.")
    print("=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


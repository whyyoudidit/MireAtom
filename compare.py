# -*- coding: cp1251 -*-
from sympy import symbols, simplify
from sympy.parsing.latex import parse_latex
from graphviz import Digraph

def parse_formula(latex):
    """
    Парсит LaTeX-формулу в AST.
    """
    try:
        return parse_latex(latex)
    except Exception as e:
        raise ValueError(f"Ошибка парсинга LaTeX: {e}")

def normalize_variables(ast):
    """
    Нормализует переменные в AST, заменяя их стандартными именами.
    """
    mapping = {}  # Соответствие оригинальных переменных и нормализованных
    next_variable_index = 1  # Индекс для следующей нормализованной переменной

    def replace_variable(expr):
        nonlocal next_variable_index
        if expr.is_Symbol:  # Если это переменная
            if expr not in mapping:
                mapping[expr] = symbols(f"x_{next_variable_index}")
                next_variable_index += 1
            return mapping[expr]
        elif expr.args:  # Если это функция или оператор
            return expr.func(*[replace_variable(arg) for arg in expr.args])
        return expr  # Число или неизменяемый объект

    normalized_ast = replace_variable(ast)
    return normalized_ast, mapping

def compare_asts_with_similarity(ast1, ast2):
    """
    Рекурсивно сравнивает два AST и возвращает количество совпадающих узлов и общее количество узлов.
    Узлы считаются совпадающими, если их структура совпадает, а различие только в значении (например, 4 и 2).
    """
    # Если узлы полностью совпадают
    if ast1 == ast2:
        return 1, 1  # Совпадение: 1 совпадающий узел из 1

    # Если узел является числом или переменной
    if not hasattr(ast1, 'args') or not hasattr(ast2, 'args'):
        return (0, 1) if type(ast1) != type(ast2) else (0.5, 1)  # Частичное совпадение для одинаковых типов

    # Если узлы — операции или функции
    matches = 0
    total = 1  # Текущий узел (сам узел тоже учитываем)
    if ast1.func == ast2.func:  # Совпадают типы операций (например, Add, Mul)
        matches += 1  # Узлы совпадают по структуре

    # Рекурсивное сравнение дочерних узлов
    child_matches = 0
    child_total = 0
    for child1, child2 in zip(ast1.args, ast2.args):
        match, count = compare_asts_with_similarity(child1, child2)
        child_matches += match
        child_total += count

    # Добавляем совпадения дочерних узлов
    matches += child_matches
    total += child_total
    return matches, total

def visualize_ast(expr, graph=None, parent=None):
    """
    Рекурсивно строит визуализацию AST с использованием Graphviz.
    """
    if graph is None:
        graph = Digraph(format='png')
        graph.attr(dpi='300')
        graph.attr(rankdir='TB')
    
    # Текущий узел
    current_node = str(expr.func) if expr.args else str(expr)
    
    # Добавление узла
    graph.node(current_node, label=current_node, style="filled", color="lightblue" if expr.args else "lightgreen")
    
    # Если есть родительский узел, добавляем связь
    if parent:
        graph.edge(parent, current_node)
    
    # Рекурсивно обрабатываем дочерние узлы
    for arg in expr.args:
        visualize_ast(arg, graph, current_node)
    
    return graph

def main():
    print("Введите первую формулу в формате LaTeX:")
    latex1 = input("> ")
    print("Введите вторую формулу в формате LaTeX:")
    latex2 = input("> ")

    try:
        # Парсинг формул
        ast1 = parse_formula(latex1)
        ast2 = parse_formula(latex2)

        # Упрощение формул
        simplified1 = simplify(ast1)
        simplified2 = simplify(ast2)

        # Нормализация
        normalized1, mapping1 = normalize_variables(ast1)
        normalized2, mapping2 = normalize_variables(ast2)

        # Сравнение
        are_equal = simplify(normalized1 - normalized2) == 0
        matches, total = compare_asts_with_similarity(normalized1, normalized2)
        print(matches, total)
        similarity_percentage = (matches / total) * 100 if total > 0 else 0

        # Результаты сравнения
        print("\nРезультаты сравнения:")
        print(f"Формулы эквивалентны: {'Да' if are_equal else 'Нет'}")
        print(f"Процент совпадения: {similarity_percentage:.2f}%")
        print(f"Упрощённая формула 1: {simplified1}")
        print(f"Упрощённая формула 2: {simplified2}")
        print(f"Нормализованная формула 1: {normalized1}")
        print(f"Нормализованная формула 2: {normalized2}")

        # Визуализация AST
        print("\nХотите визуализировать AST-деревья формул? (да/нет)")
        if input("> ").lower() == "да":
            graph1 = visualize_ast(ast1)
            graph2 = visualize_ast(ast2)
            graph1.render("ast_visualization_formula_1", cleanup=True)
            graph2.render("ast_visualization_formula_2", cleanup=True)

            print("\nХотите визуализировать упрощённые формулы? (да/нет)")
            if input("> ").lower() == "да":
                simplified_graph1 = visualize_ast(simplified1)
                simplified_graph2 = visualize_ast(simplified2)
                simplified_graph1.render("simplified_formula_1", cleanup=True)
                simplified_graph2.render("simplified_formula_2", cleanup=True)
                print("Визуализации упрощённых формул сохранены в 'simplified_formula_1.png' и 'simplified_formula_2.png'.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()

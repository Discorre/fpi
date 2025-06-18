#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для быстрого запуска отдельных математических фигур
"""

from mathematical_figures import MathematicalFigures

def demo_all_figures():
    """Демонстрация всех фигур по очереди"""
    print("🎨 Демонстрация всех математических фигур")
    print("=" * 50)
    
    math_fig = MathematicalFigures()
    
    print("1. Спираль Фибоначчи...")
    math_fig.fibonacci_spiral()
    
    print("2. Фрактал Мандельброта...")
    math_fig.mandelbrot_set()
    
    print("3. Кривая Лиссажу...")
    math_fig.lissajous_curve()
    
    print("4. Полярная роза...")
    math_fig.polar_rose()
    
    print("5. Аттрактор Лоренца...")
    math_fig.lorenz_attractor()
    
    print("6. Треугольник Серпинского...")
    math_fig.sierpinski_triangle()
    
    print("7. Кривая дракона...")
    math_fig.dragon_curve()
    
    print("8. Параметрическая поверхность...")
    math_fig.parametric_surface_3d()
    
    print("✅ Демонстрация завершена!")

if __name__ == "__main__":
    demo_all_figures()
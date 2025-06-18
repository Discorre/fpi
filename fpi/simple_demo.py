#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое демо для демонстрации математических фигур
"""

import matplotlib
matplotlib.use('Agg')  # Использовать не-интерактивный backend для background режима

from mathematical_figures import MathematicalFigures
import matplotlib.pyplot as plt

def simple_demo():
    """Простая демонстрация нескольких математических фигур"""
    print("🎨 Демонстрация математических фигур")
    print("=" * 40)
    
    figures = MathematicalFigures()
    
    try:
        print("📐 Создаем параметрические кривые...")
        figures.parametric_curves()
        plt.savefig('parametric_curves.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✅ Сохранено: parametric_curves.png")
        
        print("🌀 Создаем спирали...")
        figures.spirals()
        plt.savefig('spirals.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✅ Сохранено: spirals.png")
        
        print("🔢 Создаем множество Мандельброта...")
        figures.mandelbrot_set()
        plt.savefig('mandelbrot.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("✅ Сохранено: mandelbrot.png")
        
        print("\n🎉 Демонстрация завершена!")
        print("📂 Все изображения сохранены в текущей директории.")
        
    except Exception as e:
        print(f"❌ Ошибка при создании фигур: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_demo()
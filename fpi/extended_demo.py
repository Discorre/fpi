#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенное демо для демонстрации всех математических фигур
"""

import matplotlib
matplotlib.use('Agg')  # Использовать не-интерактивный backend

from mathematical_figures import MathematicalFigures
import matplotlib.pyplot as plt

def extended_demo():
    """Полная демонстрация всех математических фигур"""
    print("🎨 Расширенная демонстрация математических фигур")
    print("=" * 50)
    
    figures = MathematicalFigures()
    
    demos = [
        ("📐 Параметрические кривые", "parametric_curves", "parametric_curves.png"),
        ("🌀 Спирали", "spirals", "spirals.png"),
        ("🔢 Множество Мандельброта", "mandelbrot_set", "mandelbrot.png"),
        ("🔮 Множество Жюлиа", "julia_set", "julia_set.png"),
        ("🏔️ 3D поверхности", "complex_3d_surfaces", "3d_surfaces.png"),
        ("⚡ Аттрактор Лоренца", "lorenz_attractor", "lorenz_attractor.png"),
        ("🎯 Эпициклы Фурье", "fourier_epicycles", "fourier_epicycles.png"),
    ]
    
    successful = 0
    total = len(demos)
    
    for desc, method_name, filename in demos:
        try:
            print(f"{desc}...")
            method = getattr(figures, method_name)
            method()
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"✅ Сохранено: {filename}")
            successful += 1
        except Exception as e:
            print(f"❌ Ошибка при создании {desc}: {e}")
    
    print(f"\n🎉 Демонстрация завершена!")
    print(f"📊 Успешно создано: {successful}/{total} фигур")
    print(f"📂 Все изображения сохранены в директории: {filename.split('/')[-1] if '/' in str(filename) else 'текущей'}")

if __name__ == "__main__":
    extended_demo()
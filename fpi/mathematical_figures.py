#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для рисования сложных математических фигур
Автор: AI Assistant
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from scipy.special import factorial
import warnings
warnings.filterwarnings('ignore')

# Настройка matplotlib для поддержки русских шрифтов
plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MathematicalFigures:
    """Класс для создания сложных математических фигур"""
    
    def __init__(self):
        self.fig_size = (12, 8)
        
    def mandelbrot_set(self, width=800, height=600, max_iter=100):
        """Рисует множество Мандельброта"""
        # Определяем область комплексной плоскости
        xmin, xmax = -2.5, 1.5
        ymin, ymax = -1.5, 1.5
        
        # Создаем сетку точек
        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        # Инициализируем Z и массив итераций
        Z = np.zeros_like(C)
        iterations = np.zeros(C.shape, dtype=int)
        
        # Итерируем формулу z = z^2 + c
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            iterations[mask] = i
            
        plt.figure(figsize=self.fig_size)
        plt.imshow(iterations, extent=[xmin, xmax, ymin, ymax], 
                  cmap='hot', origin='lower', interpolation='bilinear')
        plt.colorbar(label='Количество итераций')
        plt.title('Множество Мандельброта', fontsize=16)
        plt.xlabel('Действительная часть')
        plt.ylabel('Мнимая часть')
        plt.tight_layout()
        plt.show()
        
    def julia_set(self, c=-0.7 + 0.27015j, width=800, height=600, max_iter=100):
        """Рисует множество Жюлиа"""
        xmin, xmax = -2, 2
        ymin, ymax = -2, 2
        
        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        
        iterations = np.zeros(Z.shape, dtype=int)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + c
            iterations[mask] = i
            
        plt.figure(figsize=self.fig_size)
        plt.imshow(iterations, extent=[xmin, xmax, ymin, ymax], 
                  cmap='viridis', origin='lower')
        plt.colorbar(label='Количество итераций')
        plt.title(f'Множество Жюлиа (c = {c:.3f})', fontsize=16)
        plt.xlabel('Действительная часть')
        plt.ylabel('Мнимая часть')
        plt.tight_layout()
        plt.show()
        
    def parametric_curves(self):
        """Рисует различные параметрические кривые"""
        t = np.linspace(0, 4*np.pi, 1000)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Роза с 8 лепестками
        k = 4
        r = np.cos(k * t)
        x1 = r * np.cos(t)
        y1 = r * np.sin(t)
        axes[0, 0].plot(x1, y1, 'r-', linewidth=2)
        axes[0, 0].set_title('Роза (r = cos(4θ))', fontsize=14)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_aspect('equal')
        
        # Лемниската Бернулли
        a = 1
        t2 = np.linspace(-np.pi/4, np.pi/4, 500)
        r2 = a * np.sqrt(2 * np.cos(2 * t2))
        x2_pos = r2 * np.cos(t2)
        y2_pos = r2 * np.sin(t2)
        x2_neg = -r2 * np.cos(t2)
        y2_neg = -r2 * np.sin(t2)
        axes[0, 1].plot(x2_pos, y2_pos, 'b-', linewidth=2)
        axes[0, 1].plot(x2_neg, y2_neg, 'b-', linewidth=2)
        axes[0, 1].set_title('Лемниската Бернулли', fontsize=14)
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_aspect('equal')
        
        # Гипоциклоида (4 лепестка)
        R, r = 4, 1
        t3 = np.linspace(0, 2*np.pi, 1000)
        x3 = (R - r) * np.cos(t3) + r * np.cos((R - r) * t3 / r)
        y3 = (R - r) * np.sin(t3) - r * np.sin((R - r) * t3 / r)
        axes[1, 0].plot(x3, y3, 'g-', linewidth=2)
        axes[1, 0].set_title('Гипоциклоида', fontsize=14)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_aspect('equal')
        
        # Эпициклоида
        R, r = 3, 1
        x4 = (R + r) * np.cos(t3) - r * np.cos((R + r) * t3 / r)
        y4 = (R + r) * np.sin(t3) - r * np.sin((R + r) * t3 / r)
        axes[1, 1].plot(x4, y4, 'm-', linewidth=2)
        axes[1, 1].set_title('Эпициклоида', fontsize=14)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_aspect('equal')
        
        plt.tight_layout()
        plt.show()
        
    def spirals(self):
        """Рисует различные типы спиралей"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Архимедова спираль
        t = np.linspace(0, 6*np.pi, 1000)
        a = 0.5
        r1 = a * t
        x1 = r1 * np.cos(t)
        y1 = r1 * np.sin(t)
        axes[0, 0].plot(x1, y1, 'r-', linewidth=2)
        axes[0, 0].set_title('Архимедова спираль (r = aθ)', fontsize=14)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_aspect('equal')
        
        # Логарифмическая спираль
        t2 = np.linspace(0, 4*np.pi, 1000)
        a, b = 0.1, 0.3
        r2 = a * np.exp(b * t2)
        x2 = r2 * np.cos(t2)
        y2 = r2 * np.sin(t2)
        axes[0, 1].plot(x2, y2, 'b-', linewidth=2)
        axes[0, 1].set_title('Логарифмическая спираль (r = ae^(bθ))', fontsize=14)
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_aspect('equal')
        
        # Спираль Ферма
        t3 = np.linspace(0, 8*np.pi, 1000)
        r3 = np.sqrt(t3)
        x3 = r3 * np.cos(t3)
        y3 = r3 * np.sin(t3)
        axes[1, 0].plot(x3, y3, 'g-', linewidth=2)
        axes[1, 0].plot(-x3, -y3, 'g-', linewidth=2)  # Вторая ветвь
        axes[1, 0].set_title('Спираль Ферма (r = √θ)', fontsize=14)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_aspect('equal')
        
        # Гиперболическая спираль
        t4 = np.linspace(0.1, 6*np.pi, 1000)
        a = 1
        r4 = a / t4
        x4 = r4 * np.cos(t4)
        y4 = r4 * np.sin(t4)
        axes[1, 1].plot(x4, y4, 'm-', linewidth=2)
        axes[1, 1].set_title('Гиперболическая спираль (r = a/θ)', fontsize=14)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_aspect('equal')
        
        plt.tight_layout()
        plt.show()
        
    def complex_3d_surfaces(self):
        """Рисует сложные 3D поверхности"""
        fig = plt.figure(figsize=(20, 15))
        
        # Поверхность седла
        ax1 = fig.add_subplot(2, 3, 1, projection='3d')
        x = np.linspace(-3, 3, 100)
        y = np.linspace(-3, 3, 100)
        X, Y = np.meshgrid(x, y)
        Z1 = X**2 - Y**2
        ax1.plot_surface(X, Y, Z1, cmap='viridis', alpha=0.8)
        ax1.set_title('Седловая поверхность (z = x² - y²)', fontsize=12)
        
        # Поверхность Монге
        ax2 = fig.add_subplot(2, 3, 2, projection='3d')
        Z2 = X**2 + Y**2
        ax2.plot_surface(X, Y, Z2, cmap='plasma', alpha=0.8)
        ax2.set_title('Параболоид (z = x² + y²)', fontsize=12)
        
        # Поверхность волны
        ax3 = fig.add_subplot(2, 3, 3, projection='3d')
        Z3 = np.sin(np.sqrt(X**2 + Y**2))
        ax3.plot_surface(X, Y, Z3, cmap='coolwarm', alpha=0.8)
        ax3.set_title('Волновая поверхность (z = sin(√(x² + y²)))', fontsize=12)
        
        # Торс
        ax4 = fig.add_subplot(2, 3, 4, projection='3d')
        u = np.linspace(0, 2*np.pi, 100)
        v = np.linspace(0, 2*np.pi, 100)
        U, V = np.meshgrid(u, v)
        R, r = 3, 1
        X4 = (R + r * np.cos(V)) * np.cos(U)
        Y4 = (R + r * np.cos(V)) * np.sin(U)
        Z4 = r * np.sin(V)
        ax4.plot_surface(X4, Y4, Z4, cmap='viridis', alpha=0.8)
        ax4.set_title('Тор', fontsize=12)
        
        # Сфера с деформацией
        ax5 = fig.add_subplot(2, 3, 5, projection='3d')
        phi = np.linspace(0, np.pi, 50)
        theta = np.linspace(0, 2*np.pi, 100)
        PHI, THETA = np.meshgrid(phi, theta)
        R5 = 2 + 0.5 * np.sin(5*THETA) * np.sin(3*PHI)
        X5 = R5 * np.sin(PHI) * np.cos(THETA)
        Y5 = R5 * np.sin(PHI) * np.sin(THETA)
        Z5 = R5 * np.cos(PHI)
        ax5.plot_surface(X5, Y5, Z5, cmap='rainbow', alpha=0.8)
        ax5.set_title('Деформированная сфера', fontsize=12)
        
        # Поверхность Клейна (проекция)
        ax6 = fig.add_subplot(2, 3, 6, projection='3d')
        u = np.linspace(0, 2*np.pi, 50)
        v = np.linspace(0, 2*np.pi, 50)
        U, V = np.meshgrid(u, v)
        a = 2
        X6 = (a + np.cos(U/2)*np.sin(V) - np.sin(U/2)*np.sin(2*V)) * np.cos(U)
        Y6 = (a + np.cos(U/2)*np.sin(V) - np.sin(U/2)*np.sin(2*V)) * np.sin(U)
        Z6 = np.sin(U/2)*np.sin(V) + np.cos(U/2)*np.sin(2*V)
        ax6.plot_surface(X6, Y6, Z6, cmap='magma', alpha=0.8)
        ax6.set_title('Бутылка Клейна (проекция)', fontsize=12)
        
        plt.tight_layout()
        plt.show()
        
    def fourier_epicycles(self, n_circles=50):
        """Рисует эпициклы Фурье для аппроксимации сложной кривой"""
        # Создаем сложную кривую (например, форму звезды)
        t = np.linspace(0, 2*np.pi, 1000)
        star_r = 1 + 0.5 * np.cos(5*t)
        star_x = star_r * np.cos(t)
        star_y = star_r * np.sin(t)
        
        # Вычисляем коэффициенты Фурье
        def fourier_coefficients(x_data, y_data, n_coeffs):
            complex_data = x_data + 1j * y_data
            coeffs = []
            N = len(complex_data)
            
            for k in range(-n_coeffs//2, n_coeffs//2 + 1):
                coeff = np.sum(complex_data * np.exp(-2j * np.pi * k * np.arange(N) / N)) / N
                coeffs.append((k, coeff))
            
            return coeffs
        
        coeffs = fourier_coefficients(star_x, star_y, n_circles)
        
        # Создаем анимацию
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Исходная кривая
        ax1.plot(star_x, star_y, 'b-', linewidth=2, label='Исходная кривая')
        ax1.set_title('Исходная форма звезды', fontsize=14)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Аппроксимация Фурье
        t_approx = np.linspace(0, 2*np.pi, 200)
        approx_x = np.zeros_like(t_approx)
        approx_y = np.zeros_like(t_approx)
        
        for k, coeff in coeffs:
            approx_x += np.real(coeff * np.exp(1j * k * t_approx))
            approx_y += np.imag(coeff * np.exp(1j * k * t_approx))
        
        ax2.plot(approx_x, approx_y, 'r-', linewidth=2, label=f'Аппроксимация ({n_circles} эпициклов)')
        ax2.plot(star_x, star_y, 'b--', alpha=0.5, label='Исходная кривая')
        ax2.set_title('Аппроксимация эпициклами Фурье', fontsize=14)
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        
    def lorenz_attractor(self):
        """Рисует аттрактор Лоренца"""
        def lorenz_system(state, t, sigma=10, rho=28, beta=8/3):
            x, y, z = state
            return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]
        
        # Численное интегрирование
        from scipy.integrate import odeint
        
        # Начальные условия
        initial_state = [1, 1, 1]
        t = np.linspace(0, 25, 10000)
        
        # Решение системы
        solution = odeint(lorenz_system, initial_state, t)
        x, y, z = solution.T
        
        # 3D визуализация
        fig = plt.figure(figsize=(15, 5))
        
        # 3D вид
        ax1 = fig.add_subplot(1, 3, 1, projection='3d')
        ax1.plot(x, y, z, lw=0.5, color='blue')
        ax1.set_title('Аттрактор Лоренца (3D)', fontsize=14)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        
        # Проекция XY
        ax2 = fig.add_subplot(1, 3, 2)
        ax2.plot(x, y, lw=0.5, color='red')
        ax2.set_title('Проекция на плоскость XY', fontsize=14)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.grid(True, alpha=0.3)
        
        # Проекция XZ
        ax3 = fig.add_subplot(1, 3, 3)
        ax3.plot(x, z, lw=0.5, color='green')
        ax3.set_title('Проекция на плоскость XZ', fontsize=14)
        ax3.set_xlabel('X')
        ax3.set_ylabel('Z')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def main():
    """Главная функция для демонстрации всех фигур"""
    print("Программа для рисования сложных математических фигур")
    print("=" * 50)
    
    figures = MathematicalFigures()
    
    try:
        print("1. Рисуем множество Мандельброта...")
        figures.mandelbrot_set()
        
        print("2. Рисуем множество Жюлиа...")
        figures.julia_set()
        
        print("3. Рисуем параметрические кривые...")
        figures.parametric_curves()
        
        print("4. Рисуем различные спирали...")
        figures.spirals()
        
        print("5. Рисуем сложные 3D поверхности...")
        figures.complex_3d_surfaces()
        
        print("6. Рисуем эпициклы Фурье...")
        figures.fourier_epicycles()
        
        print("7. Рисуем аттрактор Лоренца...")
        figures.lorenz_attractor()
        
        print("\nВсе фигуры успешно созданы!")
        
    except Exception as e:
        print(f"Ошибка при создании фигур: {e}")

if __name__ == "__main__":
    main()
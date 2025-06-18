import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
from typing import Tuple, List

class MathematicalFigures:
    """Класс для создания сложных математических фигур"""
    
    def __init__(self):
        self.fig_size = (12, 8)
        plt.style.use('dark_background')
    
    def fibonacci_spiral(self, n_squares: int = 8) -> None:
        """Рисует спираль Фибоначчи"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Числа Фибоначчи
        fib = [1, 1]
        for i in range(2, n_squares):
            fib.append(fib[i-1] + fib[i-2])
        
        # Рисуем квадраты и спираль
        x, y = 0, 0
        direction = 0  # 0: right, 1: up, 2: left, 3: down
        
        colors = plt.cm.rainbow(np.linspace(0, 1, n_squares))
        
        for i in range(n_squares):
            size = fib[i]
            
            # Рисуем квадрат
            if direction == 0:  # right
                rect = plt.Rectangle((x, y), size, size, fill=False, 
                                   edgecolor=colors[i], linewidth=2)
                center_x, center_y = x + size, y + size
                next_x, next_y = x + size, y
            elif direction == 1:  # up
                rect = plt.Rectangle((x-size, y), size, size, fill=False, 
                                   edgecolor=colors[i], linewidth=2)
                center_x, center_y = x - size, y + size
                next_x, next_y = x - size, y + size
            elif direction == 2:  # left
                rect = plt.Rectangle((x-size, y-size), size, size, fill=False, 
                                   edgecolor=colors[i], linewidth=2)
                center_x, center_y = x - size, y - size
                next_x, next_y = x, y - size
            else:  # down
                rect = plt.Rectangle((x, y-size), size, size, fill=False, 
                                   edgecolor=colors[i], linewidth=2)
                center_x, center_y = x + size, y - size
                next_x, next_y = x, y
            
            ax.add_patch(rect)
            
            # Рисуем четверть окружности (спираль)
            angles = np.linspace(direction * np.pi/2, (direction + 1) * np.pi/2, 100)
            spiral_x = center_x + size * np.cos(angles)
            spiral_y = center_y + size * np.sin(angles)
            ax.plot(spiral_x, spiral_y, color=colors[i], linewidth=3, alpha=0.8)
            
            x, y = next_x, next_y
            direction = (direction + 1) % 4
        
        ax.set_aspect('equal')
        ax.set_title('Спираль Фибоначчи', fontsize=16, color='white')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def mandelbrot_set(self, width: int = 800, height: int = 600, 
                      max_iter: int = 100) -> None:
        """Рисует фрактал Мандельброта"""
        # Определяем область комплексной плоскости
        xmin, xmax = -2.5, 1.5
        ymin, ymax = -1.5, 1.5
        
        # Создаем сетку точек
        x = np.linspace(xmin, xmax, width)
        y = np.linspace(ymin, ymax, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        # Инициализируем Z и результат
        Z = np.zeros_like(C)
        result = np.zeros(C.shape, dtype=int)
        
        # Итерации для вычисления множества Мандельброта
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            result[mask] = i
        
        # Отображение
        fig, ax = plt.subplots(figsize=self.fig_size)
        im = ax.imshow(result, extent=[xmin, xmax, ymin, ymax], 
                      cmap='hot', origin='lower', interpolation='bilinear')
        ax.set_title('Фрактал Мандельброта', fontsize=16, color='white')
        ax.set_xlabel('Действительная часть', color='white')
        ax.set_ylabel('Мнимая часть', color='white')
        plt.colorbar(im, label='Количество итераций')
        plt.tight_layout()
        plt.show()
    
    def lissajous_curve(self, a: int = 3, b: int = 4, delta: float = 0) -> None:
        """Рисует кривую Лиссажу"""
        t = np.linspace(0, 2 * np.pi, 1000)
        x = np.sin(a * t + delta)
        y = np.sin(b * t)
        
        # Создаем градиент цвета
        colors = plt.cm.rainbow(np.linspace(0, 1, len(t)))
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Рисуем кривую с градиентом
        for i in range(len(t)-1):
            ax.plot(x[i:i+2], y[i:i+2], color=colors[i], linewidth=2)
        
        ax.set_aspect('equal')
        ax.set_title(f'Кривая Лиссажу (a={a}, b={b}, δ={delta})', 
                    fontsize=16, color='white')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        plt.tight_layout()
        plt.show()
    
    def polar_rose(self, n: int = 5, k: int = 3) -> None:
        """Рисует розу в полярных координатах"""
        theta = np.linspace(0, 2 * np.pi * n, 1000)
        r = np.cos(k * theta)
        
        # Преобразуем в декартовы координаты
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Создаем градиент цвета
        colors = plt.cm.hsv(np.linspace(0, 1, len(theta)))
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Рисуем розу
        for i in range(len(theta)-1):
            ax.plot(x[i:i+2], y[i:i+2], color=colors[i], linewidth=2)
        
        ax.set_aspect('equal')
        ax.set_title(f'Полярная роза (r = cos({k}θ))', fontsize=16, color='white')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        plt.tight_layout()
        plt.show()
    
    def lorenz_attractor(self, sigma: float = 10, rho: float = 28, 
                        beta: float = 8/3, dt: float = 0.01, 
                        steps: int = 10000) -> None:
        """Рисует аттрактор Лоренца"""
        # Начальные условия
        x, y, z = 1.0, 1.0, 1.0
        xs, ys, zs = [], [], []
        
        # Численное интегрирование системы Лоренца
        for _ in range(steps):
            dx = sigma * (y - x) * dt
            dy = (rho * x - y - x * z) * dt
            dz = (x * y - beta * z) * dt
            
            x += dx
            y += dy
            z += dz
            
            xs.append(x)
            ys.append(y)
            zs.append(z)
        
        # 3D визуализация
        fig = plt.figure(figsize=self.fig_size)
        ax = fig.add_subplot(111, projection='3d')
        
        # Создаем градиент цвета по времени
        colors = plt.cm.plasma(np.linspace(0, 1, len(xs)))
        
        for i in range(len(xs)-1):
            ax.plot(xs[i:i+2], ys[i:i+2], zs[i:i+2], 
                   color=colors[i], linewidth=0.5)
        
        ax.set_title('Аттрактор Лоренца', fontsize=16, color='white')
        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.set_zlabel('Z', color='white')
        plt.tight_layout()
        plt.show()
    
    def sierpinski_triangle(self, depth: int = 6) -> None:
        """Рисует треугольник Серпинского"""
        def sierpinski_recursive(ax, vertices, depth, color_intensity):
            if depth == 0:
                triangle = plt.Polygon(vertices, alpha=color_intensity, 
                                     color=plt.cm.plasma(color_intensity))
                ax.add_patch(triangle)
            else:
                # Находим середины сторон
                mid1 = [(vertices[0][0] + vertices[1][0])/2, 
                       (vertices[0][1] + vertices[1][1])/2]
                mid2 = [(vertices[1][0] + vertices[2][0])/2, 
                       (vertices[1][1] + vertices[2][1])/2]
                mid3 = [(vertices[2][0] + vertices[0][0])/2, 
                       (vertices[2][1] + vertices[0][1])/2]
                
                # Рекурсивно рисуем три меньших треугольника
                sierpinski_recursive(ax, [vertices[0], mid1, mid3], 
                                    depth-1, color_intensity * 1.1)
                sierpinski_recursive(ax, [mid1, vertices[1], mid2], 
                                    depth-1, color_intensity * 1.1)
                sierpinski_recursive(ax, [mid3, mid2, vertices[2]], 
                                    depth-1, color_intensity * 1.1)
        
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Начальный треугольник
        vertices = [[0, 0], [1, 0], [0.5, np.sqrt(3)/2]]
        sierpinski_recursive(ax, vertices, depth, 0.1)
        
        ax.set_aspect('equal')
        ax.set_title(f'Треугольник Серпинского (глубина {depth})', 
                    fontsize=16, color='white')
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.0)
        ax.axis('off')
        plt.tight_layout()
        plt.show()
    
    def dragon_curve(self, iterations: int = 12) -> None:
        """Рисует кривую дракона"""
        def dragon_sequence(n):
            if n == 0:
                return [1]
            prev = dragon_sequence(n-1)
            return prev + [1] + [1-x for x in reversed(prev)]
        
        # Получаем последовательность поворотов
        turns = dragon_sequence(iterations)
        
        # Строим кривую
        x, y = [0], [0]
        direction = 0  # 0: right, 1: up, 2: left, 3: down
        
        for turn in turns:
            if turn == 1:  # поворот влево
                direction = (direction + 1) % 4
            else:  # поворот вправо
                direction = (direction - 1) % 4
            
            # Двигаемся в новом направлении
            if direction == 0:
                x.append(x[-1] + 1)
                y.append(y[-1])
            elif direction == 1:
                x.append(x[-1])
                y.append(y[-1] + 1)
            elif direction == 2:
                x.append(x[-1] - 1)
                y.append(y[-1])
            else:
                x.append(x[-1])
                y.append(y[-1] - 1)
        
        # Рисуем кривую
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Создаем градиент цвета
        colors = plt.cm.rainbow(np.linspace(0, 1, len(x)))
        
        for i in range(len(x)-1):
            ax.plot(x[i:i+2], y[i:i+2], color=colors[i], linewidth=1)
        
        ax.set_aspect('equal')
        ax.set_title(f'Кривая дракона ({iterations} итераций)', 
                    fontsize=16, color='white')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def parametric_surface_3d(self) -> None:
        """Рисует сложную параметрическую поверхность"""
        u = np.linspace(0, 2*np.pi, 100)
        v = np.linspace(0, 2*np.pi, 100)
        U, V = np.meshgrid(u, v)
        
        # Параметрические уравнения для сложной поверхности
        X = (3 + np.cos(V)) * np.cos(U)
        Y = (3 + np.cos(V)) * np.sin(U)
        Z = np.sin(V) + np.sin(3*U) * 0.3
        
        fig = plt.figure(figsize=self.fig_size)
        ax = fig.add_subplot(111, projection='3d')
        
        # Рисуем поверхность с цветовой картой
        surf = ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.8, 
                              linewidth=0, antialiased=True)
        
        ax.set_title('Параметрическая поверхность', fontsize=16, color='white')
        ax.set_xlabel('X', color='white')
        ax.set_ylabel('Y', color='white')
        ax.set_zlabel('Z', color='white')
        
        fig.colorbar(surf, shrink=0.5, aspect=20)
        plt.tight_layout()
        plt.show()


def main():
    """Главная функция для демонстрации всех фигур"""
    print("🎨 Генератор сложных математических фигур")
    print("=" * 50)
    
    math_fig = MathematicalFigures()
    
    while True:
        print("\nВыберите фигуру для отображения:")
        print("1. Спираль Фибоначчи")
        print("2. Фрактал Мандельброта")
        print("3. Кривая Лиссажу")
        print("4. Полярная роза")
        print("5. Аттрактор Лоренца")
        print("6. Треугольник Серпинского")
        print("7. Кривая дракона")
        print("8. Параметрическая поверхность")
        print("9. Показать все фигуры")
        print("0. Выход")
        
        choice = input("\nВведите номер (0-9): ").strip()
        
        try:
            if choice == '1':
                math_fig.fibonacci_spiral()
            elif choice == '2':
                math_fig.mandelbrot_set()
            elif choice == '3':
                math_fig.lissajous_curve()
            elif choice == '4':
                math_fig.polar_rose()
            elif choice == '5':
                math_fig.lorenz_attractor()
            elif choice == '6':
                math_fig.sierpinski_triangle()
            elif choice == '7':
                math_fig.dragon_curve()
            elif choice == '8':
                math_fig.parametric_surface_3d()
            elif choice == '9':
                print("\nОтображение всех фигур...")
                math_fig.fibonacci_spiral()
                math_fig.mandelbrot_set()
                math_fig.lissajous_curve()
                math_fig.polar_rose()
                math_fig.lorenz_attractor()
                math_fig.sierpinski_triangle()
                math_fig.dragon_curve()
                math_fig.parametric_surface_3d()
            elif choice == '0':
                print("До свидания! 👋")
                break
            else:
                print("❌ Неверный выбор. Попробуйте еще раз.")
        
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()
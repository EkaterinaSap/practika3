import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from typing import Optional


class ImageProcessorApp:
    """Главный класс приложения для обработки изображений"""
    def __init__(self, master):
        """Инициализация приложения
        Args: master (tk.Tk): Главное окно Tkinter"""
        self.master = master
        self.master.title("Image Processor")
        self.master.geometry("800x600")

        # Инициализация всех атрибутов
        self.image: Optional[np.ndarray] = None
        self.display_image: Optional[np.ndarray] = None
        self.camera: Optional[cv2.VideoCapture] = None
        self.tk_image: Optional[ImageTk.PhotoImage] = None

        # Виджеты
        self.load_frame: Optional[tk.Frame] = None
        self.image_label: Optional[tk.Label] = None
        self.ops_frame: Optional[tk.Frame] = None
        self.channel_var: Optional[tk.StringVar] = None

        # Интерфейс (создание)
        self.create_widgets()

    def create_widgets(self):
        """Функция, которая создает графический интерфейс приложения"""
        # Кнопки загрузки изображения
        self.load_frame = tk.Frame(self.master)
        self.load_frame.pack(pady=10)

        tk.Button(self.load_frame, text="Загрузить изображение",
                  command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.load_frame, text="Сделать снимок",
                  command=self.capture_image).pack(side=tk.LEFT, padx=5)

        # Поле для отображения изображения
        self.image_label = tk.Label(self.master)
        self.image_label.pack(pady=10, fill=tk.BOTH, expand=True)

        # Операции с изображением
        self.ops_frame = tk.Frame(self.master)
        self.ops_frame.pack(pady=10)

        tk.Button(self.ops_frame, text="Показать изображение",
                  command=self.show_image).pack(side=tk.LEFT, padx=5)

        self.channel_var = tk.StringVar(value="red")
        tk.Label(self.ops_frame, text="Канал:").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(self.ops_frame, textvariable=self.channel_var,
                     values=["red", "green", "blue"],
                     width=7).pack(side=tk.LEFT, padx=5)
        tk.Button(self.ops_frame, text="Показать канал",
                  command=self.show_channel).pack(side=tk.LEFT, padx=5)

        tk.Button(self.ops_frame, text="Изменить размер",
                  command=self.resize_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.ops_frame, text="Повысить яркость",
                  command=self.adjust_brightness).pack(side=tk.LEFT, padx=5)
        tk.Button(self.ops_frame, text="Нарисовать линию",
                  command=self.draw_line).pack(side=tk.LEFT, padx=5)

    def load_image(self):
        """Функция, которая загружает изображение через диалоговое окно"""
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if path:
            try:
                self.image = cv2.imread(path)
                if self.image is None:
                    raise ValueError("Ошибка загрузки изображения")
                self.show_image()
            except Exception as e:
                messagebox.showerror("Ошибка",
                                     f"Не удалось загрузить изображение: {str(e)}")

    def capture_image(self):
        """Функция, которая захватывает изображение с камеры"""
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Ошибка",
                                     "Не удалось подключить камеру")
                self.camera = None
                return

        ret, frame = self.camera.read()
        if ret:
            self.image = frame
            self.show_image()
        else:
            messagebox.showerror("Ошибка",
                                 "Не удалось сделать снимок")

    def show_image(self):
        """Функция, которая отображает исходное изображение"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return
        self.display_image = self.image.copy()
        self.update_display()

    def show_channel(self):
        """Функция, которая отображает выбранный цветовой канал"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return

        channel = self.channel_var.get()
        idx = {"red": 2, "green": 1, "blue": 0}.get(channel, 2)

        # Создаем пустую матрицу и заполняем выбранный канал
        zeros = np.zeros_like(self.image[:, :, 0])
        channels = [zeros, zeros, zeros]
        channels[idx] = self.image[:, :, idx]

        self.display_image = cv2.merge(channels)
        self.update_display()

    def resize_image(self):
        """Функция, которая изменяет размер изображения по введенным пользователем размерам"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Изменение размера")
        dialog.geometry("300x100")

        tk.Label(dialog, text="Ширина:").grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(dialog)
        width_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(dialog, text="Высота:").grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(dialog)
        height_entry.grid(row=1, column=1, padx=5, pady=5)

        def apply_resize():
            """Функция, которая измененяет размер изображения"""
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                if width <= 0 or height <= 0:
                    raise ValueError("Размеры должны быть положительными")
                self.display_image = cv2.resize(self.image, (width, height))
                self.update_display()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка",
                                     f"Некорректные данные: {str(e)}")

        tk.Button(dialog, text="Применить",
                  command=apply_resize).grid(row=2, columnspan=2, pady=5)

    def adjust_brightness(self):
        """Функция, которая корректирует яркость изображения на указанное значение"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Коррекция яркости")
        dialog.geometry("300x100")

        tk.Label(dialog, text="Значение яркости (0-100):").pack(pady=5)
        brightness_entry = tk.Entry(dialog)
        brightness_entry.pack(pady=5)

        def apply_brightness():
            try:
                value = int(brightness_entry.get())
                if not 0 <= value <= 100:
                    raise ValueError("Значение должно быть от 0 до 100")

                # Преобразуем в HSV и корректируем V-канал
                hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
                hsv = hsv.astype(np.float32)
                hsv[:, :, 2] += value
                hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)
                hsv = hsv.astype(np.uint8)

                self.display_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                self.update_display()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка",
                                     f"Некорректные данные: {str(e)}")

        tk.Button(dialog, text="Применить",
                  command=apply_brightness).pack(pady=5)

    def draw_line(self):
        """Функция, которая рисует зелёную линию на изображении
        по указанным координатам"""
        if self.image is None:
            messagebox.showwarning("Предупреждение",
                                   "Сначала загрузите изображение")
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Рисование линии")
        dialog.geometry("300x150")

        entries = {}
        fields = [
            ("X начальная", "x1"),
            ("Y начальная", "y1"),
            ("X конечная", "x2"),
            ("Y конечная", "y2"),
            ("Толщина", "thickness")
        ]

        for i, (label, name) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i,
                                              column=0, padx=5, pady=2)
            entry = tk.Entry(dialog)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entries[name] = entry

        def apply_line():
            try:
                x1 = int(entries["x1"].get())
                y1 = int(entries["y1"].get())
                x2 = int(entries["x2"].get())
                y2 = int(entries["y2"].get())
                thickness = int(entries["thickness"].get())

                if thickness <= 0:
                    raise ValueError("Толщина должна быть положительной")

                img_copy = self.image.copy()
                cv2.line(img_copy, (x1, y1), (x2, y2),
                         (0, 255, 0), thickness)
                self.display_image = img_copy
                self.update_display()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка",
                                     f"Некорректные данные: {str(e)}")

        tk.Button(dialog, text="Применить",
                  command=apply_line).grid(row=5, columnspan=2, pady=10)

    def update_display(self):
        """Функция, которая обновляет отображаемое изображение в интерфейсе"""
        if self.display_image is None:
            return

        # Конвертация для Tkinter
        img_rgb = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # Явное создание объекта PhotoImage
        self.tk_image = ImageTk.PhotoImage(image=img_pil)

        self.image_label.configure(image=self.tk_image)
        self.image_label.image = self.tk_image

    def __del__(self):
        """Функция, которая освобождает ресурсы при
        завершении работы приложения"""
        if self.camera is not None:
            self.camera.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

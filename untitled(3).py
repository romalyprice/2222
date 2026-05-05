import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Создаем главное окно
root = tk.Tk()
root.title("Weather Diary")
root.geometry("800x600")

# Переменные для ввода
date_var = tk.StringVar()
temp_var = tk.StringVar()
desc_var = tk.StringVar()
precip_var = tk.StringVar(value="Нет")  # Значение по умолчанию

# Ввод данных
tk.Label(root, text="Дата (ГГГГ-ММ-ДД)").grid(row=0, column=0, padx=5, pady=5, sticky='w')
tk.Entry(root, textvariable=date_var, width=15).grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Температура (°C)").grid(row=1, column=0, padx=5, pady=5, sticky='w')
tk.Entry(root, textvariable=temp_var, width=10).grid(row=1, column=1, padx=5, pady=5)

tk.Label(root, text="Описание погоды").grid(row=2, column=0, padx=5, pady=5, sticky='w')
tk.Entry(root, textvariable=desc_var, width=30).grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Осадки").grid(row=3, column=0, padx=5, pady=5, sticky='w')
precip_options = ["Нет", "Да"]
ttk.Combobox(root, textvariable=precip_var, values=precip_options, state="readonly", width=10).grid(row=3, column=1, padx=5, pady=5)

# Таблица для отображения записей
columns = ("Дата", "Температура", "Описание", "Осадки")
tree = ttk.Treeview(root, columns=columns, show='headings', height=15)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.grid(row=7, column=0, columnspan=4, padx=5, pady=10)

# Список для хранения данных
records = []

# Функция очистки полей
def clear_fields():
    date_var.set("")
    temp_var.set("")
    desc_var.set("")
    precip_var.set("Нет")

# Функция добавления записи
def add_record():
    date_str = date_var.get().strip()
    temp_str = temp_var.get().strip()
    desc = desc_var.get().strip()
    precip = precip_var.get()

    # Проверка корректности
    # дата
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Ошибка", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД.")
        return
    # температура
    if not temp_str or not temp_str.replace('-', '').isdigit():
        messagebox.showerror("Ошибка", "Температура должна быть числом.")
        return
    # описание
    if not desc:
        messagebox.showerror("Ошибка", "Описание не должно быть пустым.")
        return

    temp = int(temp_str)
    record = {
        "Дата": date_str,
        "Температура": temp,
        "Описание": desc,
        "Осадки": precip
    }
    records.append(record)
    tree.insert('', tk.END, values=(date_str, temp, desc, precip))
    clear_fields()

# Кнопка добавления
tk.Button(root, text="Добавить запись", command=add_record).grid(row=6, column=0, padx=5, pady=10)

# --- Фильтрация ---
filter_date_var = tk.StringVar()
filter_temp_var = tk.StringVar()

tk.Label(root, text="Фильтр по дате (ГГГГ-ММ-ДД)").grid(row=8, column=0, padx=5, pady=5, sticky='w')
tk.Entry(root, textvariable=filter_date_var, width=15).grid(row=8, column=1, padx=5, pady=5)

tk.Label(root, text="Температура выше").grid(row=8, column=2, padx=5, pady=5, sticky='w')
tk.Entry(root, textvariable=filter_temp_var, width=10).grid(row=8, column=3, padx=5, pady=5)

def apply_filter():
    date_filter = filter_date_var.get().strip()
    temp_filter = filter_temp_var.get().strip()

    # Очистка таблицы
    for item in tree.get_children():
        tree.delete(item)

    for rec in records:
        # фильтр по дате
        if date_filter:
            try:
                datetime.strptime(date_filter, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректный формат даты фильтра.")
                return
            if rec["Дата"] != date_filter:
                continue
        # фильтр по температуре
        if temp_filter:
            if not temp_filter.isdigit():
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом.")
                return
            if rec["Температура"] <= int(temp_filter):
                continue
        tree.insert('', tk.END, values=(
            rec["Дата"],
            rec["Температура"],
            rec["Описание"],
            rec["Осадки"]
        ))

def reset_filter():
    filter_date_var.set("")
    filter_temp_var.set("")
    # переотобразить все записи
    for item in tree.get_children():
        tree.delete(item)
    for rec in records:
        tree.insert('', tk.END, values=(
            rec["Дата"],
            rec["Температура"],
            rec["Описание"],
            rec["Осадки"]
        ))

tk.Button(root, text="Применить фильтр", command=apply_filter).grid(row=9, column=0, padx=5, pady=10)
tk.Button(root, text="Сбросить фильтр", command=reset_filter).grid(row=9, column=1, padx=5, pady=10)

# --- Сохраняем и загружаем ---
def save_to_json():
    try:
        with open("weather_records.json", "w", encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успех", "Данные сохранены успешно.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

def load_from_json():
    if os.path.exists("weather_records.json"):
        try:
            with open("weather_records.json", "r", encoding='utf-8') as f:
                loaded = json.load(f)
            for rec in loaded:
                records.append(rec)
                tree.insert('', tk.END, values=(
                    rec["Дата"],
                    rec["Температура"],
                    rec["Описание"],
                    rec["Осадки"]
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")

# Загружаем при старте
load_from_json()

# Кнопки сохранения
tk.Button(root, text="Сохранить в JSON", command=save_to_json).grid(row=10, column=0, padx=5, pady=10)

# Запуск
root.mainloop()
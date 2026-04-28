import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# ---------- Конфигурация ----------
API_KEY = "ВАШ_API_КЛЮЧ"  # Получить на https://app.exchangerate-api.com/sign-up
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"
HISTORY_FILE = "history.json"

VALID_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY", "TRY", "KZT", "UAH", "CHF"]

# ---------- Загрузка / сохранение истории ----------
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

# ---------- Получение курса ----------
def get_exchange_rate(from_curr, to_curr):
    try:
        response = requests.get(BASE_URL + from_curr)
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"].get(to_curr)
        else:
            messagebox.showerror("API Error", "Не удалось получить курсы. Проверьте API-ключ.")
            return None
    except Exception as e:
        messagebox.showerror("Connection Error", f"Ошибка сети: {e}")
        return None

# ---------- Конвертация ----------
def convert():
    try:
        amount = float(entry_amount.get())
        if amount <= 0:
            messagebox.showwarning("Ошибка ввода", "Сумма должна быть положительным числом")
            return
    except ValueError:
        messagebox.showwarning("Ошибка ввода", "Введите числовое значение суммы")
        return

    from_curr = combo_from.get()
    to_curr = combo_to.get()

    rate = get_exchange_rate(from_curr, to_curr)
    if rate is None:
        return

    result = amount * rate
    result_label.config(text=f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}")

    # Сохраняем в историю
    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_curr,
        "to": to_curr,
        "amount": amount,
        "rate": rate,
        "result": result
    }
    history = load_history()
    history.append(record)
    save_history(history)

    update_history_table()

# ---------- Обновление таблицы истории ----------
def update_history_table():
    for row in tree.get_children():
        tree.delete(row)
    history = load_history()
    for entry in history[-10:]:  # последние 10 записей
        tree.insert("", tk.END, values=(
            entry["date"],
            entry["from"],
            entry["to"],
            entry["amount"],
            f"{entry['rate']:.4f}",
            f"{entry['result']:.2f}"
        ))

# ---------- Создание GUI ----------
root = tk.Tk()
root.title("Currency Converter")
root.geometry("800x500")
root.resizable(False, False)

# Верхняя рамка с вводом
frame_top = ttk.LabelFrame(root, text="Конвертация", padding=10)
frame_top.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_top, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_amount = ttk.Entry(frame_top, width=15)
entry_amount.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_top, text="Из валюты:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
combo_from = ttk.Combobox(frame_top, values=VALID_CURRENCIES, width=8)
combo_from.set("USD")
combo_from.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(frame_top, text="В валюту:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
combo_to = ttk.Combobox(frame_top, values=VALID_CURRENCIES, width=8)
combo_to.set("EUR")
combo_to.grid(row=0, column=5, padx=5, pady=5)

btn_convert = ttk.Button(frame_top, text="Конвертировать", command=convert)
btn_convert.grid(row=0, column=6, padx=10, pady=5)

result_label = ttk.Label(frame_top, text="", font=("Arial", 10, "bold"))
result_label.grid(row=1, column=0, columnspan=7, pady=10)

# Нижняя рамка с историей
frame_bottom = ttk.LabelFrame(root, text="История конвертаций", padding=10)
frame_bottom.pack(fill="both", expand=True, padx=10, pady=10)

columns = ("Дата", "Из", "В", "Сумма", "Курс", "Результат")
tree = ttk.Treeview(frame_bottom, columns=columns, show="headings", height=12)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

scrollbar = ttk.Scrollbar(frame_bottom, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Загружаем историю при старте
update_history_table()

root.mainloop()

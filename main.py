
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

API_KEY = "47e84c82d2b2790697b1fa51"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"
LOG_FILE = "history.json"

def get_history():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(record):
    data = get_history()
    data.append(record)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def update_table():
    for i in tree.get_children():
        tree.delete(i)
    for r in reversed(get_history()):
        tree.insert("", tk.END, values=(r["date"], r["from"], r["to"], r["amount"], r["res"]))

def run_conversion():
    f_curr = cb_from.get()
    t_curr = cb_to.get()
    
    if not f_curr or not t_curr:
        messagebox.showerror("Ошибка", "Выберите валюты в обоих списках")
        return
        
    val = ent_amount.get()
    try:
        val = float(val)
        if val <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Ошибка", "Введите положительное число")
        return

    try:
        response = requests.get(BASE_URL + f_curr, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("result") == "success":
            rate = data["conversion_rates"].get(t_curr)
            if rate:
                res = round(val * rate, 2)
                record = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "from": f_curr, "to": t_curr, "amount": val, "res": res
                }
                save_history(record)
                update_table()
                lbl_res.config(text=f"{res} {t_curr}")
            else:
                messagebox.showerror("Ошибка", "Валюта не найдена")
        else:
            messagebox.showerror("Ошибка API", data.get("error-type", "Неизвестная ошибка"))
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Связь", "Ошибка сети: проверьте интернет")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Детали: {str(e)}")

root = tk.Tk()
root.title("Currency Converter")
root.geometry("500x550")

currencies = ["USD", "EUR", "RUB", "BYN", "KZT", "GBP"]

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Из:").grid(row=0, column=0)
cb_from = ttk.Combobox(frame, values=currencies, width=10, state="readonly")
cb_from.grid(row=0, column=1, padx=5)

tk.Label(frame, text="В:").grid(row=0, column=2)
cb_to = ttk.Combobox(frame, values=currencies, width=10, state="readonly")
cb_to.grid(row=0, column=3, padx=5)

tk.Label(frame, text="Сумма:").grid(row=1, column=0, pady=10)
ent_amount = tk.Entry(frame, width=12)
ent_amount.grid(row=1, column=1, pady=10)

btn = tk.Button(frame, text="Конвертировать", command=run_conversion)
btn.grid(row=1, column=2, columnspan=2, sticky="we", padx=5)

lbl_res = tk.Label(root, text="0.00", font=("Arial", 16, "bold"))
lbl_res.pack(pady=10)

tree = ttk.Treeview(root, columns=("D", "F", "T", "A", "R"), show="headings", height=10)
tree.heading("D", text="Дата"); tree.heading("F", text="Из")
tree.heading("T", text="В"); tree.heading("A", text="Сумма"); tree.heading("R", text="Итог")

for col in ("D", "F", "T", "A", "R"):
    tree.column(col, width=90, anchor="center")

tree.pack(padx=10, pady=10, fill=tk.BOTH)
update_table()
root.mainloop()

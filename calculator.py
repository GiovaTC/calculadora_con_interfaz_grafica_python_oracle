import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# 👉 Importa tus funciones auxiliares (asegúrate de tener estos módulos en tu proyecto)
# from utils import safe_eval
# from db import insert_calculation, fetch_recent_calculations

# Para pruebas locales sin BD, puedes usar estas versiones dummy:
def safe_eval(expr):
    return eval(expr)

def insert_calculation(expr, result):
    print(f"Guardando en BD: {expr} = {result}")

def fetch_recent_calculations(limit=30):
    return [
        (1, "2+2", "4", datetime.now()),
        (2, "5*3", "15", datetime.now()),
    ]


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora con Oracle")

        # Display
        self.display_var = tk.StringVar()
        display_entry = ttk.Entry(self, textvariable=self.display_var, font=("Arial", 16))
        display_entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Botones de la calculadora
        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
            ("C", 5, 0)
        ]

        for (text, row, col) in buttons:
            btn = ttk.Button(self, text=text, command=lambda t=text: self._on_button_click(t))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Historial
        lbl = ttk.Label(self, text="Historial (Oracle):")
        lbl.grid(row=0, column=4, padx=10, pady=10)

        self.history_lb = tk.Listbox(self, height=25, width=45)
        self.history_lb.grid(row=1, column=4, rowspan=6, padx=(10, 10), pady=10, sticky="nsew")
        self.history_lb.bind("<Double-Button-1>", self._on_history_double_click)

        # Cargar historial inicial
        self._load_history()

    def _on_button_click(self, label):
        if label == "C":
            self.display_var.set("")
        elif label == "=":
            expr = self.display_var.get().strip()
            if not expr:
                return
            try:
                result = safe_eval(expr)
                # Formatear resultado
                if isinstance(result, float) and result.is_integer():
                    result_str = str(int(result))
                else:
                    result_str = str(result)
                # Mostrar en display
                self.display_var.set(result_str)
                # Guardar en BD
                try:
                    insert_calculation(expr, result_str)
                except Exception as db_e:
                    messagebox.showwarning("BD", f"Error guardando en BD: {db_e}")
                # Actualizar historial
                self._load_history()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo evaluar la expresión:\n{e}")
        else:
            cur = self.display_var.get()
            new = cur + label
            self.display_var.set(new)

    def _load_history(self):
        try:
            rows = fetch_recent_calculations(limit=30)
            self.history_lb.delete(0, tk.END)
            for r in rows:
                _id, expr, result, created = r
                created_str = created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(created, datetime) else str(created)
                line = f"[{_id}] {created_str} — {expr} = {result}"
                self.history_lb.insert(tk.END, line)
        except Exception as e:
            self.history_lb.delete(0, tk.END)
            self.history_lb.insert(tk.END, f"Error cargando historial: {e}")

    def _on_history_double_click(self, event):
        sel = self.history_lb.curselection()
        if not sel:
            return
        text = self.history_lb.get(sel[0])
        try:
            parts = text.split("—", 1)
            if len(parts) >= 2:
                right = parts[1].strip()
                expr_part = right.rsplit("=", 1)[0].strip()
                self.display_var.set(expr_part)
        except Exception:
            pass


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()

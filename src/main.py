# src/main.py
import tkinter as tk
from gui.app import HTSEmailGeneratorApp


def main():
    root = tk.Tk()
    app = HTSEmailGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

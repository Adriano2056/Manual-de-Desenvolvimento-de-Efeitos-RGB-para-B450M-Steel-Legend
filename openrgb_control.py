import os
import importlib.util
import threading
import time
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

# ======================================================
#  CONFIGURAÇÃO E CONEXÃO
# ======================================================
OPENRGB_ADDRESS = "127.0.0.1"
OPENRGB_PORT = 6742
CLIENT_NAME = "Modular_RGB_Controller"

try:
    client = OpenRGBClient(address=OPENRGB_ADDRESS, port=OPENRGB_PORT, name=CLIENT_NAME)
except Exception as e:
    messagebox.showerror("OpenRGB", f"Erro ao conectar no OpenRGB:\n{e}")
    raise SystemExit(1)

# Detecta dispositivos
devices = client.devices
main_device = None
ram_devices = []
for d in devices:
    name = d.name.lower()
    if "ene dram" in name or "ram" in name:
        ram_devices.append(d)
    elif "motherboard" in name or "header" in name:
        main_device = d
if not main_device:
    main_device = devices[0]

# ======================================================
#  MAPA DE LEDS (estático)
# ======================================================
led_map = {
    "nada": 0,
    "nada 2": 1,
    "chipset 1": 2,
    "chipset 2": 3,
    "chipset 3": 4,
    "chipset 4": 5,
    "chipset 5": 6,
    "chipset 6": 7,
    "chipset 7": 8,
    "chipset 8": 9,
    "backplate 1": 10,
    "backplate 2": 11,
    "backplate 3": 12,
    "backplate 4": 13,
    "backplate 5": 14,
    "backplate 6": 15,
    "backplate 7": 16,
    "backplate 8": 17,
    "backplate 9": 18,
    "backplate 10": 19,
    "saida argb 3 pino da placa mae ligou os cooler": 20
}

# ======================================================
#  FUNÇÕES BÁSICAS DE LED
# ======================================================
io_lock = threading.Lock()
speed_value = 5.0

def get_delay(base_delay=0.1):
    val = max(1, min(speed_value, 10))
    return base_delay * (11 - val) / 5

def set_speed(v):
    global speed_value
    try:
        speed_value = float(v)
    except:
        pass

def grb_invert(r, g, b):
    return g, r, b

def set_led(name, r, g, b):
    invert = "chipset" in name.lower()
    if invert:
        r, g, b = grb_invert(r, g, b)
    idx = led_map.get(name)
    if idx is None:
        return
    with io_lock:
        try:
            main_device.leds[idx].set_color(RGBColor(r, g, b))
        except:
            pass

def set_leds(names, r, g, b):
    for n in names:
        set_led(n, r, g, b)

# ======================================================
#  SISTEMA DE EFEITOS EXTERNOS (MODULAR)
# ======================================================
effects_dir = "effects"
effect_threads = []
active_effects = {}
effect_categories = ["Backplate", "Chipset", "Cooler", "Memory_RAM", "Global_Effects"]

def load_effects():
    loaded = {cat: [] for cat in effect_categories}
    if not os.path.exists(effects_dir):
        os.makedirs(effects_dir)
        for cat in effect_categories:
            os.makedirs(os.path.join(effects_dir, cat), exist_ok=True)
        return loaded

    for cat in effect_categories:
        cat_path = os.path.join(effects_dir, cat)
        os.makedirs(cat_path, exist_ok=True)
        for file in os.listdir(cat_path):
            if file.endswith(".py"):
                path = os.path.join(cat_path, file)
                spec = importlib.util.spec_from_file_location(file[:-3], path)
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                    effect_name = getattr(mod, "EFFECT_NAME", file[:-3])
                    loaded[cat].append({"name": effect_name, "module": mod})
                except Exception as e:
                    print(f"Erro ao carregar efeito {file}: {e}")
    return loaded

effects = load_effects()

# ======================================================
#  EXECUÇÃO DE EFEITOS (AGORA COM ESCOLHA DE COR)
# ======================================================
def start_effect(category, effect_obj):
    name = f"{category}:{effect_obj['name']}"
    if name in active_effects:
        return

    # --- 🔹 Pergunta cores, se o efeito solicitar ---
    piece_color = None
    bg_color = None
    if hasattr(effect_obj["module"], "ASK_COLORS") and effect_obj["module"].ASK_COLORS:
        piece_color = colorchooser.askcolor(title="Escolha a cor da peça")[0]
        bg_color = colorchooser.askcolor(title="Escolha a cor de fundo")[0]
        if not piece_color or not bg_color:
            return  # Usuário cancelou

    # --- Contexto completo passado ao efeito ---
    ctx = {
        "leds": get_led_list(category),
        "set_led": set_led,
        "delay": get_delay,
        "running": lambda: name in active_effects,
        "ram_devices": ram_devices,
        "main_device": main_device,
        "client": client,
        "set_leds": set_leds,
        "piece_color": tuple(map(int, piece_color)) if piece_color else None,
        "bg_color": tuple(map(int, bg_color)) if bg_color else None
    }

    t = threading.Thread(target=effect_obj["module"].run_effect, args=(ctx,), daemon=True)
    active_effects[name] = t
    t.start()

def stop_effect(category, effect_obj):
    name = f"{category}:{effect_obj['name']}"
    if name in active_effects:
        del active_effects[name]

def get_led_list(category):
    if category == "Backplate":
        return [f"backplate {i}" for i in range(1, 11)]
    elif category == "Chipset":
        return [f"chipset {i}" for i in range(1, 9)]
    elif category == "Cooler":
        return ["saida argb 3 pino da placa mae ligou os cooler"]
    elif category == "Memory_RAM":
        leds = []
        for ch in range(1, 5):
            for i in range(1, 9):
                leds.append(f"ram{ch}_{i}")
        return leds
    elif category == "Global_Effects":
        leds = []
        leds += [f"backplate {i}" for i in range(1, 11)]
        leds += [f"ram{ch}_{i}" for ch in range(1, 5) for i in range(1, 9)]
        leds += [f"chipset {i}" for i in range(1, 9)]
        return leds
    return []

# ======================================================
#  CRIAÇÃO AUTOMÁTICA DAS PASTAS DE EFEITOS
# ======================================================
def ensure_effects_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    effects_dir = os.path.join(base_dir, "effects")
    categories = ["Backplate", "Chipset", "Cooler", "Memory_RAM", "Global_Effects"]

    os.makedirs(effects_dir, exist_ok=True)
    for cat in categories:
        os.makedirs(os.path.join(effects_dir, cat), exist_ok=True)
    return effects_dir

effects_path = ensure_effects_structure()
print(f"📁 Pasta de efeitos garantida em: {effects_path}")

# ======================================================
#  GUI TKINTER
# ======================================================
root = tk.Tk()
root.title("OpenRGB Modular Controller")
root.geometry("920x1100")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

def create_category_tab(category, effects_list):
    frame = tk.Frame(notebook)
    notebook.add(frame, text=category.replace("_", " "))

    tk.Label(frame, text=f"Efeitos para {category}", font=("Arial", 11, "bold")).pack(pady=6)
    if not effects_list:
        tk.Label(frame, text="(Nenhum efeito encontrado nesta categoria)").pack(pady=4)
    else:
        for eff in effects_list:
            frame_inner = tk.Frame(frame)
            frame_inner.pack(pady=2)
            tk.Button(frame_inner, text=f"Iniciar: {eff['name']}",
                      width=40, command=lambda e=eff: start_effect(category, e)).pack(side="left", padx=2)
            tk.Button(frame_inner, text="Parar", command=lambda e=eff: stop_effect(category, e)).pack(side="left", padx=2)

for cat in effects:
    create_category_tab(cat, effects[cat])

# Aba de controle geral
f_ctrl = tk.Frame(notebook)
notebook.add(f_ctrl, text="Controle Geral")
tk.Label(f_ctrl, text="Velocidade Global", font=("Arial", 10, "bold")).pack(pady=8)
tk.Scale(f_ctrl, from_=1, to=10, orient='horizontal', command=set_speed).pack()
tk.Label(f_ctrl, text="Adicione novos efeitos em /effects/<categoria>", font=("Arial", 9, "italic")).pack(pady=6)

def on_close():
    active_effects.clear()
    try:
        client.disconnect()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

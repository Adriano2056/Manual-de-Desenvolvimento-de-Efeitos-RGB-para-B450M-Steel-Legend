EFFECT_NAME = "Tetris Global Sincronizado"
ASK_COLORS = True

def run_effect(ctx):
    import time
    from openrgb.utils import RGBColor

    leds = ctx["leds"]
    ram_modules = ctx["ram_devices"]
    set_led = ctx["set_led"]
    delay = ctx["delay"]
    running = ctx["running"]

    # --- Cores escolhidas ---
    piece_color = ctx.get("piece_color", (0, 120, 255))
    bg_color = ctx.get("bg_color", (0, 0, 0))
    ...


    # ======================================================
    #  CONSTRUÇÃO DA ORDEM GLOBAL DE LEDs
    # ======================================================
    full_order = []

    # 1️⃣ Backplate (ordem direta)
    for n in leds:
        if "backplate" in n.lower():
            full_order.append(("main", n))

    # 2️⃣ Memórias RAM (8 LEDs por pente, até 4 canais)
    for idx, ram in enumerate(ram_modules):
        for i in range(min(8, len(ram.leds))):
            full_order.append(("ram", (idx, i)))

    # 3️⃣ Chipset (ordem anti-horária)
    chipset_order = [
        "chipset 2", "chipset 3", "chipset 5",
        "chipset 6", "chipset 7", "chipset 8",
        "chipset 4", "chipset 1"
    ]
    for n in chipset_order:
        full_order.append(("main", n))

    # ======================================================
    #  INICIALIZAÇÃO
    # ======================================================
    stack = [bg_color] * len(full_order)

    # Limpa tudo no início
    for kind, data in full_order:
        if kind == "main":
            set_led(data, *bg_color)
        else:
            ram_modules[data[0]].leds[data[1]].set_color(RGBColor(*bg_color))

    # ======================================================
    #  LOOP PRINCIPAL DO EFEITO
    # ======================================================
    while running():
        # Encontra o próximo LED livre (do fim para o início)
        target = next((i for i in range(len(stack) - 1, -1, -1) if stack[i] == bg_color), -1)

        # Se nenhum livre, reseta
        if target == -1:
            for kind, data in full_order:
                if kind == "main":
                    set_led(data, *bg_color)
                else:
                    ram_modules[data[0]].leds[data[1]].set_color(RGBColor(*bg_color))
            stack = [bg_color] * len(full_order)
            time.sleep(delay(0.5))
            continue

        # Simula a "queda" da peça até o LED alvo
        for pos in range(target + 1):
            if not running():
                return

            # Atualiza o fundo
            for i, (kind, data) in enumerate(full_order):
                r, g, b = stack[i]
                if kind == "main":
                    set_led(data, r, g, b)
                else:
                    ram_modules[data[0]].leds[data[1]].set_color(RGBColor(r, g, b))

            # Desenha a peça atual
            kind, data = full_order[pos]
            if kind == "main":
                set_led(data, *piece_color)
            else:
                ram_modules[data[0]].leds[data[1]].set_color(RGBColor(*piece_color))

            time.sleep(delay(0.05))

        # Fixa a peça no local
        stack[target] = piece_color
        kind, data = full_order[target]
        if kind == "main":
            set_led(data, *piece_color)
        else:
            ram_modules[data[0]].leds[data[1]].set_color(RGBColor(*piece_color))

        time.sleep(delay(0.15))

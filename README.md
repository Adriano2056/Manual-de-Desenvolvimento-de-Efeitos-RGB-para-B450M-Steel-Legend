💡 Manual de Desenvolvimento de Efeitos RGB para B450M Steel Legend

Este repositório contém o controlador modular OpenRGB desenvolvido para a ASRock B450M Steel Legend, permitindo criar e executar efeitos RGB personalizados diretamente pela interface Tkinter.

O sistema é totalmente modular: você pode adicionar, editar ou criar novos efeitos facilmente usando Python.

📘 Conteúdo do Manual

O manual (disponível em PDF no repositório) explica:

Todas as funções disponíveis no controlador e no contexto (ctx)

Fluxo interno de inicialização e execução dos efeitos

Estrutura completa de diretórios e boas práticas

Mapa visual dos LEDs da placa B450M Steel Legend

Exemplos de efeitos simples, intermediários e avançados

Explicação sobre o padrão de cor GRB utilizado na região do chipset

📄 Arquivo: Manual_Desenvolvimento_Efeitos_RGB_B450M_Steel_Legend_v2.pdf

⚙️ Como usar o controlador
1️⃣ Execute o controlador pela primeira vez

Baixe o repositório, abra o terminal na pasta onde está o arquivo e execute:

python openrgb_control.py


O programa irá:

Conectar ao servidor OpenRGB (certifique-se que ele está rodando com “Allow Remote Control” ativado).

Criar automaticamente as pastas necessárias dentro de effects/.

Exemplo de estrutura criada:

effects/
├── Backplate/
├── Chipset/
├── Cooler/
├── Memory_RAM/
└── Global_Effects/

2️⃣ Feche o programa

Após verificar que as pastas foram criadas corretamente, você pode fechar o openrgb_control.py.

3️⃣ Adicione um efeito

Coloque o arquivo do efeito desejado dentro da pasta correspondente.
Por exemplo, para o efeito Tetris Global, copie o arquivo tetris_global.py para:

effects/Global_Effects/

4️⃣ Execute novamente

Abra o programa outra vez (python openrgb_control.py) e vá até a aba “Global Effects” na interface.
O efeito Tetris Global Sincronizado aparecerá disponível para iniciar.

🧩 Criando seus próprios efeitos

Você pode criar novos efeitos em qualquer categoria (Backplate, Chipset, Cooler, Memory_RAM ou Global_Effects).

Um efeito deve conter, no mínimo:

EFFECT_NAME = "Meu Efeito"
ASK_COLORS = True

def run_effect(ctx):
    import time
    leds = ctx["leds"]
    set_led = ctx["set_led"]
    delay = ctx["delay"]
    running = ctx["running"]
    piece = ctx.get("piece_color") or (0, 150, 255)

    while running():
        for n in leds:
            set_led(n, *piece)
        time.sleep(delay(0.3))
        for n in leds:
            set_led(n, 0, 0, 0)
        time.sleep(delay(0.3))


📚 Consulte o manual em PDF para entender todas as chaves do ctx e funções auxiliares disponíveis.


🖥️ Mapa de LEDs da B450M Steel Legend

O controlador utiliza um mapa fixo que associa nomes lógicos a LEDs físicos da placa:

Região	LEDs disponíveis	Observação
Backplate	1–10	LEDs localizados no canto superior esquerdo
Chipset	1–8	Região inferior direita (usa esquema GRB)
Cooler ARGB	1	Saída ARGB de 3 pinos conectada ao cooler

⚙️ Nota: O chipset usa esquema de cor GRB (Green–Red–Blue) em vez de RGB.
O controlador inverte automaticamente essa ordem — use cores RGB normalmente no código.

🧠 Requisitos

OpenRGB (com “Allow Remote Control” ativado)

Python 3.8+

Biblioteca:

pip install openrgb-python

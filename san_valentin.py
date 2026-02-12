import tkinter as tk
import random
import math


NOMBRE = "Mi amor"

TITULO_VENTANA = "Para Victoria ♥"

PREGUNTA = f"{NOMBRE}, ¿quieres ser mi San Valentín? ♥"
SUBTEXTO = "Dime que si y te doy un beso ♥"

TEXTO_SI = "Sí ♥"
TEXTO_NO = "No!"

# Pantalla NO (si logra clickear)
NO_TITULO = "VERÁS QUE ME RESIENTO!!"
NO_SUBTEXTO = "Piénsalo bien Victoria! ):("
NO_BOTON_VOLVER = "Era bromimi, yo te amo y estoy obesionada contigo ♥"

# Pantalla SÍ
SI_TITULO = "Sabía que dirías que sí ♥"
SI_MENSAJE = f"{NOMBRE}, seamos pololos ♥"
SI_NOTA = "Te amo mas que nada en este mundo ♥"
SI_BOTON_CERRAR = "Cerrar ♥"



W, H = 720, 520

# Paleta blanco/rosado
BG_TOP = "#ffffff"
BG_BOTTOM = "#fff0f5"
ACCENT = "#ff4d6d"
ACCENT_2 = "#ff8fab"
TEXT = "#2b2b2b"
MUTED = "#7a7a7a"
CARD_BORDER = "#ffd1dc"

HEART_CHAR = "♥"
HEART_COLOR = "#ffffff"  # corazones blancos

# Separación mínima entre NO y el rectángulo del SÍ (sube si lo quieres más lejos)
MIN_SEPARACION = 75

# Margen para que NO no quede pegado a los bordes de la ventana
SCREEN_MARGIN = 12

random.seed()


def hex_to_rgb(hx: str):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(lerp(r1, r2, t))
    g = int(lerp(g1, g2, t))
    b = int(lerp(b1, b2, t))
    return rgb_to_hex((r, g, b))


def rects_intersect(a, b) -> bool:
    """a,b = (x1,y1,x2,y2)"""
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def inflate_rect(r, pad):
    return (r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad)


class ValentineApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TITULO_VENTANA)
        self.root.geometry(f"{W}x{H}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=W, height=H, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Animación
        self.hearts = []
        self.ticks = 0

        # UI state
        self.win_no = None
        self.no_btn = None
        self.yes_btn = None

        # Geometría para restricciones
        self.yes_rect = None          # rect exacto del botón SÍ
        self.no_size = (120, 48)      # se recalcula
        self.no_pos = (0, 0)          # (x,y) actual

        self.show_main()
        self.animate()
        self.root.mainloop()

    # ------------------ Fondo ------------------
    def draw_gradient(self):
        self.canvas.delete("bg")
        steps = 90
        for i in range(steps):
            t = i / (steps - 1)
            color = lerp_color(BG_TOP, BG_BOTTOM, t)
            y1 = int(i * H / steps)
            y2 = int((i + 1) * H / steps)
            self.canvas.create_rectangle(0, y1, W, y2, fill=color, outline=color, tags=("bg",))

    # ------------------ Hearts ------------------
    def spawn_heart(self):
        x = random.randint(20, W - 20)
        y = H + random.randint(10, 70)
        size = random.randint(12, 22)
        speed = random.uniform(0.9, 2.0)
        drift = random.uniform(-0.5, 0.5)

        h = self.canvas.create_text(
            x, y, text=HEART_CHAR, font=("Segoe UI", size),
            fill=HEART_COLOR, tags=("heart",)
        )
        g = self.canvas.create_text(
            x + 1, y + 1, text=HEART_CHAR, font=("Segoe UI", size),
            fill="#ffd1dc", tags=("heart",)
        )
        self.hearts.append({"h": h, "g": g, "x": x, "y": y, "speed": speed, "drift": drift})

    def animate(self):
        self.ticks += 1
        if self.ticks % 22 == 0 and len(self.hearts) < 70:
            self.spawn_heart()

        alive = []
        for item in self.hearts:
            item["y"] -= item["speed"]
            item["x"] += item["drift"]
            self.canvas.coords(item["h"], item["x"], item["y"])
            self.canvas.coords(item["g"], item["x"] + 1, item["y"] + 1)
            if item["y"] > -40:
                alive.append(item)
            else:
                self.canvas.delete(item["h"])
                self.canvas.delete(item["g"])
        self.hearts = alive
        self.root.after(16, self.animate)

    # ------------------ Helpers UI ------------------
    def clear_screen(self):
        self.canvas.delete("ui")
        self.root.unbind("<Motion>")
        self.win_no = None
        self.no_btn = None
        self.yes_btn = None
        self.yes_rect = None

    def draw_card(self):
        card_w, card_h = 560, 340
        x1 = (W - card_w) // 2
        y1 = (H - card_h) // 2
        x2 = x1 + card_w
        y2 = y1 + card_h

        self.canvas.create_rectangle(x1 + 8, y1 + 10, x2 + 8, y2 + 10,
                                     fill="#000000", outline="", stipple="gray25", tags=("ui",))
        self.canvas.create_rectangle(x1, y1, x2, y2,
                                     fill="white", outline=CARD_BORDER, width=2, tags=("ui",))
        return x1, y1, x2, y2

    def compute_button_rect(self, win_id, widget):
        # coords del window en el canvas (top-left anchor)
        x, y = self.canvas.coords(win_id)
        w = widget.winfo_width()
        h = widget.winfo_height()
        return (x, y, x + w, y + h)

    # ------------------ Pantallas ------------------
    def show_main(self):
        self.clear_screen()
        self.draw_gradient()

        x1, y1, x2, y2 = self.draw_card()

        self.canvas.create_text(
            W // 2, y1 + 70,
            text="Tengo una pregunta importante ♥",
            font=("Segoe UI Semibold", 22),
            fill=TEXT,
            tags=("ui",)
        )
        self.canvas.create_text(
            W // 2, y1 + 135,
            text=PREGUNTA,
            font=("Segoe UI", 22, "bold"),
            fill=ACCENT,
            tags=("ui",)
        )
        self.canvas.create_text(
            W // 2, y1 + 185,
            text=SUBTEXTO,
            font=("Segoe UI", 12),
            fill=MUTED,
            tags=("ui",)
        )

        # Botones
        self.yes_btn = tk.Button(
            self.root, text=TEXTO_SI,
            font=("Segoe UI Semibold", 14),
            bg=ACCENT, fg="white",
            activebackground=ACCENT_2, activeforeground="white",
            bd=0, padx=26, pady=10, cursor="hand2",
            command=self.show_yes
        )
        self.no_btn = tk.Button(
            self.root, text=TEXTO_NO,
            font=("Segoe UI Semibold", 13),
            bg="#f5f5f5", fg=TEXT,
            activebackground="#eeeeee", activeforeground=TEXT,
            bd=0, padx=24, pady=10, cursor="hand2",
            command=self.show_no
        )

        yes_x, yes_y = W // 2 - 125, y1 + 235
        no_x, no_y = W // 2 + 40, y1 + 235

        win_yes = self.canvas.create_window(yes_x, yes_y, window=self.yes_btn, anchor="nw", tags=("ui",))
        self.win_no = self.canvas.create_window(no_x, no_y, window=self.no_btn, anchor="nw", tags=("ui",))
        self.no_pos = (no_x, no_y)

        # Forzar layout para obtener tamaños reales
        self.root.update_idletasks()

        # Rect exacto del SÍ
        self.yes_rect = self.compute_button_rect(win_yes, self.yes_btn)

        # Tamaño real del NO
        self.no_size = (self.no_btn.winfo_width(), self.no_btn.winfo_height())

        # Activar huida del NO (por toda la ventana)
        self.root.bind("<Motion>", self.on_mouse_move)

    def show_no(self):
        self.clear_screen()
        self.draw_gradient()
        self.draw_card()

        self.canvas.create_text(W // 2, H // 2 - 40, text=NO_TITULO,
                                font=("Segoe UI Semibold", 24), fill=TEXT, tags=("ui",))
        self.canvas.create_text(W // 2, H // 2 + 15, text=NO_SUBTEXTO,
                                font=("Segoe UI", 12), fill=MUTED, tags=("ui",))

        btn_back = tk.Button(
            self.root, text=NO_BOTON_VOLVER,
            font=("Segoe UI Semibold", 12),
            bg=ACCENT, fg="white",
            activebackground=ACCENT_2, activeforeground="white",
            bd=0, padx=18, pady=10, cursor="hand2",
            command=self.show_main
        )
        self.canvas.create_window(W // 2, H // 2 + 95, window=btn_back, anchor="center", tags=("ui",))

        for _ in range(10):
            self.spawn_heart()

    def show_yes(self):
        self.clear_screen()
        self.draw_gradient()
        self.draw_card()

        self.canvas.create_text(W // 2, H // 2 - 55, text=SI_TITULO,
                                font=("Segoe UI Semibold", 24), fill=TEXT, tags=("ui",))
        self.canvas.create_text(W // 2, H // 2 + 5, text=SI_MENSAJE,
                                font=("Segoe UI", 18, "bold"), fill=ACCENT, tags=("ui",))
        self.canvas.create_text(W // 2, H // 2 + 55, text=SI_NOTA,
                                font=("Segoe UI", 11), fill=MUTED, tags=("ui",))

        btn_close = tk.Button(
            self.root, text=SI_BOTON_CERRAR,
            font=("Segoe UI Semibold", 12),
            bg=ACCENT, fg="white",
            activebackground=ACCENT_2, activeforeground="white",
            bd=0, padx=18, pady=10, cursor="hand2",
            command=self.root.destroy
        )
        self.canvas.create_window(W // 2, H // 2 + 110, window=btn_close, anchor="center", tags=("ui",))

        for _ in range(18):
            self.spawn_heart()

    # ------------------ NO que huye (toda la ventana + anti-overlap/cercanía) ------------------
    def on_mouse_move(self, event):
        if not self.win_no or not self.yes_rect:
            return

        bx, by = self.no_pos
        bw, bh = self.no_size
        mx, my = event.x, event.y

        dist = math.hypot((mx - (bx + bw / 2)), (my - (by + bh / 2)))
        if dist < 95:
            self.move_no_anywhere()

    def move_no_anywhere(self):
        bw, bh = self.no_size
        forbidden = inflate_rect(self.yes_rect, MIN_SEPARACION)

        # área válida: toda la pantalla, menos márgenes
        min_x = SCREEN_MARGIN
        min_y = SCREEN_MARGIN
        max_x = W - SCREEN_MARGIN - bw
        max_y = H - SCREEN_MARGIN - bh

        # Rechazo por overlap o cercanía al SÍ
        for _ in range(120):
            nx = random.randint(min_x, max_x)
            ny = random.randint(min_y, max_y)
            no_rect = (nx, ny, nx + bw, ny + bh)

            if rects_intersect(no_rect, forbidden):
                continue

            self.no_pos = (nx, ny)
            self.canvas.coords(self.win_no, nx, ny)

            if random.random() < 0.55:
                self.spawn_heart()
            return

        # Fallback: manda NO a la esquina más lejana del SÍ
        yx1, yy1, yx2, yy2 = self.yes_rect
        yc = ((yx1 + yx2) / 2, (yy1 + yy2) / 2)
        corners = [
            (min_x, min_y),
            (max_x, min_y),
            (min_x, max_y),
            (max_x, max_y),
        ]
        best = None
        best_d = -1
        for cx, cy in corners:
            d = math.hypot(cx - yc[0], cy - yc[1])
            if d > best_d:
                best_d = d
                best = (cx, cy)

        self.no_pos = best
        self.canvas.coords(self.win_no, best[0], best[1])


if __name__ == "__main__":
    ValentineApp()

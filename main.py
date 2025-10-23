import customtkinter as ctk
import tkinter as tk
from math import sqrt
import heapq

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

APP_TITLE = "Aplicación de Ruta Más Corta"
APP_W, APP_H = 1200, 700
MIN_W, MIN_H = 1000, 650

panel_color   = "#E9ECEF"
section_color = "#F7F9FC"
button_color  = "#2563EB"
text_color    = "#0B132B"
font_family   = "Poppins"
button_font_size = 14

node_fill_color    = "#6EC1E4"
node_outline_color = "#0F172A"
edge_color         = "#1E3A8A"
edge_text_color    = "#B91C1C"


highlight_main_color  = "#10B981"   
highlight_glow_color  = "#A7F3D0"   
highlight_line_w      = 5
highlight_glow_w      = 9


nodos = {}    
aristas = []  
selected_node = None
dragging_node = None
radio_base = 22


highlight_items = [] 
last_path_nodes = []  


def get_node_at_pos(x, y):
    for node_id, data in nodos.items():
        nx, ny = data["x"], data["y"]
        r = data["radio"]
        if (nx - r <= x <= nx + r) and (ny - r <= y <= ny + r):
            return node_id
    return None

def distance_point_to_line(px, py, x1, y1, x2, y2):
    line_mag = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if line_mag < 1e-6:
        return sqrt((px - x1) ** 2 + (py - y1) ** 2)
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
    u = max(min(u, 1), 0)
    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    return sqrt((px - ix) ** 2 + (py - iy) ** 2)

def get_edge_at_pos(x, y, threshold=6):
    closest = None
    best_d = float("inf")
    for edge in aristas:
        x1, y1 = nodos[edge["nodo1"]]["x"], nodos[edge["nodo1"]]["y"]
        x2, y2 = nodos[edge["nodo2"]]["x"], nodos[edge["nodo2"]]["y"]
        d = distance_point_to_line(x, y, x1, y1, x2, y2)
        if d < threshold and d < best_d:
            best_d = d
            closest = edge
    return closest


def crear_o_seleccionar_nodo(event):
    global dragging_node
    node_id = get_node_at_pos(event.x, event.y)
    if node_id is not None:
        dragging_node = node_id
    else:
        node_id = len(nodos) + 1
        x, y = event.x, event.y
        r = radio_base
        oval = graph_canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=node_fill_color, outline=node_outline_color, width=2,
            tags=f"node{node_id}"
        )
        text = graph_canvas.create_text(
            x, y, text=str(node_id), font=(font_family, 12, "bold"),
            fill=text_color, tags=f"node{node_id}"
        )
        nodos[node_id] = {
            "x": x, "y": y, "oval": oval, "text": text,
            "nombre": str(node_id), "radio": r
        }

        graph_canvas.tag_raise(oval)
        graph_canvas.tag_raise(text)

        actualizar_info()


def start_arista(event):
    global selected_node
    node_id = get_node_at_pos(event.x, event.y)
    if node_id is None:
        return
    if selected_node is None:
        selected_node = node_id
        graph_canvas.itemconfig(nodos[node_id]["oval"], outline="#E11D48", width=3)
    else:
        nodo1, nodo2 = selected_node, node_id
        graph_canvas.itemconfig(nodos[selected_node]["oval"], outline=node_outline_color, width=2)
        selected_node = None
        if nodo1 == nodo2:
            return

        x1, y1 = nodos[nodo1]["x"], nodos[nodo1]["y"]
        x2, y2 = nodos[nodo2]["x"], nodos[nodo2]["y"]
        line = graph_canvas.create_line(x1, y1, x2, y2, width=2.5, fill=edge_color)

        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        text_label = graph_canvas.create_text(
            mx, my - 10, text="1.0",
            font=(font_family, 14, "bold"),
            fill=edge_text_color
        )
        aristas.append({
            "line": line, "text": text_label,
            "nodo1": nodo1, "nodo2": nodo2, "peso": 1.0,
            "glow_line": None
        })
        actualizar_info()

def drag_node(event):
    global dragging_node
    if dragging_node is None:
        return
    nodos[dragging_node]["x"] = event.x
    nodos[dragging_node]["y"] = event.y
    r = nodos[dragging_node]["radio"]
    graph_canvas.coords(nodos[dragging_node]["oval"], event.x - r, event.y - r, event.x + r, event.y + r)
    graph_canvas.coords(nodos[dragging_node]["text"], event.x, event.y)

    for edge in aristas:
        x1, y1 = nodos[edge["nodo1"]]["x"], nodos[edge["nodo1"]]["y"]
        x2, y2 = nodos[edge["nodo2"]]["x"], nodos[edge["nodo2"]]["y"]
        graph_canvas.coords(edge["line"], x1, y1, x2, y2)
        if edge["glow_line"] is not None:
            graph_canvas.coords(edge["glow_line"], x1, y1, x2, y2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        graph_canvas.coords(edge["text"], mx, my - 10)
    graph_canvas.tag_raise(nodos[dragging_node]["oval"])
    graph_canvas.tag_raise(nodos[dragging_node]["text"])


def stop_drag(event):
    global dragging_node
    dragging_node = None

def ajustar_tamano_nodo(node_id):
    texto = nodos[node_id]["nombre"]
    base = radio_base
    nuevo_radio = max(base, 6 * len(texto))
    nodos[node_id]["radio"] = nuevo_radio
    x, y = nodos[node_id]["x"], nodos[node_id]["y"]
    graph_canvas.coords(nodos[node_id]["oval"], x - nuevo_radio, y - nuevo_radio, x + nuevo_radio, y + nuevo_radio)

def cambiar_nombre_nodo(event):
    node_id = get_node_at_pos(event.x, event.y)
    if node_id is None:
        return

    popup = ctk.CTkToplevel(app)
    popup.title("Cambiar nombre del nodo")
    popup.geometry("280x140")
    popup.transient(app)
    popup.grab_set()
    popup.focus_force()

    ctk.CTkLabel(popup, text="Nuevo nombre:", font=(font_family, 13)).pack(pady=(12, 6))
    entry = ctk.CTkEntry(popup)
    entry.pack(pady=4)
    entry.insert(0, nodos[node_id]["nombre"])
    entry.focus()

    error_label = ctk.CTkLabel(popup, text="", text_color="#DC2626")
    error_label.pack(pady=2)

    def guardar_nombre():
        nombre = entry.get().strip()
        if not nombre:
            error_label.configure(text="El nombre no puede estar vacío.")
            return
        for nid, data in nodos.items():
            if nid != node_id and data["nombre"] == nombre:
                error_label.configure(text="Ya existe un nodo con ese nombre.")
                return
        nodos[node_id]["nombre"] = nombre
        graph_canvas.itemconfig(nodos[node_id]["text"], text=nombre)
        ajustar_tamano_nodo(node_id)
        popup.destroy()
        actualizar_info()

    ctk.CTkButton(popup, text="Guardar", command=guardar_nombre, fg_color=button_color).pack(pady=10)

def cambiar_peso_arista(event):
    edge = get_edge_at_pos(event.x, event.y)
    if edge is None:
        return

    popup = ctk.CTkToplevel(app)
    popup.title("Cambiar peso")
    popup.geometry("280x150")
    popup.transient(app)
    popup.grab_set()
    popup.focus_force()

    ctk.CTkLabel(popup, text="Peso de la arista (> 0):", font=(font_family, 13)).pack(pady=(12, 6))
    entry = ctk.CTkEntry(popup)
    entry.pack(pady=4)
    entry.insert(0, str(edge["peso"]))
    entry.focus()

    error_label = ctk.CTkLabel(popup, text="", text_color="#DC2626")
    error_label.pack(pady=2)

    def guardar_peso():
        s = entry.get().strip()
        try:
            peso = float(s)
            if peso <= 0:
                raise ValueError
        except Exception:
            error_label.configure(text="Ingresa un número válido mayor que 0.")
            return
        edge["peso"] = peso
        graph_canvas.itemconfig(edge["text"], text=str(peso))
        popup.destroy()
        actualizar_info()

    ctk.CTkButton(popup, text="Guardar", command=guardar_peso, fg_color=button_color).pack(pady=10)


def resolver_nodo(valor):
    if not valor:
        return None
    if valor.isdigit():
        nid = int(valor)
        if nid in nodos:
            return nid
    for nid, data in nodos.items():
        if data["nombre"] == valor:
            return nid
    return None

def construir_grafo():
    g = {nid: [] for nid in nodos.keys()}
    for e in aristas:
        a, b, w = e["nodo1"], e["nodo2"], e["peso"]
        g[a].append((b, w))
        g[b].append((a, w))
    return g

def dijkstra(origen, destino):
    g = construir_grafo()
    dist = {v: float("inf") for v in g}
    prev = {v: None for v in g}
    dist[origen] = 0.0
    pq = [(0.0, origen)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        if u == destino:
            break
        for v, w in g[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dist[destino] == float("inf"):
        return None, None
    camino = []
    cur = destino
    while cur is not None:
        camino.append(cur)
        cur = prev[cur]
    camino.reverse()
    return camino, dist[destino]

def encontrar_arista_entre(a, b):
    for e in aristas:
        if (e["nodo1"] == a and e["nodo2"] == b) or (e["nodo1"] == b and e["nodo2"] == a):
            return e
    return None

def restaurar_estilos():
    global highlight_items, last_path_nodes
    for e in aristas:
        graph_canvas.itemconfig(e["line"], fill=edge_color, width=2.5)
        if e.get("glow_line"):
            graph_canvas.delete(e["glow_line"])
            e["glow_line"] = None
    highlight_items.clear()
    last_path_nodes = []

def resaltar_camino(camino):
    if not camino or len(camino) < 2:
        return
    for i in range(len(camino) - 1):
        a, b = camino[i], camino[i + 1]
        e = encontrar_arista_entre(a, b)
        if e is None:
            continue
        x1, y1 = nodos[e["nodo1"]]["x"], nodos[e["nodo1"]]["y"]
        x2, y2 = nodos[e["nodo2"]]["x"], nodos[e["nodo2"]]["y"]

        glow = graph_canvas.create_line(x1, y1, x2, y2, width=highlight_glow_w, fill=highlight_glow_color)
        graph_canvas.tag_lower(glow, e["line"])  
        e["glow_line"] = glow
   
        graph_canvas.itemconfig(e["line"], fill=highlight_main_color, width=highlight_line_w)


app = ctk.CTk()
app.title(APP_TITLE)
app.geometry(f"{APP_W}x{APP_H}")
app.minsize(MIN_W, MIN_H)
app.grid_columnconfigure(0, weight=1, uniform="column")
app.grid_columnconfigure(1, weight=2, uniform="column")
app.grid_rowconfigure(0, weight=1)


control_frame = ctk.CTkFrame(app, corner_radius=20, fg_color=panel_color)
control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
control_frame.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(control_frame, text="Panel de Control", font=(font_family, 22, "bold"), text_color=text_color)\
    .pack(pady=(20, 10))


graph_section = ctk.CTkFrame(control_frame, fg_color=section_color, corner_radius=15)
graph_section.pack(fill="x", padx=15, pady=(10, 15))
ctk.CTkLabel(graph_section, text="Configuración del Grafo", font=(font_family, 16, "bold"),
             text_color=text_color).pack(pady=10)
clear_button = ctk.CTkButton(graph_section, text="Limpiar Grafo", height=45, fg_color="#F59E0B",
                             hover_color="#FBBF24", font=(font_family, button_font_size))
clear_button.pack(pady=(5, 15))


route_section = ctk.CTkFrame(control_frame, fg_color=section_color, corner_radius=15)
route_section.pack(fill="x", padx=15, pady=(10, 15))
ctk.CTkLabel(route_section, text="Ruta Más Corta", font=(font_family, 16, "bold"),
             text_color=text_color).pack(pady=10)

start_entry = ctk.CTkEntry(route_section, placeholder_text="Nodo inicio (id o nombre)")
start_entry.pack(pady=4)
end_entry = ctk.CTkEntry(route_section, placeholder_text="Nodo fin (id o nombre)")
end_entry.pack(pady=4)

def calcular_ruta():
    restaurar_estilos()
    s_ini = start_entry.get().strip()
    s_fin = end_entry.get().strip()

    ini = resolver_nodo(s_ini)
    fin = resolver_nodo(s_fin)
    if ini is None or fin is None:
        route_info_label.configure(text="Nodo inicio o fin inválido (no existe).")
        return
    if ini == fin:
        route_info_label.configure(text="Inicio y fin son el mismo nodo.")
        return
    if not aristas:
        route_info_label.configure(text="No hay aristas en el grafo.")
        return

    camino, total = dijkstra(ini, fin)
    if camino is None:
        route_info_label.configure(text="No existe camino entre los nodos.")
        return

    nombres = " → ".join(nodos[n]["nombre"] for n in camino)
    route_info_label.configure(text=f"Ruta: {nombres}   |   Distancia total: {total:.3f}")
    resaltar_camino(camino)

ctk.CTkButton(route_section, text="Calcular", command=calcular_ruta, fg_color=button_color)\
    .pack(pady=6)

route_info_label = ctk.CTkLabel(route_section, text="", font=(font_family, 13), text_color="#111111", justify="left")
route_info_label.pack(pady=(6, 10))

info_section = ctk.CTkFrame(control_frame, fg_color=section_color, corner_radius=15)
info_section.pack(fill="x", padx=15, pady=(10, 15))
ctk.CTkLabel(info_section, text="Información del Grafo", font=(font_family, 16, "bold"),
             text_color=text_color).pack(pady=10)
info_text = tk.Text(info_section, height=9, width=35, font=(font_family, 12))
info_text.pack(pady=(0, 8))

def actualizar_info():
    info_text.delete("1.0", tk.END)
    info_text.insert(tk.END, f"Nodos: {len(nodos)}\n")
    info_text.insert(tk.END, f"Aristas: {len(aristas)}\n\n")
    info_text.insert(tk.END, "Nodos:\n")
    for nid, data in nodos.items():
        info_text.insert(tk.END, f"  {nid}: {data['nombre']}\n")
    info_text.insert(tk.END, "\nAristas:\n")
    for e in aristas:
        info_text.insert(tk.END, f"  {nodos[e['nodo1']]['nombre']} ↔ {nodos[e['nodo2']]['nombre']}: {e['peso']}\n")

ctk.CTkButton(info_section, text="Actualizar Info", command=actualizar_info, fg_color=button_color)\
    .pack(pady=5)

graph_frame = ctk.CTkFrame(app, corner_radius=20, fg_color="#F0F4F8")
graph_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
graph_frame.grid_rowconfigure(1, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(graph_frame, text="Visualización del Grafo", font=(font_family, 20, "bold"),
             text_color=text_color).grid(row=0, column=0, pady=(15, 0))

graph_canvas = tk.Canvas(graph_frame, bg="#E2E8F0", highlightthickness=0)
graph_canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)


guide_group = {"bg": None, "text": None}

def draw_guide():
    padding = 14
    w = graph_canvas.winfo_width()
    h = graph_canvas.winfo_height()
    if w <= 0 or h <= 0:
        app.after(50, draw_guide)
        return

    guide_text = (
        "Guía de uso:\n"
        "• Click izquierdo: crear / mover nodo\n"
        "• Click derecho: crear arista\n"
        "• Doble click izquierdo: renombrar nodo\n"
        "• Rueda del mouse: cambiar peso de conexión"
    )

   
    if guide_group["text"] is None:
        t = graph_canvas.create_text(0, 0, text=guide_text, anchor="nw",
                                     font=(font_family, 11),
                                     fill="#0B132B")
        guide_group["text"] = t
    else:
        t = guide_group["text"]
        graph_canvas.itemconfig(t, text=guide_text)

    bbox = graph_canvas.bbox(t) 
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = w - text_w - padding - 12
    y = h - text_h - padding - 12

 
    if guide_group["bg"] is None:
        try:
            r = graph_canvas.create_rectangle(0, 0, 0, 0, outline="#CBD5E1",
                                              fill="#FFFFFF", stipple="gray25", width=1)
        except tk.TclError:
            r = graph_canvas.create_rectangle(0, 0, 0, 0, outline="#CBD5E1",
                                              fill="#FFFFFF", width=1)
        guide_group["bg"] = r

    r = guide_group["bg"]
    graph_canvas.coords(r, x - 10, y - 8, x + text_w + 10, y + text_h + 8)
    graph_canvas.tag_lower(r)
    graph_canvas.coords(t, x, y)

graph_canvas.bind("<Configure>", lambda e: draw_guide())


graph_canvas.bind("<Button-1>", crear_o_seleccionar_nodo)
graph_canvas.bind("<B1-Motion>", drag_node)
graph_canvas.bind("<ButtonRelease-1>", stop_drag)

graph_canvas.bind("<Button-3>", start_arista)
graph_canvas.bind("<Double-1>", cambiar_nombre_nodo)


graph_canvas.bind("<Button-2>", cambiar_peso_arista)


def limpiar_grafo():
    global nodos, aristas, selected_node, dragging_node
    restaurar_estilos()
    nodos.clear()
    aristas.clear()
    selected_node = None
    dragging_node = None
    graph_canvas.delete("all")
    draw_guide()
    route_info_label.configure(text="")
    actualizar_info()

clear_button.configure(command=limpiar_grafo)


app.after(150, draw_guide)

app.mainloop()

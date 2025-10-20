import customtkinter as ctk
import tkinter as tk
from math import sqrt


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Aplicación de Ruta Más Corta")
app.geometry("1200x700")
app.minsize(1000, 650)
app.grid_columnconfigure(0, weight=1, uniform="column")
app.grid_columnconfigure(1, weight=2, uniform="column")
app.grid_rowconfigure(0, weight=1)


panel_color = "#E0E0E0"
section_color = "#F5F5F5"
button_color = "#3B82F6"
text_color = "#111111"
font_family = "Poppins"
button_font_size = 14
entry_width = 300


node_fill_color = "#6EC1E4"  
node_outline_color = "#0F172A"  
edge_color = "#1E40AF"  
edge_text_color = "#B91C1C"  


nodos = {}  
aristas = []  
selected_node = None
dragging_node = None
radio_base = 22


def get_node_at_pos(x, y):
    for node_id, data in nodos.items():
        nx, ny = data["x"], data["y"]
        r = data["radio"]
        if (nx - r <= x <= nx + r) and (ny - r <= y <= ny + r):
            return node_id
    return None

def distance_point_to_line(px, py, x1, y1, x2, y2):
    line_mag = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if line_mag < 0.000001:
        return sqrt((px - x1)**2 + (py - y1)**2)
    u = ((px - x1)*(x2 - x1) + (py - y1)*(y2 - y1)) / (line_mag**2)
    u = max(min(u, 1), 0)
    ix = x1 + u*(x2 - x1)
    iy = y1 + u*(y2 - y1)
    return sqrt((px - ix)**2 + (py - iy)**2)

def get_edge_at_pos(x, y):
    for edge in aristas:
        x1, y1 = nodos[edge["nodo1"]]["x"], nodos[edge["nodo1"]]["y"]
        x2, y2 = nodos[edge["nodo2"]]["x"], nodos[edge["nodo2"]]["y"]
        if distance_point_to_line(x, y, x1, y1, x2, y2) < 6:
            return edge
    return None

# funciones para crear los nodos 
def crear_o_seleccionar_nodo(event):
    global nodos, dragging_node
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
        nodos[node_id] = {"x": x, "y": y, "oval": oval, "text": text, "nombre": str(node_id), "radio": r}

def start_arista(event):
    global selected_node
    node_id = get_node_at_pos(event.x, event.y)
    if node_id is not None:
        if selected_node is None:
            selected_node = node_id
            graph_canvas.itemconfig(nodos[node_id]["oval"], outline="#E11D48", width=3)
        else:
            nodo1, nodo2 = selected_node, node_id
            if nodo1 != nodo2:
                x1, y1 = nodos[nodo1]["x"], nodos[nodo1]["y"]
                x2, y2 = nodos[nodo2]["x"], nodos[nodo2]["y"]
                line = graph_canvas.create_line(x1, y1, x2, y2, width=2.5, fill=edge_color)

                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                text_label = graph_canvas.create_text(
                    mx, my - 10, text="1.0",
                    font=(font_family, 14, "bold"),
                    fill=edge_text_color
                )

                aristas.append({"line": line, "text": text_label, "nodo1": nodo1, "nodo2": nodo2, "peso": 1.0})

            graph_canvas.itemconfig(nodos[selected_node]["oval"], outline=node_outline_color, width=2)
            selected_node = None

def drag_node(event):
    global dragging_node
    if dragging_node is not None:
        nodos[dragging_node]["x"] = event.x
        nodos[dragging_node]["y"] = event.y
        r = nodos[dragging_node]["radio"]
        graph_canvas.coords(nodos[dragging_node]["oval"], event.x - r, event.y - r, event.x + r, event.y + r)
        graph_canvas.coords(nodos[dragging_node]["text"], event.x, event.y)

        for edge in aristas:
            x1, y1 = nodos[edge["nodo1"]]["x"], nodos[edge["nodo1"]]["y"]
            x2, y2 = nodos[edge["nodo2"]]["x"], nodos[edge["nodo2"]]["y"]
            graph_canvas.coords(edge["line"], x1, y1, x2, y2)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            graph_canvas.coords(edge["text"], mx, my - 10)

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
    if node_id is not None:
        popup = ctk.CTkToplevel(app)
        popup.title("Cambiar nombre del nodo")
        popup.geometry("250x120")
        popup.transient(app)
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Nuevo nombre:", font=(font_family, 13)).pack(pady=5)
        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)
        entry.insert(0, nodos[node_id]["nombre"])
        entry.focus()

        def guardar_nombre():
            nombre = entry.get().strip()
            if nombre:
                nodos[node_id]["nombre"] = nombre
                graph_canvas.itemconfig(nodos[node_id]["text"], text=nombre)
                ajustar_tamano_nodo(node_id)
            popup.destroy()

        ctk.CTkButton(popup, text="Guardar", command=guardar_nombre, fg_color=button_color).pack(pady=5)

def cambiar_peso_arista(event):
    edge = get_edge_at_pos(event.x, event.y)
    if edge is not None:
        popup = ctk.CTkToplevel(app)
        popup.title("Cambiar peso de la arista")
        popup.geometry("250x120")
        popup.transient(app)
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Peso de la arista:", font=(font_family, 13)).pack(pady=5)
        entry = ctk.CTkEntry(popup)
        entry.pack(pady=5)
        entry.insert(0, str(edge["peso"]))
        entry.focus()

        def guardar_peso():
            try:
                peso = float(entry.get())
                edge["peso"] = peso
                graph_canvas.itemconfig(edge["text"], text=str(peso))
                popup.destroy()
            except ValueError:
                pass

        ctk.CTkButton(popup, text="Guardar", command=guardar_peso, fg_color=button_color).pack(pady=5)


#panel izquierdo
control_frame = ctk.CTkFrame(app, corner_radius=20, fg_color=panel_color)
control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
control_frame.grid_columnconfigure(0, weight=1)

ctk.CTkLabel(control_frame, text="Panel de Control", font=(font_family, 22, "bold"), text_color=text_color).pack(pady=(20, 10))

#configurar el grafo
graph_section = ctk.CTkFrame(control_frame, fg_color=section_color, corner_radius=15)
graph_section.pack(fill="x", padx=15, pady=(10, 15))
ctk.CTkLabel(graph_section, text="Configuración del Grafo", font=(font_family, 16, "bold"), text_color=text_color).pack(pady=10)
clear_button = ctk.CTkButton(graph_section, text="Limpiar Grafo", height=45, fg_color="#F59E0B",
                             hover_color="#FBBF24", font=(font_family, button_font_size))
clear_button.pack(pady=(5, 15))

# ruta mas corta
route_section = ctk.CTkFrame(control_frame, fg_color=section_color, corner_radius=15)
route_section.pack(fill="x", padx=15, pady=(10, 15))
ctk.CTkLabel(route_section, text="Ruta Más Corta", font=(font_family, 16, "bold"), text_color=text_color).pack(pady=10)
start_entry = ctk.CTkEntry(route_section, placeholder_text="Nodo inicio")
start_entry.pack(pady=5)
end_entry = ctk.CTkEntry(route_section, placeholder_text="Nodo fin")
end_entry.pack(pady=5)

def calcular_ruta():
    inicio = start_entry.get().strip()
    fin = end_entry.get().strip()
    if inicio.isdigit() and fin.isdigit():
        inicio, fin = int(inicio), int(fin)
        if inicio in nodos and fin in nodos:
            message = f"Ruta simulada: {inicio} → {fin}"  
        else:
            message = "Nodo inicio o fin no existe"
    else:
        message = "Ingrese valores numéricos válidos"
    route_info_label.configure(text=message)

ctk.CTkButton(route_section, text="Calcular", command=calcular_ruta, fg_color=button_color).pack(pady=5)
route_info_label = ctk.CTkLabel(route_section, text="", font=(font_family, 13), text_color="#111111")
route_info_label.pack(pady=5)

#informacion del grafo
info_section = ctk.CTkFrame(control_frame, fg_color=section_color, corner_radius=15)
info_section.pack(fill="x", padx=15, pady=(10, 15))
ctk.CTkLabel(info_section, text="Información del Grafo", font=(font_family, 16, "bold"), text_color=text_color).pack(pady=10)
info_text = tk.Text(info_section, height=8, width=35, font=(font_family, 12))
info_text.pack(pady=5)

def actualizar_info():
    info_text.delete("1.0", tk.END)
    info_text.insert(tk.END, f"Nodos: {len(nodos)}\n")
    info_text.insert(tk.END, f"Aristas: {len(aristas)}\n\n")
    info_text.insert(tk.END, "Nodos:\n")
    for nid, data in nodos.items():
        info_text.insert(tk.END, f"  {nid}: {data['nombre']}\n")
    info_text.insert(tk.END, "\nAristas:\n")
    for e in aristas:
        info_text.insert(tk.END, f"  {e['nodo1']} → {e['nodo2']}: {e['peso']}\n")

ctk.CTkButton(info_section, text="Actualizar Info", command=actualizar_info, fg_color=button_color).pack(pady=5)

#panel del graf
graph_frame = ctk.CTkFrame(app, corner_radius=20, fg_color="#F0F4F8")
graph_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
graph_frame.grid_rowconfigure(0, weight=1)
graph_frame.grid_columnconfigure(0, weight=1)
ctk.CTkLabel(graph_frame, text="Visualización del Grafo", font=(font_family, 20, "bold"), text_color=text_color).pack(pady=15)
graph_canvas = tk.Canvas(graph_frame, bg="#E2E8F0", highlightthickness=0)
graph_canvas.pack(expand=True, fill="both", padx=20, pady=20)

#botones para crear los nodos y las aristas
graph_canvas.bind("<Button-1>", crear_o_seleccionar_nodo)
graph_canvas.bind("<Button-3>", start_arista)
graph_canvas.bind("<B1-Motion>", drag_node)
graph_canvas.bind("<ButtonRelease-1>", stop_drag)
graph_canvas.bind("<Double-1>", cambiar_nombre_nodo)
graph_canvas.bind("<Button-2>", cambiar_peso_arista)


def limpiar_grafo():
    global nodos, aristas, selected_node, dragging_node
    nodos.clear()
    aristas.clear()
    selected_node = None
    dragging_node = None
    graph_canvas.delete("all")

clear_button.configure(command=limpiar_grafo)


app.mainloop()

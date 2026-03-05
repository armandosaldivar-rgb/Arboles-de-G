import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq
import random
import string

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafos y Árboles Óptimos - Interactivo")
        self.root.geometry("1200x800")

        self.G = nx.Graph()                  # Grafo principal
        self.frecuencias = {}                # Para Huffman y OBST
        self.arbol = None                    # Árbol generado
        self.raiz = None
        self.arbol_type = None               # "mst", "obst", "huffman"
        self.obst_cost = None
        self.huffman_root = None
        self.pos = {}                        # Posiciones interactivas
        self.node_letters = iter(string.ascii_uppercase)  # Solo letras: A, B, C...
        self.selected_node = None
        self.dragging = False
        self.mode = tk.StringVar(value="Ninguno")

        # Panel izquierdo
        left_frame = ttk.Frame(root, padding=12)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Modos interactivos
        ttk.Label(left_frame, text="Modos (clic en canvas)", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
        modes_frame = ttk.Frame(left_frame)
        modes_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(modes_frame, text="Agregar Vértice", variable=self.mode, value="Add Node").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(modes_frame, text="Agregar Arista", variable=self.mode, value="Add Edge").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(modes_frame, text="Mover Vértice", variable=self.mode, value="Move Node").pack(side=tk.LEFT, padx=5)

        # Agregar vértice
        ttk.Label(left_frame, text="Agregar Vértice (tecla N)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10,0))
        nodo_frame = ttk.Frame(left_frame)
        nodo_frame.pack(fill=tk.X, pady=3)
        ttk.Label(nodo_frame, text="Nombre:").pack(side=tk.LEFT)
        self.entry_nodo = ttk.Entry(nodo_frame, width=12)
        self.entry_nodo.pack(side=tk.LEFT, padx=4)
        ttk.Label(nodo_frame, text="Frecuencia:").pack(side=tk.LEFT)
        self.entry_freq = ttk.Entry(nodo_frame, width=7)
        self.entry_freq.insert(0, "10")
        self.entry_freq.pack(side=tk.LEFT, padx=4)
        ttk.Button(nodo_frame, text="Agregar", command=self.agregar_nodo).pack(side=tk.LEFT, padx=4)

        # Agregar arista
        ttk.Label(left_frame, text="Agregar Arista (tecla E)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(12,0))
        arista_frame = ttk.Frame(left_frame)
        arista_frame.pack(fill=tk.X, pady=3)
        ttk.Label(arista_frame, text="Origen:").pack(side=tk.LEFT)
        self.combo_origen = ttk.Combobox(arista_frame, width=10, state="readonly")
        self.combo_origen.pack(side=tk.LEFT, padx=4)
        ttk.Label(arista_frame, text="Destino:").pack(side=tk.LEFT)
        self.combo_destino = ttk.Combobox(arista_frame, width=10, state="readonly")
        self.combo_destino.pack(side=tk.LEFT, padx=4)
        ttk.Label(arista_frame, text="Peso:").pack(side=tk.LEFT)
        self.entry_peso = ttk.Entry(arista_frame, width=6)
        self.entry_peso.insert(0, "5")
        self.entry_peso.pack(side=tk.LEFT, padx=4)
        ttk.Button(arista_frame, text="Agregar", command=self.agregar_arista).pack(side=tk.LEFT, padx=4)

        # Borrar todo
        ttk.Button(left_frame, text="Borrar Todo el Grafo", command=self.borrar_todo).pack(pady=10, fill=tk.X)

        # Raíz
        ttk.Label(left_frame, text="Raíz para búsquedas:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10,0))
        self.entry_raiz = ttk.Entry(left_frame, width=15)
        self.entry_raiz.pack(fill=tk.X, pady=3)
        self.entry_raiz.insert(0, "A")

        # Verificar y clasificar árbol
        ttk.Button(left_frame, text="Verificar si es Árbol y Clasificar", command=self.verificar_arbol).pack(pady=10, fill=tk.X)

        # Árboles óptimos
        ttk.Label(left_frame, text="Árboles Óptimos", font=("Arial", 11, "bold")).pack(anchor="w", pady=(15,5))
        mst_frame = ttk.Frame(left_frame)
        mst_frame.pack(fill=tk.X, pady=3)
        ttk.Label(mst_frame, text="MST (tecla M):").pack(side=tk.LEFT)
        self.combo_mst = ttk.Combobox(mst_frame, values=["Kruskal", "Prim"], width=10, state="readonly")
        self.combo_mst.set("Kruskal")
        self.combo_mst.pack(side=tk.LEFT, padx=5)
        ttk.Button(mst_frame, text="Generar", command=self.generar_mst).pack(side=tk.LEFT)

        ttk.Button(left_frame, text="Huffman (tecla H)", command=self.generar_huffman).pack(pady=6, fill=tk.X)
        ttk.Button(left_frame, text="OBST (tecla O)", command=self.mostrar_dialogo_obst).pack(pady=6, fill=tk.X)

        # Búsquedas
        ttk.Label(left_frame, text="Búsquedas (teclas B / D)", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15,5))
        ttk.Button(left_frame, text="BFS (Anchura)", command=self.mostrar_bfs).pack(fill=tk.X, pady=2)
        ttk.Button(left_frame, text="DFS (Profundidad)", command=self.mostrar_dfs).pack(fill=tk.X, pady=2)

        # Estado / Resultados
        ttk.Label(left_frame, text="Estado y Resultados", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15,5))
        self.estado_text = tk.Text(left_frame, height=16, width=40, font=("Consolas", 10))
        self.estado_text.pack(pady=5)

        # Área de dibujo
        self.fig, self.ax = plt.subplots(figsize=(8, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Eventos del mouse
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.actualizar_combos()

        # Atajos de teclado
        self.root.bind('<n>', lambda e: self.agregar_nodo())
        self.root.bind('<e>', lambda e: self.agregar_arista())
        self.root.bind('<g>', lambda e: self.generar_aleatorio())
        self.root.bind('<m>', lambda e: self.generar_mst())
        self.root.bind('<h>', lambda e: self.generar_huffman())
        self.root.bind('<o>', lambda e: self.mostrar_dialogo_obst())
        self.root.bind('<b>', lambda e: self.mostrar_bfs())
        self.root.bind('<d>', lambda e: self.mostrar_dfs())

    def on_press(self, event):
        if not event.inaxes:
            return
        x, y = event.xdata, event.ydata
        mode = self.mode.get()

        if mode == "Add Node":
            nombre = self.entry_nodo.get().strip() or next(self.node_letters, "Z")
            self.G.add_node(nombre)
            self.frecuencias[nombre] = int(self.entry_freq.get() or 10)
            self.pos[nombre] = (x, y)
            self.dibujar_grafo_original()
            self.actualizar_combos()
            self.actualizar_estado(f"Vértice {nombre} agregado")

        elif mode == "Add Edge":
            if not self.pos:
                return
            closest = min(self.pos, key=lambda n: ((self.pos[n][0]-x)**2 + (self.pos[n][1]-y)**2)**0.5)
            dist = ((self.pos[closest][0]-x)**2 + (self.pos[closest][1]-y)**2)**0.5
            if dist < 0.15:
                if self.selected_node is None:
                    self.selected_node = closest
                    self.actualizar_estado(f"Primer nodo: {closest} - selecciona segundo")
                else:
                    peso = float(self.entry_peso.get() or 5)
                    self.G.add_edge(self.selected_node, closest, weight=peso)
                    self.actualizar_estado(f"Arista {self.selected_node} → {closest} (peso {peso})")
                    self.selected_node = None
                    self.dibujar_grafo_original()

        elif mode == "Move Node":
            if not self.pos:
                return
            closest = min(self.pos, key=lambda n: ((self.pos[n][0]-x)**2 + (self.pos[n][1]-y)**2)**0.5)
            dist = ((self.pos[closest][0]-x)**2 + (self.pos[closest][1]-y)**2)**0.5
            if dist < 0.15:
                self.selected_node = closest
                self.dragging = True

    def on_release(self, event):
        self.dragging = False
        if self.mode.get() == "Move Node" and self.selected_node:
            self.dibujar_grafo_original()

    def on_motion(self, event):
        if not self.dragging or not self.selected_node or not event.inaxes:
            return
        self.pos[self.selected_node] = (event.xdata, event.ydata)
        self.dibujar_grafo_original()

    def dibujar_grafo_original(self):
        self.ax.clear()
        if len(self.G.nodes()) == 0:
            self.canvas.draw()
            return

        pos = self.pos if self.pos else nx.spring_layout(self.G, seed=42)
        nx.draw(self.G, pos, ax=self.ax, with_labels=True,
                node_color="lightblue", node_size=700, font_weight="bold")
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=self.ax)
        self.ax.set_title("Grafo Actual")
        self.canvas.draw()

    def actualizar_combos(self):
        nodos = sorted(self.G.nodes())
        self.combo_origen['values'] = nodos
        self.combo_destino['values'] = nodos

    def actualizar_estado(self, msg=""):
        self.estado_text.delete(1.0, tk.END)
        txt = "NODOS:\n"
        for n in sorted(self.G.nodes()):
            txt += f"  {n} (freq={self.frecuencias.get(n, '-')})\n"
        txt += "\nARISTAS:\n"
        for u,v,d in sorted(self.G.edges(data=True)):
            txt += f"  {u} — {v}  peso={d.get('weight', '-')}\n"
        if msg:
            txt += f"\n{msg}"
        self.estado_text.insert(tk.END, txt)

    def agregar_nodo(self):
        nombre = self.entry_nodo.get().strip() or next(self.node_letters, "Z")
        if nombre in self.G:
            messagebox.showwarning("Error", "Nodo ya existe")
            return
        try:
            freq = int(self.entry_freq.get() or 10)
        except:
            freq = 10
        self.G.add_node(nombre)
        self.frecuencias[nombre] = freq
        if nombre not in self.pos:
            self.pos[nombre] = (random.random()*2-1, random.random()*2-1)
        self.entry_nodo.delete(0, tk.END)
        self.actualizar_combos()
        self.actualizar_estado()
        self.dibujar_grafo_original()

    def agregar_arista(self):
        u = self.combo_origen.get()
        v = self.combo_destino.get()
        if not u or not v or u == v:
            messagebox.showwarning("Error", "Selecciona dos nodos diferentes")
            return
        try:
            peso = float(self.entry_peso.get() or 5)
        except:
            peso = 5
        self.G.add_edge(u, v, weight=peso)
        self.actualizar_estado(f"Arista {u}→{v} ({peso}) agregada")
        self.dibujar_grafo_original()

    def borrar_todo(self):
        self.G.clear()
        self.frecuencias.clear()
        self.pos.clear()
        self.arbol = None
        self.raiz = None
        self.arbol_type = None
        self.obst_cost = None
        self.huffman_root = None
        self.actualizar_combos()
        self.actualizar_estado("Grafo borrado completamente")
        self.ax.clear()
        self.canvas.draw()

    def verificar_arbol(self):
        if len(self.G.nodes()) == 0:
            messagebox.showwarning("Error", "No hay grafo")
            return
        if not nx.is_connected(self.G):
            self.actualizar_estado("No es un árbol: No conectado")
            return
        if nx.number_of_edges(self.G) != len(self.G.nodes()) - 1:
            self.actualizar_estado("No es un árbol: Tiene ciclos o no es acíclico")
            return

        # Es un árbol - clasificar
        raiz = self.entry_raiz.get().strip() or list(self.G.nodes())[0]
        self.arbol = nx.Graph(self.G)  # Copia como árbol
        self.raiz = raiz
        tipos = self.clasificar_arbol(raiz)
        niveles = self.calcular_niveles(raiz)
        palabras = self.generar_palabras(raiz)

        msg = "¡Es un árbol!\nTipos: " + ", ".join(tipos) + "\nNiveles:\n" + "\n".join(f"  {n}: nivel {lv}" for n,lv in niveles.items()) + "\nPalabras posibles (DFS/BFS): " + palabras
        self.actualizar_estado(msg)
        self.dibujar_arbol()

    def clasificar_arbol(self, raiz):
        tipos = []
        tree = nx.bfs_tree(self.G, raiz)  # Convertir a árbol dirigido desde raíz

        # Max hijos
        max_hijos = max(len(tree.successors(n)) for n in tree.nodes())
        if max_hijos <= 2:
            tipos.append("Binario")
        if max_hijos <= 3:
            tipos.append("Trinario")

        # Balanceado
        def altura(node):
            if not list(tree.successors(node)):
                return 0
            return 1 + max(altura(child) for child in tree.successors(node))
        def es_balanceado(node):
            hijos = list(tree.successors(node))
            if not hijos:
                return True
            alts = [altura(h) for h in hijos]
            if max(alts) - min(alts) > 1:
                return False
            return all(es_balanceado(h) for h in hijos)
        if es_balanceado(raiz):
            tipos.append("Balanceado")

        # Óptimo (asumiendo MST si tiene pesos)
        if nx.get_edge_attributes(self.G, 'weight'):
            tipos.append("Óptimo (MST)")

        # Binario óptimo (si es binario y óptimo)
        if "Binario" in tipos and "Óptimo (MST)" in tipos:
            tipos.append("Binario Óptimo")

        return tipos if tipos else ["General"]

    def calcular_niveles(self, raiz):
        niveles = {}
        queue = [(raiz, 0)]
        while queue:
            node, lv = queue.pop(0)
            niveles[node] = lv
            for child in self.G.neighbors(node):
                if child not in niveles:  # Evitar ciclos aunque no haya
                    queue.append((child, lv + 1))
        return niveles

    def generar_palabras(self, raiz):
        # DFS y BFS para formar "palabras" con letras de nodos
        dfs = " ".join([raiz] + [v for _,v in nx.dfs_edges(self.G, raiz)])
        bfs = " ".join([raiz] + [v for _,v in nx.bfs_edges(self.G, raiz)])
        return f"DFS: {dfs.replace(' ', '')}, BFS: {bfs.replace(' ', '')}"

    def generar_aleatorio(self):
        self.G.clear()
        self.frecuencias.clear()
        self.pos.clear()
        nodos = [next(self.node_letters) for _ in range(10)]
        self.G.add_nodes_from(nodos)
        for n in nodos:
            self.frecuencias[n] = random.randint(5, 35)
            self.pos[n] = (random.uniform(-1, 1), random.uniform(-1, 1))
        for _ in range(18):
            u = random.choice(nodos)
            v = random.choice(nodos)
            if u != v and not self.G.has_edge(u, v):
                self.G.add_edge(u, v, weight=random.randint(1, 25))
        self.actualizar_combos()
        self.actualizar_estado("Grafo aleatorio generado")
        self.dibujar_grafo_original()

    def generar_mst(self):
        if len(self.G.edges()) == 0:
            messagebox.showwarning("Error", "Agrega aristas primero")
            return
        raiz = self.entry_raiz.get().strip() or list(self.G.nodes())[0]
        algo = self.combo_mst.get().lower()
        try:
            self.arbol = nx.minimum_spanning_tree(self.G, algorithm=algo)
            self.raiz = raiz
            self.arbol_type = "mst"
            self.huffman_root = None
            self.obst_cost = None
            self.dibujar_arbol()
            self.actualizar_estado(f"MST generado con {algo.capitalize()}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generar_huffman(self):
        if len(self.frecuencias) < 2:
            messagebox.showwarning("Error", "Necesitas al menos 2 nodos con frecuencia")
            return

        class Node:
            def __init__(self, freq, symbol=None):
                self.freq = freq
                self.symbol = symbol
                self.left = None
                self.right = None
            def __lt__(self, other):
                return self.freq < other.freq

        heap = [Node(freq, sym) for sym, freq in self.frecuencias.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(heap, merged)

        root_node = heap[0]
        self.arbol = nx.DiGraph()
        self._build_huffman_graph(root_node)
        self.raiz = root_node.symbol or "Root"
        self.arbol_type = "huffman"
        self.huffman_root = root_node
        self.obst_cost = None
        self.dibujar_arbol()
        self.mostrar_codigos_huffman()

    def _build_huffman_graph(self, node, parent=None, side=""):
        if node is None:
            return
        node_id = node.symbol if node.symbol else f"I{len(self.arbol.nodes())}"
        self.arbol.add_node(node_id, freq=node.freq, symbol=node.symbol)
        if parent is not None:
            label = "0" if side == "left" else "1"
            self.arbol.add_edge(parent, node_id, label=label, weight=node.freq)
        self._build_huffman_graph(node.left, node_id, "left")
        self._build_huffman_graph(node.right, node_id, "right")

    def mostrar_codigos_huffman(self):
        if not self.huffman_root:
            return
        codes = {}
        def traverse(node, code=""):
            if node is None:
                return
            if node.symbol:
                codes[node.symbol] = code
                return
            traverse(node.left, code + "0")
            traverse(node.right, code + "1")
        traverse(self.huffman_root)
        txt = "CÓDIGOS HUFFMAN:\n" + "\n".join(f"  {s}: {c}" for s, c in sorted(codes.items()))
        self.actualizar_estado(txt)

    def mostrar_dialogo_obst(self):
        top = tk.Toplevel(self.root)
        top.title("Árbol Binario de Búsqueda Óptimo (OBST)")
        top.geometry("450x220")
        top.grab_set()

        ttk.Label(top, text="Claves separadas por coma:").pack(anchor="w", padx=20, pady=(10,0))
        entry_keys = ttk.Entry(top, width=50)
        entry_keys.pack(padx=20, pady=2)
        entry_keys.insert(0, "A,B,C,D")

        ttk.Label(top, text="Frecuencias separadas por coma:").pack(anchor="w", padx=20)
        entry_freq = ttk.Entry(top, width=50)
        entry_freq.pack(padx=20, pady=2)
        entry_freq.insert(0, "0.4,0.3,0.2,0.1")

        def calcular():
            try:
                keys = [x.strip() for x in entry_keys.get().split(',') if x.strip()]
                freq = [float(x.strip()) for x in entry_freq.get().split(',') if x.strip()]
                if len(keys) != len(freq) or len(keys) < 2:
                    raise ValueError("Deben coincidir y haber al menos 2 claves")
                costo = self.construir_obst(keys, freq)
                messagebox.showinfo("Éxito", f"¡Árbol Binario Óptimo creado!\nCosto esperado mínimo: {costo:.4f}")
                self.dibujar_arbol()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(top, text="Calcular y Dibujar Árbol", command=calcular).pack(pady=15)

    def construir_obst(self, keys, freq):
        n = len(keys)
        cost = [[0.0] * n for _ in range(n)]
        root_table = [[0] * n for _ in range(n)]

        for i in range(n):
            cost[i][i] = freq[i]
            root_table[i][i] = i

        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                cost[i][j] = float('inf')
                sum_freq = sum(freq[k] for k in range(i, j + 1))
                for r in range(i, j + 1):
                    left = cost[i][r - 1] if r > i else 0.0
                    right = cost[r + 1][j] if r < j else 0.0
                    total = left + right + sum_freq
                    if total < cost[i][j]:
                        cost[i][j] = total
                        root_table[i][j] = r

        # Construir el árbol
        self.arbol = nx.DiGraph()
        def build(i, j, parent=None):
            if i > j:
                return None
            r = root_table[i][j]
            node = keys[r]
            if parent is not None:
                self.arbol.add_edge(parent, node)
            build(i, r - 1, node)
            build(r + 1, j, node)
            return node

        self.raiz = keys[root_table[0][n - 1]]
        build(0, n - 1)
        self.arbol_type = "obst"
        self.huffman_root = None
        self.obst_cost = cost[0][n - 1]
        return self.obst_cost

    def dibujar_arbol(self):
        if self.arbol is None:
            return

        self.ax.clear()
        pos = nx.spring_layout(self.arbol, seed=42)

        color = 'lightcoral' if self.arbol_type == "huffman" else 'lightgreen' if self.arbol_type == "mst" else 'lightblue'
        nx.draw(self.arbol, pos, ax=self.ax, with_labels=True, node_color=color, node_size=800)
        labels = nx.get_edge_attributes(self.arbol, 'weight')
        nx.draw_networkx_edge_labels(self.arbol, pos, edge_labels=labels, ax=self.ax)

        # Resaltar raíz
        nx.draw_networkx_nodes(self.arbol, pos, nodelist=[self.raiz], node_color="orange", node_size=900, ax=self.ax)

        # Etiquetas 0/1 en Huffman
        if self.arbol_type == "huffman":
            label_dict = {(u, v): d.get('label', '') for u, v, d in self.arbol.edges(data=True)}
            nx.draw_networkx_edge_labels(self.arbol, pos, edge_labels=label_dict, ax=self.ax, font_color="red", font_size=10)

        titulo = f"Árbol {'MST (' + self.combo_mst.get() + ')' if self.arbol_type=='mst' else 'Binario Óptimo Huffman' if self.arbol_type=='huffman' else 'OBST (Costo: ' + str(self.obst_cost) + ')'}"
        self.ax.set_title(titulo + f" - Raíz: {self.raiz}")
        self.canvas.draw()

    def mostrar_bfs(self):
        if not self.arbol or not self.raiz:
            messagebox.showwarning("Error", "Necesitas un árbol y raíz")
            return

        try:
            bfs_edges = list(nx.bfs_edges(self.arbol, self.raiz))
            nodos_bfs = [self.raiz] + [v for u,v in bfs_edges]
            texto = "BFS (anchura): " + " → ".join(nodos_bfs)
            self.actualizar_estado(texto)
        except:
            self.actualizar_estado("Error en BFS")

    def mostrar_dfs(self):
        if not self.arbol or not self.raiz:
            messagebox.showwarning("Error", "Necesitas un árbol y raíz")
            return

        try:
            dfs_edges = list(nx.dfs_edges(self.arbol, self.raiz))
            nodos_dfs = [self.raiz] + [v for u,v in dfs_edges]
            texto = "DFS (profundidad): " + " → ".join(nodos_dfs)
            self.actualizar_estado(texto)
        except:
            self.actualizar_estado("Error en DFS")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    app = GraphApp(root)
    root.mainloop()
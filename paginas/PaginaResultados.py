from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QPlainTextEdit,
    QHeaderView,
    QWidget,
)
from PyQt5.QtCore import Qt
from .PaginaBase import PaginaBase
from math import exp, erf, sqrt
from scipy.stats import chi2
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class PaginaResultados(PaginaBase):
    def __init__(self, callback_volver, callback_cerrar, 
                 datos: list[float], nombre: str = "", 
                 intervalos: int = 10, *parametros):
        super().__init__("Resultados de la Generación", callback_volver, callback_cerrar, )
        self.datos = datos
        self.distribucion = nombre
        self.intervalos = intervalos
        self.parametros = parametros # (μ,σ) ó (λ,) ó (A,B) para chi2

        self.agregar_widget(
            QLabel(f"<h2>Resultados para distribución: {self.distribucion}</h2>"))

        self.stack = QStackedWidget()
        self.stack.addWidget(self.crear_tabla())
        self.stack.addWidget(self.crear_histograma())
        self.stack.addWidget(self.crear_serie())
        self.stack.addWidget(self.crear_chi2())

        botones_layout = QHBoxLayout()
        self.btnTabla = QPushButton("Mostrar Tabla de Frecuencias")
        self.btnHist = QPushButton("Mostrar Histograma")
        self.btnSerie = QPushButton("Mostrar Serie de Numeros")
        self.btnChi2 = QPushButton("Prueba Chi-Cuadrado")

        self.btnTabla.clicked.connect(self.mostrar_tabla)
        self.btnHist.clicked.connect(self.mostrar_histograma)
        self.btnSerie.clicked.connect(self.mostrar_serie)
        self.btnChi2.clicked.connect(self.mostrar_chi2)

        botones_layout.addWidget(self.btnTabla)
        botones_layout.addWidget(self.btnHist)
        botones_layout.addWidget(self.btnSerie)
        botones_layout.addWidget(self.btnChi2)
        self.contenedor.addLayout(botones_layout)

        # Botones navegación y exportar (solo visibles en vista Serie)
        self.btn_anterior = QPushButton("← Anterior")
        self.btn_siguiente = QPushButton("Siguiente →")
        self.btn_exportar = QPushButton("Exportar .txt")
        self.btn_anterior.clicked.connect(self.pagina_anterior)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)
        self.btn_exportar.clicked.connect(self.exportar_serie)

        self.nav_layout = QHBoxLayout()
        self.nav_layout.addWidget(self.btn_anterior)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.btn_exportar)
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.btn_siguiente)
        self.nav_layout_widget = QWidget()
        self.nav_layout_widget.setLayout(self.nav_layout)
        self.nav_layout_widget.hide()  # Oculto por defecto

        self.contenedor.addWidget(self.nav_layout_widget)
        self.boton_extra.hide()
        self.agregar_widget(self.stack)

    def crear_tabla(self):
        tabla = QTableWidget(self.intervalos, 5)
        tabla.setHorizontalHeaderLabels(
            ["Intervalo N°", "Límite Inferior", "Límite Superior", "FO", "FE"])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        minim = min(self.datos)
        maxim = max(self.datos)
        alcance = maxim - minim
        rango = alcance / self.intervalos
        li = minim

        n_intervalo = 1

        while n_intervalo <= self.intervalos:
            if n_intervalo == self.intervalos:
                ls = maxim
                fo = sum(1 for x in self.datos if li <= x <= ls)
            else:
                ls = round(li + rango - (0.0001 / 10), 4)
                fo = sum(1 for x in self.datos if li <= x < ls)
            
            n = len(self.datos)
            fe = n * ( self._cdf(ls) - self._cdf(li) )
            
            # Crear cada celda como no editable
            celda_intervalo = QTableWidgetItem(str(n_intervalo))
            celda_intervalo.setFlags(
                celda_intervalo.flags() & ~Qt.ItemIsEditable)

            celda_li = QTableWidgetItem(f"{li:.4f}")
            celda_li.setFlags(celda_li.flags() & ~Qt.ItemIsEditable)

            celda_ls = QTableWidgetItem(f"{ls:.4f}")
            celda_ls.setFlags(celda_ls.flags() & ~Qt.ItemIsEditable)

            celda_fo = QTableWidgetItem(f"{fo}")
            celda_fo.setFlags(celda_fo.flags() & ~Qt.ItemIsEditable)

            celda_fe = QTableWidgetItem(f"{fe:.4f}")
            celda_fe.setFlags(celda_fe.flags() & ~Qt.ItemIsEditable)
            
            # Insertar en la tabla
            tabla.setItem(n_intervalo - 1, 0, celda_intervalo)
            tabla.setItem(n_intervalo - 1, 1, celda_li)
            tabla.setItem(n_intervalo - 1, 2, celda_ls)
            tabla.setItem(n_intervalo - 1, 3, celda_fo)
            tabla.setItem(n_intervalo - 1, 4, celda_fe)

            li = ls
            n_intervalo += 1
        return tabla

    def crear_histograma(self):
        fig = Figure(figsize=(6, 4), facecolor='#f9f9f9')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        # ✅ Calcular bins (bordes) explícitamente
        frecuencias, bordes = np.histogram(self.datos, bins=self.intervalos)

        # Dibujar histograma con los bordes definidos
        ax.hist(
            self.datos,
            bins=bordes,
            edgecolor='white',
            linewidth=1.2,
            color='#5c7cfa',
            alpha=0.9
        )

        # Mostrar los límites de los intervalos en el eje X
        etiquetas = [f"{b:.2f}" for b in bordes]
        ax.set_xticks(bordes)
        ax.set_xticklabels(etiquetas, rotation=45, ha='right', fontsize=9)

        # Estética
        ax.set_title(f"Histograma de Frecuencias de Distribución {self.distribucion}", fontsize=14,
                     fontweight='bold', color='#343a40')
        ax.set_xlabel("Límites de Intervalos", fontsize=12)
        ax.set_ylabel("Frecuencia Observada", fontsize=12)
        ax.tick_params(axis='both', labelsize=10)
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
        ax.set_facecolor('#ffffff')

        fig.subplots_adjust(bottom=0.25)

        return canvas

    def actualizar_critico(self):
            """
            Recalcula y muestra el valor crítico de χ²
            según el df = k − 1 − p (p = nº parámetros estimados).
            """
            # Nivel de significación
            alpha = float(self.alpha_combo.currentText())
            # p = nº parámetros estimados por distribución
            if self.distribucion == "Uniforme":
                p = 0
            elif self.distribucion == "Exponencial Negativa":
                p = 1
            elif self.distribucion == "Normal":
                p = 2
            else:
                p = 0

            # grados de libertad
            df = self.intervalos - 1 - p
            # valor crítico para cola derecha
            crit = chi2.ppf(1 - alpha, df)
            # Actualizamos label
            self.lbl_critico.setText(f"χ² crítico (df={df}, α={alpha}): {crit:.4f}")



    def crear_chi2(self):
        """
        Construye la pestaña de χ²: selector de α, valor crítico y tabla.
        """
        cont = QWidget()
        layout = QVBoxLayout()

        # ——— Selector de nivel de significación α ———
        self.alpha_combo = QComboBox()
        self.alpha_combo.addItems(["0.1", "0.05", "0.025", "0.01", "0.005"])
        self.alpha_combo.setCurrentText("0.05")
        self.alpha_combo.currentTextChanged.connect(self.actualizar_critico)
        layout.addWidget(QLabel("Nivel de significación α:"))
        layout.addWidget(self.alpha_combo)

        # Label donde mostraremos el χ² crítico
        self.lbl_critico = QLabel()
        layout.addWidget(self.lbl_critico)
        # Tabla de χ²
        layout.addWidget(self.crear_chi2_tabla())
        
        # Mantén los botones de navegación/exportar si lo necesitas
        # layout.addWidget(self.nav_layout_widget)

        cont.setLayout(layout)

        # Inicializar el valor crítico
        self.actualizar_critico()

        return cont


    def crear_chi2_tabla(self):
        """
        Construye un QTableWidget con la tabla de Chi²:
        - calcula FO y FE a partir de histogramas y CDF normal
        - agrupa clases hasta FE>=5
        - calcula (FO-FE)^2/FE por grupo
        """
        
        
        # --- 0) asegurarnos de que self.datos sólo contenga los valores
        arr = np.array(self.datos)
        if arr.ndim > 1:
            data = arr[:, 1]   # tomo la segunda columna
        else:
            data = arr
        
        # --- 1) calcular FO y FE por clase
        frecuencias, bordes = np.histogram(data, bins=self.intervalos)
        n = len(data)

        clases = []
        for i, fo in enumerate(frecuencias):
            li, ls = bordes[i], bordes[i+1]
            fe = n * ( self._cdf(ls) - self._cdf(li) )
            clases.append({'li': li, 'ls': ls, 'fo': int(fo), 'fe': fe})

        # --- 2) agrupar hasta FE>=5
        agrupadas = []
        current = clases[0].copy()
        for c in clases[1:]:
            if current['fe'] < 5:
                # extiendo el grupo actual
                current['ls'] = c['ls']
                current['fo'] += c['fo']
                current['fe'] += c['fe']
            else:
                agrupadas.append(current)
                current = c.copy()
        # fusionar resto si quedó FE<5
        if current['fe'] < 5 and agrupadas:
            prev = agrupadas[-1]
            prev['ls']  = current['ls']
            prev['fo'] += current['fo']
            prev['fe'] += current['fe']
        else:
            agrupadas.append(current)

        # --- 3) construir tabla de Chi²
        filas = len(agrupadas)
        tabla = QTableWidget(filas, 6)
        tabla.setHorizontalHeaderLabels([
            "Desde", "Hasta", "FO", "FE", "χ²", "χ² Acumulado"
        ])
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        chi2_acum = 0.0
        for k, grp in enumerate(agrupadas):
            fo_k = grp['fo']
            fe_k = grp['fe']
            chi2 = (fo_k - fe_k)**2 / fe_k
            chi2_acum += chi2

            cells = [
                QTableWidgetItem(f"{grp['li']:.4f}"),
                QTableWidgetItem(f"{grp['ls']:.4f}"),
                QTableWidgetItem(str(fo_k)),
                QTableWidgetItem(f"{fe_k:.4f}"),
                QTableWidgetItem(f"{chi2:.4f}"),
                QTableWidgetItem(f"{chi2_acum:.4f}")
            ]
            for col, item in enumerate(cells):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                tabla.setItem(k, col, item)

        # (Opcional) podrías exponer chi2_total y gl en algún widget aparte
        # self.chi2_value = chi2_total
        # self.grados_libertad = filas - 1 - self.parametros_estimados

        return tabla

    def crear_serie(self):
        self.texto_serie = QPlainTextEdit()
        self.texto_serie.setReadOnly(True)

        self.pagina_actual = 0
        self.items_por_pagina = 10000
        self.total_paginas = (len(self.datos) - 1) // self.items_por_pagina + 1
        self.mostrar_pagina()

        return self.texto_serie

    def mostrar_pagina(self):
        inicio = self.pagina_actual * self.items_por_pagina
        fin = min(len(self.datos), inicio + self.items_por_pagina)
        fragmento = ', '.join(f"{x:.4f}" for x in self.datos[inicio:fin])
        self.texto_serie.setPlainText(
            f"[{inicio + 1}-{fin}] de {len(self.datos)}:\n{fragmento}")

    def pagina_anterior(self):
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.mostrar_pagina()

    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas - 1:
            self.pagina_actual += 1
            self.mostrar_pagina()

    @staticmethod
    def redondear(x):
        if x >= 0:
            return int(x + 0.5)
        else:
            return int(x - 0.5)

    def frecuencia_en_intervalo(datos, li, ls):
        return sum(1 for x in datos if li <= x < ls)

    def exportar_serie(self):
        try:
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nom_archivo = f"serie_exportada_{fecha}.txt"
            with open(nom_archivo, "w") as f:
                f.write(', '.join(f"{x:.4f}" for x in self.datos))
        except Exception as e:
            print("Error al exportar:", e)

    def mostrar_tabla(self):
        self.stack.setCurrentIndex(0)
        self.nav_layout_widget.hide()

    def mostrar_histograma(self):
        self.stack.setCurrentIndex(1)
        self.nav_layout_widget.hide()

    def mostrar_serie(self):
        self.stack.setCurrentIndex(2)
        self.nav_layout_widget.show()
        
    def mostrar_chi2(self):
        self.stack.setCurrentIndex(3)
        self.nav_layout_widget.hide()

    def _cdf(self, x):
        """Función de distribución acumulada de la dist. teórica."""
        if self.distribucion == "Uniforme":
            A, B = self.parametros
            # CDF uniforme truncada en [A,B]
            return max(0.0, min(1.0, (x - A) / (B - A)))
        elif self.distribucion == "Exponencial Negativa":
            (lmd,) = self.parametros
            return 1 - exp(-lmd * x)
        elif self.distribucion == "Normal":
            media, desv = self.parametros
            return 0.5 * (1 + erf((x - media) / (desv * sqrt(2))))
        else:
            return 0.0
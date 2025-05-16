from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QPlainTextEdit,
    QHeaderView,
    QWidget
)
from PyQt5.QtCore import Qt
from .PaginaBase import PaginaBase
from sympy import nextprime
from math import sqrt
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class PaginaResultados(PaginaBase):
    def __init__(self, callback_volver, callback_cerrar, datos: list[float], nombre: str = "", intervalos: int = 10):
        super().__init__("Resultados de la Generación", callback_volver, callback_cerrar, )
        self.datos = datos
        self.distribucion = nombre
        self.intervalos = intervalos

        self.agregar_widget(
            QLabel(f"<h2>Resultados para distribución: {self.distribucion}</h2>"))

        self.stack = QStackedWidget()
        self.stack.addWidget(self.crear_tabla())
        self.stack.addWidget(self.crear_histograma())
        self.stack.addWidget(self.crear_serie())

        botones_layout = QHBoxLayout()
        self.btnTabla = QPushButton("Mostrar Tabla de Frecuencias")
        self.btnHist = QPushButton("Mostrar Histograma")
        self.btnSerie = QPushButton("Mostrar Serie de Numeros")

        self.btnTabla.clicked.connect(self.mostrar_tabla)
        self.btnHist.clicked.connect(self.mostrar_histograma)
        self.btnSerie.clicked.connect(self.mostrar_serie)

        botones_layout.addWidget(self.btnTabla)
        botones_layout.addWidget(self.btnHist)
        botones_layout.addWidget(self.btnSerie)

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
        tabla = QTableWidget(self.intervalos, 4)
        tabla.setHorizontalHeaderLabels(
            ["Intervalo N°", "Límite Inferior", "Límite Superior", "Frecuencia Observada"])
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

            # Insertar en la tabla
            tabla.setItem(n_intervalo - 1, 0, celda_intervalo)
            tabla.setItem(n_intervalo - 1, 1, celda_li)
            tabla.setItem(n_intervalo - 1, 2, celda_ls)
            tabla.setItem(n_intervalo - 1, 3, celda_fo)

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

    def mostrar_serie(self):
        self.stack.setCurrentIndex(2)
        self.nav_layout_widget.show()

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

from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QTableWidget, QTableWidgetItem, QPlainTextEdit, QWidget, QHeaderView,
    QComboBox
)
from PyQt5.QtCore import Qt
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.generadores import (
    frecuencias_observadas,
    frecuencias_esperadas,
    obtener_histograma,
    chi2_critico,
    calcular_clases_chi2,
)

from .PaginaBase import PaginaBase


class PaginaResultados(PaginaBase):
    def __init__(
        self,
        callback_volver,
        callback_cerrar,
        datos,
        nombre_dist="",
        intervalos=10,
        media=None,
        desviacion=None,
        lmd=None,
        A=None,
        B=None,
    ):
        super().__init__("Resultados", callback_volver, callback_cerrar)
        self.boton_extra.hide()
        self.datos, self.intervalos = datos, intervalos
        self.distribucion = nombre_dist
        self.param_media, self.param_desv, self.param_lmd = media, desviacion, lmd
        self.param_A, self.param_B = A, B

        self.agregar_widget(
            QLabel(f"<h2>Distribución: {self.distribucion}</h2>"))
        self.stack = QStackedWidget()
        self.stack.addWidget(self._widget_tabla())
        self.stack.addWidget(self._widget_histograma())
        self.stack.addWidget(self._widget_serie())

        # Botones de navegación de vistas
        botones = QHBoxLayout()
        for txt, handler in [
            ("Tabla de Frecuencias", self.mostrar_tabla),
            ("Histograma", self.mostrar_histograma),
            ("Serie", self.mostrar_serie)
        ]:
            btn = QPushButton(txt)
            btn.clicked.connect(handler)
            botones.addWidget(btn)
        self.contenedor.addLayout(botones)

        # Navegación interna de serie
        self._crear_controles_serie()
        self.contenedor.addWidget(self.stack)

    def _widget_tabla(self):
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        # Generar datos de tabla
        datos_interv = frecuencias_observadas(self.datos, self.intervalos)
        # extraer sólo límites para FE
        limites = [(li, ls) for (li, ls, fo) in datos_interv]

        # Crear tabla con 5 columnas
        tabla = QTableWidget(len(datos_interv), 5)
        tabla.setHorizontalHeaderLabels(
            ["Intervalo N°", "Límite Inf.", "Límite Sup.", "FO", "FE"]
        )
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Calcular FE según distribución
        total = len(self.datos)
        if self.distribucion == "Uniforme":
            params = (self.param_A, self.param_B)
        elif self.distribucion == "Exponencial Negativa":
            params = (self.param_lmd,)
        else:  # "Normal"
            params = (self.param_media, self.param_desv)
        fe_list = frecuencias_esperadas(
            limites, total, self.distribucion, params)

        # Poblar Tabla
        for i, (li, ls, fo) in enumerate(datos_interv):
            valores = [
                i + 1,
                f"{li:.4f}",
                f"{ls:.4f}",
                fo,
                f"{fe_list[i]:.4f}",
            ]
            for j, v in enumerate(valores):
                item = QTableWidgetItem(str(v))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                tabla.setItem(i, j, item)
        layout.addWidget(tabla)

        # Crear Tabla de chi2
        layout.addLayout(self._crear_seccion_chi2())

        return contenedor

    def actualizar_critico(self):
        """
        Actualiza el label con el valor crítico de χ² según el valor
        seleccionado en el QComboBox de alpha.
        """
        alpha = float(self.alpha_combo.currentText())
        k = len(self._agrupadas_chi2)
        p_crit = chi2_critico(k, alpha)
        self.lbl_critico.setText(
            f"χ² Tabla (Grad Lib={k - 1}, Alpha={alpha}): {p_crit:.4f}")

        if self._chi2_calculado > p_crit:
            self.lbl_resultado.setText("Se rechaza la H0.")
        else:
            self.lbl_resultado.setText(
                "No se tiene suficiente evidencia para rechazar H0.")

        return p_crit

    def agrupar_intervalos_chi2(self, clases):
        """
        Agrupa los intervalos de la tabla de χ² hasta que cada grupo
        tenga FE >= 5. Devuelve la lista de grupos agrupados.
        """
        agrupadas = []
        current = clases[0].copy()
        for c in clases[1:]:
            if current['fe'] < 5:
                current['ls'] = c['ls']
                current['fo'] += c['fo']
                current['fe'] += c['fe']
            else:
                agrupadas.append(current)
                current = c.copy()

        if current['fe'] < 5 and agrupadas:
            prev = agrupadas[-1]
            prev['ls'] = current['ls']
            prev['fo'] += current['fo']
            prev['fe'] += current['fe']
        else:
            agrupadas.append(current)

        return agrupadas

    def _get_tabla_chi2(self, agrupadas):
        """
        Crea una tabla QTableWidget con los resultados de χ² agrupados:
        - cada fila es un grupo de intervalos
        - cada columna es:
            - Desde: límite inferior del grupo
            - Hasta: límite superior del grupo
            - FO: frecuencia observada en el grupo
            - FE: frecuencia esperada en el grupo
            - χ²: (FO - FE)^2 / FE para cada grupo
            - χ² Acumulado: suma de los χ² de cada grupo
        """

        filas = len(agrupadas)
        tabla = QTableWidget(filas, 6)
        tabla.setHorizontalHeaderLabels(
            ["Desde", "Hasta", "FO", "FE", "χ²", "χ² Acumulado"]
        )
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        chi2_acum = 0.0
        for k, grp in enumerate(agrupadas):
            fo_k = grp['fo']
            fe_k = grp['fe']
            chi2_val = (fo_k - fe_k) ** 2 / fe_k
            chi2_acum += chi2_val

            datos_fila = [
                f"{grp['li']:.4f}",
                f"{grp['ls']:.4f}",
                str(fo_k),
                f"{fe_k:.4f}",
                f"{chi2_val:.4f}",
                f"{chi2_acum:.4f}",
            ]
            for col, txt in enumerate(datos_fila):
                item = QTableWidgetItem(txt)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                tabla.setItem(k, col, item)
        self._chi2_calculado = chi2_acum
        self.lbl_calculado.setText(f"χ² calculado: {self._chi2_calculado:.4f}")

        return tabla

    def _crear_seccion_chi2(self):
        if self.distribucion == "Uniforme":
            params = (self.param_A, self.param_B)
        elif self.distribucion == "Exponencial Negativa":
            params = (self.param_lmd,)
        else:
            params = (self.param_media, self.param_desv)

        clases = calcular_clases_chi2(
            self.datos, self.intervalos, self.distribucion, params)
        agrupadas = self.agrupar_intervalos_chi2(clases)

        # Gaurdar valores en contexto
        self._agrupadas_chi2 = agrupadas

        # Widget contenedor
        layout = QVBoxLayout()

        # Seleccion de alpha
        layout.addWidget(QLabel("Nivel de significancia Alpha:"))
        self.alpha_combo = QComboBox()
        for alpha in ["0.5", "0.1", "0.05", "0.025", "0.01", "0.005"]:
            self.alpha_combo.addItem(alpha)
        self.alpha_combo.setCurrentText("0.05")
        self.alpha_combo.currentTextChanged.connect(self.actualizar_critico)
        layout.addWidget(self.alpha_combo)

        # Etiquetas de resultado
        self.lbl_critico = QLabel()
        self.lbl_calculado = QLabel(
        )
        self.lbl_resultado = QLabel()
        layout.addWidget(self.lbl_critico)
        layout.addWidget(self.lbl_calculado)
        layout.addWidget(self.lbl_resultado)

        # Tabla de χ²
        tabla = self._get_tabla_chi2(agrupadas)
        layout.addWidget(tabla)

        # Inicializa las etiquetas
        self.actualizar_critico()
        return layout

    def _widget_histograma(self):
        _, bins = obtener_histograma(self.datos, self.intervalos)
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)

        # Dibujar histograma
        ax.hist(
            self.datos,
            bins=bins,
            edgecolor='white',
            linewidth=1.2,
            color='#5c7cfa',
            alpha=0.9
        )

        # Mostrar los límites de los intervalos en el eje X
        etiquetas = [f"{b:.2f}" for b in bins]
        ax.set_xticks(bins)
        ax.set_xticklabels(etiquetas, rotation=45, ha='right', fontsize=9)

        # Detalles
        ax.set_title(f"Histograma de la Distribución {
                     self.distribucion}", fontweight='bold')
        ax.set_xlabel("Intervalos", fontsize=12)
        ax.set_ylabel("Frecuencia Observada", fontsize=12)
        ax.tick_params(axis='both')
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
        fig.subplots_adjust(bottom=0.25)
        return FigureCanvas(fig)

    def _widget_serie(self):
        self.texto = QPlainTextEdit(readOnly=True)
        self.pagina, items_por_pagina = 0, 10000
        self.max_pag = (len(self.datos)-1) // items_por_pagina
        self._mostrar_pagina(items_por_pagina)
        return self.texto

    def _crear_controles_serie(self):
        self.nav = QWidget()
        layout = QHBoxLayout(self.nav)
        for txt, cb in [("←", self._ant), ("Exportar", self._exp), ("→", self._sig)]:
            btn = QPushButton(txt)
            btn.clicked.connect(cb)
            layout.addWidget(btn)
        self.nav.hide()
        self.contenedor.addWidget(self.nav)

    def _mostrar_pagina(self, items_por_pagina):
        inicio = self.pagina * items_por_pagina
        fin = min(len(self.datos), inicio + items_por_pagina)
        txt = ', '.join(f"{x:.4f}" for x in self.datos[inicio:fin])
        self.texto.setPlainText(
            f"[{inicio+1}-{fin}] de {len(self.datos)}:\n{txt}")

    def _ant(self):
        if self.pagina > 0:
            self.pagina -= 1
            self._mostrar_pagina(10000)

    def _sig(self):
        if self.pagina < self.max_pag:
            self.pagina += 1
            self._mostrar_pagina(10000)

    def _exp(self):
        fn = f"serie_{datetime.now():%Y%m%d_%H%M%S}.txt"
        with open(fn, "w") as f:
            f.write(', '.join(f"{x:.4f}" for x in self.datos))

    # Vistas
    def mostrar_tabla(self):
        self.stack.setCurrentIndex(0)
        self.nav.hide()

    def mostrar_histograma(self):
        self.stack.setCurrentIndex(1)
        self.nav.hide()

    def mostrar_serie(self):
        self.stack.setCurrentIndex(2)
        self.nav.show()

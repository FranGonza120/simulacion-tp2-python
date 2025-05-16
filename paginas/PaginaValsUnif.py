from PyQt5.QtWidgets import QLabel, QSpinBox
from .PaginaBase import PaginaBase


class PaginaValsUnif(PaginaBase):
    LIM_MIN = -1_000_000
    LIM_MAX = 1_000_000

    def __init__(self, cantidad, intervalos,
                 callback_generado, callback_volver, callback_cerrar):
        super().__init__("Parámetros de Uniforme entre A y B",
                         callback_volver, callback_cerrar)
        self.cantidad = cantidad
        self.intervalos = intervalos
        self.callback = callback_generado

        # ---------- Entrada A ----------
        self.entrada_a = QSpinBox()
        self.entrada_a.setRange(self.LIM_MIN, self.LIM_MAX - 1)  # A < B ⇒ máx = LIM_MAX-1
        self.entrada_a.setValue(0)
        self.entrada_a.valueChanged.connect(self._actualizar_min_b)

        # ---------- Entrada B ----------
        self.entrada_b = QSpinBox()
        self.entrada_b.setRange(self.LIM_MIN + 1, self.LIM_MAX)  # B > A ⇒ mín = LIM_MIN+1
        self.entrada_b.setValue(1)
        self.entrada_b.valueChanged.connect(self._actualizar_max_a)

        # ---------- Botón y layout ----------
        self.set_boton_extra_texto("Generar")
        self.conectar_boton_extra(self._generar)

        self.agregar_widget(QLabel("Ingrese el valor de A:"))
        self.agregar_widget(self.entrada_a)
        self.agregar_widget(QLabel(" "))

        self.agregar_widget(QLabel("Ingrese el valor de B:"))
        self.agregar_widget(self.entrada_b)

    # Callbacks
    def _generar(self):
        a = self.entrada_a.value()
        b = self.entrada_b.value()
        self.callback("Uniforme", self.cantidad, self.intervalos, a, b)

    def _actualizar_min_b(self):
        """Cuando cambia A, B debe ser ≥ A + 1."""
        nuevo_min = self.entrada_a.value() + 1
        self.entrada_b.setMinimum(nuevo_min)
        if self.entrada_b.value() < nuevo_min:
            self.entrada_b.setValue(nuevo_min)

    def _actualizar_max_a(self):
        """Cuando cambia B, A debe ser ≤ B - 1."""
        nuevo_max = self.entrada_b.value() - 1
        self.entrada_a.setMaximum(nuevo_max)
        if self.entrada_a.value() > nuevo_max:
            self.entrada_a.setValue(nuevo_max)

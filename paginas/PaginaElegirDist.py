from PyQt5.QtWidgets import QLabel, QSpinBox, QComboBox
from .PaginaBase import PaginaBase


class PaginaElegirDist(PaginaBase):
    def __init__(self, callback_seleccion, callback_volver, callback_cerrar):
        super().__init__("Elija una distribucion", callback_volver, callback_cerrar)

        self.callback = callback_seleccion

        self.combo = QComboBox()
        self.combo.addItems(["Normal", "Uniforme", "Exponencial Negativa"])

        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self.spin.setMaximum(1000000)
        self.spin.setValue(100)

        self.intervalos_combo = QComboBox()
        self.intervalos_combo.addItems(["10", "15", "20", "25"])

        self.set_boton_extra_texto("Continuar")
        self.conectar_boton_extra(self.enviar_datos)

        label_input_dist = QLabel(
            "Seleccione una distribucion con la que quiera generar los valores: ")
        label_input_dist.setWordWrap(True)
        self.agregar_widget(label_input_dist)
        self.agregar_widget(self.combo)
        self.agregar_widget(QLabel(" "))

        label_intervalos = QLabel(
            "Seleccione la cantidad de intervalos para el histograma:")
        label_intervalos.setWordWrap(True)
        self.agregar_widget(label_intervalos)
        self.agregar_widget(self.intervalos_combo)
        self.agregar_widget(QLabel(" "))

        label_input_val = QLabel(
            "Ingrese la cantidad de valores que desea generar (1 a 1.000.000):")
        label_input_val.setWordWrap(True)
        self.agregar_widget(label_input_val)
        self.agregar_widget(self.spin)

    def enviar_datos(self):
        dist = self.combo.currentText()
        cantidad = self.spin.value()
        intervalos = int(self.intervalos_combo.currentText())
        self.callback(dist, cantidad, intervalos)

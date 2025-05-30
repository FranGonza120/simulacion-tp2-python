from PyQt5.QtWidgets import QLabel, QDoubleSpinBox
from .PaginaBase import PaginaBase


class PaginaValsNorm(PaginaBase):
    def __init__(self, cantidad, intervalos, callback_generado, callback_volver, callback_cerrar):
        super().__init__("Parametros de Normal", callback_volver, callback_cerrar)
        self.cantidad = cantidad
        self.callback = callback_generado
        self.intervalos = intervalos

        self.entrada_md = QDoubleSpinBox()
        self.entrada_md.setDecimals(4)
        self.entrada_md.setSingleStep(0.0001)
        self.entrada_md.setValue(0)
        self.entrada_md.setRange(-1e6, 1e6)

        self.entrada_desv = QDoubleSpinBox()
        self.entrada_desv.setDecimals(4)
        self.entrada_desv.setSingleStep(0.0001)
        self.entrada_desv.setValue(1)
        self.entrada_desv.setRange(-1e6, 1e6)
        # Corroborar si es correcto poner este limite en el rango para la desv estandar

        self.set_boton_extra_texto("Generar")
        self.conectar_boton_extra(self.generar)

        self.agregar_widget(QLabel("Ingrese la Media μ :"))
        self.agregar_widget(self.entrada_md)
        self.agregar_widget(QLabel(" "))
        
        self.agregar_widget(QLabel("Ingrese la Desviacion Estandar σ :"))
        self.agregar_widget(self.entrada_desv)

    def generar(self):
        md = self.entrada_md.value()
        desv = self.entrada_desv.value()
        self.callback("Normal", self.cantidad, self.intervalos, md, desv)

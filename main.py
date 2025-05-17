import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget

from core.generadores import (
    generar_numeros_pseudoaleatorios,
    darDistExp,
    darDistNorm,
    darDistUnifAB,
)
from core.utilidades import aplicar_estilo

from paginas.PaginaInicio import PaginaInicio
from paginas.PaginaElegirDist import PaginaElegirDist
from paginas.PaginaValsExp import PaginaValsExp
from paginas.PaginaValsNorm import PaginaValsNorm
from paginas.PaginaValsUnif import PaginaValsUnif
from paginas.PaginaResultados import PaginaResultados


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Variables Aleatorias")
        self.setGeometry(100, 100, 800, 900)

        # Layout principal
        main_layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Página inicial
        inicio = PaginaInicio(
            callback_seleccion=self.elegir_dist,
            callback_volver=self.volver,
            callback_cerrar=self.cerrar_aplicacion,
        )
        self.stack.addWidget(inicio)

    def elegir_dist(self):
        elegir = PaginaElegirDist(
            callback_seleccion=self.ir_a_parametros,
            callback_volver=self.volver,
            callback_cerrar=self.cerrar_aplicacion,
        )
        self.stack.addWidget(elegir)
        self.stack.setCurrentWidget(elegir)

    def ir_a_parametros(self, distribucion, cantidad, intervalos):
        self.distribucion = distribucion
        self.cantidad = cantidad
        self.intervalos = intervalos

        if distribucion == "Normal":
            pagina = PaginaValsNorm(
                cantidad,
                intervalos,
                callback_generado=self.ir_a_resultados,
                callback_volver=self.volver,
                callback_cerrar=self.cerrar_aplicacion,
            )
        elif distribucion == "Exponencial Negativa":
            pagina = PaginaValsExp(
                cantidad,
                intervalos,
                callback_generado=self.ir_a_resultados,
                callback_volver=self.volver,
                callback_cerrar=self.cerrar_aplicacion,
            )
        else:  # Uniforme
            pagina = PaginaValsUnif(
                cantidad,
                intervalos,
                callback_generado=self.ir_a_resultados,
                callback_volver=self.volver,
                callback_cerrar=self.cerrar_aplicacion,
            )

        self.stack.addWidget(pagina)
        self.stack.setCurrentWidget(pagina)

    def ir_a_resultados(self, distribucion, cantidad, *params):
        datos = generar_numeros_pseudoaleatorios(cantidad)
        media = None
        desviacion = None
        lmd = None
        val_A = None
        val_B = None
        
        if distribucion == "Normal":
            # PaginaValsNorm te pasa (cantidad, intervalos, media, desviacion)
            datos = darDistNorm(datos, *params[1:])
            media, desviacion = params[1], params[2]
        elif distribucion == "Exponencial Negativa":
            # PaginaValsExp te pasa (cantidad, intervalos, lmd)
            datos = darDistExp(datos, *params[1:])
            lmd, = params[1:]
        else:  # Uniforme
            # PaginaValsUnif te pasa (cantidad, intervalos, A, B)
            datos = darDistUnifAB(datos, *params[1:])
            val_A, val_B = params[1], params[2]

        pagina = PaginaResultados(
            callback_volver=self.volver,
            callback_cerrar=self.cerrar_aplicacion,
            datos=datos,
            nombre_dist=distribucion,
            intervalos=self.intervalos,
            media=media,
            desviacion=desviacion,
            lmd=lmd,
            A=val_A,
            B=val_B,
        )
        self.stack.addWidget(pagina)
        self.stack.setCurrentWidget(pagina)

    def volver(self, pagina_actual):
        self.stack.removeWidget(pagina_actual)
        self.stack.setCurrentIndex(self.stack.count() - 1)

    @staticmethod
    def cerrar_aplicacion(self):
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    aplicar_estilo(app, modo="oscuro")

    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())

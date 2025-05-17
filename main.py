import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from paginas.PaginaInicio import PaginaInicio
from paginas.PaginaElegirDist import PaginaElegirDist
from paginas.PaginaValsExp import PaginaValsExp
from paginas.PaginaValsNorm import PaginaValsNorm
from paginas.PaginaValsUnif import PaginaValsUnif
from paginas.PaginaResultados import PaginaResultados
from core.generadores import generar_numeros_pseudoaleatorios, darDistExp, darDistNorm, darDistUnifAB
from core.utilidades import aplicar_estilo


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Variables Aleatorias")
        self.setGeometry(100, 100, 800, 700)

        self.tema_actual = "oscuro"  # default

        # Layout principal
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Stack principal con las páginas
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Página inicial
        self.pagina_inicio = PaginaInicio(
            self.elegir_dist, self.volver, self.cerrar_aplicacion)
        self.stack.addWidget(self.pagina_inicio)

    def elegir_dist(self):
        pagina_elegir = PaginaElegirDist(
            self.ir_a_parametros, self.volver, self.cerrar_aplicacion)
        self.stack.addWidget(pagina_elegir)
        self.stack.setCurrentWidget(pagina_elegir)

    def ir_a_parametros(self, distribucion, cantidad, intervalos):
        self.distribucion = distribucion
        self.cantidad = cantidad
        self.intervalos = intervalos

        if distribucion == "Normal":
            pagina = PaginaValsNorm(
                cantidad, intervalos, self.ir_a_resultados, self.volver, self.cerrar_aplicacion)
        elif distribucion == "Exponencial Negativa":
            pagina = PaginaValsExp(
                cantidad, intervalos, self.ir_a_resultados, self.volver, self.cerrar_aplicacion)
        elif distribucion == "Uniforme":
            pagina = PaginaValsUnif(
                cantidad, intervalos, self.ir_a_resultados, self.volver, self.cerrar_aplicacion)

        self.stack.addWidget(pagina)
        self.stack.setCurrentWidget(pagina)

    def ir_a_resultados(self, tipo, cantidad, intervalos, *dist_params):
        datos = generar_numeros_pseudoaleatorios(cantidad)
        if tipo == "Normal":
            datos = darDistNorm(datos, *dist_params)
        elif tipo == "Exponencial Negativa":
            datos = darDistExp(datos, *dist_params)
        elif tipo == "Uniforme":
            datos = darDistUnifAB(datos, *dist_params)
        
        pagina_resultados = PaginaResultados(
            self.volver,
            self.cerrar_aplicacion,
            datos,
            tipo,
            intervalos,
            *dist_params
        )
                
        self.stack.addWidget(pagina_resultados)
        self.stack.setCurrentWidget(pagina_resultados)

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

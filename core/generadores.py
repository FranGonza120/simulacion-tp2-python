import random
import numpy as np
from math import sqrt, log, pi, cos, sin, erf, exp
from scipy.stats import chi2 as chi2_dist


def generar_numeros_pseudoaleatorios(n):
    """Genera una lista de n numeros pseudoaleatorios entre 0 y 1."""
    nums = [random.random() for _ in range(n)]
    return nums

def darDistExp(nums, lmd):
    """Transforma una lista de numeros pseudoaleatorios a una lista de numeros
    distribuidos segun la exponencial negativa de parametro lmd.
    """
    for i in range(len(nums)):
        num = round(-1 / lmd * log(nums[i]), 4)
        nums[i] = num
    return nums

def darDistNorm(nums, media, desviacion):
    """Transforma una lista de numeros pseudoaleatorios a una lista de numeros
    distribuidos segun la normal de parametro media y desviacion.
    """
    for i in range(0, len(nums) - 1, 2):
        if i == len(nums) - 1 and i % 2 != 0:
            num1 = nums[i]
            num2 = random.random() * 2 * pi
            n1 = ((sqrt((-2) * (log(num1))) * cos(num2)) * desviacion) + media
            nums[i] = n1
        else:
            num1 = nums[i]
            num2 = nums[i + 1] * 2 * pi
            n1 = ((sqrt((-2) * (log(num1))) * cos(num2)) * desviacion) + media
            n2 = ((sqrt((-2) * (log(num1))) * sin(num2)) * desviacion) + media
            nums[i] = round(n1, 4)
            nums[i + 1] = round(n2, 4)
    return nums

def darDistUnifAB(nums, A, B):
    """Transforma una lista de numeros pseudoaleatorios a una lista de numeros
    distribuidos segun la uniforme en [A, B].
    """
    for i in range(len(nums)):
        # Calculo de X = A + RND*(B - A)
        num = round((B - A) * nums[i] + A, 4)
        nums[i] = num
    return nums

def frecuencias_observadas(datos, n_intervalos):
    """
    Dado un conjunto de datos y un numero de intervalos,
    devuelve una lista de tuplas (li, ls, fo) donde
    - li y ls son los bordes del intervalo
    - fo es la frecuencia observada en ese intervalo
    """
    minim = min(datos)
    maxim = max(datos)

    # Genera “n_intervalos + 1” equidistantes desde minim hasta maxim
    bordes = np.linspace(minim, maxim, n_intervalos+1)
    
    # np.histogram devuelve fo (Frecuencia Observada) 
    # Utilizando el intervalo [li, ls) (excepto el ultimo)
    fo_list, _ = np.histogram(datos, bins=bordes)
    
    resultado = []
    for i in range(n_intervalos):
        li, ls = bordes[i], bordes[i + 1]
        # Lim Inf - Lim Sup - Frec Observada
        resultado.append((li, ls, int(fo_list[i])))
    return resultado

def cdf_exp(x, lmd):
    """CDF (función de distribución acumulativa) de la exponencial negativa."""
    return 1 - exp(-lmd * x)

def cdf_norm(x, media, desviacion):
    """CDF (función de distribución acumulativa) de la normal N(media, desviacion)."""
    return 0.5 * (1 + erf((x - media) / (desviacion * sqrt(2))))

def frecuencias_esperadas(limites, total, distrib, params):
    """
    Para cada (li, ls) en [limites], calcula Feᵢ = [F(ls)-F(li)] * total.
    - distrib: "Uniforme", "Exponencial Negativa" o "Normal"
    - params: (lmd,) para exponencial; (media, desviacion) para normal
    """
    fe = []
    if distrib == "Uniforme":
        fe = [total/len(limites)] * len(limites)
    elif distrib == "Exponencial Negativa":
        lmd, = params
        fe = [(cdf_exp(ls, lmd) - cdf_exp(li, lmd)) * total for li, ls in limites]
    elif distrib == "Normal":
        media, desviacion = params
        fe = [(cdf_norm(ls, media, desviacion) - cdf_norm(li, media, desviacion)) * total for li, ls in limites]
    return fe

def obtener_histograma(datos, intervalos):
    """
    Retorna (frecuencias, bordes) para pasar directamente a matplotlib.
    """
    frecuencias, bordes = np.histogram(datos, bins=intervalos)
    return frecuencias.tolist(), bordes.tolist()

def calcular_clases_chi2(datos, intervalos, distrib, params):
    """
    Calcula FO y FE por clase para χ².
    Devuelve lista de dicts: {'li', 'ls', 'fo', 'fe'}.
    """
    fo_list, bordes = np.histogram(datos, bins=intervalos)
    limites = list(zip(bordes[:-1], bordes[1:]))
    fe_list = frecuencias_esperadas(limites, len(datos), distrib, params)

    clases = [
        {"li": li, "ls": ls, "fo": fo, "fe": fe}
        for (li, ls), fo, fe in zip(limites, fo_list, fe_list)
    ]
    
    return clases

def chi2_critico(k, m, alpha):
    """
    Devuelve (grad_lib, valor crítico χ²)
    según:
     - distrib: "Uniforme", "Exponencial Negativa" o "Normal"
     - intervalos: k
     - alpha: nivel de significancia
    """
    grad_lib = k - 1 - m
    p_crit = chi2_dist.ppf(1 - alpha, grad_lib)
    return grad_lib, p_crit

def chi2_estadistico(observadas, esperadas, param_estimados):
    """
    Calcula χ² = Σ (Oᵢ - Eᵢ)² / Eᵢ y el p-valor.
    """
    chi2 = sum((fo - fe)**2 / fe for fo, fe in zip(observadas, esperadas))
    # grados de libertad (ajustar según parámetros estimados)
    grad_lib = len(observadas) - 1 - param_estimados  
    p_valor = 1 - chi2_dist.cdf(chi2, grad_lib)
    return chi2, p_valor
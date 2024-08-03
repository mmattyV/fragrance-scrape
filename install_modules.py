import sys
import subprocess
import importlib

def instala(modules):
    print("Instalando módulos")
    for m in modules:
        p = m.find("[")
        mi = m if p == -1 else m[:p]
        p = mi.find("==")
        mi = mi if p == -1 else mi[:p]
        try:
            importlib.import_module(mi)
            print(m, "encontrado")
        except ImportError:
            print(m, "No encontrado, instalando...", end="")
            try:
                r = subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", m])
                print("¡hecho!")
            except Exception as e:
                print(f";¡Problema al instalar {m}! ¿seguro que el módulo existe? Error: {e}")
    print("¡Terminado!")

modules = ["selenium", "chromedriver_autoinstaller", "undetected-chromedriver", "beautifulsoup4", "requests", "plotly", "missingno", "statsmodels"]
instala(modules)

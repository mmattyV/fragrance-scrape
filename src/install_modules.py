import sys
import os.path
from subprocess import check_call
import importlib

def instala(modules):
    print("Instalando módulos")
    for m in modules:
        p = m.find("[")
        mi = m if p == -1 else m[:p]
        p = mi.find("==")
        mi = mi if p == -1 else mi[:p]
        torch_loader = importlib.util.find_spec(mi)
        if torch_loader is not None:
            print(m, "encontrado")
        else:
            print(m, "No encontrado, instalando...", end="")
            try:
                r = check_call([sys.executable, "-m", "pip", "install", "--user", m])
                print("¡hecho!")
            except:
                print(";¡Problema al instalar", m, "! ¿seguro que el módulo existe?", sep="")
    print("¡Terminado!")

modules = ["selenium", "chromedriver_autoinstaller"]
instala(modules)

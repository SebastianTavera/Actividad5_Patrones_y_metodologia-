"""Paso 3.3 · La prueba de fuego del caso de estudio "Tipos de Pruebas y Herramientas".

Ejecuta por separado los tres conjuntos de pruebas (equivalencia, valores límite y
ramas) contra una versión de la función y registra casos, cobertura de ramas y fallas.
No modifica domicilio.py: trabaja sobre copias en una carpeta temporal.

    python scripts/prueba_de_fuego.py                         # contra domicilio_equipo.py (raíz) o el ejemplo
    python scripts/prueba_de_fuego.py ruta/domicilio_equipo.py
    python scripts/prueba_de_fuego.py --mutantes              # mutantes de comparación sobre domicilio.py
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONJUNTOS = [
    ("Partición de equivalencia", "test_equivalencia.py"),
    ("Valores límite", "test_valores_limite.py"),
    ("Ramas (Paso 3.2)", "test_ramas.py"),
]

# (clave, descripción, texto original, texto mutado)
MUTANTES = [
    ("M1", "distancia_km <= 0  ->  < 0", "distancia_km <= 0", "distancia_km < 0"),
    ("M2", "distancia_km > 8   ->  >= 8", "distancia_km > 8", "distancia_km >= 8"),
    ("M3", "hora < 6           ->  <= 6", "hora < 6", "hora <= 6"),
    ("M4", "hora > 21          ->  >= 21", "hora > 21", "hora >= 21"),
    ("M5", "tramo 1: <= 2      ->  < 2", "if distancia_km <= 2:", "if distancia_km < 2:"),
    ("M6", "tramo 2: <= 5      ->  < 5", "elif distancia_km <= 5", "elif distancia_km < 5"),
    ("M7", "recargo: >= 19     ->  > 19", "hora >= 19", "hora > 19"),
    ("M8", "frecuente: <= 2    ->  < 2", "and distancia_km <= 2:", "and distancia_km < 2:"),
]


def ejecutar(codigo: str, archivo_prueba: str) -> dict:
    """Corre un conjunto de pruebas con coverage de ramas contra `codigo` (texto de domicilio.py)."""
    with tempfile.TemporaryDirectory() as carpeta:
        destino = Path(carpeta)
        (destino / "domicilio.py").write_text(codigo, encoding="utf-8")
        shutil.copy(RAIZ / archivo_prueba, destino / archivo_prueba)
        run = lambda *a: subprocess.run([sys.executable, "-m", *a], cwd=destino,
                                        capture_output=True, text=True)
        pruebas = run("pytest", "-q", "-p", "no:cacheprovider", "--collect-only", archivo_prueba)
        casos = int(re.search(r"(\d+) tests? collected", pruebas.stdout).group(1))
        resultado = run("coverage", "run", "--branch", "--include=domicilio.py",
                        "-m", "pytest", "-q", "-p", "no:cacheprovider", archivo_prueba)
        run("coverage", "json", "-o", "cov.json")
        totales = json.loads((destino / "cov.json").read_text())["totals"]
        fallas = len(re.findall(r"^FAILED", resultado.stdout, re.M))
        return {"casos": casos, "fallas": fallas,
                "ramas": f"{totales['covered_branches']}/{totales['num_branches']}",
                "pct": 100 * totales["covered_branches"] / totales["num_branches"]}


def prueba_de_fuego(ruta: Path) -> None:
    codigo = ruta.read_text(encoding="utf-8")
    print(f"Versión probada: {ruta.relative_to(RAIZ) if ruta.is_relative_to(RAIZ) else ruta}\n")
    print(f"{'Conjunto de pruebas':<28}{'Casos':>6}{'Ramas cubiertas':>18}{'Fallas':>8}")
    for nombre, archivo in CONJUNTOS:
        r = ejecutar(codigo, archivo)
        ramas = f"{r['ramas']} ({r['pct']:.0f} %)"
        print(f"{nombre:<28}{r['casos']:>6}{ramas:>18}{r['fallas']:>8}")


def mutantes() -> int:
    original = (RAIZ / "domicilio.py").read_text(encoding="utf-8")
    print(f"{'Mutante':<8}{'Cambio':<32}" + "".join(f"{n:<14}" for n in ("Equivalencia", "Val. límite", "Ramas")))
    supervivientes = {a: 0 for _, a in CONJUNTOS}
    for clave, descripcion, buscar, reemplazo in MUTANTES:
        assert original.count(buscar) == 1, f"'{buscar}' no es único en domicilio.py"
        fila = f"{clave:<8}{descripcion:<32}"
        for _, archivo in CONJUNTOS:
            detectado = ejecutar(original.replace(buscar, reemplazo), archivo)["fallas"] > 0
            supervivientes[archivo] += not detectado
            fila += f"{'detecta' if detectado else 'SOBREVIVE':<14}"
        print(fila)
    print(f"\nMutantes que sobreviven: " + ", ".join(
        f"{n} = {supervivientes[a]}" for n, a in CONJUNTOS))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--mutantes"]:
        return mutantes()
    if args:
        ruta = Path(args[0]).resolve()
    else:
        ruta = next(p for p in (RAIZ / "domicilio_equipo.py",
                                RAIZ / "scripts" / "domicilio_equipo_ejemplo.py") if p.exists())
    prueba_de_fuego(ruta)
    return 0


if __name__ == "__main__":
    sys.exit(main())

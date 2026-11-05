"""Prueba de mutación manual (Paso 4.2), automatizada.

Para cada mutante: copia pedido.py con el defecto sembrado a una carpeta temporal,
ejecuta SOLO test_pedido.py contra él y reporta si las pruebas lo detectan.

    python scripts/mutantes.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

MUTANTES = [
    ("M1", "Descuento solo si el subtotal es estrictamente mayor que 100.000",
     "subtotal >= UMBRAL_DESCUENTO", "subtotal > UMBRAL_DESCUENTO"),
    ("M2", "Domicilio también cuando el subtotal es exactamente 50.000",
     "subtotal < UMBRAL_DOMICILIO", "subtotal <= UMBRAL_DOMICILIO"),
    ("M3", "La cantidad 0 deja de considerarse inválida",
     "item.cantidad <= 0", "item.cantidad < 0"),
]


def ejecutar_mutante(original: str, buscar: str, reemplazo: str) -> tuple[bool, str]:
    assert original.count(buscar) == 1, f"No se encontró un único '{buscar}' en pedido.py"
    with tempfile.TemporaryDirectory() as carpeta:
        destino = Path(carpeta)
        (destino / "pedido.py").write_text(original.replace(buscar, reemplazo), encoding="utf-8")
        shutil.copy(RAIZ / "test_pedido.py", destino / "test_pedido.py")
        resultado = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_pedido.py"],
            cwd=destino, capture_output=True, text=True,
        )
        fallidas = [l.split("::")[1].split(" ")[0] for l in resultado.stdout.splitlines()
                    if l.startswith("FAILED")]
        return resultado.returncode != 0, ", ".join(fallidas)


def main() -> int:
    original = (RAIZ / "pedido.py").read_text(encoding="utf-8")
    detectados = 0
    print(f"{'Mutante':<8}{'Resultado':<12}Pruebas que lo detectan")
    for clave, descripcion, buscar, reemplazo in MUTANTES:
        detectado, pruebas = ejecutar_mutante(original, buscar, reemplazo)
        detectados += detectado
        estado = "DETECTADO" if detectado else "SOBREVIVE"
        print(f"{clave:<8}{estado:<12}{pruebas or '-'}")
        print(f"        {descripcion}")
    print(f"\nMutantes detectados: {detectados} de {len(MUTANTES)}")
    return 0 if detectados == len(MUTANTES) else 1


if __name__ == "__main__":
    sys.exit(main())

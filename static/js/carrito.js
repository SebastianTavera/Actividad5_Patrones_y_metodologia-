// Estado del carrito (solo ids y cantidades). Los precios y totales SIEMPRE los
// calcula el backend con pedido.py: el navegador nunca duplica reglas de negocio.
const CLAVE = 'mercabarrio.carrito';
const MAXIMO = 99;

function leer() {
  try {
    const datos = JSON.parse(localStorage.getItem(CLAVE) || '{}');
    return new Map(Object.entries(datos).map(([id, n]) => [Number(id), Number(n)]).filter(([, n]) => n > 0));
  } catch { return new Map(); }
}

class Carrito {
  #items = leer();
  #oyentes = new Set();

  suscribir(fn) { this.#oyentes.add(fn); return () => this.#oyentes.delete(fn); }

  #emitir(cambio) {
    try { localStorage.setItem(CLAVE, JSON.stringify(Object.fromEntries(this.#items))); } catch { /* modo privado */ }
    this.#oyentes.forEach((fn) => fn(cambio));
  }

  cantidad(id) { return this.#items.get(id) || 0; }
  get unidades() { let n = 0; this.#items.forEach((c) => { n += c; }); return n; }
  get vacio() { return this.#items.size === 0; }
  solicitudes() { return [...this.#items].map(([producto_id, cantidad]) => ({ producto_id, cantidad })); }

  fijar(id, cantidad) {
    const antes = this.cantidad(id);
    const nueva = Math.max(0, Math.min(MAXIMO, cantidad));
    if (nueva === antes) return;
    if (nueva === 0) this.#items.delete(id); else this.#items.set(id, nueva);
    this.#emitir({ id, antes, ahora: nueva });
  }

  sumar(id, delta = 1) { this.fijar(id, this.cantidad(id) + delta); }

  vaciar() { this.#items.clear(); this.#emitir({ id: null, antes: 0, ahora: 0 }); }
}

export const carrito = new Carrito();

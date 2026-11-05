// Cliente HTTP de la API. Único módulo que conoce las URLs del backend.
export class ErrorApi extends Error {
  constructor(mensaje, estado) { super(mensaje); this.estado = estado; }
}

let claveAdmin = '';
export const fijarClaveAdmin = (clave) => { claveAdmin = clave; };

async function pedir(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(cuerpo);
  }
  if (ruta.startsWith('/admin')) opciones.headers['X-Admin-Clave'] = claveAdmin;
  let respuesta;
  try {
    respuesta = await fetch(`/api${ruta}`, opciones);
  } catch {
    throw new ErrorApi('No hay conexión con la tienda. Intenta de nuevo.', 0);
  }
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) throw new ErrorApi(datos.error || 'Algo salió mal', respuesta.status);
  return datos;
}

const consulta = (params) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== '' && v != null));
  return q.toString() ? `?${q}` : '';
};

export const api = {
  reglas: () => pedir('GET', '/reglas'),
  categorias: () => pedir('GET', '/categorias'),
  productos: (filtros = {}) => pedir('GET', `/productos${consulta(filtros)}`),
  producto: (id) => pedir('GET', `/productos/${id}`),
  cotizar: (items) => pedir('POST', '/carrito/cotizar', { items }),
  crearPedido: (cliente, items, notas) => pedir('POST', '/pedidos', { cliente, items, notas }),
  misPedidos: (telefono) => pedir('GET', `/pedidos${consulta({ telefono })}`),
  cancelarPedido: (id, telefono) => pedir('POST', `/pedidos/${id}/cancelar`, { telefono }),
  admin: {
    sesion: () => pedir('GET', '/admin/sesion'),
    resumen: () => pedir('GET', '/admin/resumen'),
    pedidos: (estado) => pedir('GET', `/admin/pedidos${consulta({ estado })}`),
    cambiarEstado: (id, estado) => pedir('PATCH', `/admin/pedidos/${id}`, { estado }),
    productos: (q) => pedir('GET', `/admin/productos${consulta({ q })}`),
    crearProducto: (datos) => pedir('POST', '/admin/productos', datos),
    actualizarProducto: (id, datos) => pedir('PUT', `/admin/productos/${id}`, datos),
    eliminarProducto: (id) => pedir('DELETE', `/admin/productos/${id}`),
  },
};

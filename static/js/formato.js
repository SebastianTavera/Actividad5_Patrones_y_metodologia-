// Formato de presentación (pesos colombianos, fechas, HTML seguro).
const pesos = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });
const fecha = new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeStyle: 'short' });

export const dinero = (valor) => pesos.format(Math.round(valor)).replace(/\s/g, '');
export const fechaHora = (iso) => fecha.format(new Date(iso));

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const html = (texto) => String(texto ?? '').replace(/[&<>"']/g, (c) => ESCAPES[c]);

export const ESTADOS = {
  recibido: 'Recibido',
  preparando: 'En preparación',
  en_camino: 'En camino',
  entregado: 'Entregado',
  cancelado: 'Cancelado',
};

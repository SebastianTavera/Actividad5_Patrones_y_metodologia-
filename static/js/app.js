// Punto de entrada: enrutador por hash y composición de las vistas.
import { api } from './api.js';
import { activarReflejo, crearBurbujas, cruzar, moverIndicador } from './anim.js';
import { iniciarAdmin, mostrarAdmin } from './admin.js';
import { iniciarCajon } from './cajon.js';
import { dinero } from './formato.js';
import { iniciarPedidos, mostrarPedidos } from './pedidos.js';
import { iniciarTienda, refrescarTienda, reubicarIndicadorCategorias } from './tienda.js';

const pestanas = document.querySelector('.pestanas');
const VISTAS = {
  tienda: { alMostrar: reubicarIndicadorCategorias },
  pedidos: { alMostrar: mostrarPedidos },
  admin: { alMostrar: mostrarAdmin },
};
let vistaActual = null;

function vistaDesdeHash() {
  const nombre = location.hash.replace(/^#\/?/, '');
  return VISTAS[nombre] ? nombre : 'tienda';
}

async function navegar({ inicial = false } = {}) {
  const nombre = vistaDesdeHash();
  const enlace = pestanas.querySelector(`[data-vista="${nombre}"]`);
  pestanas.querySelectorAll('a').forEach((a) => {
    a.classList.toggle('activa', a === enlace);
    a.toggleAttribute('aria-current', a === enlace);
  });
  moverIndicador(pestanas, enlace, { instantaneo: inicial });
  if (nombre === vistaActual) return;

  const saliente = vistaActual && document.getElementById(`vista-${vistaActual}`);
  const entrante = document.getElementById(`vista-${nombre}`);
  vistaActual = nombre;
  window.scrollTo({ top: 0, behavior: inicial ? 'auto' : 'smooth' });
  await cruzar(saliente, entrante, VISTAS[nombre].alMostrar);
}

async function pintarReglas() {
  try {
    const r = await api.reglas();
    document.querySelectorAll('[data-regla]').forEach((el) => { el.textContent = dinero(r[el.dataset.regla]); });
  } catch { /* se conservan los valores por defecto del HTML */ }
}

function barraAlDesplazar() {
  const barra = document.getElementById('barra');
  const alto = () => barra.classList.toggle('compacta', window.scrollY > 12);
  window.addEventListener('scroll', alto, { passive: true });
  alto();
}

async function iniciar() {
  crearBurbujas(document.querySelector('.burbujas'));
  activarReflejo();
  barraAlDesplazar();

  document.querySelectorAll('.vista').forEach((v) => { v.hidden = true; });
  iniciarCajon({
    comprado: () => refrescarTienda(),
    verPedidos: () => { if (vistaActual === 'pedidos') mostrarPedidos(); else location.hash = '#/pedidos'; },
  });
  iniciarPedidos();
  iniciarAdmin({ inventarioCambiado: () => refrescarTienda() });

  window.addEventListener('hashchange', () => navegar());
  window.addEventListener('resize', () => moverIndicador(pestanas, pestanas.querySelector('.activa'), { instantaneo: true }));

  await document.fonts?.ready;
  navegar({ inicial: true });
  pintarReglas();
  await iniciarTienda();
}

iniciar();

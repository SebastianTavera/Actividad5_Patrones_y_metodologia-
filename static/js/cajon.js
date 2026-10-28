// Cajón lateral: carrito -> datos de entrega -> confirmación.
import { api } from './api.js';
import { cascada, colapsar, contar } from './anim.js';
import { carrito } from './carrito.js';
import { dinero, html } from './formato.js';
import { icono, MAS, MENOS, svgCategoria } from './iconos.js';
import { conCarga, tostada } from './ui.js';

const $ = (id) => document.getElementById(id);
const cajon = $('cajon');
const velo = $('velo');
const lineas = $('lineas-carrito');
const accion = $('accion-cajon');
const textoAccion = accion.querySelector('.boton-texto');
const contador = $('contador-carrito');
const form = $('form-entrega');
const PASOS = ['carrito', 'entrega', 'listo'];
const TITULOS = { carrito: 'Tu carrito', entrega: 'Datos de entrega', listo: 'Confirmación' };

let paso = 'carrito';
let cotizacion = null;
let espera = null;
let version = 0;
let alComprar = () => {};
let alVerPedidos = () => {};

// ---------- Abrir / cerrar ----------

export function abrirCajon() {
  if (cajon.classList.contains('abierto')) return;
  velo.hidden = false;
  velo.offsetWidth;
  velo.classList.add('visible');
  cajon.classList.add('abierto');
  cajon.removeAttribute('inert');
  cajon.setAttribute('aria-hidden', 'false');
  document.body.classList.add('bloqueado');
  if (paso === 'listo') irA('carrito', { instantaneo: true });
  cascada(lineas.children);
  setTimeout(() => $('cerrar-cajon').focus({ preventScroll: true }), 300);
}

export function cerrarCajon() {
  if (!cajon.classList.contains('abierto')) return;
  velo.classList.remove('visible');
  cajon.classList.remove('abierto');
  cajon.setAttribute('inert', '');
  cajon.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('bloqueado');
  velo.addEventListener('transitionend', () => { if (!velo.classList.contains('visible')) velo.hidden = true; }, { once: true });
  $('abrir-carrito').focus({ preventScroll: true });
}

// ---------- Pasos ----------

function irA(destino, { instantaneo = false } = {}) {
  const indice = PASOS.indexOf(destino);
  document.querySelectorAll('.paso').forEach((el) => {
    const i = PASOS.indexOf(el.dataset.paso);
    if (instantaneo) el.style.transition = 'none';
    el.classList.toggle('antes', i < indice);
    el.classList.toggle('despues', i > indice);
    el.inert = i !== indice;
    if (instantaneo) { el.offsetWidth; el.style.transition = ''; }
  });
  paso = destino;
  $('titulo-cajon').textContent = TITULOS[destino];
  $('atras-cajon').hidden = destino !== 'entrega';
  $('resumen').hidden = destino === 'listo';
  actualizarAccion();
  if (destino === 'entrega') setTimeout(() => form.elements.nombre.focus({ preventScroll: true }), 380);
}

function actualizarAccion() {
  const total = cotizacion?.total ?? 0;
  const bloqueado = carrito.vacio || !cotizacion || cotizacion.sin_stock.length > 0;
  accion.disabled = bloqueado;
  textoAccion.textContent = paso === 'entrega'
    ? `Confirmar pedido · ${dinero(total)}`
    : 'Continuar con la entrega';
}

// ---------- Líneas del carrito ----------

function htmlLinea(l, faltante) {
  return `
    <div class="miniatura" style="--h:${icono(l.categoria).h}">${svgCategoria(l.categoria)}</div>
    <div>
      <h4>${html(l.nombre)}</h4>
      <div class="detalle ${faltante ? 'falta' : ''}">${faltante ? `Solo quedan ${faltante.disponible}` : `${dinero(l.precio_final)} c/u${l.gravado ? ' · IVA incl.' : ''}`}</div>
    </div>
    <div class="linea-derecha">
      <span class="linea-importe">${dinero(l.importe_final)}</span>
      <div class="stepper">
        <button data-d="-1" aria-label="Quitar uno de ${html(l.nombre)}">${MENOS}</button>
        <span class="valor">${l.cantidad}</span>
        <button data-d="1" aria-label="Agregar uno de ${html(l.nombre)}">${MAS}</button>
      </div>
    </div>`;
}

/** Reconciliación por id: solo entran/salen con animación las líneas que cambian. */
function pintarLineas(datos) {
  const presentes = new Set();
  const faltantes = new Map(datos.sin_stock.map((f) => [f.producto_id, f]));
  const nuevas = [];
  datos.lineas.forEach((l) => {
    presentes.add(String(l.producto_id));
    let el = lineas.querySelector(`.linea[data-id="${l.producto_id}"]:not(.saliendo)`);
    const contenido = htmlLinea(l, faltantes.get(l.producto_id));
    if (!el) {
      el = document.createElement('div');
      el.className = 'linea';
      el.dataset.id = l.producto_id;
      el.innerHTML = contenido;
      lineas.append(el);
      nuevas.push(el);
    } else {
      const valorPrevio = el.querySelector('.valor').textContent;
      el.innerHTML = contenido;
      if (valorPrevio !== String(l.cantidad)) el.querySelector('.valor').classList.add('cambia');
    }
  });
  lineas.querySelectorAll('.linea:not(.saliendo)').forEach((el) => {
    if (!presentes.has(el.dataset.id)) { el.classList.add('saliendo'); colapsar(el); }
  });
  if (nuevas.length) cascada(nuevas);
}

function pintarResumen(datos) {
  ['subtotal', 'iva', 'domicilio', 'total'].forEach((campo) =>
    contar(document.querySelector(`[data-campo="${campo}"]`), datos[campo], dinero));
  contar(document.querySelector('[data-campo="descuento"]'), -datos.descuento, (v) => (v ? `−${dinero(-v)}` : dinero(0)));
  document.querySelector('[data-fila="descuento"]').classList.toggle('oculto', datos.descuento === 0);

  const textos = {
    domicilio_gratis: (m) => (m.faltante ? `Te faltan <b>${dinero(m.faltante)}</b> para domicilio gratis` : '¡Tienes domicilio gratis!'),
    descuento: (m) => (m.faltante ? `Te faltan <b>${dinero(m.faltante)}</b> para 10 % de descuento` : '¡Ganaste 10 % de descuento!'),
  };
  document.querySelectorAll('.meta').forEach((el) => {
    const m = datos.metas[el.dataset.meta];
    el.classList.toggle('cumplida', m.faltante === 0);
    el.querySelector('.meta-etiqueta').innerHTML = textos[el.dataset.meta](m);
    el.querySelector('.meta-barra i').style.transform = `scaleX(${m.progreso})`;
  });

  const aviso = $('aviso-stock');
  aviso.hidden = datos.sin_stock.length === 0;
  aviso.textContent = datos.sin_stock.length
    ? `Ajusta las cantidades: ${datos.sin_stock.map((f) => `${f.nombre} (quedan ${f.disponible})`).join(', ')}.`
    : '';
  pintarBarra(datos.total);
}

/** Barra fija del celular: cuántos productos llevas y el total, siempre a la vista. */
function pintarBarra(total) {
  const n = carrito.unidades;
  const barra = $('barra-carrito');
  const visible = n > 0;
  barra.classList.toggle('visible', visible);
  barra.tabIndex = visible ? 0 : -1;
  barra.setAttribute('aria-hidden', String(!visible));
  document.body.classList.toggle('con-barra', visible);
  $('barra-unidades').textContent = n;
  $('barra-palabra').textContent = n === 1 ? 'producto' : 'productos';
  contar($('barra-total'), total, dinero, 500);
}

async function cotizar() {
  const mia = ++version;
  const vacio = carrito.vacio;
  $('carrito-vacio').hidden = !vacio;
  $('metas').hidden = vacio;
  if (vacio) {
    cotizacion = { lineas: [], sin_stock: [], subtotal: 0, descuento: 0, iva: 0, domicilio: 0, total: 0,
      metas: { domicilio_gratis: { faltante: 0, progreso: 0 }, descuento: { faltante: 0, progreso: 0 } } };
    pintarLineas(cotizacion);
    pintarResumen(cotizacion);
    if (paso === 'entrega') irA('carrito');
    actualizarAccion();
    return;
  }
  try {
    const datos = await api.cotizar(carrito.solicitudes());
    if (mia !== version) return;
    if (datos.no_disponibles.length) {
      datos.no_disponibles.forEach((id) => carrito.fijar(id, 0));
      tostada('Quitamos de tu carrito productos que ya no están disponibles', 'error');
      return;                                   // fijar() dispara una nueva cotización
    }
    cotizacion = datos;
    pintarLineas(datos);
    pintarResumen(datos);
  } catch (e) {
    if (mia === version) tostada(e.message, 'error');
  }
  actualizarAccion();
}

function alCambiarCarrito({ antes, ahora }) {
  const n = carrito.unidades;
  contador.hidden = n === 0;
  if (contador.textContent !== String(n)) {
    contador.textContent = n;
    if (ahora > antes) { contador.classList.remove('salto'); contador.offsetWidth; contador.classList.add('salto'); }
  }
  clearTimeout(espera);
  espera = setTimeout(cotizar, 90);
}

// ---------- Checkout ----------

function validarFormulario() {
  let primero = null;
  form.querySelectorAll('.campo').forEach((campo) => {
    const input = campo.querySelector('input, textarea');
    let valido = input.checkValidity();
    if (input.name === 'telefono') {
      const digitos = input.value.replace(/\D/g, '').length;
      valido = digitos >= 7 && digitos <= 12;
    }
    campo.classList.remove('invalido');
    if (!valido) { campo.offsetWidth; campo.classList.add('invalido'); primero ??= input; }
  });
  if (primero) {
    $('error-entrega').textContent = 'Revisa los campos marcados.';
    primero.focus();
    return false;
  }
  $('error-entrega').textContent = '';
  return true;
}

async function confirmarPedido() {
  if (!validarFormulario()) return;
  const datos = Object.fromEntries(new FormData(form));
  try {
    const pedido = await conCarga(accion, api.crearPedido(
      { nombre: datos.nombre, telefono: datos.telefono, direccion: datos.direccion },
      carrito.solicitudes(), datos.notas));
    try { localStorage.setItem('mercabarrio.telefono', pedido.cliente.telefono); } catch { /* sin almacenamiento */ }
    $('texto-confirmacion').innerHTML =
      `Tu pedido <b>#${pedido.id}</b> por <b>${dinero(pedido.total)}</b> va en camino a <b>${html(pedido.cliente.direccion)}</b>.`;
    irA('listo');
    carrito.vaciar();
    form.elements.notas.value = '';
    alComprar(pedido);
  } catch (e) {
    $('error-entrega').textContent = e.message;
    tostada(e.message, 'error');
    if (e.estado === 409) { irA('carrito'); cotizar(); }
  }
}

export function iniciarCajon({ comprado, verPedidos }) {
  alComprar = comprado;
  alVerPedidos = verPedidos;
  irA('carrito', { instantaneo: true });

  $('abrir-carrito').addEventListener('click', abrirCajon);
  $('barra-carrito').addEventListener('click', abrirCajon);
  $('cerrar-cajon').addEventListener('click', cerrarCajon);
  velo.addEventListener('click', cerrarCajon);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && cajon.classList.contains('abierto') && document.getElementById('modal-capa').hidden) cerrarCajon();
  });
  $('atras-cajon').addEventListener('click', () => irA('carrito'));
  $('ir-a-tienda').addEventListener('click', () => { cerrarCajon(); location.hash = '#/tienda'; });
  $('ver-mis-pedidos').addEventListener('click', () => { cerrarCajon(); alVerPedidos(); });

  accion.addEventListener('click', () => (paso === 'carrito' ? irA('entrega') : confirmarPedido()));
  form.addEventListener('submit', (e) => { e.preventDefault(); confirmarPedido(); });
  form.addEventListener('input', (e) => e.target.closest('.campo')?.classList.remove('invalido'));

  lineas.addEventListener('click', (e) => {
    const boton = e.target.closest('[data-d]');
    if (!boton) return;
    const id = Number(boton.closest('.linea').dataset.id);
    carrito.sumar(id, Number(boton.dataset.d));
  });

  carrito.suscribir(alCambiarCarrito);
  alCambiarCarrito({ antes: 0, ahora: 0 });
}

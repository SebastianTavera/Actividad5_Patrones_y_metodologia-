// Vista Tienda: catálogo, búsqueda, filtros y detalle de producto.
import { api } from './api.js';
import { cascada, moverIndicador, volar } from './anim.js';
import { carrito } from './carrito.js';
import { dinero, html } from './formato.js';
import { icono, MAS, MENOS, svgCategoria } from './iconos.js';
import { abrirModal, cerrarModal, tostada } from './ui.js';

const $ = (id) => document.getElementById(id);
const grilla = $('grilla');
const chips = $('categorias');
const botonCarrito = $('abrir-carrito');
const POCAS_UNIDADES = 10;

const filtros = { q: '', categoria: '', orden: 'relevancia', impuesto: '' };
let productos = new Map();
let solicitud = 0;

// ---------- Tarjetas ----------

function controlCantidad(p) {
  const n = carrito.cantidad(p.id);
  return `
    <div class="control-cantidad ${n ? 'abierto' : ''}" data-control="${p.id}">
      <button class="menos" data-accion="menos" aria-label="Quitar uno" tabindex="${n ? 0 : -1}">${MENOS}</button>
      <span class="valor" aria-live="polite">${n || ''}</span>
      <button class="mas" data-accion="mas" aria-label="Agregar ${html(p.nombre)}">${MAS}</button>
    </div>`;
}

function tarjeta(p) {
  const pocas = p.stock > 0 && p.stock < POCAS_UNIDADES;
  return `
    <article class="tarjeta vidrio" data-id="${p.id}" tabindex="0" aria-label="${html(p.nombre)}">
      <div class="lienzo" style="--h:${icono(p.categoria).h}">
        ${svgCategoria(p.categoria)}
        <span class="etiqueta ${p.gravado ? '' : 'exento'}">${p.gravado ? '+ IVA 19 %' : 'Canasta básica'}</span>
        ${pocas ? `<span class="etiqueta pocas">Quedan ${p.stock}</span>` : ''}
      </div>
      <div class="tarjeta-info">
        <h3>${html(p.nombre)}</h3>
        <span class="unidad">${html(p.unidad)}</span>
        <div class="tarjeta-pie">
          <span class="precio">${dinero(p.precio)}</span>
          ${p.stock > 0 ? controlCantidad(p) : '<span class="agotado">Agotado</span>'}
        </div>
      </div>
    </article>`;
}

function esqueletos(n = 8) {
  grilla.innerHTML = Array.from({ length: n }, () => '<div class="esqueleto"></div>').join('');
}

async function cargar({ animar = true } = {}) {
  const mia = ++solicitud;
  if (!productos.size) esqueletos();
  let lista;
  try {
    lista = await api.productos(filtros);
  } catch (e) {
    tostada(e.message, 'error');
    return;
  }
  if (mia !== solicitud) return;           // llegó una búsqueda más reciente
  productos = new Map(lista.map((p) => [p.id, p]));
  if (animar && grilla.children.length && !grilla.querySelector('.esqueleto')) {
    await grilla.animate([{ opacity: 1 }, { opacity: 0, transform: 'translateY(6px)' }],
      { duration: 160, easing: 'ease-out', fill: 'forwards' }).finished;
    if (mia !== solicitud) return;
  }
  grilla.getAnimations().forEach((a) => a.cancel());
  grilla.innerHTML = lista.map(tarjeta).join('');
  $('sin-resultados').hidden = lista.length > 0;
  cascada(grilla.children);
}

export const producto = (id) => productos.get(id);

/** Refleja el carrito en los controles de cantidad sin volver a dibujar la grilla. */
function sincronizarControl(control, n) {
  if (!control) return;
  control.classList.toggle('abierto', n > 0);
  control.querySelector('.menos').tabIndex = n ? 0 : -1;
  const valor = control.querySelector('.valor');
  if (valor.textContent !== String(n || '')) {
    valor.textContent = n || '';
    valor.classList.remove('cambia'); valor.offsetWidth; valor.classList.add('cambia');
  }
}

function alCambiarCarrito({ id }) {
  const ids = id == null ? [...productos.keys()] : [id];
  ids.forEach((pid) => {
    document.querySelectorAll(`[data-control="${pid}"]`).forEach((c) => sincronizarControl(c, carrito.cantidad(pid)));
  });
}

function agregar(id, boton) {
  const p = productos.get(id);
  if (!p) return;
  if (carrito.cantidad(id) >= p.stock) {
    tostada(`Solo quedan ${p.stock} unidades de ${p.nombre}`, 'error');
    return;
  }
  const primera = carrito.cantidad(id) === 0;
  carrito.sumar(id, 1);
  if (primera) {
    volar(boton, botonCarrito).then(() => {
      botonCarrito.classList.remove('recibe'); botonCarrito.offsetWidth; botonCarrito.classList.add('recibe');
    });
  }
}

// ---------- Detalle de producto ----------

function abrirDetalle(id, origen) {
  const p = productos.get(id);
  if (!p) return;
  let cantidad = Math.max(1, carrito.cantidad(id));
  const contenido = `
    <div class="detalle-producto">
      <div class="lienzo" style="--h:${icono(p.categoria).h}">
        ${svgCategoria(p.categoria)}
        <span class="etiqueta ${p.gravado ? '' : 'exento'}">${p.gravado ? '+ IVA 19 %' : 'Canasta básica · sin IVA'}</span>
      </div>
      <div class="detalle-info">
        <span class="categoria">${html(p.categoria)}</span>
        <h2 id="modal-titulo">${html(p.nombre)}</h2>
        <p>${html(p.descripcion || 'Producto de la tienda del barrio.')}</p>
        <span class="precio">${dinero(p.precio)}</span>
        <div class="datos">
          <div class="dato"><small>Presentación</small><b>${html(p.unidad)}</b></div>
          <div class="dato"><small>Disponibles</small><b>${p.stock > 0 ? `${p.stock} und` : 'Agotado'}</b></div>
          <div class="dato"><small>Impuesto</small><b>${p.gravado ? 'IVA 19 %' : 'Exento'}</b></div>
          <div class="dato"><small>Precio con IVA</small><b>${dinero(p.gravado ? p.precio * 1.19 : p.precio)}</b></div>
        </div>
        ${p.stock > 0 ? `
        <div class="detalle-acciones">
          <div class="stepper">
            <button data-d="-1" aria-label="Menos">${MENOS}</button>
            <span class="valor">${cantidad}</span>
            <button data-d="1" aria-label="Más">${MAS}</button>
          </div>
          <button class="boton primario" data-agregar autofocus>${carrito.cantidad(id) ? 'Actualizar carrito' : 'Agregar al carrito'}</button>
        </div>` : ''}
      </div>
    </div>`;
  abrirModal(contenido, origen, {
    montar: (m) => {
      const valor = m.querySelector('.stepper .valor');
      m.querySelectorAll('[data-d]').forEach((b) => b.addEventListener('click', () => {
        cantidad = Math.max(1, Math.min(p.stock, cantidad + Number(b.dataset.d)));
        valor.textContent = cantidad;
        valor.classList.remove('cambia'); valor.offsetWidth; valor.classList.add('cambia');
      }));
      m.querySelector('[data-agregar]')?.addEventListener('click', (e) => {
        const nuevo = carrito.cantidad(id) === 0;
        carrito.fijar(id, cantidad);
        if (nuevo) volar(e.currentTarget, botonCarrito);
        tostada(`${p.nombre} × ${cantidad} en tu carrito`);
        cerrarModal();
      });
    },
  });
}

// ---------- Filtros ----------

async function pintarCategorias() {
  const categorias = await api.categorias().catch(() => []);
  const botones = ['', ...categorias].map((c) =>
    `<button class="chip ${c === filtros.categoria ? 'activo' : ''}" role="tab" data-categoria="${html(c)}">${html(c || 'Todo')}</button>`).join('');
  chips.insertAdjacentHTML('beforeend', botones);
  requestAnimationFrame(() => moverIndicador(chips, chips.querySelector('.chip.activo'), { instantaneo: true }));
}

function eventos() {
  let espera;
  $('buscar').addEventListener('input', (e) => {
    clearTimeout(espera);
    espera = setTimeout(() => { filtros.q = e.target.value; cargar(); }, 220);
  });
  $('filtro-impuesto').addEventListener('change', (e) => { filtros.impuesto = e.target.value; cargar(); });
  $('orden').addEventListener('change', (e) => { filtros.orden = e.target.value; cargar(); });

  chips.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip || chip.classList.contains('activo')) return;
    chips.querySelector('.chip.activo')?.classList.remove('activo');
    chip.classList.add('activo');
    chip.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    moverIndicador(chips, chip);
    filtros.categoria = chip.dataset.categoria;
    cargar();
  });

  grilla.addEventListener('click', (e) => {
    const tarjetaEl = e.target.closest('.tarjeta');
    if (!tarjetaEl) return;
    const id = Number(tarjetaEl.dataset.id);
    const accion = e.target.closest('[data-accion]')?.dataset.accion;
    if (accion === 'mas') agregar(id, e.target.closest('button'));
    else if (accion === 'menos') carrito.sumar(id, -1);
    else if (!e.target.closest('.control-cantidad')) abrirDetalle(id, tarjetaEl);
  });
  grilla.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.classList.contains('tarjeta')) abrirDetalle(Number(e.target.dataset.id), e.target);
  });

  window.addEventListener('resize', () => moverIndicador(chips, chips.querySelector('.chip.activo'), { instantaneo: true }));
}

export async function iniciarTienda() {
  eventos();
  carrito.suscribir(alCambiarCarrito);
  await Promise.all([pintarCategorias(), cargar({ animar: false })]);
}

/** Recarga existencias (p. ej. después de comprar) sin animar toda la grilla. */
export const refrescarTienda = () => cargar({ animar: false });
export const reubicarIndicadorCategorias = () =>
  moverIndicador(chips, chips.querySelector('.chip.activo'), { instantaneo: true });

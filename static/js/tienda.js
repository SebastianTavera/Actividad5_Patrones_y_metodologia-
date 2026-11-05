// Vista Tienda: catálogo, búsqueda, filtros, favoritos y detalle de producto.
import { api } from './api.js';
import { colapsar, deslizable, moverIndicador, revelar, volar } from './anim.js';
import { carrito } from './carrito.js';
import { dinero, html } from './formato.js';
import { CORAZON, icono, MAS, MENOS, svgCategoria } from './iconos.js';
import { abrirModal, cerrarModal, tostada } from './ui.js';

const $ = (id) => document.getElementById(id);
const grilla = $('grilla');
const chips = $('categorias');
const botonCarrito = $('abrir-carrito');
const POCAS_UNIDADES = 10;
const FAVORITOS = '__favoritos';

const filtros = { q: '', categoria: '', orden: 'relevancia', impuesto: '' };
let productos = new Map();
let solicitud = 0;
const yaMostrados = new Set();   // cada producto se anima solo la primera vez que aparece

// Preferencias locales de quien navega (no son datos del negocio).
function leerLocal(clave, porDefecto) {
  try { return JSON.parse(localStorage.getItem(clave)) ?? porDefecto; } catch { return porDefecto; }
}
function guardarLocal(clave, valor) {
  try { localStorage.setItem(clave, JSON.stringify(valor)); } catch { /* sin almacenamiento */ }
}
const favoritos = new Set(leerLocal('mercabarrio.favoritos', []));
let vista = leerLocal('mercabarrio.vista', 'lista');

// ---------- Piezas de la tarjeta ----------

const miles = new Intl.NumberFormat('es-CO');

function valoracion(p) {
  if (!p.resenas) return '<div class="valoracion"><span>Sin reseñas</span></div>';
  return `
    <div class="valoracion" aria-label="${p.calificacion.toFixed(1)} de 5 estrellas, ${p.resenas} reseñas">
      <span class="estrellas" style="--nota:${p.calificacion}"></span>
      <b>${p.calificacion.toFixed(1)}</b><span>(${miles.format(p.resenas)})</span>
    </div>`;
}

function precios(p) {
  return `
    <div class="precios">
      <span class="precio">${dinero(p.precio_final)}</span>
      ${p.descuento_pct ? `<s>${dinero(p.precio_anterior_final)}</s>` : ''}
    </div>
    <small class="nota-impuesto">${p.gravado ? 'IVA incluido' : 'Canasta básica · sin IVA'}</small>`;
}

function controlCantidad(p) {
  const n = carrito.cantidad(p.id);
  return `
    <div class="control-cantidad ${n ? 'abierto' : ''}" data-control="${p.id}">
      <button class="agregar" data-accion="mas" tabindex="${n ? -1 : 0}">Agregar</button>
      <div class="stepper-linea">
        <button class="menos" data-accion="menos" aria-label="Quitar uno de ${html(p.nombre)}" tabindex="${n ? 0 : -1}">${MENOS}</button>
        <span class="valor" aria-live="polite">${n || ''}</span>
        <button class="mas" data-accion="mas" aria-label="Agregar otro ${html(p.nombre)}" tabindex="${n ? 0 : -1}">${MAS}</button>
      </div>
    </div>`;
}

function botonFavorito(p) {
  const activo = favoritos.has(p.id);
  return `<button class="favorito ${activo ? 'activo' : ''}" data-accion="favorito" aria-pressed="${activo}"
    aria-label="${activo ? 'Quitar de' : 'Agregar a'} favoritos">${CORAZON}</button>`;
}

function tarjeta(p) {
  const pocas = p.stock > 0 && p.stock < POCAS_UNIDADES;
  const extra = pocas ? `<span class="aviso-pocas">Quedan ${p.stock}</span>` : '';
  return `
    <article class="producto vidrio" data-id="${p.id}" tabindex="0" aria-label="${html(p.nombre)}">
      <div class="producto-media">
        ${p.descuento_pct ? `<span class="descuento">-${p.descuento_pct}%</span>` : ''}
        <div class="lienzo" style="--h:${icono(p.categoria).h}">${svgCategoria(p.categoria)}</div>
      </div>
      <div class="producto-info">
        <h3>${html(p.nombre)}</h3>
        <span class="unidad">${html(p.unidad)}${extra ? ' · ' : ''}${extra}</span>
        ${valoracion(p)}
      </div>
      <div class="producto-precio">${precios(p)}</div>
      <div class="acciones-compra">
        ${p.stock > 0 ? controlCantidad(p) : '<div class="agotado">Agotado</div>'}
        ${botonFavorito(p)}
      </div>
    </article>`;
}

function esqueletos(n = 6) {
  grilla.innerHTML = Array.from({ length: n }, () => '<div class="esqueleto"></div>').join('');
}

// ---------- Carga y dibujo ----------

function textoVacio() {
  if (filtros.categoria === FAVORITOS && !favoritos.size) {
    return 'Aún no tienes favoritos. Toca el ♥ de un producto para guardarlo aquí.';
  }
  return 'No encontramos productos con esos filtros.';
}

function actualizarConteo() {
  const n = grilla.querySelectorAll('.producto:not(.saliendo)').length;
  $('conteo').textContent = n ? `${n} producto${n === 1 ? '' : 's'}` : '';
  $('sin-resultados').hidden = n > 0;
  $('sin-resultados').textContent = textoVacio();
}

async function cargar() {
  const mia = ++solicitud;
  if (!productos.size) esqueletos();
  const enFavoritos = filtros.categoria === FAVORITOS;
  let lista;
  try {
    lista = await api.productos({ ...filtros, categoria: enFavoritos ? '' : filtros.categoria });
  } catch (e) {
    tostada(e.message, 'error');
    return;
  }
  if (mia !== solicitud) return;           // llegó una búsqueda más reciente
  if (enFavoritos) lista = lista.filter((p) => favoritos.has(p.id));
  productos = new Map(lista.map((p) => [p.id, p]));
  grilla.innerHTML = lista.map(tarjeta).join('');
  actualizarConteo();
  revelar([...grilla.children].filter((el) => !yaMostrados.has(el.dataset.id)));
  lista.forEach((p) => yaMostrados.add(String(p.id)));
}

export const producto = (id) => productos.get(id);

/** Refleja el carrito en los controles de cantidad sin volver a dibujar la grilla. */
function sincronizarControl(control, n) {
  if (!control) return;
  control.classList.toggle('abierto', n > 0);
  control.querySelector('.agregar').tabIndex = n ? -1 : 0;
  control.querySelectorAll('.stepper-linea button').forEach((b) => { b.tabIndex = n ? 0 : -1; });
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

// ---------- Favoritos ----------

function pintarChipFavoritos() {
  const chip = chips.querySelector(`[data-categoria="${FAVORITOS}"] .chip-cuenta`);
  if (chip) chip.textContent = favoritos.size || '';
}

function alternarFavorito(id, boton) {
  const p = productos.get(id);
  const activo = !favoritos.has(id);
  if (activo) favoritos.add(id); else favoritos.delete(id);
  guardarLocal('mercabarrio.favoritos', [...favoritos]);
  pintarChipFavoritos();
  document.querySelectorAll(`.producto[data-id="${id}"] .favorito, #modal .favorito`).forEach((b) => {
    b.classList.toggle('activo', activo);
    b.setAttribute('aria-pressed', activo);
    b.setAttribute('aria-label', `${activo ? 'Quitar de' : 'Agregar a'} favoritos`);
  });
  if (activo) { boton.classList.remove('late'); boton.offsetWidth; boton.classList.add('late'); }
  if (!activo && filtros.categoria === FAVORITOS) {        // en la vista de favoritos, la fila se va
    const fila = grilla.querySelector(`.producto[data-id="${id}"]`);
    if (fila) { fila.classList.add('saliendo'); colapsar(fila).then(actualizarConteo); }
  }
  tostada(activo ? `${p.nombre} en tus favoritos` : `${p.nombre} salió de favoritos`);
}

// ---------- Detalle de producto (aquí sí va la ficha completa) ----------

function abrirDetalle(id, origen) {
  const p = productos.get(id);
  if (!p) return;
  let cantidad = Math.max(1, carrito.cantidad(id));
  const ficha = p.caracteristicas.length
    ? `<ul class="specs">${p.caracteristicas.map(([etiqueta, valor]) =>
      `<li>${html(etiqueta)}<b>${html(valor)}</b></li>`).join('')}</ul>`
    : '';
  const contenido = `
    <div class="detalle-producto">
      <div class="producto-media">
        ${p.descuento_pct ? `<span class="descuento">-${p.descuento_pct}%</span>` : ''}
        <div class="lienzo" style="--h:${icono(p.categoria).h}">${svgCategoria(p.categoria)}</div>
      </div>
      <div class="detalle-info aparece">
        <span class="categoria">${html(p.categoria)}</span>
        <h2 id="modal-titulo">${html(p.nombre)}</h2>
        ${valoracion(p)}
        <p>${html(p.descripcion || 'Producto de la tienda del barrio.')}</p>
        ${precios(p)}
        ${ficha}
        <div class="datos">
          <div class="dato"><small>Presentación</small><b>${html(p.unidad)}</b></div>
          <div class="dato"><small>Disponibles</small><b>${p.stock > 0 ? `${p.stock} und` : 'Agotado'}</b></div>
          <div class="dato"><small>Impuesto</small><b>${p.gravado ? 'IVA 19 %' : 'Exento'}</b></div>
          <div class="dato"><small>Precio sin IVA</small><b>${dinero(p.precio)}</b></div>
        </div>
        ${p.stock > 0 ? `
        <div class="detalle-acciones">
          <div class="stepper">
            <button data-d="-1" aria-label="Menos">${MENOS}</button>
            <span class="valor">${cantidad}</span>
            <button data-d="1" aria-label="Más">${MAS}</button>
          </div>
          <button class="boton primario" data-agregar autofocus>${carrito.cantidad(id) ? 'Actualizar carrito' : 'Agregar al carrito'}</button>
          ${botonFavorito(p)}
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
      m.querySelector('.favorito')?.addEventListener('click', (e) => alternarFavorito(id, e.currentTarget));
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

// ---------- Filtros y vista ----------

async function pintarCategorias() {
  const categorias = await api.categorias().catch(() => []);
  const chip = (valor, texto) =>
    `<button class="chip ${valor === filtros.categoria ? 'activo' : ''}" role="tab" data-categoria="${html(valor)}">${texto}</button>`;
  chips.insertAdjacentHTML('beforeend', [
    chip('', 'Todo'),
    chip(FAVORITOS, `<span class="chip-corazon">♥</span> Favoritos <span class="chip-cuenta">${favoritos.size || ''}</span>`),
    ...categorias.map((c) => chip(c, html(c))),
  ].join(''));
  requestAnimationFrame(() => {
    moverIndicador(chips, chips.querySelector('.chip.activo'), { instantaneo: true });
    deslizable(chips);
  });
}

function aplicarVista(nueva, { animar = false } = {}) {
  vista = nueva;
  guardarLocal('mercabarrio.vista', vista);
  document.querySelectorAll('.vista-boton').forEach((b) => {
    b.classList.toggle('activo', b.dataset.vista === vista);
    b.setAttribute('aria-pressed', b.dataset.vista === vista);
  });
  if (!animar) { grilla.classList.toggle('cuadricula', vista === 'cuadricula'); return; }
  grilla.animate([{ opacity: 1 }, { opacity: 0, transform: 'scale(.99)' }], { duration: 140, easing: 'ease-out' })
    .finished.then(() => {
      grilla.classList.toggle('cuadricula', vista === 'cuadricula');
      grilla.animate([{ opacity: 0, transform: 'scale(.99)' }, { opacity: 1, transform: 'none' }],
        { duration: 260, easing: 'cubic-bezier(.22,1,.36,1)' });
    });
}

function eventos() {
  let espera;
  $('buscar').addEventListener('input', (e) => {
    clearTimeout(espera);
    espera = setTimeout(() => { filtros.q = e.target.value; cargar(); }, 220);
  });
  $('filtro-impuesto').addEventListener('change', (e) => { filtros.impuesto = e.target.value; cargar(); });
  $('orden').addEventListener('change', (e) => { filtros.orden = e.target.value; cargar(); });
  document.querySelectorAll('.vista-boton').forEach((b) =>
    b.addEventListener('click', () => { if (b.dataset.vista !== vista) aplicarVista(b.dataset.vista, { animar: true }); }));

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
    const tarjetaEl = e.target.closest('.producto');
    if (!tarjetaEl) return;
    const id = Number(tarjetaEl.dataset.id);
    const accion = e.target.closest('[data-accion]')?.dataset.accion;
    if (accion === 'mas') agregar(id, e.target.closest('button'));
    else if (accion === 'menos') carrito.sumar(id, -1);
    else if (accion === 'favorito') alternarFavorito(id, e.target.closest('button'));
    else if (!e.target.closest('.acciones-compra')) abrirDetalle(id, tarjetaEl.querySelector('.lienzo'));
  });
  grilla.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.target.classList.contains('producto')) {
      abrirDetalle(Number(e.target.dataset.id), e.target.querySelector('.lienzo'));
    }
  });

  window.addEventListener('resize', () => moverIndicador(chips, chips.querySelector('.chip.activo'), { instantaneo: true }));
}

export async function iniciarTienda() {
  aplicarVista(vista);
  eventos();
  carrito.suscribir(alCambiarCarrito);
  await Promise.all([pintarCategorias(), cargar()]);
}

/** Recarga existencias (p. ej. después de comprar) sin repetir animaciones. */
export const refrescarTienda = () => cargar();
export const reubicarIndicadorCategorias = () =>
  moverIndicador(chips, chips.querySelector('.chip.activo'), { instantaneo: true });

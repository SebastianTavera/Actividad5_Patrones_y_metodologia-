// Componentes de interfaz reutilizables: tostadas, modal y confirmación.
import { crecerDesde, encogerHacia, esperar } from './anim.js';
import { CERRAR } from './iconos.js';
import { html } from './formato.js';

const tostadas = document.getElementById('tostadas');
export function tostada(mensaje, tipo = 'ok') {
  const t = document.createElement('div');
  t.className = `tostada ${tipo === 'error' ? 'error' : ''}`;
  t.innerHTML = `<i>${tipo === 'error' ? '!' : '✓'}</i><span>${html(mensaje)}</span>`;
  tostadas.append(t);
  setTimeout(() => {
    t.classList.add('sale');
    t.addEventListener('animationend', () => t.remove(), { once: true });
  }, tipo === 'error' ? 4200 : 2600);
}

const capa = document.getElementById('modal-capa');
const modal = document.getElementById('modal');
let origen = null;
let alCerrar = null;
let abierto = false;
let generacion = 0;

/** Abre el modal haciendo que crezca desde `elementoOrigen` (FLIP). */
export async function abrirModal(contenido, elementoOrigen, { cerrar, ancho = '', montar } = {}) {
  generacion += 1;
  modal.getAnimations().forEach((a) => a.cancel());
  origen = elementoOrigen || null;
  modal.style.width = ancho;
  alCerrar = cerrar || null;
  modal.innerHTML = `<button class="icono-boton cerrar-modal" aria-label="Cerrar">${CERRAR}</button>`;
  if (typeof contenido === 'string') modal.insertAdjacentHTML('beforeend', contenido); else modal.append(contenido);
  modal.querySelector('.cerrar-modal').addEventListener('click', () => cerrarModal());
  montar?.(modal);
  capa.hidden = false;
  document.body.classList.add('bloqueado');
  abierto = true;
  capa.offsetWidth;
  capa.classList.add('visible');
  await crecerDesde(modal, origen?.isConnected ? origen.getBoundingClientRect() : null);
  modal.querySelector('[autofocus]')?.focus();
  return modal;
}

export async function cerrarModal(resultado) {
  if (!abierto) return;
  abierto = false;
  const propia = generacion;
  const fn = alCerrar; alCerrar = null;
  capa.classList.remove('visible');
  await encogerHacia(modal, origen?.isConnected ? origen.getBoundingClientRect() : null);
  fn?.(resultado);
  if (propia !== generacion) return;   // otro modal se abrió mientras este se cerraba
  capa.hidden = true;
  modal.getAnimations().forEach((a) => a.cancel());
  modal.innerHTML = '';
  document.body.classList.remove('bloqueado');
  origen?.focus?.({ preventScroll: true });
}

capa.addEventListener('pointerdown', (e) => { if (e.target === capa) cerrarModal(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && abierto) cerrarModal(); });

export function confirmar(titulo, texto, { aceptar = 'Confirmar', peligro = false, origen: el } = {}) {
  return new Promise((resolver) => {
    abrirModal(`
      <div style="padding:14px 8px 4px; max-width:420px">
        <h2 class="modal-titulo" id="modal-titulo">${html(titulo)}</h2>
        <p style="margin:0 6px 22px; color:var(--texto-2)">${html(texto)}</p>
        <div style="display:flex; gap:10px; justify-content:flex-end">
          <button class="boton fantasma" data-r="no">Volver</button>
          <button class="boton ${peligro ? 'peligro' : 'primario'}" data-r="si" autofocus>${html(aceptar)}</button>
        </div>
      </div>`, el, {
      ancho: 'min(460px, 100%)',
      cerrar: (r) => resolver(r === true),
      montar: (m) => {
        m.querySelector('[data-r="si"]').addEventListener('click', () => cerrarModal(true));
        m.querySelector('[data-r="no"]').addEventListener('click', () => cerrarModal(false));
      },
    });
  });
}

/** Pone un botón en estado de carga mientras se resuelve la promesa. */
export async function conCarga(boton, promesa) {
  boton.classList.add('cargando');
  boton.disabled = true;
  try { return await promesa; } finally {
    await esperar(120);
    boton.classList.remove('cargando');
    boton.disabled = false;
  }
}

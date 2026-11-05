// Vista Mis pedidos: seguimiento por teléfono y cancelación.
import { api } from './api.js';
import { cascada, cuadro } from './anim.js';
import { dinero, fechaHora, html, ESTADOS } from './formato.js';
import { confirmar, conCarga, tostada } from './ui.js';

const $ = (id) => document.getElementById(id);
const lista = $('lista-pedidos');
const input = $('telefono-consulta');
const HITOS = ['recibido', 'preparando', 'en_camino', 'entregado'];
const CANCELABLES = new Set(['recibido', 'preparando']);

function lineaDeTiempo(estado) {
  const actual = HITOS.indexOf(estado);
  return `<div class="linea-tiempo">${HITOS.map((h, i) => `
    <div class="hito" style="--i:${i}" data-hecho="${i <= actual}" ${i === actual ? 'data-actual' : ''}>
      <i></i><span>${ESTADOS[h]}</span>
    </div>`).join('')}</div>`;
}

function tarjetaPedido(p) {
  const unidades = p.lineas.reduce((n, l) => n + l.cantidad, 0);
  return `
    <article class="pedido vidrio" data-id="${p.id}">
      <div class="pedido-cabecera">
        <h3>Pedido #${p.id}</h3>
        <span class="pedido-total">${dinero(p.total)}</span>
      </div>
      <time datetime="${p.creado}">${fechaHora(p.creado)} · ${unidades} producto${unidades === 1 ? '' : 's'}</time>
      ${p.estado === 'cancelado'
        ? '<div class="pedido-cancelado">Este pedido fue cancelado y no se cobró.</div>'
        : lineaDeTiempo(p.estado)}
      <div class="pedido-items">${p.lineas.map((l) => `<span>${l.cantidad} × ${html(l.nombre)}</span>`).join('')}</div>
      <div class="pedido-pie">
        <span>Subtotal ${dinero(p.subtotal)}${p.descuento ? ` · Descuento −${dinero(p.descuento)}` : ''} · IVA ${dinero(p.iva)} · Domicilio ${p.domicilio ? dinero(p.domicilio) : 'gratis'}</span>
        ${CANCELABLES.has(p.estado) ? '<button class="boton peligro mini" data-cancelar>Cancelar pedido</button>' : ''}
      </div>
    </article>`;
}

/** Los hitos se marcan después de pintar, para que la línea "se llene" con transición. */
async function encenderHitos(raiz) {
  await cuadro();
  raiz.querySelectorAll('.hito[data-hecho="true"]').forEach((h) => h.classList.add('hecho'));
  raiz.querySelectorAll('.hito[data-actual]').forEach((h) => h.classList.add('actual'));
}

async function consultar(boton) {
  const telefono = input.value.trim();
  if (!telefono) return;
  try {
    const pedidos = await (boton ? conCarga(boton, api.misPedidos(telefono)) : api.misPedidos(telefono));
    try { localStorage.setItem('mercabarrio.telefono', telefono); } catch { /* sin almacenamiento */ }
    lista.innerHTML = pedidos.length
      ? pedidos.map(tarjetaPedido).join('')
      : '<p class="vacio">No encontramos pedidos con ese teléfono.</p>';
    cascada(lista.children);
    encenderHitos(lista);
  } catch (e) {
    tostada(e.message, 'error');
  }
}

export function iniciarPedidos() {
  try { input.value = localStorage.getItem('mercabarrio.telefono') || ''; } catch { /* sin almacenamiento */ }
  $('form-consulta').addEventListener('submit', (e) => {
    e.preventDefault();
    consultar(e.submitter);
  });
  lista.addEventListener('click', async (e) => {
    const boton = e.target.closest('[data-cancelar]');
    if (!boton) return;
    const tarjeta = boton.closest('.pedido');
    const id = Number(tarjeta.dataset.id);
    const ok = await confirmar(`¿Cancelar el pedido #${id}?`,
      'Los productos vuelven al inventario y no se te cobrará nada.', { aceptar: 'Sí, cancelar', peligro: true, origen: boton });
    if (!ok) return;
    try {
      const actualizado = await conCarga(boton, api.cancelarPedido(id, input.value));
      const nuevo = document.createElement('div');
      nuevo.innerHTML = tarjetaPedido(actualizado);
      const reemplazo = nuevo.firstElementChild;
      tarjeta.replaceWith(reemplazo);
      cascada([reemplazo]);
      tostada(`Pedido #${id} cancelado`);
    } catch (err) {
      tostada(err.message, 'error');
    }
  });
}

/** Al entrar a la vista se consulta automáticamente si ya conocemos el teléfono. */
export function mostrarPedidos() {
  try { input.value = localStorage.getItem('mercabarrio.telefono') || input.value; } catch { /* sin almacenamiento */ }
  if (input.value) consultar(); else lista.innerHTML = '';
}


// Vista Admin: indicadores, gestión de pedidos, inventario y reporte.
import { api, fijarClaveAdmin } from './api.js';
import { cascada, contar, cruzar, moverIndicador } from './anim.js';
import { dinero, fechaHora, html, ESTADOS } from './formato.js';
import { abrirModal, cerrarModal, confirmar, conCarga, tostada } from './ui.js';

const $ = (id) => document.getElementById(id);
const CLAVE_SESION = 'mercabarrio.admin';
const ACCIONES = { preparando: 'Preparar', en_camino: 'Enviar', entregado: 'Entregado', cancelado: 'Cancelar' };
const segmentos = document.querySelector('.segmentos');
const chipsEstado = $('filtro-estados');

let panelActual = 'admin-pedidos';
let estadoFiltro = '';
let inventario = [];
let alCambiarInventario = () => {};

function reubicarIndicadores() {
  moverIndicador(segmentos, segmentos.querySelector('.activo'), { instantaneo: true });
  moverIndicador(chipsEstado, chipsEstado.querySelector('.activo'), { instantaneo: true });
}

// ---------- Sesión ----------

async function entrar(clave, boton) {
  fijarClaveAdmin(clave);
  try {
    await (boton ? conCarga(boton, api.admin.sesion()) : api.admin.sesion());
  } catch (e) {
    fijarClaveAdmin('');
    try { sessionStorage.removeItem(CLAVE_SESION); } catch { /* sin almacenamiento */ }
    if (boton) {
      tostada(e.estado === 401 ? 'Clave incorrecta' : e.message, 'error');
      const campo = $('clave-admin').closest('.campo');
      campo.classList.remove('invalido'); campo.offsetWidth; campo.classList.add('invalido');
    }
    return false;
  }
  try { sessionStorage.setItem(CLAVE_SESION, clave); } catch { /* sin almacenamiento */ }
  await cruzar($('form-login'), $('panel-admin'), reubicarIndicadores);
  refrescar();
  return true;
}

async function salir() {
  fijarClaveAdmin('');
  try { sessionStorage.removeItem(CLAVE_SESION); } catch { /* sin almacenamiento */ }
  $('clave-admin').value = '';
  await cruzar($('panel-admin'), $('form-login'));
}

// ---------- KPIs ----------

async function pintarKpis() {
  const r = await api.admin.resumen();
  const kpis = $('kpis');
  const datos = [
    ['ingresos', 'Ingresos', r.ingresos, dinero],
    ['pedidos', 'Pedidos', r.pedidos, String],
    ['ticket', 'Ticket promedio', r.ticket_promedio, dinero],
    ['pendientes', 'Por despachar', r.pendientes, String],
  ];
  if (!kpis.children.length) {
    kpis.innerHTML = datos.map(([k, t]) => `<div class="kpi vidrio"><small>${t}</small><b data-kpi="${k}">0</b></div>`).join('');
    cascada(kpis.children);
  }
  datos.forEach(([k, , v, f]) => contar(kpis.querySelector(`[data-kpi="${k}"]`), v, f, 900));
  return r;
}

// ---------- Pedidos ----------

function filaPedido(p) {
  const acciones = p.siguientes_estados
    .sort((a, b) => (a === 'cancelado') - (b === 'cancelado'))
    .map((e) => `<button class="boton mini ${e === 'cancelado' ? 'peligro' : 'fantasma'}" data-estado="${e}">${ACCIONES[e]}</button>`)
    .join('');
  return `
    <div class="fila-pedido vidrio" data-id="${p.id}">
      <span class="num">#${p.id}</span>
      <div class="quien"><b>${html(p.cliente.nombre)}</b><small>${html(p.cliente.telefono)} · ${html(p.cliente.direccion)}</small></div>
      <div class="que">${p.lineas.map((l) => `${l.cantidad}× ${html(l.nombre)}`).join(', ')}<br><small>${fechaHora(p.creado)}${p.notas ? ` · “${html(p.notas)}”` : ''}</small></div>
      <span class="estado ${p.estado}">${ESTADOS[p.estado]}</span>
      <span class="monto">${dinero(p.total)}</span>
      <div class="acciones">${acciones}</div>
    </div>`;
}

async function pintarPedidos() {
  const pedidos = await api.admin.pedidos(estadoFiltro);
  const tabla = $('tabla-pedidos');
  tabla.innerHTML = pedidos.length ? pedidos.map(filaPedido).join('') : '<p class="vacio">No hay pedidos en este estado.</p>';
  cascada(tabla.children);
}

function pintarChipsEstado() {
  const opciones = ['', ...Object.keys(ESTADOS)];
  chipsEstado.insertAdjacentHTML('beforeend', opciones.map((e) =>
    `<button class="chip ${e === estadoFiltro ? 'activo' : ''}" data-estado="${e}">${e ? ESTADOS[e] : 'Todos'}</button>`).join(''));
}

// ---------- Inventario ----------

function filaProducto(p) {
  return `
    <tr data-id="${p.id}">
      <td><b>${html(p.nombre)}</b><br><small style="color:var(--texto-3)">${html(p.unidad)}</small></td>
      <td>${html(p.categoria)}</td>
      <td>${p.gravado ? 'IVA 19 %' : '<span style="color:var(--exito)">Exento</span>'}</td>
      <td class="num">${dinero(p.precio)}</td>
      <td class="num"><span class="${p.stock < 10 ? 'bajo' : ''}">${p.stock}</span></td>
      <td><div class="acciones">
        <button class="boton mini fantasma" data-editar>Editar</button>
        <button class="boton mini peligro" data-eliminar>Retirar</button>
      </div></td>
    </tr>`;
}

async function pintarInventario() {
  inventario = await api.admin.productos($('buscar-inventario').value);
  $('tabla-inventario').innerHTML = `
    <table>
      <thead><tr><th>Producto</th><th>Categoría</th><th>Impuesto</th><th style="text-align:right">Precio</th><th style="text-align:right">Stock</th><th></th></tr></thead>
      <tbody>${inventario.map(filaProducto).join('')}</tbody>
    </table>`;
  cascada($('tabla-inventario').querySelectorAll('tbody tr'), { maximo: 20 });
}

function formularioProducto(p) {
  p ??= {};
  const categorias = [...new Set(inventario.map((x) => x.categoria))];
  return `
    <h2 class="modal-titulo" id="modal-titulo">${p.id ? 'Editar producto' : 'Nuevo producto'}</h2>
    <form class="form-producto" novalidate>
      <label class="campo completo"><span>Nombre</span><input name="nombre" required value="${html(p.nombre)}" autofocus></label>
      <label class="campo"><span>Precio (COP, sin IVA)</span><input name="precio" type="number" min="1" step="1" required value="${p.precio ?? ''}"></label>
      <label class="campo"><span>Stock</span><input name="stock" type="number" min="0" step="1" required value="${p.stock ?? 0}"></label>
      <label class="campo"><span>Categoría</span><input name="categoria" list="lista-categorias" required value="${html(p.categoria)}">
        <datalist id="lista-categorias">${categorias.map((c) => `<option value="${html(c)}">`).join('')}</datalist></label>
      <label class="campo"><span>Presentación</span><input name="unidad" value="${html(p.unidad ?? 'und')}"></label>
      <label class="campo completo"><span>Descripción</span><textarea name="descripcion" rows="2">${html(p.descripcion)}</textarea></label>
      <label class="interruptor completo"><input type="checkbox" name="gravado" ${p.gravado ?? true ? 'checked' : ''}> Producto gravado con IVA 19 % (desmarcar si es canasta básica)</label>
      <p class="error-form completo" role="alert"></p>
      <div class="acciones">
        <button type="button" class="boton fantasma" data-cancelar>Cancelar</button>
        <button type="submit" class="boton primario"><span class="boton-texto">${p.id ? 'Guardar cambios' : 'Crear producto'}</span><span class="girador"></span></button>
      </div>
    </form>`;
}

function editarProducto(producto, origen) {
  abrirModal(formularioProducto(producto), origen, {
    ancho: 'min(620px, 100%)',
    montar: (m) => {
      const form = m.querySelector('form');
      m.querySelector('[data-cancelar]').addEventListener('click', () => cerrarModal());
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const d = new FormData(form);
        const datos = {
          nombre: d.get('nombre'), precio: Number(d.get('precio')), stock: Number(d.get('stock')),
          categoria: d.get('categoria'), unidad: d.get('unidad'), descripcion: d.get('descripcion'),
          gravado: d.get('gravado') === 'on',
        };
        try {
          await conCarga(e.submitter, producto?.id
            ? api.admin.actualizarProducto(producto.id, datos)
            : api.admin.crearProducto(datos));
          tostada(producto?.id ? 'Producto actualizado' : 'Producto creado');
          cerrarModal();
          pintarInventario();
          alCambiarInventario();
        } catch (err) {
          form.querySelector('.error-form').textContent = err.message;
        }
      });
    },
  });
}

// ---------- Reporte ----------

async function pintarReporte() {
  const r = await api.admin.resumen();
  const maxVendido = Math.max(1, ...r.mas_vendidos.map((v) => v.unidades));
  const totalEstados = Math.max(1, ...Object.values(r.por_estado));
  const barras = (items) => items.map(([etiqueta, valor, max], i) => `
    <div class="barra-dato"><span>${etiqueta}</span><b>${valor}</b>
      <div class="pista"><i style="--i:${i}; width:${(valor / max) * 100}%"></i></div></div>`).join('');
  $('reporte').innerHTML = `
    <div class="vidrio"><h3>Más vendidos</h3>${r.mas_vendidos.length
      ? barras(r.mas_vendidos.map((v) => [html(v.nombre), v.unidades, maxVendido]))
      : '<p class="vacio">Aún no hay ventas.</p>'}</div>
    <div class="vidrio"><h3>Pedidos por estado</h3>${barras(Object.entries(r.por_estado).map(([e, n]) => [ESTADOS[e], n, totalEstados]))}</div>
    <div class="vidrio"><h3>Impuestos</h3><p style="margin:0;color:var(--texto-2)">IVA recaudado en pedidos vigentes</p><b style="font-size:28px">${dinero(r.iva_recaudado)}</b></div>
    <div class="vidrio"><h3>Stock bajo (menos de 10)</h3>${r.stock_bajo.length
      ? r.stock_bajo.map((p) => `<div class="barra-dato"><span>${html(p.nombre)}</span><b style="color:var(--alerta)">${p.stock}</b></div>`).join('')
      : '<p class="vacio">Todo el inventario está bien abastecido.</p>'}</div>`;
  cascada($('reporte').children);
}

// ---------- Navegación interna ----------

const PINTORES = { 'admin-pedidos': pintarPedidos, 'admin-inventario': pintarInventario, 'admin-reporte': pintarReporte };

async function refrescar() {
  try {
    await Promise.all([pintarKpis(), PINTORES[panelActual]()]);
  } catch (e) {
    if (e.estado === 401) salir();
    tostada(e.message, 'error');
  }
}

async function cambiarPanel(id) {
  if (id === panelActual) return;
  const anterior = $(panelActual);
  panelActual = id;
  // Los datos se piden en paralelo a la transición: el panel entra ya con contenido.
  const carga = PINTORES[id]().catch((e) => tostada(e.message, 'error'));
  await Promise.all([cruzar(anterior, $(id), reubicarIndicadores), carga]);
}

export function iniciarAdmin({ inventarioCambiado }) {
  alCambiarInventario = inventarioCambiado;
  pintarChipsEstado();

  $('form-login').addEventListener('submit', (e) => {
    e.preventDefault();
    entrar($('clave-admin').value, e.submitter);
  });
  $('salir-admin').addEventListener('click', salir);

  segmentos.addEventListener('click', (e) => {
    const b = e.target.closest('[data-panel]');
    if (!b || b.classList.contains('activo')) return;
    segmentos.querySelector('.activo').classList.remove('activo');
    b.classList.add('activo');
    moverIndicador(segmentos, b);
    cambiarPanel(b.dataset.panel);
  });

  chipsEstado.addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip || chip.classList.contains('activo')) return;
    chipsEstado.querySelector('.activo')?.classList.remove('activo');
    chip.classList.add('activo');
    moverIndicador(chipsEstado, chip);
    estadoFiltro = chip.dataset.estado;
    pintarPedidos().catch((err) => tostada(err.message, 'error'));
  });

  $('tabla-pedidos').addEventListener('click', async (e) => {
    const b = e.target.closest('[data-estado]');
    if (!b) return;
    const fila = b.closest('.fila-pedido');
    const id = Number(fila.dataset.id);
    if (b.dataset.estado === 'cancelado') {
      const ok = await confirmar(`¿Cancelar el pedido #${id}?`, 'Las unidades volverán al inventario.',
        { aceptar: 'Cancelar pedido', peligro: true, origen: b });
      if (!ok) return;
    }
    try {
      const p = await conCarga(b, api.admin.cambiarEstado(id, b.dataset.estado));
      const temporal = document.createElement('div');
      temporal.innerHTML = filaPedido(p);
      const nueva = temporal.firstElementChild;
      fila.replaceWith(nueva);
      cascada([nueva]);
      tostada(`Pedido #${id}: ${ESTADOS[p.estado]}`);
      pintarKpis();
      if (p.estado === 'cancelado') alCambiarInventario();
    } catch (err) {
      tostada(err.message, 'error');
    }
  });

  let espera;
  $('buscar-inventario').addEventListener('input', () => {
    clearTimeout(espera);
    espera = setTimeout(() => pintarInventario().catch((e) => tostada(e.message, 'error')), 220);
  });
  $('nuevo-producto').addEventListener('click', (e) => editarProducto(null, e.currentTarget));
  $('tabla-inventario').addEventListener('click', async (e) => {
    const fila = e.target.closest('tr[data-id]');
    if (!fila) return;
    const producto = inventario.find((p) => p.id === Number(fila.dataset.id));
    if (e.target.closest('[data-editar]')) editarProducto(producto, fila);
    if (e.target.closest('[data-eliminar]')) {
      const ok = await confirmar(`¿Retirar "${producto.nombre}"?`, 'Dejará de mostrarse en la tienda. Los pedidos anteriores no cambian.',
        { aceptar: 'Retirar', peligro: true, origen: e.target.closest('button') });
      if (!ok) return;
      try {
        await api.admin.eliminarProducto(producto.id);
        fila.animate([{ opacity: 1 }, { opacity: 0, transform: 'translateX(30px)' }],
          { duration: 320, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'forwards' }).finished.then(() => fila.remove());
        tostada('Producto retirado');
        alCambiarInventario();
      } catch (err) {
        tostada(err.message, 'error');
      }
    }
  });

  window.addEventListener('resize', reubicarIndicadores);
}

/** Al entrar a la vista: restaura la sesión guardada o muestra el acceso. */
export async function mostrarAdmin() {
  let clave = '';
  try { clave = sessionStorage.getItem(CLAVE_SESION) || ''; } catch { /* sin almacenamiento */ }
  if (clave && $('panel-admin').hidden) await entrar(clave);
  else if (!$('panel-admin').hidden) refrescar();
  requestAnimationFrame(reubicarIndicadores);
}

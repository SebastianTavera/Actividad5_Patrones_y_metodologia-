// Coreografía de movimiento. Todas las animaciones comparten las mismas curvas
// (las mismas variables de styles.css) para que cada transición conecte con la siguiente.
export const SALIDA = 'cubic-bezier(.22, 1, .36, 1)';
export const SUAVE = 'cubic-bezier(.65, 0, .35, 1)';

export const reducido = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const duracion = (ms) => (reducido() ? 1 : ms);
export const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
export const cuadro = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));

/** Desliza la "píldora" de un grupo de pestañas/chips hasta el elemento activo. */
export function moverIndicador(contenedor, activo, { instantaneo = false } = {}) {
  const indicador = contenedor.querySelector(':scope > [class$="-indicador"]');
  if (!indicador) return;
  if (!activo) { indicador.style.opacity = '0'; return; }
  if (instantaneo) indicador.style.transition = 'none';
  indicador.style.opacity = '1';
  indicador.style.width = `${activo.offsetWidth}px`;
  indicador.style.transform = `translateX(${activo.offsetLeft}px)`;
  if (instantaneo) { indicador.offsetWidth; indicador.style.transition = ''; }
}

/** Entrada en cascada: cada elemento aparece 45 ms después del anterior. */
export function cascada(elementos, { maximo = 14 } = {}) {
  [...elementos].forEach((el, i) => {
    el.style.setProperty('--i', Math.min(i, maximo));
    el.classList.remove('entra');
    el.offsetWidth;
    el.classList.add('entra');
    el.addEventListener('animationend', () => el.classList.remove('entra'), { once: true });
  });
}

/** Cuenta un número desde su valor actual hasta el nuevo con desaceleración exponencial. */
const conteos = new WeakMap();
export function contar(el, hasta, formatear, ms = 650) {
  const desde = conteos.get(el)?.valor ?? hasta;
  cancelAnimationFrame(conteos.get(el)?.raf);
  if (desde === hasta || reducido()) {
    el.textContent = formatear(hasta);
    conteos.set(el, { valor: hasta });
    return;
  }
  const inicio = performance.now();
  const estado = { valor: desde };
  const paso = (ahora) => {
    const t = Math.min((ahora - inicio) / ms, 1);
    const curva = t === 1 ? 1 : 1 - 2 ** (-10 * t);
    estado.valor = Math.round(desde + (hasta - desde) * curva);
    el.textContent = formatear(estado.valor);
    if (t < 1) estado.raf = requestAnimationFrame(paso);
  };
  conteos.set(el, estado);
  estado.raf = requestAnimationFrame(paso);
}

/** Un punto de luz vuela en arco desde el botón pulsado hasta el carrito. */
export function volar(origen, destino) {
  if (reducido()) return Promise.resolve();
  const a = origen.getBoundingClientRect();
  const b = destino.getBoundingClientRect();
  const x0 = a.left + a.width / 2, y0 = a.top + a.height / 2;
  const x1 = b.left + b.width / 2, y1 = b.top + b.height / 2;
  const cx = (x0 + x1) / 2, cy = Math.min(y0, y1) - 120;
  const punto = document.createElement('div');
  punto.className = 'vuelo';
  document.body.append(punto);
  const cuadros = Array.from({ length: 13 }, (_, i) => {
    const t = i / 12;
    const x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1;
    const y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t ** 2 * y1;
    const escala = 1 + Math.sin(t * Math.PI) * 0.35 - t * 0.55;
    return { transform: `translate3d(${x}px, ${y}px, 0) scale(${escala})`, opacity: t > 0.92 ? 0 : 1 };
  });
  return punto.animate(cuadros, { duration: 720, easing: SUAVE }).finished.then(() => punto.remove());
}

/** Cambio de vista: la saliente se difumina hacia arriba, la entrante emerge desde abajo. */
export async function cruzar(saliente, entrante, alMostrar) {
  if (saliente && saliente !== entrante && !saliente.hidden) {
    await saliente.animate(
      [{ opacity: 1, transform: 'none', filter: 'blur(0)' },
       { opacity: 0, transform: 'translate3d(0,-10px,0)', filter: 'blur(6px)' }],
      { duration: duracion(220), easing: SALIDA, fill: 'forwards' }).finished;
    saliente.hidden = true;
    saliente.getAnimations().forEach((a) => a.cancel());
  }
  entrante.hidden = false;
  alMostrar?.();
  return entrante.animate(
    [{ opacity: 0, transform: 'translate3d(0,16px,0)', filter: 'blur(6px)' },
     { opacity: 1, transform: 'none', filter: 'blur(0)' }],
    { duration: duracion(520), easing: SALIDA }).finished;
}

/** FLIP: el elemento crece desde el rectángulo de origen hasta su posición final. */
export function crecerDesde(el, rectOrigen) {
  const destino = el.getBoundingClientRect();
  if (!rectOrigen || reducido()) {
    return el.animate([{ opacity: 0, transform: 'scale(.96)' }, { opacity: 1, transform: 'none' }],
      { duration: duracion(360), easing: SALIDA }).finished;
  }
  const dx = rectOrigen.left - destino.left, dy = rectOrigen.top - destino.top;
  const sx = rectOrigen.width / destino.width, sy = rectOrigen.height / destino.height;
  return el.animate([
    { transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})`, opacity: 0.6, borderRadius: '22px' },
    { transform: 'none', opacity: 1 },
  ], { duration: 560, easing: SALIDA }).finished;
}

export function encogerHacia(el, rectDestino) {
  const actual = el.getBoundingClientRect();
  if (!rectDestino || !rectDestino.width || reducido()) {
    return el.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: 'scale(.96)' }],
      { duration: duracion(240), easing: SALIDA, fill: 'forwards' }).finished;
  }
  const dx = rectDestino.left - actual.left, dy = rectDestino.top - actual.top;
  const sx = rectDestino.width / actual.width, sy = rectDestino.height / actual.height;
  return el.animate([
    { transform: 'none', opacity: 1 },
    { transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})`, opacity: 0 },
  ], { duration: 420, easing: SALIDA, fill: 'forwards' }).finished;
}

/** Sale deslizando y luego colapsa su altura, para que la lista se cierre sin saltos. */
export function colapsar(el) {
  const alto = el.offsetHeight;
  const estilo = getComputedStyle(el);
  return el.animate([
    { opacity: 1, transform: 'none', height: `${alto}px`, marginBottom: estilo.marginBottom },
    { opacity: 0, transform: 'translateX(40px) scale(.97)', height: `${alto}px`, marginBottom: estilo.marginBottom, offset: 0.5 },
    { opacity: 0, transform: 'translateX(40px) scale(.97)', height: '0px', marginBottom: '0px', paddingTop: '0px', paddingBottom: '0px' },
  ], { duration: duracion(520), easing: SALIDA, fill: 'forwards' }).finished.then(() => el.remove());
}

/** Reflejo líquido: el brillo del vidrio sigue al puntero. */
export function activarReflejo() {
  let pendiente = null;
  document.addEventListener('pointermove', (e) => {
    pendiente = e;
    requestAnimationFrame(() => {
      if (!pendiente) return;
      const vidrio = pendiente.target.closest?.('.vidrio');
      if (vidrio) {
        const r = vidrio.getBoundingClientRect();
        vidrio.style.setProperty('--mx', `${pendiente.clientX - r.left}px`);
        vidrio.style.setProperty('--my', `${pendiente.clientY - r.top}px`);
      }
      pendiente = null;
    });
  }, { passive: true });
}

/** Fondo: dos luces difusas siguen al puntero con inercia (la segunda, más lenta). */
export function activarLuz(principal, eco) {
  if (reducido()) return;
  const destino = { x: innerWidth * 0.5, y: innerHeight * 0.3 };
  const a = { ...destino }, b = { ...destino };
  let quieto = true;
  addEventListener('pointermove', (e) => { destino.x = e.clientX; destino.y = e.clientY; quieto = false; }, { passive: true });
  const t0 = performance.now();
  const paso = (ahora) => {
    if (quieto) {                       // sin puntero (táctil): deriva lenta
      const t = (ahora - t0) / 1000;
      destino.x = innerWidth * (0.5 + 0.25 * Math.sin(t * 0.21));
      destino.y = innerHeight * (0.35 + 0.15 * Math.cos(t * 0.17));
    }
    a.x += (destino.x - a.x) * 0.08; a.y += (destino.y - a.y) * 0.08;
    b.x += (innerWidth - destino.x - b.x) * 0.025; b.y += (innerHeight * 0.9 - destino.y * 0.4 - b.y) * 0.025;
    principal.style.transform = `translate3d(${a.x}px, ${a.y}px, 0)`;
    eco.style.transform = `translate3d(${b.x}px, ${b.y}px, 0)`;
    requestAnimationFrame(paso);
  };
  requestAnimationFrame(paso);
}

/** Aparición rápida y escalonada al entrar en pantalla. Quien llama decide qué elementos
 *  son nuevos: los que ya se vieron aparecen sin animación. */
let observador = null;
export function revelar(elementos) {
  const lista = [...elementos];
  if (!lista.length || reducido() || !('IntersectionObserver' in window)) return;
  observador ??= new IntersectionObserver((entradas) => {
    entradas.filter((e) => e.isIntersecting).forEach((e, orden) => {
      const el = e.target;
      observador.unobserve(el);
      el.style.setProperty('--i', Math.min(orden, 8));
      el.classList.add('aparece');
      setTimeout(() => el.classList.remove('revelable', 'aparece'), 1000 + Math.min(orden, 8) * 35);
    });
  }, { rootMargin: '0px 0px -4% 0px', threshold: 0.05 });
  lista.forEach((el) => { el.classList.add('revelable'); observador.observe(el); });
}

/** Difumina los bordes de una fila deslizable para indicar que hay más contenido a los lados. */
export function deslizable(el) {
  const actualizar = () => {
    const resto = el.scrollWidth - el.clientWidth - el.scrollLeft;
    el.classList.toggle('hay-izquierda', el.scrollLeft > 4);
    el.classList.toggle('hay-derecha', resto > 4);
  };
  el.addEventListener('scroll', actualizar, { passive: true });
  addEventListener('resize', actualizar);
  actualizar();
}

/** Onda que nace donde se pulsa cualquier botón principal. */
export function activarOndas() {
  document.addEventListener('pointerdown', (e) => {
    const boton = e.target.closest('.boton, .agregar');
    if (!boton || boton.disabled || reducido()) return;
    const r = boton.getBoundingClientRect();
    const tam = Math.max(r.width, r.height) * 2.2;
    const onda = document.createElement('span');
    onda.className = 'onda';
    Object.assign(onda.style, { width: `${tam}px`, height: `${tam}px`,
      left: `${e.clientX - r.left - tam / 2}px`, top: `${e.clientY - r.top - tam / 2}px` });
    boton.append(onda);
    onda.addEventListener('animationend', () => onda.remove(), { once: true });
  });
}

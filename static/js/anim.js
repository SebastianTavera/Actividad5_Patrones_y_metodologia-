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

export function crearBurbujas(contenedor, cantidad = 16) {
  if (reducido()) return;
  for (let i = 0; i < cantidad; i++) {
    const b = document.createElement('span');
    const tam = 4 + Math.random() * 14;
    Object.assign(b.style, {
      width: `${tam}px`, height: `${tam}px`, left: `${Math.random() * 100}%`,
      animationDuration: `${16 + Math.random() * 22}s`, animationDelay: `${-Math.random() * 30}s`,
    });
    contenedor.append(b);
  }
}

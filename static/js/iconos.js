// Ilustraciones lineales por categoría; todas dentro de la paleta marina (tono = hue).
const ICONOS = {
  'Despensa': { h: 192, svg: '<path d="M7 4h10"/><path d="M8 4v3c-2 1-3 3-3 5v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6c0-2-1-4-3-5V4"/><path d="M5 13h14"/>' },
  'Lácteos y huevos': { h: 206, svg: '<path d="M8 3h8v3l3 4v10a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V10l3-4z"/><path d="M5 10h14"/><path d="M8 6h8"/>' },
  'Frutas y verduras': { h: 172, svg: '<path d="M12 7c-2-2-7-2-7 4s3 10 5 10c1 0 1.2-.6 2-.6s1 .6 2 .6c2 0 5-4 5-10s-5-6-7-4z"/><path d="M12 7c0-2 1-4 3-4"/>' },
  'Bebidas': { h: 198, svg: '<path d="M10 2h4v3c0 1 2 2 2 5v10a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2V10c0-3 2-4 2-5z"/><path d="M8 12h8M8 17h8"/>' },
  'Aseo': { h: 214, svg: '<rect x="5" y="9" width="14" height="11" rx="3"/><path d="M9 9V6h6v3"/><circle cx="16" cy="3.5" r="1.2"/><circle cx="19.5" cy="5.5" r=".9"/>' },
  'Snacks': { h: 184, svg: '<circle cx="12" cy="12" r="9"/><circle cx="9" cy="9" r=".9"/><circle cx="15" cy="10" r=".9"/><circle cx="10.5" cy="15" r=".9"/><circle cx="15.5" cy="15.5" r=".8"/>' },
};
const GENERICO = { h: 200, svg: '<path d="M6 7h12l-1 13H7z"/><path d="M9 7a3 3 0 0 1 6 0"/>' };

export const icono = (categoria) => ICONOS[categoria] || GENERICO;
export const svgCategoria = (categoria) => `<svg viewBox="0 0 24 24" aria-hidden="true">${icono(categoria).svg}</svg>`;

export const MAS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>';
export const MENOS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/></svg>';
export const CERRAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
export const CORAZON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.4C1.5 7.9 3.6 4.5 7 4.5c2 0 3.6 1.1 5 3 1.4-1.9 3-3 5-3 3.4 0 5.5 3.4 4.3 6.6-1.8 4.8-9.3 9.4-9.3 9.4z"/></svg>';

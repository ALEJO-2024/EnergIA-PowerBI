import { paleta } from "./tema";

const tooltip = document.createElement("div");
tooltip.className = "tooltip";
document.body.appendChild(tooltip);

function mostrar(x: number, y: number, texto: string) {
  tooltip.style.display = "block";
  tooltip.textContent = texto;
  const margen = 14;
  const ancho = tooltip.offsetWidth;
  const alto = tooltip.offsetHeight;
  const left = Math.min(x + margen, window.innerWidth - ancho - 8);
  const top = Math.min(y + margen, window.innerHeight - alto - 8);
  tooltip.style.left = left + "px";
  tooltip.style.top = top + "px";
}

function ocultar() {
  tooltip.style.display = "none";
}

function medida(canvas: HTMLCanvasElement, alto: number) {
  const ancho = canvas.parentElement?.clientWidth ?? 640;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.floor(ancho * dpr);
  canvas.height = Math.floor(alto * dpr);
  canvas.style.width = "100%";
  canvas.style.height = alto + "px";
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("El navegador no dibujó el gráfico");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, ancho, alto);
  ctx.font = "12px IBM Plex Sans";
  return { ctx, ancho, alto };
}

function eje(valor: number): string {
  const absoluto = Math.abs(valor);
  if (absoluto >= 1_000_000) return (valor / 1_000_000).toFixed(1).replace(".", ",") + " M";
  if (absoluto >= 10_000) return Math.round(valor / 1000) + " mil";
  if (absoluto >= 1000) return (valor / 1000).toFixed(1).replace(".", ",") + " mil";
  return String(Math.round(valor));
}

function escuchar(canvas: HTMLCanvasElement, zonas: { x: number; y: number; w: number; h: number; texto: string }[]) {
  canvas.onmousemove = (evento) => {
    const rect = canvas.getBoundingClientRect();
    const x = evento.clientX - rect.left;
    const y = evento.clientY - rect.top;
    const zona = zonas.find((item) => x >= item.x && x <= item.x + item.w && y >= item.y && y <= item.y + item.h);
    if (!zona) {
      ocultar();
      return;
    }
    mostrar(evento.clientX, evento.clientY, zona.texto);
  };
  canvas.onmouseleave = ocultar;
}

type Serie = { nombre: string; color: string; valores: number[]; detalle?: string[] };

export function linea(
  canvas: HTMLCanvasElement,
  etiquetas: string[],
  series: Serie[],
  alto = 250,
  opciones: { ejesSeparados?: boolean; desdeCero?: boolean; marca?: number | null } = {},
) {
  const colores = paleta();
  const ejesSeparados = opciones.ejesSeparados ?? false;
  const desdeCero = opciones.desdeCero ?? true;
  const { ctx, ancho } = medida(canvas, alto);
  const pad = { l: 58, r: ejesSeparados ? 58 : 12, t: 16, b: 28 };
  const topes = series.map((serie) => Math.max(...serie.valores, 1));
  const pisos = series.map((serie) => (desdeCero ? 0 : Math.min(...serie.valores)));
  const tope = Math.max(...topes);
  const piso = desdeCero ? 0 : Math.min(...pisos);
  const n = Math.max(etiquetas.length, 1);
  const paso = (ancho - pad.l - pad.r) / Math.max(n - 1, 1);
  const base = alto - pad.b;
  const zonaH = alto - pad.t - pad.b;
  const yDe = (valor: number, indice: number) => {
    const arriba = ejesSeparados ? topes[indice] : tope;
    const abajo = ejesSeparados ? pisos[indice] : piso;
    return base - ((valor - abajo) / (arriba - abajo || 1)) * zonaH;
  };
  ctx.strokeStyle = colores.linea;
  for (let i = 0; i < 4; i++) {
    const y = pad.t + (zonaH * i) / 3;
    ctx.beginPath();
    ctx.moveTo(pad.l, y);
    ctx.lineTo(ancho - pad.r, y);
    ctx.stroke();
    const fraccion = 1 - i / 3;
    ctx.fillStyle = series[0]?.color ?? colores.tinta;
    const izquierda = ejesSeparados ? pisos[0] + (topes[0] - pisos[0]) * fraccion : piso + (tope - piso) * fraccion;
    ctx.fillText(eje(izquierda), 4, y + 4);
    if (ejesSeparados && series[1]) {
      ctx.fillStyle = series[1].color;
      ctx.fillText(eje(pisos[1] + (topes[1] - pisos[1]) * fraccion), ancho - pad.r + 8, y + 4);
    }
  }
  ctx.fillStyle = colores.tinta;
  etiquetas.forEach((etiqueta, i) => {
    if (n > 12 && i % 2) return;
    ctx.fillText(etiqueta, pad.l + i * paso - 8, alto - 8);
  });
  if (opciones.marca != null && opciones.marca >= 0) {
    const x = pad.l + opciones.marca * paso;
    ctx.save();
    ctx.strokeStyle = colores.marca;
    ctx.setLineDash([3, 4]);
    ctx.beginPath();
    ctx.moveTo(x, pad.t);
    ctx.lineTo(x, base);
    ctx.stroke();
    ctx.restore();
  }
  series.forEach((serie, indice) => {
    ctx.beginPath();
    ctx.strokeStyle = serie.color;
    ctx.lineWidth = 2;
    serie.valores.forEach((valor, i) => {
      const x = pad.l + i * paso;
      const y = yDe(valor, indice);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    serie.valores.forEach((valor, i) => {
      const x = pad.l + i * paso;
      const y = yDe(valor, indice);
      ctx.fillStyle = serie.color;
      ctx.beginPath();
      ctx.arc(x, y, i === opciones.marca ? 5 : 3, 0, Math.PI * 2);
      ctx.fill();
    });
  });
  const zonas = etiquetas.map((etiqueta, i) => ({
    x: pad.l + i * paso - paso / 2,
    y: pad.t,
    w: paso,
    h: zonaH,
    texto: `${etiqueta}\n${series.map((serie) => `${serie.nombre}: ${serie.detalle?.[i] ?? eje(serie.valores[i])}`).join("\n")}`,
  }));
  escuchar(canvas, zonas);
}

export function barras(canvas: HTMLCanvasElement, etiquetas: string[], valores: number[], color?: string, alto = 250) {
  const colores = paleta();
  const relleno = color ?? colores.teal;
  const { ctx, ancho } = medida(canvas, alto);
  const pad = { l: 58, r: 12, t: 16, b: 36 };
  const maximo = Math.max(1, ...valores);
  const n = valores.length || 1;
  const hueco = (ancho - pad.l - pad.r) / n;
  const base = alto - pad.b;
  const zonaH = alto - pad.t - pad.b;
  ctx.fillStyle = colores.tinta;
  ctx.fillText(eje(maximo), 4, pad.t + 8);
  const zonas = valores.map((valor, i) => {
    const h = (valor / maximo) * zonaH;
    const x = pad.l + i * hueco + hueco * 0.18;
    const w = hueco * 0.64;
    const y = base - h;
    ctx.fillStyle = relleno;
    ctx.fillRect(x, y, w, h);
    ctx.fillStyle = colores.tinta;
    ctx.fillText(etiquetas[i], x, alto - 16);
    return { x, y: pad.t, w, h: zonaH, texto: `${etiquetas[i]}\n${eje(valor)}` };
  });
  escuchar(canvas, zonas);
}

export function apiladas(
  canvas: HTMLCanvasElement,
  etiquetas: string[],
  series: { nombre: string; color: string; valores: number[] }[],
  alto = 250,
) {
  const colores = paleta();
  const { ctx, ancho } = medida(canvas, alto);
  const pad = { l: 48, r: 12, t: 16, b: 36 };
  const totales = etiquetas.map((_, i) => series.reduce((suma, serie) => suma + serie.valores[i], 0));
  const maximo = Math.max(1, ...totales);
  const n = etiquetas.length || 1;
  const hueco = (ancho - pad.l - pad.r) / n;
  const base = alto - pad.b;
  const zonaH = alto - pad.t - pad.b;
  const zonas = etiquetas.map((etiqueta, i) => {
    let y = base;
    const x = pad.l + i * hueco + hueco * 0.18;
    const w = hueco * 0.64;
    for (const serie of series) {
      const h = (serie.valores[i] / maximo) * zonaH;
      y -= h;
      ctx.fillStyle = serie.color;
      ctx.fillRect(x, y, w, h);
    }
    ctx.fillStyle = colores.tinta;
    ctx.fillText(etiqueta, x, alto - 16);
    const detalle = series.map((serie) => `${serie.nombre}: ${serie.valores[i]}`).join("\n");
    return { x, y: pad.t, w, h: zonaH, texto: `${etiqueta}\n${detalle}` };
  });
  escuchar(canvas, zonas);
}

export function dispersion(
  canvas: HTMLCanvasElement,
  puntos: { x: number; y: number; texto: string }[],
  alto = 280,
) {
  const colores = paleta();
  const { ctx, ancho } = medida(canvas, alto);
  const pad = { l: 40, r: 16, t: 16, b: 32 };
  const maxX = Math.max(10, ...puntos.map((punto) => punto.x));
  const maxY = Math.max(1, ...puntos.map((punto) => punto.y));
  const zonaW = ancho - pad.l - pad.r;
  const zonaH = alto - pad.t - pad.b;
  ctx.strokeStyle = colores.linea;
  ctx.beginPath();
  ctx.moveTo(pad.l, pad.t);
  ctx.lineTo(pad.l, alto - pad.b);
  ctx.lineTo(ancho - pad.r, alto - pad.b);
  ctx.stroke();
  ctx.fillStyle = colores.tinta;
  ctx.fillText("antigüedad", ancho - 88, alto - 10);
  ctx.fillText("fallas", 4, 14);
  const zonas = puntos.map((punto) => {
    const x = pad.l + (punto.x / maxX) * zonaW;
    const y = alto - pad.b - (punto.y / maxY) * zonaH;
    ctx.fillStyle = colores.punto;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
    return { x: x - 6, y: y - 6, w: 12, h: 12, texto: punto.texto };
  });
  escuchar(canvas, zonas);
}

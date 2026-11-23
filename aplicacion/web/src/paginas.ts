import type { Falla, Resumen } from "./datos";
import { MESES, TIPOS, enPeriodo, etiquetaPeriodo, num, pesos } from "./datos";
import { apiladas, barras, dispersion, linea } from "./graficos";
import { paleta } from "./tema";

function suma(valores: number[]): number {
  return valores.reduce((total, valor) => total + valor, 0);
}

function kpi(etiqueta: string, valor: string, detalle: string): string {
  return `<article class="kpi"><p class="etiqueta">${etiqueta}</p><strong>${valor}</strong><em>${detalle}</em></article>`;
}

function leyenda(items: { nombre: string; color: string }[]): string {
  return `<div class="leyenda">${items
    .map((item) => `<span><i style="background:${item.color}"></i>${item.nombre}</span>`)
    .join("")}</div>`;
}

function canvas(id: string): HTMLCanvasElement {
  const nodo = document.getElementById(id);
  if (!(nodo instanceof HTMLCanvasElement)) throw new Error("Falta el gráfico " + id);
  return nodo;
}

function perfil(datos: Resumen, periodo: string | null, tipo: string): number[] {
  return Array.from({ length: 24 }, (_, hora) => {
    const celdas = enPeriodo(datos.consumo.por_hora, periodo).filter((fila) => fila.tipo === tipo && fila.hora === hora);
    const kwh = suma(celdas.map((fila) => fila.kwh));
    const n = suma(celdas.map((fila) => fila.n));
    return n ? kwh / n : 0;
  });
}

function marca(datos: Resumen, periodo: string | null): number | null {
  if (!periodo) return null;
  const indice = datos.periodos.indexOf(periodo);
  return indice < 0 ? null : indice;
}

function forma(valores: number[]): number[] {
  const pico = Math.max(...valores, 0.0001);
  return valores.map((valor) => (valor / pico) * 100);
}

function kwhHora(valores: number[]): string[] {
  return valores.map((valor) => num(valor, 2) + " kWh");
}

function horaMasAlta(datos: Resumen, periodo: string | null, tipo: string): { hora: number; promedio: number } {
  const valores = perfil(datos, periodo, tipo);
  let hora = 0;
  valores.forEach((valor, indice) => {
    if (valor > valores[hora]) hora = indice;
  });
  return { hora, promedio: valores[hora] };
}

export function paginaMedidor(datos: Resumen, periodo: string | null): void {
  const filas = enPeriodo(datos.consumo.por_tipo, periodo);
  const total = suma(filas.map((fila) => fila.kwh));
  const porTipo = TIPOS.map((tipo) => suma(filas.filter((fila) => fila.tipo === tipo).map((fila) => fila.kwh)));
  const estratos = [1, 2, 3, 4, 5, 6].map((estrato) =>
    suma(enPeriodo(datos.consumo.por_estrato, periodo).filter((fila) => fila.estrato === estrato).map((fila) => fila.kwh)),
  );
  const horaPico = horaMasAlta(datos, periodo, "Residencial");
  const raiz = document.querySelector("#pagina");
  if (!raiz) return;
  raiz.innerHTML = `
    <p class="historia">La energía medida ${etiquetaPeriodo(periodo)} no es una línea plana. En una casa pesa el final de la tarde. El estrato 3 suma más kWh que el 2, aunque hay más cuentas en el 2: cada casa de estrato alto gasta más, y el total lo mueven las cuentas del medio. Esta página mira el medidor, no la factura.</p>
    <section class="kpis">
      ${kpi("kWh medidos", num(total, 0), "Suma de la muestra")}
      ${kpi("Por cliente", num(total / datos.corte.clientes, 0) + " kWh", num(datos.corte.clientes) + " cuentas")}
      ${kpi("Hora residencial más alta", horaPico.hora + ":00", num(horaPico.promedio, 2) + " kWh promedio")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Consumo mes a mes</h2><canvas id="g-mes"></canvas></article>
      <article class="panel"><h2>Quién consume</h2><canvas id="g-tipo"></canvas></article>
    </section>
    <section class="rejilla igual">
      <article class="panel"><h2>Forma del día</h2>
        <p class="eje-nota">100 es la hora más alta de cada tipo. El residencial sube al anochecer; el industrial se mantiene de día.</p>
        ${leyenda([
        { nombre: "Residencial", color: paleta().teal },
        { nombre: "Comercial", color: paleta().rain },
        { nombre: "Industrial", color: paleta().gold },
      ])}<canvas id="g-hora"></canvas></article>
      <article class="panel"><h2>Residencial por estrato</h2><canvas id="g-estrato"></canvas></article>
    </section>
    <p class="nota">Muestra de ${num(datos.corte.clientes)} clientes en Medellín. No son los ${num(datos.corte.suscriptores_publicados)} suscriptores que publicó el SUI, y estos kWh no se suman con los de la factura.</p>`;

  const etiquetas = datos.periodos.map((item) => MESES[Number(item.slice(5)) - 1]);
  linea(
    canvas("g-mes"),
    etiquetas,
    [
      {
        nombre: "kWh",
        color: paleta().teal,
        valores: datos.periodos.map((item) => suma(enPeriodo(datos.consumo.por_tipo, item).map((fila) => fila.kwh))),
      },
    ],
    250,
    { marca: marca(datos, periodo) },
  );
  barras(canvas("g-tipo"), ["Resid.", "Indust.", "Comerc.", "Oficial", "Otros"], porTipo);
  const residencial = perfil(datos, periodo, "Residencial");
  const comercial = perfil(datos, periodo, "Comercial");
  const industrial = perfil(datos, periodo, "Industrial");
  linea(canvas("g-hora"), Array.from({ length: 24 }, (_, hora) => String(hora)), [
    { nombre: "Residencial", color: paleta().teal, valores: forma(residencial), detalle: kwhHora(residencial) },
    { nombre: "Comercial", color: paleta().rain, valores: forma(comercial), detalle: kwhHora(comercial) },
    { nombre: "Industrial", color: paleta().gold, valores: forma(industrial), detalle: kwhHora(industrial) },
  ]);
  barras(canvas("g-estrato"), ["E1", "E2", "E3", "E4", "E5", "E6"], estratos);
}

export function paginaCuenta(datos: Resumen, periodo: string | null): void {
  const meses = enPeriodo(datos.factura.por_mes, periodo);
  const valor = suma(meses.map((fila) => fila.valor));
  const kwh = suma(meses.map((fila) => fila.kwh));
  const pagada = suma(meses.map((fila) => fila.pagada));
  const pendiente = suma(meses.map((fila) => fila.pendiente));
  const mora = suma(meses.map((fila) => fila.mora));
  const raiz = document.querySelector("#pagina");
  if (!raiz) return;
  raiz.innerHTML = `
    <p class="historia">Cada cliente tiene una sola cuenta por mes. Esa cuenta es la suma de sus horas, multiplicada por el precio que EPM publicó. El valor puede subir aunque el medidor no lo haga, si la tarifa de ese mes subió.</p>
    <section class="kpis cinco">
      ${kpi("Valor facturado", pesos(valor), etiquetaPeriodo(periodo))}
      ${kpi("kWh facturados", num(kwh, 0), "Ya incluye las horas del mes")}
      ${kpi("Pagadas", num(pagada), "Cuentas al día")}
      ${kpi("Pendientes", num(pendiente), "Sin pago registrado")}
      ${kpi("En mora", num(mora), "Pasaron la fecha")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Valor por mes</h2><canvas id="g-valor"></canvas></article>
      <article class="panel"><h2>Valor por tipo de cliente</h2><canvas id="g-tipo-valor"></canvas></article>
    </section>
    <article class="panel ancho"><h2>Precio medio de la muestra</h2><canvas id="g-tarifa"></canvas></article>
    <article class="panel ancho"><h2>Estado de las cuentas</h2>${leyenda([
      { nombre: "Pagada", color: paleta().teal },
      { nombre: "Pendiente", color: paleta().gold },
      { nombre: "En mora", color: paleta().coral },
    ])}<canvas id="g-estado"></canvas></article>
    <p class="nota">El cliente C0001, en enero, midió 145,9701 kWh y su factura trae ese mismo número, a 573,05 pesos el kWh de estrato 1. El precio medio de arriba mezcla todos los estratos de la muestra.</p>`;

  const visibles = datos.periodos;
  const etiquetas = visibles.map((item) => MESES[Number(item.slice(5)) - 1]);
  const de = (item: string) => datos.factura.por_mes.find((fila) => fila.periodo === item);
  const señal = { marca: marca(datos, periodo) };
  linea(canvas("g-valor"), etiquetas, [
    { nombre: "Pesos", color: paleta().teal, valores: visibles.map((item) => de(item)?.valor ?? 0) },
  ], 250, señal);
  linea(canvas("g-tarifa"), etiquetas, [
    { nombre: "Pesos / kWh", color: paleta().rain, valores: visibles.map((item) => de(item)?.tarifa ?? 0) },
  ], 250, { ...señal, desdeCero: false });
  const tiposFactura = TIPOS.map((tipo) =>
    suma(enPeriodo(datos.factura.por_tipo, periodo).filter((fila) => fila.tipo === tipo).map((fila) => fila.valor)),
  );
  barras(canvas("g-tipo-valor"), ["Resid.", "Indust.", "Comerc.", "Oficial", "Otros"], tiposFactura, paleta().rain);
  apiladas(canvas("g-estado"), etiquetas, [
    { nombre: "Pagada", color: paleta().teal, valores: visibles.map((item) => de(item)?.pagada ?? 0) },
    { nombre: "Pendiente", color: paleta().gold, valores: visibles.map((item) => de(item)?.pendiente ?? 0) },
    { nombre: "En mora", color: paleta().coral, valores: visibles.map((item) => de(item)?.mora ?? 0) },
  ]);
}

function rankearHoras(eventos: Falla[]): { cuando: string; n: number }[] {
  const cuenta = new Map<string, number>();
  for (const falla of eventos) cuenta.set(falla.cuando, (cuenta.get(falla.cuando) ?? 0) + 1);
  return [...cuenta.entries()].map(([cuando, n]) => ({ cuando, n })).sort((a, b) => b.n - a.n);
}

function mapa(eventos: Falla[]): string {
  const grupos = new Map<string, { lat: number; lon: number; n: number; tipo: string }>();
  for (const falla of eventos) {
    const actual = grupos.get(falla.activo) ?? { lat: falla.lat, lon: falla.lon, n: 0, tipo: falla.tipo };
    actual.n += 1;
    grupos.set(falla.activo, actual);
  }
  const puntos = [...grupos.values()];
  if (!puntos.length) return `<p class="nota">No hay fallas en este mes.</p>`;
  const minLat = Math.min(...puntos.map((punto) => punto.lat));
  const maxLat = Math.max(...puntos.map((punto) => punto.lat));
  const minLon = Math.min(...puntos.map((punto) => punto.lon));
  const maxLon = Math.max(...puntos.map((punto) => punto.lon));
  const circulos = puntos
    .map((punto) => {
      const x = 40 + ((punto.lon - minLon) / (maxLon - minLon || 1)) * 560;
      const y = 300 - ((punto.lat - minLat) / (maxLat - minLat || 1)) * 250;
      const r = 4 + Math.min(punto.n, 12);
      return `<circle class="punto" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}"><title>${punto.tipo}: ${punto.n} fallas</title></circle>`;
    })
    .join("");
  return `<svg class="mapa" viewBox="0 0 640 340" role="img" aria-label="Mapa de fallas en Medellín">${circulos}</svg>`;
}

export function paginaFallas(datos: Resumen, periodo: string | null): void {
  const eventos = enPeriodo(datos.fallas, periodo);
  const ranking = rankearHoras(eventos).slice(0, 5);
  const maximo = ranking[0]?.n ?? 1;
  const raiz = document.querySelector("#pagina");
  if (!raiz) return;
  raiz.innerHTML = `
    <p class="historia">Cada falla cae sobre un equipo que ya está dentro de Medellín. El mapa muestra dónde se juntan. El ranking ordena las horas con más eventos: es una lista, no un pronóstico. La lluvia va en el gráfico de abajo, una vez por mes, no dentro de cada falla.</p>
    <section class="kpis">
      ${kpi("Fallas", num(eventos.length), etiquetaPeriodo(periodo))}
      ${kpi("Clientes alcanzados", num(suma(eventos.map((falla) => falla.afectados))), "Suma de cada evento")}
      ${kpi("Minutos", num(suma(eventos.map((falla) => falla.minutos))), "Duración acumulada")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Dónde ocurrieron</h2>${mapa(eventos)}</article>
      <article class="panel"><h2>Horas con más fallas</h2>
        <ol class="lista">${ranking
          .map(
            (fila) =>
              `<li><span>${fila.cuando.slice(5, 16)}</span><span class="barra"><span style="width:${(fila.n / maximo) * 100}%"></span></span><strong>${fila.n}</strong></li>`,
          )
          .join("")}</ol>
      </article>
    </section>
    <article class="panel ancho"><h2>Lluvia del mes y número de fallas</h2>${leyenda([
      { nombre: "Fallas", color: paleta().teal },
      { nombre: "Lluvia, mm", color: paleta().rain },
    ])}<canvas id="g-lluvia"></canvas></article>
    <p class="nota">Un mes con muchas fallas cuenta la lluvia una sola vez. La falla F00001, el 3 de marzo a la 01:00, afectó a 38 clientes durante 129 minutos. Esa hora no tuvo lluvia.</p>`;

  linea(
    canvas("g-lluvia"),
    MESES,
    [
      { nombre: "Fallas", color: paleta().teal, valores: datos.periodos.map((item) => datos.fallas.filter((falla) => falla.periodo === item).length) },
      { nombre: "Lluvia mm", color: paleta().rain, valores: datos.periodos.map((item) => datos.lluvia.find((fila) => fila.periodo === item)?.mm ?? 0) },
    ],
    250,
    { ejesSeparados: true },
  );
}

export function paginaEquipos(datos: Resumen, periodo: string | null): void {
  const eventos = enPeriodo(datos.fallas, periodo);
  const trabajos = enPeriodo(datos.mantenimiento, periodo);
  const costo = suma(trabajos.map((trabajo) => trabajo.costo));
  const preventivo = suma(trabajos.filter((trabajo) => trabajo.tipo === "preventivo").map((trabajo) => trabajo.costo));
  const correctivo = suma(trabajos.filter((trabajo) => trabajo.tipo === "correctivo").map((trabajo) => trabajo.costo));
  const porTipo = ["poste", "transformador", "linea", "proteccion", "subestacion"].map(
    (tipo) => eventos.filter((falla) => falla.tipo === tipo).length,
  );
  const conteo = new Map<string, number>();
  for (const falla of eventos) conteo.set(falla.activo, (conteo.get(falla.activo) ?? 0) + 1);
  const top = [...conteo.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
  const raiz = document.querySelector("#pagina");
  if (!raiz) return;
  raiz.innerHTML = `
    <p class="historia">Los ${num(datos.corte.activos)} equipos no fallan igual. Un transformador viejo puede cargar más eventos que un poste nuevo. El mantenimiento es otra cuenta: un preventivo por equipo y un correctivo después de parte de las fallas.</p>
    <section class="kpis">
      ${kpi("Costo de atender", pesos(costo), etiquetaPeriodo(periodo))}
      ${kpi("Preventivo", pesos(preventivo), "Trabajo programado")}
      ${kpi("Correctivo", pesos(correctivo), "Después de una falla")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Fallas por tipo de equipo</h2><canvas id="g-equipo"></canvas></article>
      <article class="panel"><h2>Edad y número de fallas</h2><canvas id="g-edad"></canvas></article>
    </section>
    <article class="panel ancho"><h2>Equipos con más eventos</h2>
      <ol class="lista">${top
        .map(([id, n]) => {
          const equipo = datos.equipos.find((item) => item.id === id);
          return `<li><span>${id}</span><span>${equipo?.tipo ?? ""} · ${equipo?.edad ?? ""} años</span><strong>${n}</strong></li>`;
        })
        .join("")}</ol>
    </article>
    <p class="nota">El equipo no se une a un cliente. El estado en esta corrida es “en servicio”: la página ordena por lo que ya falló, no anuncia el próximo daño.</p>`;

  barras(canvas("g-equipo"), ["Poste", "Transf.", "Línea", "Protec.", "Subest."], porTipo);
  dispersion(
    canvas("g-edad"),
    datos.equipos.map((equipo) => ({
      x: equipo.edad,
      y: conteo.get(equipo.id) ?? 0,
      texto: `${equipo.id}\n${equipo.tipo}, ${equipo.edad} años\n${conteo.get(equipo.id) ?? 0} fallas`,
    })),
  );
}

export function paginaContexto(datos: Resumen, periodo: string | null): void {
  const mes = periodo ? Number(periodo.slice(5)) : 1;
  const precio = datos.contexto.tarifa.find((fila) => fila.mes === mes)?.precio ?? 0;
  const estratos = datos.contexto.sui.estratos;
  const maximo = Math.max(...estratos.map((fila) => fila.usuarios));
  const raiz = document.querySelector("#pagina");
  if (!raiz) return;
  raiz.innerHTML = `
    <p class="historia">Esta página no habla de un cliente de la muestra. Habla del municipio. Los habitantes, los suscriptores y el precio del kWh se miran juntos y no se suman entre sí. Tampoco se reparten entre las 1.000 cuentas de las páginas anteriores.</p>
    <section class="kpis">
      ${kpi("Habitantes", num(datos.contexto.habitantes.total), "DANE, área Total, 2021")}
      ${kpi("Suscriptores", num(datos.contexto.sui.suscriptores), "SUI, EPM, año 2021")}
      ${kpi("Tarifa estrato 1", pesos(precio, 2), periodo ? etiquetaPeriodo(periodo) : "Enero, por encima de subsistencia")}
    </section>
    <section class="rejilla">
      <article class="panel"><h2>Suscriptores por estrato</h2>
        <ol class="lista">${estratos
          .map(
            (fila) =>
              `<li><span>E${fila.estrato}</span><span class="barra"><span style="width:${(fila.usuarios / maximo) * 100}%"></span></span><strong>${num(fila.usuarios)}</strong></li>`,
          )
          .join("")}</ol>
      </article>
      <article class="panel"><h2>Resto de cuentas</h2><canvas id="g-otros"></canvas></article>
    </section>
    <article class="panel ancho"><h2>Precio publicado por EPM en 2021</h2><canvas id="g-precio"></canvas></article>
    <p class="nota">Contexto publicado. La cabecera tiene ${num(datos.contexto.habitantes.cabecera)} habitantes y el resto del municipio ${num(datos.contexto.habitantes.resto)}. Esas dos cifras ya están dentro del total. La tarifa no tiene municipio.</p>`;

  barras(
    canvas("g-otros"),
    datos.contexto.sui.otros.map((fila) => fila.tipo),
    datos.contexto.sui.otros.map((fila) => fila.usuarios),
  );
  linea(canvas("g-precio"), MESES, [
    { nombre: "Pesos / kWh", color: paleta().teal, valores: datos.contexto.tarifa.map((fila) => fila.precio) },
  ], 250, { desdeCero: false, marca: periodo ? Number(periodo.slice(5)) - 1 : null });
}

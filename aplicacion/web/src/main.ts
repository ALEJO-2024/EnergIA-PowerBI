import "./estilos.css";
import type { Resumen } from "./datos";
import { MESES } from "./datos";
import { paginaContexto, paginaCuenta, paginaEquipos, paginaFallas, paginaMedidor } from "./paginas";
import { montarChat } from "./chat";
import { alternarTema, temaActual } from "./tema";

const PAGINAS = [
  { id: "medidor", numero: "01", nombre: "Medidor", dibujar: paginaMedidor },
  { id: "cuenta", numero: "02", nombre: "Cuenta", dibujar: paginaCuenta },
  { id: "fallas", numero: "03", nombre: "Fallas", dibujar: paginaFallas },
  { id: "equipos", numero: "04", nombre: "Equipos", dibujar: paginaEquipos },
  { id: "contexto", numero: "05", nombre: "Contexto", dibujar: paginaContexto },
];

let datos: Resumen | null = null;
let pagina = "medidor";
let periodo: string | null = null;

async function iniciar() {
  const raiz = document.querySelector("#app");
  if (!raiz) return;
  raiz.innerHTML = `<p class="estado">Cargando el año de Medellín…</p>`;
  const respuesta = await fetch("/api/resumen");
  if (!respuesta.ok) {
    raiz.innerHTML = `<p class="estado">No se pudo leer el resumen. Revisa que la API esté encendida.</p>`;
    return;
  }
  datos = (await respuesta.json()) as Resumen;
  pintar();
  montarChat();
}

function pintar() {
  const raiz = document.querySelector("#app");
  if (!raiz || !datos) return;
  const etiquetaTema = temaActual() === "dark" ? "Vista clara" : "Vista oscura";
  raiz.innerHTML = `
    <main class="marco">
      <header class="cabecera">
        <div>
          <p class="ceja">EnergIA · Business intelligence</p>
          <h1>Medellín, un año de servicio</h1>
          <p class="bajada">2021, código 05001. Consumo, cuenta, fallas y el municipio que publican el DANE, el SUI y EPM.</p>
        </div>
        <button type="button" class="tema" id="tema">${etiquetaTema}</button>
      </header>
      <nav class="nav">${PAGINAS.map(
        (item) =>
          `<button type="button" data-pagina="${item.id}" class="${item.id === pagina ? "activa" : ""}"><strong>${item.numero}</strong><span>${item.nombre}</span></button>`,
      ).join("")}</nav>
      <div class="filtros">
        <button type="button" data-periodo="" class="${periodo === null ? "activa" : ""}">Año</button>
        ${datos.periodos
          .map(
            (item) =>
              `<button type="button" data-periodo="${item}" class="${periodo === item ? "activa" : ""}">${MESES[Number(item.slice(5)) - 1]}</button>`,
          )
          .join("")}
      </div>
      <section id="pagina"></section>
    </main>`;

  document.querySelector("#tema")?.addEventListener("click", () => {
    alternarTema();
    pintar();
  });

  raiz.querySelectorAll<HTMLButtonElement>("[data-pagina]").forEach((boton) => {
    boton.addEventListener("click", () => {
      pagina = boton.dataset.pagina ?? "medidor";
      pintar();
    });
  });
  raiz.querySelectorAll<HTMLButtonElement>("[data-periodo]").forEach((boton) => {
    boton.addEventListener("click", () => {
      periodo = boton.dataset.periodo || null;
      pintar();
    });
  });

  const actual = PAGINAS.find((item) => item.id === pagina) ?? PAGINAS[0];
  actual.dibujar(datos, periodo);
}

void iniciar();

type Rol = "usuario" | "asistente";

interface Burbuja {
  rol: Rol;
  texto: string;
}

const HISTORIAL: Burbuja[] = [];
let esperando = false;

function burbuja(lista: HTMLElement, item: Burbuja): void {
  const nodo = document.createElement("p");
  nodo.className = "chat-burbuja " + item.rol;
  nodo.textContent = item.texto;
  lista.appendChild(nodo);
  lista.scrollTop = lista.scrollHeight;
}

async function enviar(lista: HTMLElement, campo: HTMLTextAreaElement): Promise<void> {
  const texto = campo.value.trim();
  if (!texto || esperando) return;
  campo.value = "";
  HISTORIAL.push({ rol: "usuario", texto });
  burbuja(lista, HISTORIAL[HISTORIAL.length - 1]);
  esperando = true;
  const espera = document.createElement("p");
  espera.className = "chat-burbuja asistente";
  espera.textContent = "Revisando las cifras…";
  lista.appendChild(espera);
  lista.scrollTop = lista.scrollHeight;
  try {
    const respuesta = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mensajes: HISTORIAL.slice(-8).map((item) => ({ rol: item.rol, texto: item.texto })),
      }),
    });
    const cuerpo = (await respuesta.json()) as { respuesta?: string; detail?: string };
    const dicho = respuesta.ok
      ? cuerpo.respuesta || "No hubo respuesta."
      : cuerpo.detail || "No se pudo consultar.";
    HISTORIAL.push({ rol: "asistente", texto: dicho });
    espera.textContent = dicho;
  } catch {
    const dicho = "No se pudo consultar. Revisa que el tablero siga encendido.";
    HISTORIAL.push({ rol: "asistente", texto: dicho });
    espera.textContent = dicho;
  } finally {
    esperando = false;
    lista.scrollTop = lista.scrollHeight;
    campo.focus();
  }
}

export function montarChat(): void {
  if (document.querySelector(".chat")) return;
  const raiz = document.createElement("div");
  raiz.className = "chat";
  raiz.innerHTML = `
    <button type="button" class="chat-abrir" aria-expanded="false">Consulta</button>
    <section class="chat-panel" hidden>
      <header class="chat-cabecera">
        <div>
          <p>EnergIA</p>
          <strong>Consulta del negocio</strong>
        </div>
        <button type="button" class="chat-cerrar" aria-label="Cerrar">Cerrar</button>
      </header>
      <div class="chat-lista"></div>
      <div class="chat-ideas"></div>
      <form class="chat-forma">
        <textarea rows="2" maxlength="1500" placeholder="Pregunta sobre Medellín 2021"></textarea>
        <button type="submit">Enviar</button>
      </form>
    </section>`;
  document.body.appendChild(raiz);

  const abrir = raiz.querySelector<HTMLButtonElement>(".chat-abrir");
  const panel = raiz.querySelector<HTMLElement>(".chat-panel");
  const lista = raiz.querySelector<HTMLElement>(".chat-lista");
  const ideas = raiz.querySelector<HTMLElement>(".chat-ideas");
  const forma = raiz.querySelector<HTMLFormElement>(".chat-forma");
  const campo = raiz.querySelector<HTMLTextAreaElement>("textarea");
  if (!abrir || !panel || !lista || !ideas || !forma || !campo) return;

  const sugeridas = ["¿Qué pasó con la cuenta en enero?", "¿El estrato 3 midió más que el 2?"];
  for (const idea of sugeridas) {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.textContent = idea;
    boton.addEventListener("click", () => {
      campo.value = idea;
      void enviar(lista, campo);
    });
    ideas.appendChild(boton);
  }

  const nota = document.createElement("p");
  nota.className = "chat-nota";
  nota.textContent = "Lee la base del proyecto y solo responde sobre el servicio eléctrico de Medellín en 2021.";
  lista.appendChild(nota);

  const alternar = (abierto: boolean) => {
    panel.hidden = !abierto;
    abrir.setAttribute("aria-expanded", abierto ? "true" : "false");
    if (abierto) campo.focus();
  };
  abrir.addEventListener("click", () => alternar(panel.hidden));
  raiz.querySelector(".chat-cerrar")?.addEventListener("click", () => alternar(false));
  forma.addEventListener("submit", (evento) => {
    evento.preventDefault();
    void enviar(lista, campo);
  });
  campo.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && !evento.shiftKey) {
      evento.preventDefault();
      void enviar(lista, campo);
    }
  });
}

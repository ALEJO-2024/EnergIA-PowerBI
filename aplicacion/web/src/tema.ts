export type Tema = "light" | "dark";

const CLAVE = "energia-tema";

const CLARA = {
  tinta: "#102033",
  linea: "rgba(16, 32, 51, 0.12)",
  teal: "#0b7a68",
  marca: "rgba(11, 122, 104, 0.7)",
  punto: "rgba(11, 122, 104, 0.9)",
  rain: "#2f6f9e",
  gold: "#a67c2d",
  coral: "#c45d56",
};

const OSCURA = {
  tinta: "#f7fafc",
  linea: "rgba(158, 188, 214, 0.16)",
  teal: "#2ee6c8",
  marca: "rgba(46, 230, 200, 0.55)",
  punto: "rgba(46, 230, 200, 0.85)",
  rain: "#9fd4ff",
  gold: "#e7c27a",
  coral: "#e08b84",
};

export function temaActual(): Tema {
  return document.documentElement.dataset.tema === "dark" ? "dark" : "light";
}

export function aplicarTema(tema: Tema): void {
  document.documentElement.dataset.tema = tema;
  localStorage.setItem(CLAVE, tema);
}

export function alternarTema(): Tema {
  const siguiente: Tema = temaActual() === "dark" ? "light" : "dark";
  aplicarTema(siguiente);
  return siguiente;
}

export function paleta() {
  return temaActual() === "dark" ? OSCURA : CLARA;
}

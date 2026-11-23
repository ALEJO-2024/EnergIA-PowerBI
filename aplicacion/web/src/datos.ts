export interface Corte {
  municipio: string;
  codigo: string;
  anio: number;
  clientes: number;
  activos: number;
  suscriptores_publicados: number;
}

export interface PorTipo {
  periodo: string;
  tipo: string;
  kwh: number;
}

export interface PorEstrato {
  periodo: string;
  estrato: number;
  kwh: number;
}

export interface PorHora {
  periodo: string;
  tipo: string;
  hora: number;
  kwh: number;
  n: number;
}

export interface FacturaMes {
  periodo: string;
  valor: number;
  kwh: number;
  tarifa: number;
  pagada: number;
  pendiente: number;
  mora: number;
}

export interface FacturaTipo {
  periodo: string;
  tipo: string;
  valor: number;
  kwh: number;
}

export interface Falla {
  id: string;
  activo: string;
  tipo: string;
  lat: number;
  lon: number;
  cuando: string;
  periodo: string;
  afectados: number;
  minutos: number;
  edad: number;
  estado: string;
}

export interface Equipo {
  id: string;
  tipo: string;
  lat: number;
  lon: number;
  edad: number;
  estado: string;
}

export interface Trabajo {
  activo: string;
  fecha: string;
  periodo: string;
  tipo: string;
  costo: number;
}

export interface Resumen {
  corte: Corte;
  periodos: string[];
  consumo: {
    total_kwh: number;
    por_tipo: PorTipo[];
    por_estrato: PorEstrato[];
    por_hora: PorHora[];
  };
  factura: { por_mes: FacturaMes[]; por_tipo: FacturaTipo[] };
  fallas: Falla[];
  lluvia: { periodo: string; mm: number }[];
  equipos: Equipo[];
  mantenimiento: Trabajo[];
  contexto: {
    habitantes: { total: number; cabecera: number; resto: number };
    sui: {
      suscriptores: number;
      estratos: { estrato: number; usuarios: number }[];
      otros: { tipo: string; usuarios: number }[];
    };
    tarifa: { mes: number; precio: number }[];
  };
}

export const TIPOS = ["Residencial", "Industrial", "Comercial", "Oficial", "Otros"];
export const MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

export function num(valor: number, decimales = 0): string {
  return new Intl.NumberFormat("es-CO", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(valor);
}

export function pesos(valor: number, decimales = 0): string {
  return "$\u00a0" + num(valor, decimales);
}

export function enPeriodo<T extends { periodo: string }>(filas: T[], periodo: string | null): T[] {
  if (!periodo) return filas;
  return filas.filter((fila) => fila.periodo === periodo);
}

export function etiquetaPeriodo(periodo: string | null): string {
  if (!periodo) return "en 2021";
  return "en " + MESES[Number(periodo.slice(5)) - 1].toLowerCase() + " de 2021";
}

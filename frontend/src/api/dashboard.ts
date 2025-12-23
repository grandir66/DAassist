import apiClient from './client';

export interface TicketStats {
  totali: number;
  aperti: number;
  nuovi: number;
  in_lavorazione: number;
  chiusi_oggi: number;
  chiusi_settimana: number;
  chiusi_mese: number;
}

export interface InterventoStats {
  totali: number;
  pianificati: number;
  in_corso: number;
  completati_oggi: number;
  completati_settimana: number;
  completati_mese: number;
}

export interface TicketRecente {
  id: number;
  numero: string;
  cliente_ragione_sociale: string | null;
  oggetto: string;
  priorita_codice: string;
  priorita_descrizione: string;
  stato_codice: string;
  stato_descrizione: string;
  created_at: string;
}

export interface InterventoOggi {
  id: number;
  numero: string;
  cliente_ragione_sociale: string;
  oggetto: string;
  tipo_descrizione: string;
  tipo_richiede_viaggio: boolean;
  stato_codice: string;
  stato_descrizione: string;
  data_inizio: string | null;
}

export interface DashboardData {
  ticket_stats: TicketStats;
  intervento_stats: InterventoStats;
  recent_tickets: TicketRecente[];
  interventi_oggi: InterventoOggi[];
}

export const dashboardApi = {
  async getData(): Promise<DashboardData> {
    const response = await apiClient.get<DashboardData>('/dashboard');
    return response.data;
  },
};

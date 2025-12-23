import apiClient from './client';

export interface Cliente {
  id: number;
  codice_gestionale: string;
  ragione_sociale: string;
  partita_iva?: string;
  codice_fiscale?: string;
  indirizzo?: string;
  cap?: string;
  citta?: string;
  provincia?: string;
  nazione: string;
  telefono?: string;
  email?: string;
  pec?: string;
  sito_web?: string;
  stato_cliente?: string;
  classificazione?: string;
  referente_it_id?: number;
  orari_servizio?: string;
  nomi_alternativi?: string;
  note?: string;
  ultimo_sync: string;
  created_at: string;
  updated_at?: string;
  attivo: boolean;
}

export interface Contratto {
  id: number;
  cliente_id: number;
  codice_gestionale: string;
  descrizione: string;
  tipologia_descrizione?: string;
  data_inizio?: string;
  data_fine?: string;
  ore_incluse?: number;
  ore_utilizzate: number;
  attivo: boolean;
  created_at: string;
}

export interface SedeCliente {
  id: number;
  cliente_id: number;
  nome_sede: string;
  codice_sede?: string;
  indirizzo: string;
  cap?: string;
  citta: string;
  provincia?: string;
  nazione: string;
  telefono?: string;
  email?: string;
  orari_servizio?: string;
  note?: string;
  attivo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Referente {
  id: number;
  cliente_id: number;
  sede_id?: number;
  nome: string;
  cognome: string;
  ruolo?: string;
  telefono?: string;
  cellulare?: string;
  interno_telefonico?: string;
  email?: string;
  contatto_principale: boolean;
  riceve_notifiche: boolean;
  referente_it: boolean;
  note?: string;
  attivo: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ClienteDetail extends Cliente {
  contratti: Contratto[];
  referenti: Referente[];
}

export interface ClienteListResponse {
  total: number;
  page: number;
  limit: number;
  clienti: Cliente[];
}

export interface ClienteFilters {
  page?: number;
  limit?: number;
  search?: string;
  attivo?: boolean;
}

export interface ClienteStats {
  total_tickets: number;
  open_tickets: number;
  total_interventi: number;
}

export const clientiApi = {
  async getAll(filters?: ClienteFilters): Promise<ClienteListResponse> {
    const response = await apiClient.get<ClienteListResponse>('/clients', {
      params: filters
    });
    return response.data;
  },

  async getById(clienteId: number): Promise<ClienteDetail> {
    const response = await apiClient.get<ClienteDetail>(`/clients/${clienteId}`);
    return response.data;
  },

  async getContratti(clienteId: number): Promise<Contratto[]> {
    const response = await apiClient.get<Contratto[]>(`/clients/${clienteId}/contratti`);
    return response.data;
  },

  async getReferenti(clienteId: number): Promise<Referente[]> {
    const response = await apiClient.get<Referente[]>(`/clients/${clienteId}/referenti`);
    return response.data;
  },

  async getSedi(clienteId: number): Promise<SedeCliente[]> {
    const response = await apiClient.get<SedeCliente[]>(`/clients/${clienteId}/sites`);
    return response.data;
  },

  async getContatti(clienteId: number, sede_id?: number): Promise<Referente[]> {
    const response = await apiClient.get<Referente[]>(`/clients/${clienteId}/contacts`, {
      params: sede_id ? { sede_id } : undefined
    });
    return response.data;
  },

  async getStats(clienteId: number): Promise<ClienteStats> {
    const response = await apiClient.get<ClienteStats>(`/clients/${clienteId}/stats`);
    return response.data;
  }
};

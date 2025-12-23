import apiClient from './client';

export interface Intervento {
  id: number;
  numero: string;
  cliente?: {
    id: number;
    codice_gestionale: string;
    ragione_sociale: string;
  };
  tecnico?: {
    id: number;
    nome_completo: string;
    email: string;
  };
  ticket_id?: number;
  tipo_intervento?: {
    id: number;
    codice: string;
    descrizione: string;
    colore?: string;
    richiede_viaggio: boolean;
  };
  stato?: {
    id: number;
    codice: string;
    descrizione: string;
    colore?: string;
    finale: boolean;
  };
  origine?: {
    id: number;
    codice: string;
    descrizione: string;
  };
  oggetto: string;
  descrizione_lavoro?: string;
  note_interne?: string;
  data_inizio?: string;
  data_fine?: string;
  firma_cliente?: string;
  firma_nome?: string;
  firma_ruolo?: string;
  firma_data?: string;
  created_at: string;
  updated_at?: string;
}

export interface InterventoCreate {
  cliente_id: number;
  ticket_id?: number;
  tecnico_id: number;
  tipo_intervento_id: number;
  stato_id: number;
  origine_id: number;
  oggetto: string;
  descrizione_lavoro?: string;
  note_interne?: string;
}

export interface InterventoUpdate {
  tipo_intervento_id?: number;
  stato_id?: number;
  oggetto?: string;
  descrizione_lavoro?: string;
  note_interne?: string;
}

export interface InterventoStartRequest {
  note_avvio?: string;
}

export interface InterventoCompleteRequest {
  descrizione_lavoro: string;
  firma_cliente?: string;
  firma_nome?: string;
  firma_ruolo?: string;
}

export interface AttivitaIntervento {
  id: number;
  intervento_id: number;
  categoria_id: number;
  categoria_descrizione: string;
  descrizione: string;
  durata: number;
  prezzo_unitario?: number;
  totale?: number;
  created_at: string;
}

export interface AttivitaInterventoCreate {
  categoria_id: number;
  descrizione: string;
  durata: number;
  prezzo_unitario?: number;
}

// Sessioni Lavoro
export interface SessioneLavoro {
  id: number;
  intervento_id: number;
  tecnico: {
    id: number;
    nome_completo: string;
    email: string;
  };
  data: string;
  ora_inizio: string;
  ora_fine?: string;
  durata_minuti?: number;
  tipo_intervento: {
    id: number;
    codice: string;
    descrizione: string;
  };
  km_percorsi?: number;
  tempo_viaggio_minuti?: number;
  note?: string;
  created_at: string;
}

export interface SessioneLavoroCreate {
  data: string;
  ora_inizio: string;
  ora_fine?: string;
  tipo_intervento_id: number;
  km_percorsi?: number;
  tempo_viaggio_minuti?: number;
  note?: string;
}

export interface SessioneLavoroUpdate {
  data?: string;
  ora_inizio?: string;
  ora_fine?: string;
  tipo_intervento_id?: number;
  km_percorsi?: number;
  tempo_viaggio_minuti?: number;
  note?: string;
}

// Righe Attività
export interface RigaAttivita {
  id: number;
  intervento_id: number;
  numero_riga: number;
  categoria_id: number;
  descrizione: string;
  quantita: number;
  unita_misura: string;
  prezzo_unitario: number;
  sconto_percentuale: number;
  fatturabile: boolean;
  in_garanzia: boolean;
  incluso_contratto: boolean;
  importo: number;
  created_at: string;
}

export interface RigaAttivitaUpdate {
  categoria_id?: number;
  descrizione?: string;
  quantita?: number;
  prezzo_unitario?: number;
  sconto_percentuale?: number;
  fatturabile?: boolean;
  in_garanzia?: boolean;
  incluso_contratto?: boolean;
}

export interface InterventoListResponse {
  total: number;
  page: number;
  limit: number;
  interventi: Intervento[];
}

export interface InterventoFilters {
  page?: number;
  limit?: number;
  stato_id?: number;
  tipo_intervento_id?: number;
  tecnico_id?: number;
  cliente_id?: number;
  ticket_id?: number;
  data_from?: string;
  data_to?: string;
  search?: string;
}

export const interventiApi = {
  async getAll(filters?: InterventoFilters): Promise<InterventoListResponse> {
    const response = await apiClient.get<InterventoListResponse>('/interventions', {
      params: filters
    });
    return response.data;
  },

  async getById(interventoId: number): Promise<Intervento> {
    const response = await apiClient.get<Intervento>(`/interventions/${interventoId}`);
    return response.data;
  },

  async create(data: InterventoCreate): Promise<Intervento> {
    const response = await apiClient.post<Intervento>('/interventions', data);
    return response.data;
  },

  async update(interventoId: number, data: InterventoUpdate): Promise<Intervento> {
    const response = await apiClient.patch<Intervento>(`/interventions/${interventoId}`, data);
    return response.data;
  },

  async start(interventoId: number, data?: InterventoStartRequest): Promise<Intervento> {
    const response = await apiClient.post<Intervento>(`/interventions/${interventoId}/start`, data || {});
    return response.data;
  },

  async complete(interventoId: number, data: InterventoCompleteRequest): Promise<Intervento> {
    const response = await apiClient.post<Intervento>(`/interventions/${interventoId}/complete`, data);
    return response.data;
  },

  async addAttivita(interventoId: number, data: AttivitaInterventoCreate): Promise<AttivitaIntervento> {
    const response = await apiClient.post<AttivitaIntervento>(`/interventions/${interventoId}/attivita`, data);
    return response.data;
  },

  async delete(interventoId: number): Promise<void> {
    await apiClient.delete(`/interventions/${interventoId}`);
  },

  // ============================================================================
  // SESSIONI LAVORO
  // ============================================================================

  async getSessions(interventoId: number): Promise<SessioneLavoro[]> {
    const response = await apiClient.get<SessioneLavoro[]>(`/interventions/${interventoId}/sessions`);
    return response.data;
  },

  async addSession(interventoId: number, data: SessioneLavoroCreate): Promise<SessioneLavoro> {
    const response = await apiClient.post<SessioneLavoro>(`/interventions/${interventoId}/sessions`, data);
    return response.data;
  },

  async updateSession(interventoId: number, sessionId: number, data: SessioneLavoroUpdate): Promise<SessioneLavoro> {
    const response = await apiClient.patch<SessioneLavoro>(`/interventions/${interventoId}/sessions/${sessionId}`, data);
    return response.data;
  },

  async deleteSession(interventoId: number, sessionId: number): Promise<void> {
    await apiClient.delete(`/interventions/${interventoId}/sessions/${sessionId}`);
  },

  // ============================================================================
  // RIGHE ATTIVITÀ
  // ============================================================================

  async getRows(interventoId: number): Promise<RigaAttivita[]> {
    const response = await apiClient.get<RigaAttivita[]>(`/interventions/${interventoId}/rows`);
    return response.data;
  },

  async updateRow(interventoId: number, rowId: number, data: RigaAttivitaUpdate): Promise<RigaAttivita> {
    const response = await apiClient.patch<RigaAttivita>(`/interventions/${interventoId}/rows/${rowId}`, data);
    return response.data;
  },

  async deleteRow(interventoId: number, rowId: number): Promise<void> {
    await apiClient.delete(`/interventions/${interventoId}/rows/${rowId}`);
  }
};

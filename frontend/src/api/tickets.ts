import apiClient from './client';

export interface Ticket {
  id: number;
  numero: string;
  oggetto: string;
  descrizione?: string;
  cliente?: {
    id: number;
    codice_gestionale: string;
    ragione_sociale: string;
  };
  priorita?: {
    id: number;
    descrizione: string;
    codice: string;
    livello: number;
  };
  stato?: {
    id: number;
    descrizione: string;
    codice: string;
  };
  canale?: {
    id: number;
    nome: string;
    codice: string;
  };
  tecnico_assegnato?: {
    id: number;
    nome_completo: string;
    email: string;
  };
  categoria?: {
    id: number;
    nome: string;
  };
  created_at: string;
  updated_at?: string;
  data_chiusura?: string;
  tipo_chiusura?: string;
  note_chiusura?: string;
}

export interface TicketListResponse {
  total: number;
  page: number;
  limit: number;
  tickets: Ticket[];
}

export interface TicketCreate {
  oggetto: string;
  descrizione?: string;
  cliente_id: number;
  priorita_id?: number;
  canale_id?: number;
  categoria_id?: number;
  richiedente_nome?: string;
  richiedente_email?: string;
  richiedente_telefono?: string;
  referente_id?: number;
  referente_nome?: string;
  contratto_id?: number;
}

export interface TicketUpdate {
  oggetto?: string;
  descrizione?: string;
  priorita_id?: number;
  categoria_id?: number;
  stato_id?: number;
  tecnico_assegnato_id?: number;
}

export interface TicketAssignRequest {
  tecnico_id: number;
}

export interface TicketCloseRequest {
  tipo_chiusura: string;
  note_chiusura?: string;
}

export interface TicketNoteCreate {
  nota: string;
}

export interface TicketMessaggioCreate {
  messaggio: string;
}

export interface TicketFilters {
  page?: number;
  limit?: number;
  stato_id?: number;
  priorita_id?: number;
  tecnico_id?: number;
  tecnico_assegnato_id?: number;
  cliente_id?: number;
  search?: string;
}

export const ticketsApi = {
  // Get list of tickets with filters
  async getAll(filters?: TicketFilters): Promise<TicketListResponse> {
    const response = await apiClient.get<TicketListResponse>('/tickets', {
      params: filters
    });
    return response.data;
  },

  // Get single ticket by ID
  async getById(ticketId: number): Promise<Ticket> {
    const response = await apiClient.get<Ticket>(`/tickets/${ticketId}`);
    return response.data;
  },

  // Create new ticket
  async create(data: TicketCreate): Promise<Ticket> {
    const response = await apiClient.post<Ticket>('/tickets', data);
    return response.data;
  },

  // Update ticket
  async update(ticketId: number, data: TicketUpdate): Promise<Ticket> {
    const response = await apiClient.patch<Ticket>(`/tickets/${ticketId}`, data);
    return response.data;
  },

  // Assign ticket to technician
  async assign(ticketId: number, data: TicketAssignRequest): Promise<Ticket> {
    const response = await apiClient.post<Ticket>(`/tickets/${ticketId}/assign`, data);
    return response.data;
  },

  // Take ticket (assign to current user)
  async take(ticketId: number): Promise<Ticket> {
    const response = await apiClient.post<Ticket>(`/tickets/${ticketId}/take`);
    return response.data;
  },

  // Close ticket
  async close(ticketId: number, data: TicketCloseRequest): Promise<Ticket> {
    const response = await apiClient.post<Ticket>(`/tickets/${ticketId}/close`, data);
    return response.data;
  },

  // Add internal note
  async addNote(ticketId: number, data: TicketNoteCreate): Promise<{ id: number; nota: string; created_at: string }> {
    const response = await apiClient.post(`/tickets/${ticketId}/notes`, data);
    return response.data;
  },

  // Add client message
  async addMessage(ticketId: number, data: TicketMessaggioCreate): Promise<{ id: number; messaggio: string; mittente_tipo: string; created_at: string }> {
    const response = await apiClient.post(`/tickets/${ticketId}/messages`, data);
    return response.data;
  },

  // Soft delete ticket
  async delete(ticketId: number): Promise<void> {
    await apiClient.delete(`/tickets/${ticketId}`);
  },

  // Create immediate intervention from ticket
  async createIntervention(ticketId: number): Promise<{ intervento_id: number; ticket_id: number; message: string }> {
    const response = await apiClient.post(`/tickets/${ticketId}/create-intervention`);
    return response.data;
  },

  // Schedule intervention request from ticket
  async scheduleIntervention(ticketId: number): Promise<{ richiesta_id: number; ticket_id: number; message: string }> {
    const response = await apiClient.post(`/tickets/${ticketId}/schedule-intervention`);
    return response.data;
  }
};

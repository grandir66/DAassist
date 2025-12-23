import apiClient from './client';

export interface LookupItem {
  id: number;
  codice: string;
  descrizione: string;
  attivo: boolean;
}

export interface Priority extends LookupItem {
  livello: number;
  colore: string;
}

export interface State extends LookupItem {
  colore: string;
  finale: boolean;
}

export interface InterventionType extends LookupItem {
  colore: string;
  richiede_viaggio: boolean;
}

export interface ActivityCategory extends LookupItem {
  prezzo_unitario_default: number;
}

export interface Department extends LookupItem {
  email: string | null;
}

export type Reparto = Department;
export type Ruolo = LookupItem;

export const lookupApi = {
  async getChannels(): Promise<LookupItem[]> {
    const response = await apiClient.get<LookupItem[]>('/lookup/channels');
    return response.data;
  },

  async getPriorities(): Promise<Priority[]> {
    const response = await apiClient.get<Priority[]>('/lookup/priorities');
    return response.data;
  },

  async getTicketStates(): Promise<State[]> {
    const response = await apiClient.get<State[]>('/lookup/ticket-states');
    return response.data;
  },

  async getInterventionStates(): Promise<State[]> {
    const response = await apiClient.get<State[]>('/lookup/intervention-states');
    return response.data;
  },

  async getInterventionTypes(): Promise<InterventionType[]> {
    const response = await apiClient.get<InterventionType[]>('/lookup/intervention-types');
    return response.data;
  },

  async getActivityCategories(): Promise<ActivityCategory[]> {
    const response = await apiClient.get<ActivityCategory[]>('/lookup/activity-categories');
    return response.data;
  },

  async getInterventionOrigins(): Promise<LookupItem[]> {
    const response = await apiClient.get<LookupItem[]>('/lookup/intervention-origins');
    return response.data;
  },

  async getDepartments(): Promise<Department[]> {
    const response = await apiClient.get<Department[]>('/lookup/departments');
    return response.data;
  },

  async getUserRoles(): Promise<LookupItem[]> {
    const response = await apiClient.get<LookupItem[]>('/lookup/user-roles');
    return response.data;
  },

  // Alias per compatibilità
  getReparti: async (): Promise<Department[]> => {
    const response = await apiClient.get<Department[]>('/lookup/departments');
    return response.data;
  },

  getRuoli: async (): Promise<LookupItem[]> => {
    const response = await apiClient.get<LookupItem[]>('/lookup/user-roles');
    return response.data;
  },
};

import { apiClient } from './client';

export interface Reparto {
  id: number;
  codice: string;
  descrizione: string;
}

export interface Ruolo {
  id: number;
  codice: string;
  descrizione: string;
}

export interface Technician {
  id: number;
  username: string;
  email: string;
  nome: string;
  cognome: string;
  telefono?: string;
  cellulare?: string;
  interno_telefonico?: string;
  telegram_id?: string;
  reparto_id?: number;
  reparto?: Reparto;
  ruolo_id: number;
  ruolo?: Ruolo;
  codice_tecnico?: string;
  ldap_dn?: string;
  ldap_enabled: boolean;
  username_ad?: string;
  colore_calendario: string;
  notifiche_email: boolean;
  notifiche_push: boolean;
  note?: string;
  ultimo_login?: string;
  attivo: boolean;
  created_at: string;
  updated_at: string;
}

export interface TechnicianCreate {
  username: string;
  email: string;
  password: string;
  nome: string;
  cognome: string;
  telefono?: string;
  cellulare?: string;
  interno_telefonico?: string;
  telegram_id?: string;
  reparto_id?: number;
  ruolo_id: number;
  codice_tecnico?: string;
  ldap_dn?: string;
  ldap_enabled?: boolean;
  username_ad?: string;
  colore_calendario?: string;
  notifiche_email?: boolean;
  notifiche_push?: boolean;
  note?: string;
}

export interface TechnicianUpdate {
  email?: string;
  password?: string;
  nome?: string;
  cognome?: string;
  telefono?: string;
  cellulare?: string;
  interno_telefonico?: string;
  telegram_id?: string;
  reparto_id?: number;
  ruolo_id?: number;
  codice_tecnico?: string;
  ldap_dn?: string;
  ldap_enabled?: boolean;
  username_ad?: string;
  colore_calendario?: string;
  notifiche_email?: boolean;
  notifiche_push?: boolean;
  note?: string;
  attivo?: boolean;
}

export interface TechnicianFilters {
  page?: number;
  limit?: number;
  search?: string;
  reparto_id?: number;
  ruolo_id?: number;
  attivo?: boolean;
}

export interface TechnicianListResponse {
  items: Technician[];
  total: number;
  page: number;
  limit: number;
}

export const techniciansApi = {
  getAll: async (filters?: TechnicianFilters): Promise<TechnicianListResponse> => {
    const response = await apiClient.get<TechnicianListResponse>('/technicians', {
      params: filters,
    });
    return response.data;
  },

  getById: async (id: number): Promise<Technician> => {
    const response = await apiClient.get<Technician>(`/technicians/${id}`);
    return response.data;
  },

  create: async (data: TechnicianCreate): Promise<Technician> => {
    const response = await apiClient.post<Technician>('/technicians', data);
    return response.data;
  },

  update: async (id: number, data: TechnicianUpdate): Promise<Technician> => {
    const response = await apiClient.put<Technician>(`/technicians/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/technicians/${id}`);
  },
};

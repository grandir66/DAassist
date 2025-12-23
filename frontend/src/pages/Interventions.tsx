import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import { Plus, Search, Filter, Clock, MapPin, X } from 'lucide-react';
import Input from '@/components/ui/Input';
import { interventiApi, type Intervento, type InterventoFilters } from '@/api/interventions';
import { lookupApi, type State } from '@/api/lookup';
import { clientiApi, type Cliente } from '@/api/clients';
import { authApi, type Tecnico } from '@/api/auth';
import InterventionCreateForm from '@/components/InterventionCreateForm';

export default function Interventions() {
  const navigate = useNavigate();
  const [interventi, setInterventi] = useState<Intervento[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<InterventoFilters>({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Filter options
  const [stati, setStati] = useState<State[]>([]);
  const [clienti, setClienti] = useState<Cliente[]>([]);
  const [tecnici, setTecnici] = useState<Tecnico[]>([]);

  // Load filter options
  useEffect(() => {
    loadFilterOptions();
  }, []);

  useEffect(() => {
    loadInterventi();
  }, [page, filters]);

  const loadFilterOptions = async () => {
    try {
      const [statiData, clientiData, tecniciData] = await Promise.all([
        lookupApi.getInterventionStates(),
        clientiApi.getAll({ page: 1, limit: 1000 }),
        authApi.getTecnici(),
      ]);
      setStati(statiData);
      setClienti(clientiData.clienti);
      setTecnici(tecniciData);
    } catch (error) {
      console.error('Failed to load filter options:', error);
    }
  };

  const loadInterventi = async () => {
    try {
      setLoading(true);
      const response = await interventiApi.getAll({
        page,
        limit,
        ...filters,
      });
      setInterventi(response.interventi);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load interventions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search });
    setPage(1);
  };

  const getTipoColor = (codice?: string) => {
    const colors: Record<string, string> = {
      CLIENTE: 'bg-blue-100 text-blue-800 border-blue-200',
      REMOTO: 'bg-green-100 text-green-800 border-green-200',
      LABORATORIO: 'bg-purple-100 text-purple-800 border-purple-200',
      TELEFONICO: 'bg-orange-100 text-orange-800 border-orange-200',
    };
    return colors[codice || ''] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatoColor = (codice?: string) => {
    const colors: Record<string, string> = {
      PIANIFICATO: 'bg-blue-100 text-blue-800 border-blue-200',
      IN_CORSO: 'bg-orange-100 text-orange-800 border-orange-200',
      COMPLETATO: 'bg-green-100 text-green-800 border-green-200',
      ANNULLATO: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[codice || ''] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const formatDurata = (minuti: number) => {
    const ore = Math.floor(minuti / 60);
    const min = minuti % 60;
    if (ore === 0) return `${min}m`;
    if (min === 0) return `${ore}h`;
    return `${ore}h ${min}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Interventi</h1>
          <p className="text-muted-foreground">Gestione interventi tecnici</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuovo Intervento
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Cerca per numero, descrizione..."
                className="pl-10"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Button type="submit" variant="outline">
              <Search className="h-4 w-4 mr-2" />
              Cerca
            </Button>
            <Button
              variant="outline"
              type="button"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filtri Avanzati
            </Button>
          </form>

          {showFilters && (
            <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium">Stato</label>
                <Select
                  value={filters.stato_id || ''}
                  onChange={(e) => {
                    const newFilters = { ...filters };
                    if (e.target.value) {
                      newFilters.stato_id = parseInt(e.target.value);
                    } else {
                      delete newFilters.stato_id;
                    }
                    setFilters(newFilters);
                    setPage(1);
                  }}
                  className="mt-1"
                >
                  <option value="">Tutti gli stati</option>
                  {stati.map(stato => (
                    <option key={stato.id} value={stato.id}>
                      {stato.descrizione}
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Cliente</label>
                <Select
                  value={filters.cliente_id || ''}
                  onChange={(e) => {
                    const newFilters = { ...filters };
                    if (e.target.value) {
                      newFilters.cliente_id = parseInt(e.target.value);
                    } else {
                      delete newFilters.cliente_id;
                    }
                    setFilters(newFilters);
                    setPage(1);
                  }}
                  className="mt-1"
                >
                  <option value="">Tutti i clienti</option>
                  {clienti.map(cliente => (
                    <option key={cliente.id} value={cliente.id}>
                      {cliente.ragione_sociale}
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Tecnico</label>
                <Select
                  value={filters.tecnico_id || ''}
                  onChange={(e) => {
                    const newFilters = { ...filters };
                    if (e.target.value) {
                      newFilters.tecnico_id = parseInt(e.target.value);
                    } else {
                      delete newFilters.tecnico_id;
                    }
                    setFilters(newFilters);
                    setPage(1);
                  }}
                  className="mt-1"
                >
                  <option value="">Tutti i tecnici</option>
                  {tecnici.map(tecnico => (
                    <option key={tecnico.id} value={tecnico.id}>
                      {tecnico.cognome} {tecnico.nome}
                    </option>
                  ))}
                </Select>
              </div>

              {Object.keys(filters).length > 0 && (
                <div className="md:col-span-3 flex justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setFilters({});
                      setPage(1);
                    }}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancella Filtri
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Interventions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista Interventi ({total})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Caricamento...</div>
          ) : interventi.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Nessun intervento trovato
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-sm">Numero</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Cliente</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Descrizione</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Tipo</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Stato</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Tecnico</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Data</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Durata</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Azioni</th>
                    </tr>
                  </thead>
                  <tbody>
                    {interventi.map((intervento) => (
                      <tr
                        key={intervento.id}
                        className="border-b hover:bg-muted/50 cursor-pointer transition-colors"
                        onClick={() => navigate(`/interventions/${intervento.id}`)}
                      >
                        <td className="py-3 px-4">
                          <span className="font-medium text-primary">{intervento.numero}</span>
                        </td>
                        <td className="py-3 px-4">{intervento.cliente?.ragione_sociale || '-'}</td>
                        <td className="py-3 px-4">
                          <span className="max-w-xs truncate block">{intervento.oggetto}</span>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getTipoColor(
                              intervento.tipo_intervento?.codice
                            )}`}
                          >
                            {intervento.tipo_intervento?.richiede_viaggio && (
                              <MapPin className="h-3 w-3 mr-1" />
                            )}
                            {intervento.tipo_intervento?.descrizione || 'N/D'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getStatoColor(
                              intervento.stato?.codice
                            )}`}
                          >
                            {intervento.stato?.descrizione || 'N/D'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {intervento.tecnico?.nome_completo || 'Non assegnato'}
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {intervento.data_inizio
                            ? new Date(intervento.data_inizio).toLocaleDateString('it-IT')
                            : '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {intervento.data_inizio && intervento.data_fine
                            ? `${Math.round((new Date(intervento.data_fine).getTime() - new Date(intervento.data_inizio).getTime()) / 60000)}m`
                            : '-'}
                        </td>
                        <td className="py-3 px-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/interventions/${intervento.id}`);
                            }}
                          >
                            Dettagli
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {total > limit && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t">
                  <div className="text-sm text-muted-foreground">
                    Pagina {page} di {Math.ceil(total / limit)} - Totale: {total} interventi
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      Precedente
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(p => p + 1)}
                      disabled={page >= Math.ceil(total / limit)}
                    >
                      Successiva
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Create Intervention Form */}
      <InterventionCreateForm
        open={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={loadInterventi}
      />
    </div>
  );
}

import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import { Plus, Search, Filter, X } from 'lucide-react';
import Input from '@/components/ui/Input';
import { ticketsApi, type Ticket, type TicketFilters } from '@/api/tickets';
import { lookupApi, type State, type Priority } from '@/api/lookup';
import { clientiApi, type Cliente } from '@/api/clients';
import { authApi, type Tecnico } from '@/api/auth';
import TicketCreateForm from '@/components/TicketCreateForm';

export default function Tickets() {
  const navigate = useNavigate();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<TicketFilters>({});
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Filter options
  const [stati, setStati] = useState<State[]>([]);
  const [priorita, setPriorita] = useState<Priority[]>([]);
  const [clienti, setClienti] = useState<Cliente[]>([]);
  const [tecnici, setTecnici] = useState<Tecnico[]>([]);

  // Load filter options
  useEffect(() => {
    loadFilterOptions();
  }, []);

  // Load tickets
  useEffect(() => {
    loadTickets();
  }, [page, filters]);

  const loadFilterOptions = async () => {
    try {
      const [statiData, prioritaData, clientiData, tecniciData] = await Promise.all([
        lookupApi.getTicketStates(),
        lookupApi.getPriorities(),
        clientiApi.getAll({ page: 1, limit: 1000 }),
        authApi.getTecnici(),
      ]);
      setStati(statiData);
      setPriorita(prioritaData);
      setClienti(clientiData.clienti);
      setTecnici(tecniciData);
    } catch (error) {
      console.error('Failed to load filter options:', error);
    }
  };

  const loadTickets = async () => {
    try {
      setLoading(true);
      const response = await ticketsApi.getAll({
        page,
        limit,
        ...filters,
      });
      setTickets(response.tickets);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search });
    setPage(1);
  };

  const getPriorityColor = (priorita: string) => {
    const colors: Record<string, string> = {
      CRITICA: 'bg-red-100 text-red-800 border-red-200',
      URGENTE: 'bg-orange-100 text-orange-800 border-orange-200',
      ALTA: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      NORMALE: 'bg-blue-100 text-blue-800 border-blue-200',
      BASSA: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[priorita] || colors.NORMALE;
  };

  const getStatoColor = (stato: string) => {
    const colors: Record<string, string> = {
      NUOVO: 'bg-blue-100 text-blue-800 border-blue-200',
      PRESO_CARICO: 'bg-purple-100 text-purple-800 border-purple-200',
      IN_LAVORAZIONE: 'bg-orange-100 text-orange-800 border-orange-200',
      SCHEDULATO: 'bg-cyan-100 text-cyan-800 border-cyan-200',
      CHIUSO: 'bg-green-100 text-green-800 border-green-200',
      ANNULLATO: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[stato] || colors.NUOVO;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ticket</h1>
          <p className="text-muted-foreground">Gestione richieste di assistenza</p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Nuovo Ticket
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Cerca per numero, cliente, oggetto..."
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
            <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-4 gap-4">
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
                <label className="text-sm font-medium">Priorità</label>
                <Select
                  value={filters.priorita_id || ''}
                  onChange={(e) => {
                    const newFilters = { ...filters };
                    if (e.target.value) {
                      newFilters.priorita_id = parseInt(e.target.value);
                    } else {
                      delete newFilters.priorita_id;
                    }
                    setFilters(newFilters);
                    setPage(1);
                  }}
                  className="mt-1"
                >
                  <option value="">Tutte le priorità</option>
                  {priorita.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.descrizione}
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
                <label className="text-sm font-medium">Tecnico Assegnato</label>
                <Select
                  value={filters.tecnico_assegnato_id || ''}
                  onChange={(e) => {
                    const newFilters = { ...filters };
                    if (e.target.value) {
                      newFilters.tecnico_assegnato_id = parseInt(e.target.value);
                    } else {
                      delete newFilters.tecnico_assegnato_id;
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
                <div className="md:col-span-4 flex justify-end">
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

      {/* Tickets Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista Ticket ({total})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Caricamento...</div>
          ) : tickets.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">Nessun ticket trovato</div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-sm">Numero</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Cliente</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Oggetto</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Priorità</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Stato</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Tecnico</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Creato</th>
                      <th className="text-left py-3 px-4 font-medium text-sm">Azioni</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tickets.map((ticket) => (
                      <tr key={ticket.id} className="border-b hover:bg-muted/50 cursor-pointer transition-colors" onClick={() => navigate(`/tickets/${ticket.id}`)}>
                        <td className="py-3 px-4">
                          <span className="font-medium text-primary">{ticket.numero}</span>
                        </td>
                        <td className="py-3 px-4">{ticket.cliente?.ragione_sociale || '-'}</td>
                        <td className="py-3 px-4">
                          <span className="max-w-xs truncate block">{ticket.oggetto}</span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getPriorityColor(ticket.priorita?.codice || 'NORMALE')}`}>
                            {ticket.priorita?.descrizione || 'Normale'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getStatoColor(ticket.stato?.codice || 'NUOVO')}`}>
                            {ticket.stato?.descrizione || 'Nuovo'}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {ticket.tecnico_assegnato?.nome_completo || 'Non assegnato'}
                        </td>
                        <td className="py-3 px-4 text-sm text-muted-foreground">
                          {new Date(ticket.created_at).toLocaleString('it-IT')}
                        </td>
                        <td className="py-3 px-4">
                          <Button variant="ghost" size="sm" onClick={() => navigate(`/tickets/${ticket.id}`)}>
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
                    Pagina {page} di {Math.ceil(total / limit)} - Totale: {total} ticket
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

      {/* Create Ticket Form */}
      <TicketCreateForm
        open={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        onSuccess={loadTickets}
      />
    </div>
  );
}

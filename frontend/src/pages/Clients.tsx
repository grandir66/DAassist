import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { Search, Building2, Phone, Mail } from 'lucide-react';
import Input from '@/components/ui/Input';
import { clientiApi, type Cliente, type ClienteFilters } from '@/api/clients';

export default function Clients() {
  const navigate = useNavigate();
  const [clienti, setClienti] = useState<Cliente[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<ClienteFilters>({});

  useEffect(() => {
    loadClienti();
  }, [page, filters]);

  const loadClienti = async () => {
    try {
      setLoading(true);
      const response = await clientiApi.getAll({
        page,
        limit,
        ...filters,
      });
      setClienti(response.clienti);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setFilters({ ...filters, search });
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Clienti</h1>
          <p className="text-muted-foreground">Gestione anagrafica clienti</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Cerca per ragione sociale, codice, P.IVA..."
                className="pl-10"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Button type="submit" variant="outline">
              <Search className="h-4 w-4 mr-2" />
              Cerca
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Clients Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            Caricamento...
          </div>
        ) : clienti.length === 0 ? (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            Nessun cliente trovato
          </div>
        ) : (
          clienti.map((cliente) => (
            <Card
              key={cliente.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => navigate(`/clients/${cliente.id}`)}
            >
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Building2 className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg truncate">
                      {cliente.ragione_sociale}
                    </CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {cliente.codice_gestionale}
                    </p>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {cliente.citta && cliente.provincia && (
                  <div className="text-sm text-muted-foreground">
                    {cliente.citta} ({cliente.provincia})
                  </div>
                )}
                {cliente.telefono && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{cliente.telefono}</span>
                  </div>
                )}
                {cliente.email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span className="truncate">{cliente.email}</span>
                  </div>
                )}
                <div className="pt-2">
                  <Button variant="outline" size="sm" className="w-full">
                    Dettagli
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Pagination */}
      {total > limit && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Pagina {page} di {Math.ceil(total / limit)} - Totale: {total} clienti
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
          </CardContent>
        </Card>
      )}
    </div>
  );
}

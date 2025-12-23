import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Phone,
  Mail,
  FileText,
  Users,
  Star,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { clientiApi, type Cliente, type SedeCliente, type Referente, type Contratto } from '@/api/clients';

type TabType = 'info' | 'sedi' | 'contatti' | 'contratti';

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [cliente, setCliente] = useState<Cliente | null>(null);
  const [sedi, setSedi] = useState<SedeCliente[]>([]);
  const [contatti, setContatti] = useState<Referente[]>([]);
  const [contratti, setContratti] = useState<Contratto[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('info');

  useEffect(() => {
    if (id) {
      loadClientData(parseInt(id));
    }
  }, [id]);

  const loadClientData = async (clienteId: number) => {
    try {
      setLoading(true);

      // Load all data in parallel
      const [clienteData, sediData, contattiData, contrattiData] = await Promise.all([
        clientiApi.getById(clienteId),
        clientiApi.getSedi(clienteId),
        clientiApi.getContatti(clienteId),
        clientiApi.getContratti(clienteId),
      ]);

      setCliente(clienteData);
      setSedi(sediData);
      setContatti(contattiData);
      setContratti(contrattiData);
    } catch (error) {
      console.error('Failed to load client data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatoColor = (stato?: string) => {
    switch (stato) {
      case 'ATTIVO':
        return 'text-green-600 bg-green-50';
      case 'SOSPESO':
        return 'text-yellow-600 bg-yellow-50';
      case 'INATTIVO':
        return 'text-gray-600 bg-gray-50';
      case 'PROSPECT':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getClassificazioneColor = (classificazione?: string) => {
    switch (classificazione) {
      case 'VIP':
        return 'text-purple-600 bg-purple-50';
      case 'PREMIUM':
        return 'text-pink-600 bg-pink-50';
      case 'ENTERPRISE':
        return 'text-emerald-600 bg-emerald-50';
      case 'STANDARD':
        return 'text-blue-600 bg-blue-50';
      case 'BASIC':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const parseOrariServizio = (orariJson?: string) => {
    if (!orariJson) return null;
    try {
      return JSON.parse(orariJson);
    } catch {
      return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!cliente) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Cliente non trovato</h3>
        <div className="mt-6">
          <Button onClick={() => navigate('/clients')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Torna ai Clienti
          </Button>
        </div>
      </div>
    );
  }

  const orariServizio = parseOrariServizio(cliente.orari_servizio);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/clients')}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{cliente.ragione_sociale}</h1>
            <p className="text-sm text-gray-500">Codice: {cliente.codice_gestionale}</p>
          </div>
        </div>
        <div className="flex gap-2">
          {cliente.stato_cliente && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatoColor(cliente.stato_cliente)}`}>
              {cliente.stato_cliente}
            </span>
          )}
          {cliente.classificazione && (
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getClassificazioneColor(cliente.classificazione)}`}>
              {cliente.classificazione}
            </span>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('info')}
            className={`${
              activeTab === 'info'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <Building2 className="inline h-4 w-4 mr-2" />
            Informazioni Generali
          </button>
          <button
            onClick={() => setActiveTab('sedi')}
            className={`${
              activeTab === 'sedi'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <MapPin className="inline h-4 w-4 mr-2" />
            Sedi Operative ({sedi.length})
          </button>
          <button
            onClick={() => setActiveTab('contatti')}
            className={`${
              activeTab === 'contatti'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <Users className="inline h-4 w-4 mr-2" />
            Contatti/Rubrica ({contatti.length})
          </button>
          <button
            onClick={() => setActiveTab('contratti')}
            className={`${
              activeTab === 'contratti'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            <FileText className="inline h-4 w-4 mr-2" />
            Contratti ({contratti.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'info' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Dati Anagrafici */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Dati Anagrafici
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Ragione Sociale</label>
                  <p className="text-gray-900">{cliente.ragione_sociale}</p>
                </div>
                {cliente.partita_iva && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Partita IVA</label>
                    <p className="text-gray-900">{cliente.partita_iva}</p>
                  </div>
                )}
                {cliente.codice_fiscale && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Codice Fiscale</label>
                    <p className="text-gray-900">{cliente.codice_fiscale}</p>
                  </div>
                )}
                {cliente.nomi_alternativi && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Nomi Alternativi</label>
                    <p className="text-gray-900">{cliente.nomi_alternativi}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Sede Legale */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Sede Legale
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {cliente.indirizzo && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Indirizzo</label>
                    <p className="text-gray-900">{cliente.indirizzo}</p>
                    {(cliente.cap || cliente.citta || cliente.provincia) && (
                      <p className="text-gray-900">
                        {cliente.cap} {cliente.citta} {cliente.provincia && `(${cliente.provincia})`}
                      </p>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Contatti */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Contatti
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {cliente.telefono && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Telefono</label>
                    <p className="text-gray-900">{cliente.telefono}</p>
                  </div>
                )}
                {cliente.email && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Email</label>
                    <p className="text-gray-900">{cliente.email}</p>
                  </div>
                )}
                {cliente.pec && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">PEC</label>
                    <p className="text-gray-900">{cliente.pec}</p>
                  </div>
                )}
                {cliente.sito_web && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Sito Web</label>
                    <p className="text-gray-900">
                      <a href={cliente.sito_web} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {cliente.sito_web}
                      </a>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Orari di Servizio */}
            {orariServizio && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5" />
                    Orari di Servizio
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {Object.entries(orariServizio).map(([giorno, orario]: [string, any]) => (
                    <div key={giorno} className="flex justify-between">
                      <span className="text-sm font-medium text-gray-700 capitalize">{giorno}</span>
                      <span className="text-sm text-gray-900">
                        {orario.inizio} - {orario.fine}
                      </span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Note */}
            {cliente.note && (
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Note
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-900 whitespace-pre-wrap">{cliente.note}</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {activeTab === 'sedi' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {sedi.length === 0 ? (
              <div className="col-span-2 text-center py-12">
                <MapPin className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Nessuna sede operativa</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Non ci sono sedi operative registrate per questo cliente
                </p>
              </div>
            ) : (
              sedi.map((sede) => (
                <Card key={sede.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MapPin className="h-5 w-5" />
                      {sede.nome_sede}
                    </CardTitle>
                    {sede.codice_sede && (
                      <p className="text-sm text-gray-500">Codice: {sede.codice_sede}</p>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Indirizzo</label>
                      <p className="text-gray-900">{sede.indirizzo}</p>
                      <p className="text-gray-900">
                        {sede.cap} {sede.citta} {sede.provincia && `(${sede.provincia})`}
                      </p>
                    </div>
                    {sede.telefono && (
                      <div>
                        <label className="text-sm font-medium text-gray-700">Telefono</label>
                        <p className="text-gray-900">{sede.telefono}</p>
                      </div>
                    )}
                    {sede.email && (
                      <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <p className="text-gray-900">{sede.email}</p>
                      </div>
                    )}
                    {sede.note && (
                      <div>
                        <label className="text-sm font-medium text-gray-700">Note</label>
                        <p className="text-sm text-gray-900">{sede.note}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'contatti' && (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            {contatti.length === 0 ? (
              <div className="text-center py-12">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Nessun contatto</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Non ci sono contatti registrati per questo cliente
                </p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nome
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ruolo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contatti
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Flags
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {contatti.map((contatto) => (
                    <tr key={contatto.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {contatto.nome} {contatto.cognome}
                            </div>
                            {contatto.contatto_principale && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                <Star className="h-3 w-3 mr-1" />
                                Principale
                              </span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{contatto.ruolo || '-'}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 space-y-1">
                          {contatto.telefono && (
                            <div className="flex items-center gap-2">
                              <Phone className="h-3 w-3 text-gray-400" />
                              {contatto.telefono}
                            </div>
                          )}
                          {contatto.cellulare && (
                            <div className="flex items-center gap-2">
                              <Phone className="h-3 w-3 text-gray-400" />
                              {contatto.cellulare}
                            </div>
                          )}
                          {contatto.interno_telefonico && (
                            <div className="text-xs text-gray-500">
                              Interno: {contatto.interno_telefonico}
                            </div>
                          )}
                          {contatto.email && (
                            <div className="flex items-center gap-2">
                              <Mail className="h-3 w-3 text-gray-400" />
                              <a href={`mailto:${contatto.email}`} className="text-blue-600 hover:underline">
                                {contatto.email}
                              </a>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          {contatto.referente_it && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                              IT
                            </span>
                          )}
                          {contatto.riceve_notifiche && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Notifiche
                            </span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'contratti' && (
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            {contratti.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Nessun contratto</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Non ci sono contratti registrati per questo cliente
                </p>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Codice
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Descrizione
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Periodo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ore
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Stato
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {contratti.map((contratto) => {
                    const orePercentuale = contratto.ore_incluse
                      ? (contratto.ore_utilizzate / contratto.ore_incluse) * 100
                      : 0;

                    return (
                      <tr key={contratto.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {contratto.codice_gestionale}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">{contratto.descrizione}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {contratto.data_inizio && new Date(contratto.data_inizio).toLocaleDateString('it-IT')}
                            {contratto.data_fine && (
                              <> - {new Date(contratto.data_fine).toLocaleDateString('it-IT')}</>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {contratto.ore_incluse ? (
                            <div className="space-y-1">
                              <div className="text-sm text-gray-900">
                                {contratto.ore_utilizzate} / {contratto.ore_incluse} ore
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full ${
                                    orePercentuale >= 90
                                      ? 'bg-red-600'
                                      : orePercentuale >= 75
                                      ? 'bg-yellow-600'
                                      : 'bg-green-600'
                                  }`}
                                  style={{ width: `${Math.min(orePercentuale, 100)}%` }}
                                />
                              </div>
                            </div>
                          ) : (
                            <span className="text-sm text-gray-500">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {contratto.attivo ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Attivo
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                              Inattivo
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

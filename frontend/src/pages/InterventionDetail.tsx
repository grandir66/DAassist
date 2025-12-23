import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Select from '@/components/ui/Select';
import Textarea from '@/components/ui/Textarea';
import {
  ArrowLeft,
  User,
  Building2,
  Clock,
  AlertCircle,
  FileText,
  PlayCircle,
  CheckCircle,
  MapPin,
  Calendar,
  ClipboardList
} from 'lucide-react';
import { interventiApi, type Intervento } from '@/api/interventions';
import { clientiApi, type Contratto } from '@/api/clients';
import { lookupApi, type State } from '@/api/lookup';
import InterventionSessionsTab from '@/components/InterventionSessionsTab';
import InterventionRowsTab from '@/components/InterventionRowsTab';

type TabType = 'dettagli' | 'sessioni' | 'righe';

export default function InterventionDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [intervento, setIntervento] = useState<Intervento | null>(null);
  const [contratti, setContratti] = useState<Contratto[]>([]);
  const [stati, setStati] = useState<State[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('dettagli');

  // Azioni
  const [showStartModal, setShowStartModal] = useState(false);
  const [noteAvvio, setNoteAvvio] = useState('');
  const [showCompleteModal, setShowCompleteModal] = useState(false);
  const [descrizioneFinale, setDescrizioneFinale] = useState('');

  useEffect(() => {
    if (id) {
      loadInterventoData(parseInt(id));
    }
  }, [id]);

  const loadInterventoData = async (interventoId: number) => {
    try {
      setLoading(true);

      // Load intervention details
      const interventoData = await interventiApi.getById(interventoId);
      setIntervento(interventoData);

      // Load related data in parallel
      const [statiData, contrattiData] = await Promise.all([
        lookupApi.getInterventionStates(),
        interventoData.cliente?.id ? clientiApi.getContratti(interventoData.cliente.id) : Promise.resolve([]),
      ]);

      setStati(statiData);
      setContratti(contrattiData);
    } catch (error) {
      console.error('Failed to load intervention:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChangeState = async (nuovoStatoId: number) => {
    if (!intervento) return;

    try {
      setUpdating(true);
      await interventiApi.update(intervento.id, { stato_id: nuovoStatoId });
      await loadInterventoData(intervento.id);
    } catch (error) {
      console.error('Failed to update intervention status:', error);
      alert('Errore nell\'aggiornamento dello stato');
    } finally {
      setUpdating(false);
    }
  };

  const handleStartIntervento = async () => {
    if (!intervento) return;

    try {
      setUpdating(true);
      await interventiApi.start(intervento.id, { note_avvio: noteAvvio });
      setShowStartModal(false);
      setNoteAvvio('');
      await loadInterventoData(intervento.id);
    } catch (error) {
      console.error('Failed to start intervention:', error);
      alert('Errore nell\'avvio dell\'intervento');
    } finally {
      setUpdating(false);
    }
  };

  const handleCompleteIntervento = async () => {
    if (!intervento || !descrizioneFinale) return;

    try {
      setUpdating(true);
      await interventiApi.complete(intervento.id, {
        descrizione_lavoro: descrizioneFinale,
      });
      setShowCompleteModal(false);
      setDescrizioneFinale('');
      await loadInterventoData(intervento.id);
    } catch (error) {
      console.error('Failed to complete intervention:', error);
      alert('Errore nel completamento dell\'intervento');
    } finally {
      setUpdating(false);
    }
  };

  const getContrattoAttivo = () => {
    const oggi = new Date();
    return contratti.find(c => {
      if (!c.data_fine) return false;
      const dataFine = new Date(c.data_fine);
      return dataFine >= oggi && c.attivo;
    });
  };

  const getStatoColor = (codice?: string) => {
    const colors: Record<string, string> = {
      PIANIFICATO: 'bg-blue-100 text-blue-800 border-blue-200',
      IN_CORSO: 'bg-orange-100 text-orange-800 border-orange-200',
      COMPLETATO: 'bg-green-100 text-green-800 border-green-200',
      ANNULLATO: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[codice || ''] || colors.PIANIFICATO;
  };

  const getTipoColor = (richiede_viaggio?: boolean) => {
    return richiede_viaggio
      ? 'bg-purple-100 text-purple-800 border-purple-200'
      : 'bg-blue-100 text-blue-800 border-blue-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <p className="mt-2 text-sm text-muted-foreground">Caricamento...</p>
        </div>
      </div>
    );
  }

  if (!intervento) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Intervento non trovato</h2>
        <Button onClick={() => navigate('/interventions')}>Torna alla lista</Button>
      </div>
    );
  }

  const contrattoAttivo = getContrattoAttivo();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/interventions')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Indietro
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{intervento.numero}</h1>
            <p className="text-muted-foreground">{intervento.oggetto}</p>
          </div>
        </div>

        <div className="flex gap-2">
          {intervento.tipo_intervento && (
            <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${getTipoColor(intervento.tipo_intervento.richiede_viaggio)}`}>
              {intervento.tipo_intervento.richiede_viaggio && <MapPin className="h-3 w-3 mr-1" />}
              {intervento.tipo_intervento.descrizione}
            </span>
          )}
          <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${getStatoColor(intervento.stato?.codice)}`}>
            {intervento.stato?.descrizione || 'Pianificato'}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-border">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('dettagli')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'dettagli'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <FileText className="h-4 w-4 inline mr-2" />
            Dettagli
          </button>
          <button
            onClick={() => setActiveTab('sessioni')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'sessioni'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Calendar className="h-4 w-4 inline mr-2" />
            Sessioni Lavoro
          </button>
          <button
            onClick={() => setActiveTab('righe')}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'righe'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <ClipboardList className="h-4 w-4 inline mr-2" />
            Righe Attività
          </button>
        </div>
      </div>

      {/* Tab Content - Dettagli */}
      {activeTab === 'dettagli' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Dettagli Intervento */}
            <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Dettagli Intervento
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {intervento.ticket_id && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Ticket Collegato</label>
                  <p
                    className="mt-1 text-primary cursor-pointer hover:underline"
                    onClick={() => navigate(`/tickets/${intervento.ticket_id}`)}
                  >
                    Vedi ticket #{intervento.ticket_id}
                  </p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-muted-foreground">Descrizione Lavoro</label>
                <p className="mt-1 whitespace-pre-wrap">
                  {intervento.descrizione_lavoro || 'Nessuna descrizione'}
                </p>
              </div>

              {intervento.note_interne && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Note Interne</label>
                  <p className="mt-1 whitespace-pre-wrap text-muted-foreground italic">
                    {intervento.note_interne}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                {intervento.data_inizio && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Data Inizio</label>
                    <p className="mt-1">{new Date(intervento.data_inizio).toLocaleString('it-IT')}</p>
                  </div>
                )}
                {intervento.data_fine && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Data Fine</label>
                    <p className="mt-1">{new Date(intervento.data_fine).toLocaleString('it-IT')}</p>
                  </div>
                )}
              </div>

              {intervento.tecnico && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Tecnico Assegnato</label>
                  <p className="mt-1 flex items-center gap-2">
                    <User className="h-4 w-4" />
                    {intervento.tecnico.nome_completo}
                  </p>
                </div>
              )}

              {intervento.origine && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Origine</label>
                  <p className="mt-1">{intervento.origine.descrizione}</p>
                </div>
              )}

              {intervento.firma_nome && (
                <div className="border-t pt-4">
                  <label className="text-sm font-medium text-muted-foreground">Firma Cliente</label>
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-md">
                    <div className="flex items-center gap-2 text-green-800">
                      <CheckCircle className="h-4 w-4" />
                      <span className="font-semibold">Firmato</span>
                    </div>
                    <p className="text-sm mt-1">
                      {intervento.firma_nome} {intervento.firma_ruolo && `- ${intervento.firma_ruolo}`}
                    </p>
                    {intervento.firma_data && (
                      <p className="text-xs text-green-700 mt-1">
                        {new Date(intervento.firma_data).toLocaleString('it-IT')}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Azioni */}
          <Card>
            <CardHeader>
              <CardTitle>Gestione Intervento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Cambio Stato */}
              <div>
                <label className="text-sm font-medium">Cambia Stato</label>
                <div className="flex gap-2 mt-2">
                  <Select
                    value={intervento.stato?.id || ''}
                    onChange={(e) => handleChangeState(parseInt(e.target.value))}
                    disabled={updating}
                    className="flex-1"
                  >
                    {stati.map(stato => (
                      <option key={stato.id} value={stato.id}>
                        {stato.descrizione}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>

              {/* Avvio Intervento */}
              {intervento.stato?.codice === 'PIANIFICATO' && (
                <div className="border-t pt-4">
                  <Button
                    className="w-full"
                    onClick={() => setShowStartModal(true)}
                  >
                    <PlayCircle className="h-4 w-4 mr-2" />
                    Avvia Intervento
                  </Button>
                </div>
              )}

              {/* Completamento Intervento */}
              {intervento.stato?.codice === 'IN_CORSO' && (
                <div className="border-t pt-4">
                  <Button
                    className="w-full"
                    onClick={() => {
                      setDescrizioneFinale(intervento.descrizione_lavoro || '');
                      setShowCompleteModal(true);
                    }}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Completa Intervento
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Cliente e Contratto */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Cliente
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="font-semibold">{intervento.cliente?.ragione_sociale}</p>
                <p className="text-sm text-muted-foreground">{intervento.cliente?.codice_gestionale}</p>
              </div>

              {/* Contratto */}
              <div className="border-t pt-4">
                <label className="text-sm font-medium">Copertura Contrattuale</label>
                {contrattoAttivo ? (
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-md">
                    <div className="flex items-center gap-2 text-green-800">
                      <CheckCircle className="h-4 w-4" />
                      <span className="font-semibold">Contratto Attivo</span>
                    </div>
                    <p className="text-sm mt-1">
                      {contrattoAttivo.tipologia_descrizione}
                    </p>
                    <p className="text-xs text-green-700 mt-1">
                      Scadenza: {new Date(contrattoAttivo.data_fine!).toLocaleDateString('it-IT')}
                    </p>
                  </div>
                ) : (
                  <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-md">
                    <div className="flex items-center gap-2 text-amber-800">
                      <AlertCircle className="h-4 w-4" />
                      <span className="font-semibold">Nessun Contratto Attivo</span>
                    </div>
                    <p className="text-xs text-amber-700 mt-1">
                      Intervento a consumo
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Cronologia */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Cronologia
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex gap-3">
                  <div className="flex-shrink-0 w-2 h-2 rounded-full bg-blue-500 mt-1.5"></div>
                  <div>
                    <p className="font-medium">Intervento creato</p>
                    <p className="text-muted-foreground">
                      {new Date(intervento.created_at).toLocaleString('it-IT')}
                    </p>
                  </div>
                </div>

                {intervento.data_inizio && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-2 h-2 rounded-full bg-orange-500 mt-1.5"></div>
                    <div>
                      <p className="font-medium">Intervento avviato</p>
                      <p className="text-muted-foreground">
                        {new Date(intervento.data_inizio).toLocaleString('it-IT')}
                      </p>
                    </div>
                  </div>
                )}

                {intervento.data_fine && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-2 h-2 rounded-full bg-green-500 mt-1.5"></div>
                    <div>
                      <p className="font-medium">Intervento completato</p>
                      <p className="text-muted-foreground">
                        {new Date(intervento.data_fine).toLocaleString('it-IT')}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      )}

      {/* Tab Content - Sessioni Lavoro */}
      {activeTab === 'sessioni' && intervento && (
        <InterventionSessionsTab interventoId={intervento.id} />
      )}

      {/* Tab Content - Righe Attività */}
      {activeTab === 'righe' && intervento && (
        <InterventionRowsTab interventoId={intervento.id} />
      )}

      {/* Modal Avvio Intervento */}
      {showStartModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowStartModal(false)} />
          <Card className="relative z-10 w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>Avvia Intervento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Note di Avvio (opzionale)</label>
                <Textarea
                  value={noteAvvio}
                  onChange={(e) => setNoteAvvio(e.target.value)}
                  placeholder="Aggiungi eventuali note sull'avvio dell'intervento..."
                  rows={3}
                  className="mt-2"
                />
              </div>

              <div className="flex gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowStartModal(false);
                    setNoteAvvio('');
                  }}
                  className="flex-1"
                >
                  Annulla
                </Button>
                <Button
                  onClick={handleStartIntervento}
                  disabled={updating}
                  className="flex-1"
                >
                  {updating ? 'Avvio...' : 'Avvia'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Modal Completamento Intervento */}
      {showCompleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowCompleteModal(false)} />
          <Card className="relative z-10 w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>Completa Intervento</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Descrizione Finale Lavoro *</label>
                <Textarea
                  value={descrizioneFinale}
                  onChange={(e) => setDescrizioneFinale(e.target.value)}
                  placeholder="Descrivi il lavoro svolto..."
                  rows={5}
                  className="mt-2"
                />
              </div>

              <div className="flex gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCompleteModal(false);
                    setDescrizioneFinale('');
                  }}
                  className="flex-1"
                >
                  Annulla
                </Button>
                <Button
                  onClick={handleCompleteIntervento}
                  disabled={!descrizioneFinale || updating}
                  className="flex-1"
                >
                  {updating ? 'Completamento...' : 'Completa'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

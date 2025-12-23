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
  Users,
  CheckCircle,
  Wrench
} from 'lucide-react';
import { ticketsApi, type Ticket } from '@/api/tickets';
import { clientiApi, type Contratto, type Referente } from '@/api/clients';
import { lookupApi, type State } from '@/api/lookup';
import { authApi, type Tecnico } from '@/api/auth';
import { interventiApi, type Intervento } from '@/api/interventions';

export default function TicketDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [contratti, setContratti] = useState<Contratto[]>([]);
  const [referenti, setReferenti] = useState<Referente[]>([]);
  const [stati, setStati] = useState<State[]>([]);
  const [tecnici, setTecnici] = useState<Tecnico[]>([]);
  const [interventi, setInterventi] = useState<Intervento[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  // Chiusura ticket
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [tipoChiusura, setTipoChiusura] = useState('');
  const [noteChiusura, setNoteChiusura] = useState('');

  useEffect(() => {
    if (id) {
      loadTicketData(parseInt(id));
    }
  }, [id]);

  const loadTicketData = async (ticketId: number) => {
    try {
      setLoading(true);

      // Load ticket details
      const ticketData = await ticketsApi.getById(ticketId);
      setTicket(ticketData);

      // Load related data in parallel
      const [statiData, contrattiData, referentiData, tecniciData, interventiData] = await Promise.all([
        lookupApi.getTicketStates(),
        ticketData.cliente?.id ? clientiApi.getContratti(ticketData.cliente.id) : Promise.resolve([]),
        ticketData.cliente?.id ? clientiApi.getReferenti(ticketData.cliente.id) : Promise.resolve([]),
        authApi.getTecnici(),
        interventiApi.getAll({ ticket_id: ticketId, limit: 100 }),
      ]);

      setStati(statiData);
      setContratti(contrattiData);
      setReferenti(referentiData);
      setTecnici(tecniciData);
      setInterventi(interventiData.interventi);
    } catch (error) {
      console.error('Failed to load ticket:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChangeState = async (nuovoStatoId: number) => {
    if (!ticket) return;

    try {
      setUpdating(true);
      await ticketsApi.update(ticket.id, { stato_id: nuovoStatoId });
      await loadTicketData(ticket.id);
    } catch (error) {
      console.error('Failed to update ticket status:', error);
      alert('Errore nell\'aggiornamento dello stato');
    } finally {
      setUpdating(false);
    }
  };

  const handleCloseTicket = async () => {
    if (!ticket || !tipoChiusura) return;

    try {
      setUpdating(true);
      await ticketsApi.close(ticket.id, {
        tipo_chiusura: tipoChiusura,
        note_chiusura: noteChiusura,
      });
      setShowCloseModal(false);
      await loadTicketData(ticket.id);
    } catch (error) {
      console.error('Failed to close ticket:', error);
      alert('Errore nella chiusura del ticket');
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignTecnico = async (tecnicoId: number | null) => {
    if (!ticket) return;

    try {
      setUpdating(true);
      await ticketsApi.update(ticket.id, {
        tecnico_assegnato_id: tecnicoId
      });
      await loadTicketData(ticket.id);
    } catch (error) {
      console.error('Failed to assign technician:', error);
      alert('Errore nell\'assegnazione del tecnico');
    } finally {
      setUpdating(false);
    }
  };

  const handleTakeTicket = async () => {
    if (!ticket) return;

    try {
      setUpdating(true);
      await ticketsApi.take(ticket.id);
      await loadTicketData(ticket.id);
      alert('Ticket preso in carico con successo');
    } catch (error) {
      console.error('Failed to take ticket:', error);
      alert('Errore nella presa in carico del ticket');
    } finally {
      setUpdating(false);
    }
  };

  const handleCreateIntervention = async () => {
    if (!ticket) return;

    if (!confirm('Vuoi creare un intervento immediato per questo ticket?')) return;

    try {
      setUpdating(true);
      const response = await ticketsApi.createIntervention(ticket.id);
      alert('Intervento creato con successo!');
      await loadTicketData(ticket.id);
      // Navigate to intervention
      navigate(`/interventions/${response.intervento_id}`);
    } catch (error) {
      console.error('Failed to create intervention:', error);
      alert('Errore nella creazione dell\'intervento');
    } finally {
      setUpdating(false);
    }
  };

  const handleScheduleIntervention = async () => {
    if (!ticket) return;

    if (!confirm('Vuoi creare una richiesta di intervento pianificato per questo ticket?')) return;

    try {
      setUpdating(true);
      await ticketsApi.scheduleIntervention(ticket.id);
      alert('Richiesta di intervento creata! Verrà pianificata nel calendario.');
      await loadTicketData(ticket.id);
    } catch (error) {
      console.error('Failed to schedule intervention:', error);
      alert('Errore nella creazione della richiesta intervento');
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

  const getPriorityColor = (codice?: string) => {
    const colors: Record<string, string> = {
      CRITICA: 'bg-red-100 text-red-800 border-red-200',
      URGENTE: 'bg-orange-100 text-orange-800 border-orange-200',
      ALTA: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      NORMALE: 'bg-blue-100 text-blue-800 border-blue-200',
      BASSA: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return colors[codice || ''] || colors.NORMALE;
  };

  const getStatoColor = (codice?: string) => {
    const colors: Record<string, string> = {
      NUOVO: 'bg-blue-100 text-blue-800 border-blue-200',
      PRESO_CARICO: 'bg-purple-100 text-purple-800 border-purple-200',
      IN_LAVORAZIONE: 'bg-orange-100 text-orange-800 border-orange-200',
      SCHEDULATO: 'bg-cyan-100 text-cyan-800 border-cyan-200',
      CHIUSO: 'bg-green-100 text-green-800 border-green-200',
      ANNULLATO: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[codice || ''] || colors.NUOVO;
  };

  const getInterventoStatoColor = (codice?: string) => {
    const colors: Record<string, string> = {
      PIANIFICATO: 'bg-blue-100 text-blue-800 border-blue-200',
      IN_CORSO: 'bg-orange-100 text-orange-800 border-orange-200',
      COMPLETATO: 'bg-green-100 text-green-800 border-green-200',
      ANNULLATO: 'bg-red-100 text-red-800 border-red-200',
    };
    return colors[codice || ''] || colors.PIANIFICATO;
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

  if (!ticket) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Ticket non trovato</h2>
        <Button onClick={() => navigate('/tickets')}>Torna alla lista</Button>
      </div>
    );
  }

  const contrattoAttivo = getContrattoAttivo();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/tickets')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Indietro
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{ticket.numero}</h1>
            <p className="text-muted-foreground">{ticket.oggetto}</p>
          </div>
        </div>

        <div className="flex gap-2">
          <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${getPriorityColor(ticket.priorita?.codice)}`}>
            {ticket.priorita?.descrizione || 'Normale'}
          </span>
          <span className={`inline-flex items-center rounded-full border px-3 py-1 text-sm font-semibold ${getStatoColor(ticket.stato?.codice)}`}>
            {ticket.stato?.descrizione || 'Nuovo'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Dettagli Ticket */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Dettagli Ticket
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground">Descrizione</label>
                <p className="mt-1">{ticket.descrizione || 'Nessuna descrizione'}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Canale</label>
                  <p className="mt-1">{ticket.canale?.codice || 'N/D'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Creato il</label>
                  <p className="mt-1">{new Date(ticket.created_at).toLocaleString('it-IT')}</p>
                </div>
              </div>

              {ticket.tecnico_assegnato && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Tecnico Assegnato</label>
                  <p className="mt-1 flex items-center gap-2">
                    <User className="h-4 w-4" />
                    {ticket.tecnico_assegnato.nome_completo}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Azioni */}
          <Card>
            <CardHeader>
              <CardTitle>Gestione Ticket</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Cambio Stato */}
              <div>
                <label className="text-sm font-medium">Cambia Stato</label>
                <div className="flex gap-2 mt-2">
                  <Select
                    value={ticket.stato?.id || ''}
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

              {/* Assegnazione Tecnico */}
              <div>
                <label className="text-sm font-medium">Assegna Tecnico</label>
                <div className="flex gap-2 mt-2">
                  <Select
                    value={ticket.tecnico_assegnato?.id || ''}
                    onChange={(e) => handleAssignTecnico(e.target.value ? parseInt(e.target.value) : null)}
                    disabled={updating}
                    className="flex-1"
                  >
                    <option value="">Nessun tecnico assegnato</option>
                    {tecnici.map(tecnico => (
                      <option key={tecnico.id} value={tecnico.id}>
                        {tecnico.cognome} {tecnico.nome}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>

              {/* Azioni Rapide */}
              {ticket.stato?.codice !== 'CHIUSO' && ticket.stato?.codice !== 'ANNULLATO' && (
                <div className="border-t pt-4 space-y-3">
                  <p className="text-sm font-medium text-muted-foreground mb-2">Azioni Rapide</p>

                  {/* Prendi in carico */}
                  {!ticket.tecnico_assegnato && (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleTakeTicket}
                      disabled={updating}
                    >
                      <User className="h-4 w-4 mr-2" />
                      Prendi in Carico
                    </Button>
                  )}

                  {/* Intervento Immediato */}
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={handleCreateIntervention}
                    disabled={updating}
                  >
                    <Wrench className="h-4 w-4 mr-2" />
                    Intervento Immediato
                  </Button>

                  {/* Richiesta Intervento Pianificato */}
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={handleScheduleIntervention}
                    disabled={updating}
                  >
                    <Clock className="h-4 w-4 mr-2" />
                    Pianifica Intervento
                  </Button>

                  {/* Chiudi Senza Intervento */}
                  <Button
                    variant="outline"
                    className="w-full text-green-600 border-green-600 hover:bg-green-50"
                    onClick={() => setShowCloseModal(true)}
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Chiudi Senza Intervento
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Interventi Collegati */}
          {interventi.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wrench className="h-5 w-5" />
                  Interventi Collegati ({interventi.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {interventi.map(intervento => (
                    <div
                      key={intervento.id}
                      className="p-4 border rounded-lg hover:bg-accent/50 transition-colors cursor-pointer"
                      onClick={() => navigate(`/interventions/${intervento.id}`)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-semibold">{intervento.numero}</p>
                            <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${getInterventoStatoColor(intervento.stato?.codice)}`}>
                              {intervento.stato?.descrizione}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            {intervento.oggetto}
                          </p>
                          {intervento.tecnico && (
                            <div className="flex items-center gap-2 text-sm">
                              <User className="h-3 w-3" />
                              <span className="text-muted-foreground">
                                {intervento.tecnico.nome_completo}
                              </span>
                            </div>
                          )}
                          {intervento.data_inizio && (
                            <div className="flex items-center gap-2 text-sm mt-1">
                              <Clock className="h-3 w-3" />
                              <span className="text-muted-foreground">
                                {new Date(intervento.data_inizio).toLocaleString('it-IT')}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
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
                <p className="font-semibold">{ticket.cliente?.ragione_sociale}</p>
                <p className="text-sm text-muted-foreground">{ticket.cliente?.codice_gestionale}</p>
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

          {/* Referenti */}
          {referenti.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Referenti Cliente
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {referenti.map(ref => (
                    <div key={ref.id} className="pb-3 border-b last:border-0 last:pb-0">
                      <p className="font-medium">{ref.nome} {ref.cognome}</p>
                      {ref.ruolo && (
                        <p className="text-sm text-muted-foreground">{ref.ruolo}</p>
                      )}
                      {ref.email && (
                        <p className="text-sm text-muted-foreground">{ref.email}</p>
                      )}
                      {ref.telefono && (
                        <p className="text-sm text-muted-foreground">{ref.telefono}</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

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
                    <p className="font-medium">Ticket creato</p>
                    <p className="text-muted-foreground">
                      {new Date(ticket.created_at).toLocaleString('it-IT')}
                    </p>
                  </div>
                </div>

                {ticket.updated_at && ticket.updated_at !== ticket.created_at && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-2 h-2 rounded-full bg-orange-500 mt-1.5"></div>
                    <div>
                      <p className="font-medium">Ultima modifica</p>
                      <p className="text-muted-foreground">
                        {new Date(ticket.updated_at).toLocaleString('it-IT')}
                      </p>
                    </div>
                  </div>
                )}

                {ticket.data_chiusura && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-2 h-2 rounded-full bg-green-500 mt-1.5"></div>
                    <div>
                      <p className="font-medium">Ticket chiuso</p>
                      <p className="text-muted-foreground">
                        {new Date(ticket.data_chiusura).toLocaleString('it-IT')}
                      </p>
                      {ticket.tipo_chiusura && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Tipo: {ticket.tipo_chiusura}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Modal Chiusura Ticket */}
      {showCloseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowCloseModal(false)} />
          <Card className="relative z-10 w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle>Chiudi Ticket</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Tipo di Chiusura *</label>
                <Select
                  value={tipoChiusura}
                  onChange={(e) => setTipoChiusura(e.target.value)}
                  className="mt-2"
                >
                  <option value="">Seleziona...</option>
                  <option value="RISOLTO">Risolto</option>
                  <option value="NON_RISOLVIBILE">Non Risolvibile</option>
                  <option value="DUPLICATO">Duplicato</option>
                  <option value="NON_PERTINENTE">Non Pertinente</option>
                  <option value="ANNULLATO">Annullato dal Cliente</option>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Note di Chiusura</label>
                <Textarea
                  value={noteChiusura}
                  onChange={(e) => setNoteChiusura(e.target.value)}
                  placeholder="Aggiungi eventuali note sulla chiusura..."
                  rows={3}
                  className="mt-2"
                />
              </div>

              <div className="flex gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCloseModal(false);
                    setTipoChiusura('');
                    setNoteChiusura('');
                  }}
                  className="flex-1"
                >
                  Annulla
                </Button>
                <Button
                  onClick={handleCloseTicket}
                  disabled={!tipoChiusura || updating}
                  className="flex-1"
                >
                  {updating ? 'Chiusura...' : 'Chiudi Ticket'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

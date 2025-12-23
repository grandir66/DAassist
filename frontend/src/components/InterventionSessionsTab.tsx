import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import Select from '@/components/ui/Select';
import { Clock, Plus, Edit2, Trash2, MapPin, Calendar } from 'lucide-react';
import { interventiApi, type SessioneLavoro, type SessioneLavoroCreate } from '@/api/interventions';
import { lookupApi } from '@/api/lookup';

interface Props {
  interventoId: number;
}

export default function InterventionSessionsTab({ interventoId }: Props) {
  const [sessioni, setSessioni] = useState<SessioneLavoro[]>([]);
  const [tipiIntervento, setTipiIntervento] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSession, setEditingSession] = useState<SessioneLavoro | null>(null);

  // Form data
  const [formData, setFormData] = useState<SessioneLavoroCreate>({
    data: new Date().toISOString().split('T')[0],
    ora_inizio: '09:00',
    ora_fine: '',
    tipo_intervento_id: 1,
    km_percorsi: undefined,
    tempo_viaggio_minuti: undefined,
    note: ''
  });

  useEffect(() => {
    loadData();
  }, [interventoId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sessioniData, tipiData] = await Promise.all([
        interventiApi.getSessions(interventoId),
        lookupApi.getInterventionTypes()
      ]);
      setSessioni(sessioniData);
      setTipiIntervento(tipiData);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (session?: SessioneLavoro) => {
    if (session) {
      setEditingSession(session);
      setFormData({
        data: session.data.split('T')[0],
        ora_inizio: session.ora_inizio.substring(0, 5),
        ora_fine: session.ora_fine?.substring(0, 5) || '',
        tipo_intervento_id: session.tipo_intervento.id,
        km_percorsi: session.km_percorsi,
        tempo_viaggio_minuti: session.tempo_viaggio_minuti,
        note: session.note || ''
      });
    } else {
      setEditingSession(null);
      setFormData({
        data: new Date().toISOString().split('T')[0],
        ora_inizio: '09:00',
        ora_fine: '',
        tipo_intervento_id: tipiIntervento[0]?.id || 1,
        km_percorsi: undefined,
        tempo_viaggio_minuti: undefined,
        note: ''
      });
    }
    setShowModal(true);
  };

  const handleSave = async () => {
    try {
      if (editingSession) {
        await interventiApi.updateSession(interventoId, editingSession.id, formData);
      } else {
        await interventiApi.addSession(interventoId, formData);
      }
      await loadData();
      setShowModal(false);
    } catch (error) {
      console.error('Failed to save session:', error);
      alert('Errore nel salvataggio della sessione');
    }
  };

  const handleDelete = async (sessionId: number) => {
    if (!confirm('Vuoi eliminare questa sessione?')) return;

    try {
      await interventiApi.deleteSession(interventoId, sessionId);
      await loadData();
    } catch (error) {
      console.error('Failed to delete session:', error);
      alert('Errore nell\'eliminazione della sessione');
    }
  };

  const formatDuration = (minuti?: number) => {
    if (!minuti) return '-';
    const ore = Math.floor(minuti / 60);
    const min = minuti % 60;
    return `${ore}h ${min}m`;
  };

  const calculateTotal = () => {
    const totalMinuti = sessioni.reduce((acc, s) => acc + (s.durata_minuti || 0), 0);
    return formatDuration(totalMinuti);
  };

  if (loading) {
    return <div className="text-center py-8">Caricamento sessioni...</div>;
  }

  return (
    <div className="space-y-4">
      {/* Header con totale ore */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Sessioni di Lavoro</h3>
          <p className="text-sm text-muted-foreground">
            Totale ore lavorate: <span className="font-semibold text-foreground">{calculateTotal()}</span>
          </p>
        </div>
        <Button onClick={() => handleOpenModal()}>
          <Plus className="h-4 w-4 mr-2" />
          Registra Tempo
        </Button>
      </div>

      {/* Lista sessioni */}
      {sessioni.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Nessuna sessione registrata. Clicca su "Registra Tempo" per iniziare.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {sessioni.map(sessione => (
            <Card key={sessione.id} className="hover:shadow-md transition-shadow">
              <CardContent className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">
                          {new Date(sessione.data).toLocaleDateString('it-IT')}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span>
                          {sessione.ora_inizio.substring(0, 5)}
                          {sessione.ora_fine && ` - ${sessione.ora_fine.substring(0, 5)}`}
                        </span>
                      </div>
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {formatDuration(sessione.durata_minuti)}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Tecnico: {sessione.tecnico.nome_completo}</span>
                      <span>Tipo: {sessione.tipo_intervento.descrizione}</span>
                      {sessione.km_percorsi && (
                        <div className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {sessione.km_percorsi} km
                          {sessione.tempo_viaggio_minuti && ` (${sessione.tempo_viaggio_minuti} min)`}
                        </div>
                      )}
                    </div>

                    {sessione.note && (
                      <p className="mt-2 text-sm text-muted-foreground italic">
                        {sessione.note}
                      </p>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpenModal(sessione)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(sessione.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal Crea/Modifica */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <Card className="w-full max-w-lg mx-4">
            <CardHeader>
              <CardTitle>
                {editingSession ? 'Modifica Sessione' : 'Nuova Sessione'}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Data</label>
                  <Input
                    type="date"
                    value={formData.data}
                    onChange={(e) => setFormData({ ...formData, data: e.target.value })}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Tipo Intervento</label>
                  <Select
                    value={formData.tipo_intervento_id}
                    onChange={(e) => setFormData({ ...formData, tipo_intervento_id: parseInt(e.target.value) })}
                    className="mt-1"
                  >
                    {tipiIntervento.map(tipo => (
                      <option key={tipo.id} value={tipo.id}>{tipo.descrizione}</option>
                    ))}
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Ora Inizio *</label>
                  <Input
                    type="time"
                    value={formData.ora_inizio}
                    onChange={(e) => setFormData({ ...formData, ora_inizio: e.target.value })}
                    className="mt-1"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Ora Fine</label>
                  <Input
                    type="time"
                    value={formData.ora_fine}
                    onChange={(e) => setFormData({ ...formData, ora_fine: e.target.value })}
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Km Percorsi</label>
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.km_percorsi || ''}
                    onChange={(e) => setFormData({ ...formData, km_percorsi: parseFloat(e.target.value) || undefined })}
                    className="mt-1"
                    placeholder="0.0"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Tempo Viaggio (min)</label>
                  <Input
                    type="number"
                    value={formData.tempo_viaggio_minuti || ''}
                    onChange={(e) => setFormData({ ...formData, tempo_viaggio_minuti: parseInt(e.target.value) || undefined })}
                    className="mt-1"
                    placeholder="0"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Note</label>
                <Textarea
                  value={formData.note}
                  onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                  rows={3}
                  className="mt-1"
                  placeholder="Eventuali note sulla sessione..."
                />
              </div>

              <div className="flex gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setShowModal(false)}
                  className="flex-1"
                >
                  Annulla
                </Button>
                <Button
                  onClick={handleSave}
                  className="flex-1"
                >
                  {editingSession ? 'Aggiorna' : 'Salva'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

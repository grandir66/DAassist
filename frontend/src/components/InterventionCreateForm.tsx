import { useState, useEffect, FormEvent } from 'react';
import Dialog from './ui/Dialog';
import Button from './ui/Button';
import Input from './ui/Input';
import Select from './ui/Select';
import Textarea from './ui/Textarea';
import { interventiApi, type InterventoCreate } from '@/api/interventions';
import { clientiApi, type Cliente } from '@/api/clients';
import { ticketsApi, type Ticket } from '@/api/tickets';
import { lookupApi, type LookupItem, type InterventionType, type State } from '@/api/lookup';
import { useAuthStore } from '@/stores/authStore';

interface InterventionCreateFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function InterventionCreateForm({ open, onClose, onSuccess }: InterventionCreateFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const currentUser = useAuthStore((state) => state.user);

  // Form data
  const [formData, setFormData] = useState<InterventoCreate>({
    cliente_id: 0,
    ticket_id: undefined,
    tipo_intervento_id: 0,
    stato_id: 0,
    origine_id: 0,
    tecnico_id: currentUser?.id || 0,
    oggetto: '',
    descrizione_lavoro: '',
    note_interne: '',
  });

  // Lookup data
  const [clienti, setClienti] = useState<Cliente[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [tipiIntervento, setTipiIntervento] = useState<InterventionType[]>([]);
  const [statiIntervento, setStatiIntervento] = useState<State[]>([]);
  const [originiIntervento, setOriginiIntervento] = useState<LookupItem[]>([]);
  const [loadingLookups, setLoadingLookups] = useState(true);

  // Load lookup data
  useEffect(() => {
    if (open) {
      loadLookupData();
    }
  }, [open]);

  // Load tickets when cliente changes
  useEffect(() => {
    if (formData.cliente_id > 0) {
      loadClienteTickets(formData.cliente_id);
    } else {
      setTickets([]);
      setFormData(prev => ({ ...prev, ticket_id: undefined }));
    }
  }, [formData.cliente_id]);

  const loadLookupData = async () => {
    try {
      setLoadingLookups(true);
      const [clientiData, tipiData, statiData, originiData] = await Promise.all([
        clientiApi.getAll({ limit: 100 }),
        lookupApi.getInterventionTypes(),
        lookupApi.getInterventionStates(),
        lookupApi.getInterventionOrigins(),
      ]);

      setClienti(clientiData.clienti);
      setTipiIntervento(tipiData);
      setStatiIntervento(statiData);
      setOriginiIntervento(originiData);

      // Set defaults
      if (tipiData.length > 0 && formData.tipo_intervento_id === 0) {
        setFormData(prev => ({ ...prev, tipo_intervento_id: tipiData[0].id }));
      }
      if (statiData.length > 0 && formData.stato_id === 0) {
        const pianificato = statiData.find(s => s.codice === 'PIANIFICATO');
        setFormData(prev => ({ ...prev, stato_id: pianificato?.id || statiData[0].id }));
      }
      if (originiData.length > 0 && formData.origine_id === 0) {
        const spontaneo = originiData.find(o => o.codice === 'SPONTANEO');
        setFormData(prev => ({ ...prev, origine_id: spontaneo?.id || originiData[0].id }));
      }
      if (currentUser?.id) {
        setFormData(prev => ({ ...prev, tecnico_id: currentUser.id }));
      }
    } catch (err) {
      console.error('Failed to load lookup data:', err);
      setError('Errore nel caricamento dei dati');
    } finally {
      setLoadingLookups(false);
    }
  };

  const loadClienteTickets = async (clienteId: number) => {
    try {
      const response = await ticketsApi.getAll({
        page: 1,
        limit: 50,
        cliente_id: clienteId,
      });
      // Filter only open tickets
      const openTickets = response.tickets.filter(t => t.stato?.codice !== 'CHIUSO' && t.stato?.codice !== 'ANNULLATO');
      setTickets(openTickets);
    } catch (err) {
      console.error('Failed to load cliente tickets:', err);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.cliente_id || !formData.tipo_intervento_id || !formData.stato_id || !formData.origine_id || !formData.tecnico_id || !formData.oggetto) {
      setError('Compila tutti i campi obbligatori');
      return;
    }

    try {
      setLoading(true);
      await interventiApi.create(formData);
      onSuccess();
      handleClose();
    } catch (err: any) {
      console.error('Failed to create intervention:', err);
      setError(err.response?.data?.detail || 'Errore nella creazione dell\'intervento');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      cliente_id: 0,
      ticket_id: undefined,
      tipo_intervento_id: tipiIntervento[0]?.id || 0,
      stato_id: statiIntervento.find(s => s.codice === 'PIANIFICATO')?.id || statiIntervento[0]?.id || 0,
      origine_id: originiIntervento.find(o => o.codice === 'SPONTANEO')?.id || originiIntervento[0]?.id || 0,
      tecnico_id: currentUser?.id || 0,
      oggetto: '',
      descrizione_lavoro: '',
      note_interne: '',
    });
    setError('');
    setTickets([]);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} title="Nuovo Intervento" maxWidth="lg">
      {loadingLookups ? (
        <div className="text-center py-8 text-muted-foreground">Caricamento...</div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            {/* Cliente */}
            <div className="space-y-2">
              <label htmlFor="cliente_id" className="text-sm font-medium">
                Cliente <span className="text-destructive">*</span>
              </label>
              <Select
                id="cliente_id"
                value={formData.cliente_id}
                onChange={(e) => setFormData({ ...formData, cliente_id: parseInt(e.target.value) })}
                required
              >
                <option value="">Seleziona un cliente</option>
                {clienti.map((cliente) => (
                  <option key={cliente.id} value={cliente.id}>
                    {cliente.ragione_sociale} ({cliente.codice_gestionale})
                  </option>
                ))}
              </Select>
            </div>

            {/* Ticket (opzionale, solo se cliente selezionato) */}
            <div className="space-y-2">
              <label htmlFor="ticket_id" className="text-sm font-medium">
                Ticket Collegato
              </label>
              <Select
                id="ticket_id"
                value={formData.ticket_id || ''}
                onChange={(e) => setFormData({ ...formData, ticket_id: e.target.value ? parseInt(e.target.value) : undefined })}
                disabled={!formData.cliente_id}
              >
                <option value="">Nessun ticket</option>
                {tickets.map((ticket) => (
                  <option key={ticket.id} value={ticket.id}>
                    {ticket.numero} - {ticket.oggetto}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Oggetto */}
          <div className="space-y-2">
            <label htmlFor="oggetto" className="text-sm font-medium">
              Oggetto <span className="text-destructive">*</span>
            </label>
            <Input
              id="oggetto"
              value={formData.oggetto}
              onChange={(e) => setFormData({ ...formData, oggetto: e.target.value })}
              placeholder="Breve descrizione dell'intervento"
              required
              maxLength={200}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            {/* Tipo Intervento */}
            <div className="space-y-2">
              <label htmlFor="tipo_intervento_id" className="text-sm font-medium">
                Tipo <span className="text-destructive">*</span>
              </label>
              <Select
                id="tipo_intervento_id"
                value={formData.tipo_intervento_id}
                onChange={(e) => setFormData({ ...formData, tipo_intervento_id: parseInt(e.target.value) })}
                required
              >
                {tipiIntervento.map((tipo) => (
                  <option key={tipo.id} value={tipo.id}>
                    {tipo.descrizione}
                  </option>
                ))}
              </Select>
            </div>

            {/* Stato */}
            <div className="space-y-2">
              <label htmlFor="stato_id" className="text-sm font-medium">
                Stato <span className="text-destructive">*</span>
              </label>
              <Select
                id="stato_id"
                value={formData.stato_id}
                onChange={(e) => setFormData({ ...formData, stato_id: parseInt(e.target.value) })}
                required
              >
                {statiIntervento.map((stato) => (
                  <option key={stato.id} value={stato.id}>
                    {stato.descrizione}
                  </option>
                ))}
              </Select>
            </div>

            {/* Origine */}
            <div className="space-y-2">
              <label htmlFor="origine_id" className="text-sm font-medium">
                Origine <span className="text-destructive">*</span>
              </label>
              <Select
                id="origine_id"
                value={formData.origine_id}
                onChange={(e) => setFormData({ ...formData, origine_id: parseInt(e.target.value) })}
                required
              >
                {originiIntervento.map((origine) => (
                  <option key={origine.id} value={origine.id}>
                    {origine.descrizione}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Descrizione Lavoro */}
          <div className="space-y-2">
            <label htmlFor="descrizione_lavoro" className="text-sm font-medium">
              Descrizione Lavoro
            </label>
            <Textarea
              id="descrizione_lavoro"
              value={formData.descrizione_lavoro}
              onChange={(e) => setFormData({ ...formData, descrizione_lavoro: e.target.value })}
              placeholder="Descrizione dettagliata del lavoro da svolgere..."
              rows={3}
            />
          </div>

          {/* Note Interne */}
          <div className="space-y-2">
            <label htmlFor="note_interne" className="text-sm font-medium">
              Note Interne
            </label>
            <Textarea
              id="note_interne"
              value={formData.note_interne}
              onChange={(e) => setFormData({ ...formData, note_interne: e.target.value })}
              placeholder="Note interne non visibili al cliente..."
              rows={2}
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={handleClose}>
              Annulla
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creazione...' : 'Crea Intervento'}
            </Button>
          </div>
        </form>
      )}
    </Dialog>
  );
}

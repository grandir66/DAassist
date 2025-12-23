import { useState, useEffect, FormEvent } from 'react';
import Dialog from './ui/Dialog';
import Button from './ui/Button';
import Input from './ui/Input';
import Select from './ui/Select';
import Textarea from './ui/Textarea';
import { ticketsApi, type TicketCreate } from '@/api/tickets';
import { clientiApi, type Cliente, type Contratto, type Referente } from '@/api/clients';
import { lookupApi, type LookupItem, type Priority, type Department } from '@/api/lookup';

interface TicketCreateFormProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function TicketCreateForm({ open, onClose, onSuccess }: TicketCreateFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Form data
  const [formData, setFormData] = useState<TicketCreate>({
    oggetto: '',
    descrizione: '',
    cliente_id: 0,
    referente_id: undefined,
    referente_nome: '',
    canale_id: 0,
    priorita_id: 0,
    contratto_id: undefined,
    asset_id: undefined,
  });

  // Lookup data
  const [clienti, setClienti] = useState<Cliente[]>([]);
  const [referenti, setReferenti] = useState<Referente[]>([]);
  const [contratti, setContratti] = useState<Contratto[]>([]);
  const [canali, setCanali] = useState<LookupItem[]>([]);
  const [priorita, setPriorita] = useState<Priority[]>([]);
  const [reparti, setReparti] = useState<Department[]>([]);
  const [loadingLookups, setLoadingLookups] = useState(true);

  // Load lookup data
  useEffect(() => {
    if (open) {
      loadLookupData();
    }
  }, [open]);

  // Load referenti and contratti when cliente changes
  useEffect(() => {
    if (formData.cliente_id > 0) {
      loadClienteData(formData.cliente_id);
    } else {
      setReferenti([]);
      setContratti([]);
      setFormData(prev => ({ ...prev, referente_id: undefined, contratto_id: undefined }));
    }
  }, [formData.cliente_id]);

  const loadLookupData = async () => {
    try {
      setLoadingLookups(true);
      const [clientiData, canaliData, prioritaData, repartiData] = await Promise.all([
        clientiApi.getAll({ limit: 100 }),
        lookupApi.getChannels(),
        lookupApi.getPriorities(),
        lookupApi.getDepartments(),
      ]);

      setClienti(clientiData.clienti);
      setCanali(canaliData);
      setPriorita(prioritaData);
      setReparti(repartiData);

      // Set defaults
      if (canaliData.length > 0 && formData.canale_id === 0) {
        setFormData(prev => ({ ...prev, canale_id: canaliData[0].id }));
      }
      if (prioritaData.length > 0 && formData.priorita_id === 0) {
        const normalePrio = prioritaData.find(p => p.codice === 'NORMALE');
        setFormData(prev => ({ ...prev, priorita_id: normalePrio?.id || prioritaData[0].id }));
      }
    } catch (err) {
      console.error('Failed to load lookup data:', err);
      setError('Errore nel caricamento dei dati');
    } finally {
      setLoadingLookups(false);
    }
  };

  const loadClienteData = async (clienteId: number) => {
    try {
      const [referentiData, contrattiData] = await Promise.all([
        clientiApi.getReferenti(clienteId),
        clientiApi.getContratti(clienteId),
      ]);

      setReferenti(referentiData);

      // Filter only active contracts
      const contrattiAttivi = contrattiData.filter(c => {
        if (!c.data_fine) return false;
        const dataFine = new Date(c.data_fine);
        return dataFine >= new Date() && c.attivo;
      });
      setContratti(contrattiAttivi);
    } catch (err) {
      console.error('Failed to load cliente data:', err);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.oggetto || !formData.cliente_id || !formData.canale_id || !formData.priorita_id) {
      setError('Compila tutti i campi obbligatori');
      return;
    }

    try {
      setLoading(true);
      await ticketsApi.create(formData);
      onSuccess();
      handleClose();
    } catch (err: any) {
      console.error('Failed to create ticket:', err);
      setError(err.response?.data?.detail || 'Errore nella creazione del ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      oggetto: '',
      descrizione: '',
      cliente_id: 0,
      referente_id: undefined,
      referente_nome: '',
      canale_id: canali[0]?.id || 0,
      priorita_id: priorita.find(p => p.codice === 'NORMALE')?.id || priorita[0]?.id || 0,
      contratto_id: undefined,
      asset_id: undefined,
    });
    setError('');
    setReferenti([]);
    setContratti([]);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} title="Nuovo Ticket" maxWidth="xl">
      {loadingLookups ? (
        <div className="text-center py-8 text-muted-foreground">Caricamento...</div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          {/* Cliente e Contratto */}
          <div className="grid grid-cols-2 gap-4">
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

            <div className="space-y-2">
              <label htmlFor="contratto_id" className="text-sm font-medium">
                Contratto
              </label>
              <Select
                id="contratto_id"
                value={formData.contratto_id || ''}
                onChange={(e) => setFormData({ ...formData, contratto_id: e.target.value ? parseInt(e.target.value) : undefined })}
                disabled={!formData.cliente_id || contratti.length === 0}
              >
                <option value="">Nessun contratto</option>
                {contratti.map((contratto) => (
                  <option key={contratto.id} value={contratto.id}>
                    {contratto.tipologia_descrizione} - Scad: {contratto.data_fine ? new Date(contratto.data_fine).toLocaleDateString('it-IT') : 'N/D'}
                  </option>
                ))}
              </Select>
              {formData.cliente_id && contratti.length === 0 && (
                <p className="text-xs text-amber-600">⚠️ Nessun contratto attivo per questo cliente</p>
              )}
            </div>
          </div>

          {/* Referente */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="referente_id" className="text-sm font-medium">
                Referente
              </label>
              <Select
                id="referente_id"
                value={formData.referente_id || ''}
                onChange={(e) => {
                  const refId = e.target.value ? parseInt(e.target.value) : undefined;
                  const ref = referenti.find(r => r.id === refId);
                  setFormData({
                    ...formData,
                    referente_id: refId,
                    referente_nome: ref ? `${ref.nome} ${ref.cognome}` : ''
                  });
                }}
                disabled={!formData.cliente_id}
              >
                <option value="">Seleziona referente</option>
                {referenti.map((ref) => (
                  <option key={ref.id} value={ref.id}>
                    {ref.nome} {ref.cognome} {ref.ruolo ? `- ${ref.ruolo}` : ''}
                  </option>
                ))}
              </Select>
            </div>

            <div className="space-y-2">
              <label htmlFor="referente_nome" className="text-sm font-medium">
                Nome Referente (alternativo)
              </label>
              <Input
                id="referente_nome"
                value={formData.referente_nome}
                onChange={(e) => setFormData({ ...formData, referente_nome: e.target.value })}
                placeholder="Nome del referente"
                disabled={!!formData.referente_id}
              />
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
              placeholder="Breve descrizione del problema"
              required
              maxLength={200}
            />
          </div>

          {/* Descrizione */}
          <div className="space-y-2">
            <label htmlFor="descrizione" className="text-sm font-medium">
              Descrizione Dettagliata
            </label>
            <Textarea
              id="descrizione"
              value={formData.descrizione}
              onChange={(e) => setFormData({ ...formData, descrizione: e.target.value })}
              placeholder="Descrizione dettagliata del problema, passi per riprodurlo, screenshot, etc..."
              rows={5}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            {/* Canale */}
            <div className="space-y-2">
              <label htmlFor="canale_id" className="text-sm font-medium">
                Canale di Richiesta <span className="text-destructive">*</span>
              </label>
              <Select
                id="canale_id"
                value={formData.canale_id}
                onChange={(e) => setFormData({ ...formData, canale_id: parseInt(e.target.value) })}
                required
              >
                {canali.map((canale) => (
                  <option key={canale.id} value={canale.id}>
                    {canale.descrizione}
                  </option>
                ))}
              </Select>
            </div>

            {/* Priorità */}
            <div className="space-y-2">
              <label htmlFor="priorita_id" className="text-sm font-medium">
                Priorità <span className="text-destructive">*</span>
              </label>
              <Select
                id="priorita_id"
                value={formData.priorita_id}
                onChange={(e) => setFormData({ ...formData, priorita_id: parseInt(e.target.value) })}
                required
              >
                {priorita.map((prio) => (
                  <option key={prio.id} value={prio.id}>
                    {prio.descrizione}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Info Aggiuntive */}
          {formData.cliente_id && referenti.length > 0 && formData.referente_id && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
              <p className="text-sm font-medium text-blue-900">Contatti Referente:</p>
              {referenti.find(r => r.id === formData.referente_id) && (
                <div className="text-sm text-blue-800 mt-1">
                  {referenti.find(r => r.id === formData.referente_id)?.email && (
                    <p>📧 {referenti.find(r => r.id === formData.referente_id)?.email}</p>
                  )}
                  {referenti.find(r => r.id === formData.referente_id)?.telefono && (
                    <p>📞 {referenti.find(r => r.id === formData.referente_id)?.telefono}</p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={handleClose}>
              Annulla
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creazione...' : 'Crea Ticket'}
            </Button>
          </div>
        </form>
      )}
    </Dialog>
  );
}

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Textarea from '@/components/ui/Textarea';
import { Edit2, Trash2 } from 'lucide-react';
import { interventiApi, type RigaAttivita, type RigaAttivitaUpdate } from '@/api/interventions';

interface Props {
  interventoId: number;
}

export default function InterventionRowsTab({ interventoId }: Props) {
  const [righe, setRighe] = useState<RigaAttivita[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingRow, setEditingRow] = useState<number | null>(null);
  const [formData, setFormData] = useState<RigaAttivitaUpdate>({});

  useEffect(() => {
    loadRighe();
  }, [interventoId]);

  const loadRighe = async () => {
    try {
      setLoading(true);
      const data = await interventiApi.getRows(interventoId);
      setRighe(data);
    } catch (error) {
      console.error('Failed to load rows:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (riga: RigaAttivita) => {
    setEditingRow(riga.id);
    setFormData({
      descrizione: riga.descrizione,
      quantita: riga.quantita,
      prezzo_unitario: riga.prezzo_unitario,
      sconto_percentuale: riga.sconto_percentuale,
      fatturabile: riga.fatturabile,
      in_garanzia: riga.in_garanzia,
      incluso_contratto: riga.incluso_contratto
    });
  };

  const handleSave = async (rowId: number) => {
    try {
      await interventiApi.updateRow(interventoId, rowId, formData);
      await loadRighe();
      setEditingRow(null);
    } catch (error) {
      console.error('Failed to update row:', error);
      alert('Errore nell\'aggiornamento della riga');
    }
  };

  const handleDelete = async (rowId: number) => {
    if (!confirm('Vuoi eliminare questa riga?')) return;

    try {
      await interventiApi.deleteRow(interventoId, rowId);
      await loadRighe();
    } catch (error) {
      console.error('Failed to delete row:', error);
      alert('Errore nell\'eliminazione della riga');
    }
  };

  const calculateTotal = () => {
    return righe.reduce((acc, r) => acc + r.importo, 0).toFixed(2);
  };

  if (loading) {
    return <div className="text-center py-8">Caricamento attività...</div>;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Righe Attività</h3>
          <p className="text-sm text-muted-foreground">
            Totale: <span className="font-semibold text-foreground">€{calculateTotal()}</span>
          </p>
        </div>
      </div>

      {/* Tabella righe */}
      {righe.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Nessuna attività registrata.
          </CardContent>
        </Card>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium">#</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Descrizione</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Quantità</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Prezzo</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Sconto</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Importo</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Flag</th>
                <th className="px-4 py-3 text-center text-sm font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {righe.map((riga) => (
                <tr key={riga.id} className="border-t hover:bg-muted/50">
                  {editingRow === riga.id ? (
                    <>
                      <td className="px-4 py-3">{riga.numero_riga}</td>
                      <td className="px-4 py-3">
                        <Textarea
                          value={formData.descrizione}
                          onChange={(e) => setFormData({ ...formData, descrizione: e.target.value })}
                          rows={2}
                          className="w-full"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <Input
                          type="number"
                          step="0.5"
                          value={formData.quantita}
                          onChange={(e) => setFormData({ ...formData, quantita: parseFloat(e.target.value) })}
                          className="w-20 text-right"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <Input
                          type="number"
                          step="0.01"
                          value={formData.prezzo_unitario}
                          onChange={(e) => setFormData({ ...formData, prezzo_unitario: parseFloat(e.target.value) })}
                          className="w-24 text-right"
                        />
                      </td>
                      <td className="px-4 py-3">
                        <Input
                          type="number"
                          step="1"
                          value={formData.sconto_percentuale}
                          onChange={(e) => setFormData({ ...formData, sconto_percentuale: parseFloat(e.target.value) })}
                          className="w-20 text-right"
                        />
                      </td>
                      <td className="px-4 py-3 text-right font-semibold">
                        €{((formData.quantita || 0) * (formData.prezzo_unitario || 0) * (1 - (formData.sconto_percentuale || 0) / 100)).toFixed(2)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col gap-1 text-xs">
                          <label className="flex items-center gap-1">
                            <input
                              type="checkbox"
                              checked={formData.fatturabile}
                              onChange={(e) => setFormData({ ...formData, fatturabile: e.target.checked })}
                            />
                            Fatt.
                          </label>
                          <label className="flex items-center gap-1">
                            <input
                              type="checkbox"
                              checked={formData.in_garanzia}
                              onChange={(e) => setFormData({ ...formData, in_garanzia: e.target.checked })}
                            />
                            Gar.
                          </label>
                          <label className="flex items-center gap-1">
                            <input
                              type="checkbox"
                              checked={formData.incluso_contratto}
                              onChange={(e) => setFormData({ ...formData, incluso_contratto: e.target.checked })}
                            />
                            Incl.
                          </label>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2 justify-center">
                          <Button
                            size="sm"
                            onClick={() => handleSave(riga.id)}
                          >
                            Salva
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setEditingRow(null)}
                          >
                            Annulla
                          </Button>
                        </div>
                      </td>
                    </>
                  ) : (
                    <>
                      <td className="px-4 py-3 text-sm">{riga.numero_riga}</td>
                      <td className="px-4 py-3 text-sm">{riga.descrizione}</td>
                      <td className="px-4 py-3 text-right text-sm">
                        {riga.quantita} {riga.unita_misura}
                      </td>
                      <td className="px-4 py-3 text-right text-sm">€{riga.prezzo_unitario.toFixed(2)}</td>
                      <td className="px-4 py-3 text-right text-sm">{riga.sconto_percentuale}%</td>
                      <td className="px-4 py-3 text-right text-sm font-semibold">€{riga.importo.toFixed(2)}</td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex gap-1 justify-center text-xs">
                          {riga.fatturabile && <span className="px-1 py-0.5 rounded bg-green-100 text-green-800">F</span>}
                          {riga.in_garanzia && <span className="px-1 py-0.5 rounded bg-blue-100 text-blue-800">G</span>}
                          {riga.incluso_contratto && <span className="px-1 py-0.5 rounded bg-purple-100 text-purple-800">C</span>}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2 justify-center">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(riga)}
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDelete(riga.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { techniciansApi, Technician, TechnicianCreate, TechnicianUpdate } from '../api/technicians';
import { lookupApi, Reparto, Ruolo } from '../api/lookup';

export default function Technicians() {
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filterReparto, setFilterReparto] = useState<number | undefined>();
  const [filterRuolo, setFilterRuolo] = useState<number | undefined>();
  const [filterAttivo, setFilterAttivo] = useState<boolean | undefined>(true);

  const [reparti, setReparti] = useState<Reparto[]>([]);
  const [ruoli, setRuoli] = useState<Ruolo[]>([]);

  const [showModal, setShowModal] = useState(false);
  const [editingTechnician, setEditingTechnician] = useState<Technician | null>(null);
  const [formData, setFormData] = useState<TechnicianCreate | TechnicianUpdate>({
    username: '',
    email: '',
    password: '',
    nome: '',
    cognome: '',
    telefono: '',
    cellulare: '',
    interno_telefonico: '',
    telegram_id: '',
    reparto_id: undefined,
    ruolo_id: 0,
    codice_tecnico: '',
    ldap_dn: '',
    ldap_enabled: false,
    username_ad: '',
    colore_calendario: '#3B82F6',
    notifiche_email: true,
    notifiche_push: true,
    note: '',
  });

  useEffect(() => {
    loadTechnicians();
    loadLookups();
  }, [page, search, filterReparto, filterRuolo, filterAttivo]);

  const loadTechnicians = async () => {
    try {
      setLoading(true);
      const response = await techniciansApi.getAll({
        page,
        limit: 50,
        search: search || undefined,
        reparto_id: filterReparto,
        ruolo_id: filterRuolo,
        attivo: filterAttivo,
      });
      setTechnicians(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load technicians:', error);
      alert('Errore nel caricamento dei tecnici');
    } finally {
      setLoading(false);
    }
  };

  const loadLookups = async () => {
    try {
      const [repartiData, ruoliData] = await Promise.all([
        lookupApi.getReparti(),
        lookupApi.getRuoli(),
      ]);
      setReparti(repartiData);
      setRuoli(ruoliData);
    } catch (error) {
      console.error('Failed to load lookups:', error);
    }
  };

  const handleCreate = () => {
    setEditingTechnician(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      nome: '',
      cognome: '',
      telefono: '',
      cellulare: '',
      interno_telefonico: '',
      telegram_id: '',
      reparto_id: undefined,
      ruolo_id: ruoli.find(r => r.codice === 'TECNICO')?.id || 0,
      codice_tecnico: '',
      ldap_dn: '',
      ldap_enabled: false,
      username_ad: '',
      colore_calendario: '#3B82F6',
      notifiche_email: true,
      notifiche_push: true,
      note: '',
    });
    setShowModal(true);
  };

  const handleEdit = (technician: Technician) => {
    setEditingTechnician(technician);
    setFormData({
      email: technician.email,
      nome: technician.nome,
      cognome: technician.cognome,
      telefono: technician.telefono,
      cellulare: technician.cellulare,
      interno_telefonico: technician.interno_telefonico,
      telegram_id: technician.telegram_id,
      reparto_id: technician.reparto_id,
      ruolo_id: technician.ruolo_id,
      codice_tecnico: technician.codice_tecnico,
      ldap_dn: technician.ldap_dn,
      ldap_enabled: technician.ldap_enabled,
      username_ad: technician.username_ad,
      colore_calendario: technician.colore_calendario,
      notifiche_email: technician.notifiche_email,
      notifiche_push: technician.notifiche_push,
      note: technician.note,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingTechnician) {
        await techniciansApi.update(editingTechnician.id, formData as TechnicianUpdate);
      } else {
        await techniciansApi.create(formData as TechnicianCreate);
      }
      setShowModal(false);
      loadTechnicians();
    } catch (error: any) {
      console.error('Failed to save technician:', error);
      alert(error.response?.data?.detail || 'Errore nel salvataggio del tecnico');
    }
  };

  // const handleDelete = async (id: number) => {
  //   if (!confirm('Confermi la disattivazione del tecnico?')) return;
  //
  //   try {
  //     await techniciansApi.delete(id);
  //     loadTechnicians();
  //   } catch (error) {
  //     console.error('Failed to delete technician:', error);
  //     alert('Errore nella disattivazione del tecnico');
  //   }
  // };

  const handleToggleActive = async (technician: Technician) => {
    try {
      await techniciansApi.update(technician.id, { attivo: !technician.attivo });
      loadTechnicians();
    } catch (error) {
      console.error('Failed to toggle technician status:', error);
      alert('Errore nel cambio stato del tecnico');
    }
  };

  if (loading && technicians.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Caricamento...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Gestione Tecnici</h1>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          + Nuovo Tecnico
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cerca
            </label>
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Nome, cognome, email..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reparto
            </label>
            <select
              value={filterReparto || ''}
              onChange={(e) => {
                setFilterReparto(e.target.value ? Number(e.target.value) : undefined);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Tutti</option>
              {reparti.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.descrizione}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ruolo
            </label>
            <select
              value={filterRuolo || ''}
              onChange={(e) => {
                setFilterRuolo(e.target.value ? Number(e.target.value) : undefined);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Tutti</option>
              {ruoli.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.descrizione}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stato
            </label>
            <select
              value={filterAttivo === undefined ? '' : filterAttivo ? 'true' : 'false'}
              onChange={(e) => {
                setFilterAttivo(
                  e.target.value === '' ? undefined : e.target.value === 'true'
                );
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Tutti</option>
              <option value="true">Attivi</option>
              <option value="false">Disattivati</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Nome Completo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Username
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Ruolo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Reparto
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                LDAP
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Stato
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                Azioni
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {technicians.map((tech) => (
              <tr key={tech.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: tech.colore_calendario }}
                    />
                    <span className="text-sm font-medium text-gray-900">
                      {tech.nome} {tech.cognome}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {tech.username}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {tech.email}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {tech.ruolo?.descrizione}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {tech.reparto?.descrizione || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  {tech.ldap_enabled ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800" title={tech.ldap_dn || 'LDAP Enabled'}>
                      LDAP
                    </span>
                  ) : (
                    <span className="text-gray-400 text-xs">-</span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleToggleActive(tech)}
                    className={`px-2 py-1 text-xs rounded-full ${
                      tech.attivo
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {tech.attivo ? 'Attivo' : 'Disattivato'}
                  </button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                  <button
                    onClick={() => handleEdit(tech)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    Modifica
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-700">
          Totale: {total} tecnici
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 border rounded-md disabled:opacity-50"
          >
            Precedente
          </button>
          <span className="px-3 py-1">Pagina {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={technicians.length < 50}
            className="px-3 py-1 border rounded-md disabled:opacity-50"
          >
            Successiva
          </button>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              {editingTechnician ? 'Modifica Tecnico' : 'Nuovo Tecnico'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {!editingTechnician && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Username *
                    </label>
                    <input
                      type="text"
                      required
                      value={(formData as TechnicianCreate).username || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, username: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                )}

                <div className={!editingTechnician ? '' : 'col-span-2'}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              {!editingTechnician && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password *
                  </label>
                  <input
                    type="password"
                    required={!editingTechnician}
                    value={(formData as TechnicianCreate).password || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              )}

              {editingTechnician && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nuova Password (lascia vuoto per non modificare)
                  </label>
                  <input
                    type="password"
                    value={(formData as TechnicianUpdate).password || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nome *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.nome || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, nome: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Cognome *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.cognome || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, cognome: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              {/* Contatti */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Contatti</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Telefono
                    </label>
                    <input
                      type="tel"
                      value={formData.telefono || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, telefono: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Cellulare
                    </label>
                    <input
                      type="tel"
                      value={formData.cellulare || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, cellulare: e.target.value })
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Interno Telefonico
                    </label>
                    <input
                      type="text"
                      value={formData.interno_telefonico || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, interno_telefonico: e.target.value })
                      }
                      placeholder="es: 101"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Telegram ID
                    </label>
                    <input
                      type="text"
                      value={formData.telegram_id || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, telegram_id: e.target.value })
                      }
                      placeholder="es: @username"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
              </div>

              {/* Organizzazione */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Organizzazione</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Codice Tecnico
                    </label>
                    <input
                      type="text"
                      value={formData.codice_tecnico || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, codice_tecnico: e.target.value })
                      }
                      placeholder="Codice per gestionale"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Colore Calendario
                    </label>
                    <input
                      type="color"
                      value={formData.colore_calendario || '#3B82F6'}
                      onChange={(e) =>
                        setFormData({ ...formData, colore_calendario: e.target.value })
                      }
                      className="w-full h-10 px-1 py-1 border border-gray-300 rounded-md"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Ruolo *
                  </label>
                  <select
                    required
                    value={formData.ruolo_id || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, ruolo_id: Number(e.target.value) })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Seleziona...</option>
                    {ruoli.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.descrizione}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Reparto
                  </label>
                  <select
                    value={formData.reparto_id || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        reparto_id: e.target.value ? Number(e.target.value) : undefined,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="">Nessuno</option>
                    {reparti.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.descrizione}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* LDAP Configuration */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Configurazione LDAP / Active Directory (opzionale)
                </h3>

                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Username Active Directory
                      </label>
                      <input
                        type="text"
                        value={formData.username_ad || ''}
                        onChange={(e) =>
                          setFormData({ ...formData, username_ad: e.target.value })
                        }
                        placeholder="es: user.name"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                      />
                    </div>

                    <div className="flex items-end">
                      <label className="flex items-center pb-2">
                        <input
                          type="checkbox"
                          checked={formData.ldap_enabled || false}
                          onChange={(e) =>
                            setFormData({ ...formData, ldap_enabled: e.target.checked })
                          }
                          className="mr-2"
                        />
                        <span className="text-sm text-gray-700">
                          Abilita autenticazione LDAP
                        </span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      LDAP DN
                    </label>
                    <input
                      type="text"
                      value={formData.ldap_dn || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, ldap_dn: e.target.value })
                      }
                      placeholder="es: cn=user,ou=users,dc=example,dc=com"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Distinguished Name per autenticazione LDAP
                    </p>
                  </div>
                </div>
              </div>

              {/* Notifications */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Notifiche</h3>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.notifiche_email || false}
                      onChange={(e) =>
                        setFormData({ ...formData, notifiche_email: e.target.checked })
                      }
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Notifiche Email</span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.notifiche_push || false}
                      onChange={(e) =>
                        setFormData({ ...formData, notifiche_push: e.target.checked })
                      }
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Notifiche Push</span>
                  </label>
                </div>
              </div>

              {/* Note */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Note</h3>
                <textarea
                  value={formData.note || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, note: e.target.value })
                  }
                  rows={3}
                  placeholder="Note aggiuntive sul tecnico..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Annulla
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {editingTechnician ? 'Salva' : 'Crea'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

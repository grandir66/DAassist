import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Ticket, Wrench, CheckCircle, Clock, MapPin, TrendingUp } from 'lucide-react';
import { dashboardApi, type DashboardData } from '@/api/dashboard';

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await dashboardApi.getData();
      setDashboardData(data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: 'Ticket Aperti',
      value: dashboardData?.ticket_stats.aperti.toString() || '0',
      change: `${dashboardData?.ticket_stats.nuovi || 0} nuovi`,
      icon: Ticket,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'In Lavorazione',
      value: dashboardData?.ticket_stats.in_lavorazione.toString() || '0',
      change: 'In corso',
      icon: Wrench,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      title: 'Completati Oggi',
      value: dashboardData?.ticket_stats.chiusi_oggi.toString() || '0',
      change: 'Chiusi',
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Interventi Oggi',
      value: dashboardData?.interventi_oggi.length.toString() || '0',
      change: `${dashboardData?.intervento_stats.pianificati || 0} pianificati`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  const getPriorityColor = (priorita: string) => {
    const colors: Record<string, string> = {
      CRITICA: 'bg-red-100 text-red-800',
      URGENTE: 'bg-orange-100 text-orange-800',
      ALTA: 'bg-yellow-100 text-yellow-800',
      NORMALE: 'bg-blue-100 text-blue-800',
      BASSA: 'bg-gray-100 text-gray-800',
    };
    return colors[priorita] || colors.NORMALE;
  };

  const getStatoColor = (stato: string) => {
    const colors: Record<string, string> = {
      NUOVO: 'bg-blue-100 text-blue-800',
      PRESO_CARICO: 'bg-purple-100 text-purple-800',
      IN_LAVORAZIONE: 'bg-orange-100 text-orange-800',
      SCHEDULATO: 'bg-cyan-100 text-cyan-800',
      CHIUSO: 'bg-green-100 text-green-800',
      ANNULLATO: 'bg-red-100 text-red-800',
    };
    return colors[stato] || colors.NUOVO;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Panoramica generale dell'assistenza</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Tickets */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Ticket Recenti</CardTitle>
            <CardDescription>Ultimi ticket aperti</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-4 text-muted-foreground">Caricamento...</div>
            ) : !dashboardData || dashboardData.recent_tickets.length === 0 ? (
              <div className="text-center py-4 text-muted-foreground">Nessun ticket</div>
            ) : (
              <div className="space-y-4">
                {dashboardData.recent_tickets.map((ticket) => (
                  <div key={ticket.id} className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{ticket.numero}</p>
                      <p className="text-sm text-muted-foreground truncate">{ticket.cliente_ragione_sociale || '-'}</p>
                      <p className="text-xs text-muted-foreground truncate mt-1">{ticket.oggetto}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1 ml-4">
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${getPriorityColor(ticket.priorita_codice)}`}>
                        {ticket.priorita_descrizione}
                      </span>
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${getStatoColor(ticket.stato_codice)}`}>
                        {ticket.stato_descrizione}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Attività Oggi */}
        <Card>
          <CardHeader>
            <CardTitle>Attività di Oggi</CardTitle>
            <CardDescription>Interventi pianificati</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-4 text-muted-foreground">Caricamento...</div>
            ) : !dashboardData || dashboardData.interventi_oggi.length === 0 ? (
              <div className="text-center py-4 text-muted-foreground">Nessun intervento pianificato per oggi</div>
            ) : (
              <div className="space-y-4">
                {dashboardData.interventi_oggi.map((intervento) => {
                  const Icon = intervento.tipo_richiede_viaggio ? MapPin : Wrench;
                  const time = intervento.data_inizio
                    ? new Date(intervento.data_inizio).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })
                    : 'N/D';

                  return (
                    <div key={intervento.id} className="flex items-center gap-4">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-full ${
                        intervento.stato_codice === 'IN_CORSO' ? 'bg-orange-100' :
                        intervento.stato_codice === 'COMPLETATO' ? 'bg-green-100' :
                        'bg-blue-100'
                      }`}>
                        <Icon className={`h-5 w-5 ${
                          intervento.stato_codice === 'IN_CORSO' ? 'text-orange-600' :
                          intervento.stato_codice === 'COMPLETATO' ? 'text-green-600' :
                          'text-blue-600'
                        }`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {intervento.tipo_descrizione} - {intervento.cliente_ragione_sociale}
                        </p>
                        <p className="text-xs text-muted-foreground truncate">
                          {time} - {intervento.oggetto}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Performance Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Performance del Mese</CardTitle>
          <CardDescription>Statistiche ticket e interventi</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <TrendingUp className="h-12 w-12 mx-auto mb-2" />
              <p>Grafici in arrivo...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

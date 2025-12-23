import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ChevronLeft, ChevronRight, MapPin, Calendar as CalendarIcon } from 'lucide-react';
import { interventiApi, Intervento } from '@/api/interventions';

// Giorni della settimana
const GIORNI_SETTIMANA = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'];

// Mesi dell'anno
const MESI = [
  'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
  'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'
];

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  interventions: Intervento[];
}

function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarDays, setCalendarDays] = useState<CalendarDay[]>([]);
  const [interventions, setInterventions] = useState<Intervento[]>([]);
  const [loading, setLoading] = useState(true);

  // Carica interventi
  useEffect(() => {
    loadInterventions();
  }, [currentDate]);

  const loadInterventions = async () => {
    try {
      setLoading(true);

      // Get first and last day of current month
      const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

      const response = await interventiApi.getAll({
        limit: 100,
        data_from: firstDay.toISOString(),
        data_to: lastDay.toISOString(),
      });

      setInterventions(response.interventi);
    } catch (error) {
      console.error('Errore nel caricamento degli interventi:', error);
    } finally {
      setLoading(false);
    }
  };

  // Genera i giorni del calendario
  useEffect(() => {
    generateCalendarDays();
  }, [currentDate, interventions]);

  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // Primo giorno del mese
    const firstDayOfMonth = new Date(year, month, 1);
    // Ultimo giorno del mese
    const lastDayOfMonth = new Date(year, month + 1, 0);

    // Giorno della settimana del primo giorno (0 = Domenica, 1 = Lunedì, ...)
    let firstDayOfWeek = firstDayOfMonth.getDay();
    // Convertiamo da formato US (Domenica = 0) a formato EU (Lunedì = 0)
    firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;

    const days: CalendarDay[] = [];
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Aggiungi giorni del mese precedente
    const prevMonthLastDay = new Date(year, month, 0);
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month - 1, prevMonthLastDay.getDate() - i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: date.getTime() === today.getTime(),
        interventions: getInterventionsForDay(date),
      });
    }

    // Aggiungi giorni del mese corrente
    for (let day = 1; day <= lastDayOfMonth.getDate(); day++) {
      const date = new Date(year, month, day);
      days.push({
        date,
        isCurrentMonth: true,
        isToday: date.getTime() === today.getTime(),
        interventions: getInterventionsForDay(date),
      });
    }

    // Aggiungi giorni del mese successivo per completare la griglia
    const remainingDays = 42 - days.length; // 6 righe x 7 giorni = 42
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month + 1, day);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: date.getTime() === today.getTime(),
        interventions: getInterventionsForDay(date),
      });
    }

    setCalendarDays(days);
  };

  const getInterventionsForDay = (date: Date): Intervento[] => {
    return interventions.filter(intervento => {
      // Check if intervention has data_inizio
      if (!intervento.data_inizio) return false;

      const interventionDate = new Date(intervento.data_inizio);
      return (
        interventionDate.getDate() === date.getDate() &&
        interventionDate.getMonth() === date.getMonth() &&
        interventionDate.getFullYear() === date.getFullYear()
      );
    });
  };

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getStatoColor = (codice?: string) => {
    switch (codice) {
      case 'PIANIFICATO':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'IN_CORSO':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'COMPLETATO':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'CHIUSO':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <CalendarIcon className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Calendario</h1>
            <p className="text-muted-foreground">
              {MESI[currentDate.getMonth()]} {currentDate.getFullYear()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={goToToday}>
            Oggi
          </Button>
          <Button variant="outline" size="icon" onClick={prevMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={nextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Calendar Grid */}
      <Card className="p-6">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Days of week header */}
            <div className="grid grid-cols-7 gap-2">
              {GIORNI_SETTIMANA.map(giorno => (
                <div
                  key={giorno}
                  className="text-center text-sm font-semibold text-muted-foreground py-2"
                >
                  {giorno}
                </div>
              ))}
            </div>

            {/* Calendar days */}
            <div className="grid grid-cols-7 gap-2">
              {calendarDays.map((day, index) => (
                <div
                  key={index}
                  className={`
                    min-h-[120px] p-2 border rounded-lg
                    ${day.isCurrentMonth ? 'bg-white' : 'bg-muted/30'}
                    ${day.isToday ? 'ring-2 ring-primary' : ''}
                  `}
                >
                  <div
                    className={`
                      text-sm font-medium mb-2
                      ${day.isCurrentMonth ? 'text-foreground' : 'text-muted-foreground'}
                      ${day.isToday ? 'text-primary font-bold' : ''}
                    `}
                  >
                    {day.date.getDate()}
                  </div>

                  <div className="space-y-1">
                    {day.interventions.map(intervento => (
                      <div
                        key={intervento.id}
                        className={`
                          text-xs p-1.5 rounded border
                          ${getStatoColor(intervento.stato?.codice)}
                          cursor-pointer hover:shadow-sm transition-shadow
                        `}
                        title={`${intervento.oggetto} - ${intervento.cliente?.ragione_sociale}`}
                      >
                        <div className="flex items-center gap-1 mb-0.5">
                          {intervento.tipo_intervento?.richiede_viaggio && (
                            <MapPin className="h-3 w-3 flex-shrink-0" />
                          )}
                          <span className="font-medium truncate">
                            {intervento.numero}
                          </span>
                        </div>
                        <div className="truncate text-xs opacity-90">
                          {intervento.cliente?.ragione_sociale}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Legend */}
      <Card className="p-4">
        <h3 className="text-sm font-semibold mb-3">Legenda</h3>
        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-blue-100 border border-blue-200"></div>
            <span className="text-sm">Pianificato</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-amber-100 border border-amber-200"></div>
            <span className="text-sm">In corso</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-purple-100 border border-purple-200"></div>
            <span className="text-sm">Completato</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-100 border border-green-200"></div>
            <span className="text-sm">Chiuso</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">Richiede viaggio</span>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default Calendar;

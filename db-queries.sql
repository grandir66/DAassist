-- DAAssist - Query SQL Utili per Database Inspection

-- ============================================
-- LISTE TABELLE
-- ============================================

-- Lista tutte le tabelle
\dt

-- Lista tabelle con dimensioni
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;


-- ============================================
-- STRUTTURE TABELLE
-- ============================================

-- Struttura tabella tecnici
\d tecnici

-- Struttura tabella ticket
\d ticket

-- Struttura tabella interventi
\d interventi

-- Struttura cache_clienti
\d cache_clienti

-- Struttura cache_contratti
\d cache_contratti


-- ============================================
-- CONTEGGI DATI
-- ============================================

-- Conteggio per ogni tabella
SELECT
    'tecnici' as tabella,
    COUNT(*) as records
FROM tecnici
UNION ALL
SELECT 'cache_clienti', COUNT(*) FROM cache_clienti
UNION ALL
SELECT 'cache_contratti', COUNT(*) FROM cache_contratti
UNION ALL
SELECT 'ticket', COUNT(*) FROM ticket
UNION ALL
SELECT 'interventi', COUNT(*) FROM interventi
UNION ALL
SELECT 'lookup_priorita', COUNT(*) FROM lookup_priorita
UNION ALL
SELECT 'lookup_stati_ticket', COUNT(*) FROM lookup_stati_ticket
UNION ALL
SELECT 'lookup_stati_intervento', COUNT(*) FROM lookup_stati_intervento
UNION ALL
SELECT 'lookup_tipi_intervento', COUNT(*) FROM lookup_tipi_intervento
UNION ALL
SELECT 'lookup_categorie_attivita', COUNT(*) FROM lookup_categorie_attivita
UNION ALL
SELECT 'lookup_reparti', COUNT(*) FROM lookup_reparti
UNION ALL
SELECT 'lookup_ruoli_utente', COUNT(*) FROM lookup_ruoli_utente
ORDER BY tabella;


-- ============================================
-- DATI LOOKUP (Tabelle di configurazione)
-- ============================================

-- Priorità
SELECT * FROM lookup_priorita ORDER BY livello;

-- Stati Ticket
SELECT * FROM lookup_stati_ticket ORDER BY ordine;

-- Stati Intervento
SELECT * FROM lookup_stati_intervento ORDER BY ordine;

-- Tipi Intervento
SELECT * FROM lookup_tipi_intervento ORDER BY ordine;

-- Categorie Attività
SELECT * FROM lookup_categorie_attivita ORDER BY ordine;

-- Reparti
SELECT * FROM lookup_reparti ORDER BY descrizione;

-- Ruoli Utente
SELECT * FROM lookup_ruoli_utente ORDER BY descrizione;


-- ============================================
-- TECNICI
-- ============================================

-- Tutti i tecnici
SELECT
    id,
    username,
    email,
    nome,
    cognome,
    attivo,
    created_at
FROM tecnici
ORDER BY cognome, nome;

-- Tecnici attivi
SELECT
    t.id,
    t.username,
    t.email,
    t.nome || ' ' || t.cognome as nome_completo,
    r.descrizione as ruolo,
    rep.descrizione as reparto
FROM tecnici t
LEFT JOIN lookup_ruoli_utente r ON t.ruolo_id = r.id
LEFT JOIN lookup_reparti rep ON t.reparto_id = rep.id
WHERE t.attivo = true
ORDER BY t.cognome, t.nome;


-- ============================================
-- CLIENTI E CONTRATTI
-- ============================================

-- Clienti
SELECT
    id,
    codice_gestionale,
    ragione_sociale,
    citta,
    email
FROM cache_clienti
ORDER BY ragione_sociale;

-- Contratti attivi
SELECT
    c.id,
    c.codice_gestionale,
    cl.ragione_sociale as cliente,
    c.descrizione,
    c.tipo_contratto,
    c.data_inizio,
    c.data_fine,
    c.ore_incluse,
    c.ore_utilizzate,
    (c.ore_incluse - c.ore_utilizzate) as ore_residue
FROM cache_contratti c
JOIN cache_clienti cl ON c.cliente_id = cl.id
WHERE c.attivo_gestionale = 1
ORDER BY cl.ragione_sociale, c.data_inizio DESC;


-- ============================================
-- TICKET
-- ============================================

-- Ultimi ticket
SELECT
    t.numero,
    t.oggetto,
    cl.ragione_sociale as cliente,
    p.descrizione as priorita,
    s.descrizione as stato,
    tec.nome || ' ' || tec.cognome as tecnico,
    t.created_at
FROM ticket t
LEFT JOIN cache_clienti cl ON t.cliente_id = cl.id
LEFT JOIN lookup_priorita p ON t.priorita_id = p.id
LEFT JOIN lookup_stati_ticket s ON t.stato_id = s.id
LEFT JOIN tecnici tec ON t.tecnico_assegnato_id = tec.id
WHERE t.attivo = true
ORDER BY t.created_at DESC
LIMIT 10;

-- Ticket aperti per tecnico
SELECT
    tec.nome || ' ' || tec.cognome as tecnico,
    COUNT(*) as ticket_aperti
FROM ticket t
JOIN tecnici tec ON t.tecnico_assegnato_id = tec.id
JOIN lookup_stati_ticket s ON t.stato_id = s.id
WHERE t.attivo = true AND s.finale = 0
GROUP BY tec.id, tec.nome, tec.cognome
ORDER BY ticket_aperti DESC;


-- ============================================
-- INTERVENTI
-- ============================================

-- Ultimi interventi
SELECT
    i.id,
    i.titolo,
    cl.ragione_sociale as cliente,
    s.descrizione as stato,
    ti.descrizione as tipo,
    i.data_pianificata,
    i.created_at
FROM interventi i
LEFT JOIN cache_clienti cl ON i.cliente_id = cl.id
LEFT JOIN lookup_stati_intervento s ON i.stato_id = s.id
LEFT JOIN lookup_tipi_intervento ti ON i.tipo_id = ti.id
WHERE i.attivo = true
ORDER BY i.created_at DESC
LIMIT 10;


-- ============================================
-- STATISTICHE
-- ============================================

-- Ticket per stato
SELECT
    s.descrizione as stato,
    COUNT(*) as totale
FROM ticket t
JOIN lookup_stati_ticket s ON t.stato_id = s.id
WHERE t.attivo = true
GROUP BY s.id, s.descrizione, s.ordine
ORDER BY s.ordine;

-- Ticket per priorità
SELECT
    p.descrizione as priorita,
    COUNT(*) as totale
FROM ticket t
JOIN lookup_priorita p ON t.priorita_id = p.id
WHERE t.attivo = true
GROUP BY p.id, p.descrizione, p.livello
ORDER BY p.livello DESC;

-- Interventi per mese (ultimi 6 mesi)
SELECT
    TO_CHAR(created_at, 'YYYY-MM') as mese,
    COUNT(*) as totale
FROM interventi
WHERE
    attivo = true
    AND created_at >= NOW() - INTERVAL '6 months'
GROUP BY TO_CHAR(created_at, 'YYYY-MM')
ORDER BY mese DESC;


-- ============================================
-- UTILITY
-- ============================================

-- Versione Alembic (migration)
SELECT * FROM alembic_version;

-- Informazioni database
SELECT
    pg_size_pretty(pg_database_size('daassist')) as database_size;

-- Tabelle più grandi
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

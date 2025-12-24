-- Script di inizializzazione database DAAssist
-- Esegui dopo aver fatto alembic upgrade head

-- Inserisci ruoli utente base
INSERT INTO lookup_ruoli_utente (codice, descrizione, permessi, ordine, attivo, created_at, updated_at)
VALUES
  ('ADMIN', 'Amministratore', '{}', 1, true, NOW(), NOW()),
  ('TECNICO', 'Tecnico', '{}', 2, true, NOW(), NOW()),
  ('OPERATORE', 'Operatore', '{}', 3, true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Inserisci utente admin (password: admin)
-- Hash generato con: bcrypt.hashpw(b'admin', bcrypt.gensalt())
INSERT INTO tecnici (username, email, hashed_password, nome, cognome, ruolo_id, attivo, created_at, updated_at)
SELECT 'admin', 'admin@daassist.local', '$2b$12$SHEkjoUySKZwcoioILdHo.lJ7mFT7tFUsZ5MJUmdliJpWuk9OfIF2', 'Admin', 'Sistema', id, true, NOW(), NOW()
FROM lookup_ruoli_utente WHERE codice = 'ADMIN'
ON CONFLICT (username) DO UPDATE SET hashed_password = EXCLUDED.hashed_password;

-- Inserisci lookup priorità base
INSERT INTO lookup_priorita (codice, descrizione, livello, tempo_risposta_ore, ordine, attivo, created_at, updated_at)
VALUES
  ('CRITICA', 'Critica', 1, 1, 1, true, NOW(), NOW()),
  ('ALTA', 'Alta', 2, 4, 2, true, NOW(), NOW()),
  ('MEDIA', 'Media', 3, 24, 3, true, NOW(), NOW()),
  ('BASSA', 'Bassa', 4, 72, 4, true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Inserisci lookup stati ticket base
INSERT INTO lookup_stati_ticket (codice, descrizione, colore, ordine, attivo, created_at, updated_at)
VALUES
  ('APERTO', 'Aperto', '#3B82F6', 1, true, NOW(), NOW()),
  ('IN_LAVORAZIONE', 'In Lavorazione', '#F59E0B', 2, true, NOW(), NOW()),
  ('IN_ATTESA', 'In Attesa', '#6B7280', 3, true, NOW(), NOW()),
  ('RISOLTO', 'Risolto', '#10B981', 4, true, NOW(), NOW()),
  ('CHIUSO', 'Chiuso', '#059669', 5, true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Inserisci lookup stati intervento base
INSERT INTO lookup_stati_intervento (codice, descrizione, colore, ordine, attivo, created_at, updated_at)
VALUES
  ('PIANIFICATO', 'Pianificato', '#3B82F6', 1, true, NOW(), NOW()),
  ('IN_CORSO', 'In Corso', '#F59E0B', 2, true, NOW(), NOW()),
  ('SOSPESO', 'Sospeso', '#EF4444', 3, true, NOW(), NOW()),
  ('COMPLETATO', 'Completato', '#8B5CF6', 4, true, NOW(), NOW()),
  ('CHIUSO', 'Chiuso', '#10B981', 5, true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Inserisci lookup canali richiesta base
INSERT INTO lookup_canali_richiesta (nome, codice, ordine, attivo, created_at, updated_at)
VALUES
  ('Telefono', 'TELEFONO', 1, true, NOW(), NOW()),
  ('Email', 'EMAIL', 2, true, NOW(), NOW()),
  ('Portale', 'PORTALE', 3, true, NOW(), NOW()),
  ('Chat', 'CHAT', 4, true, NOW(), NOW())
ON CONFLICT DO NOTHING;

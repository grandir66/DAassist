from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class KBCategoria(BaseModel):
    """Categorie Knowledge Base (gerarchiche)"""

    __tablename__ = "kb_categorie"

    nome = Column(String(100), nullable=False)
    descrizione = Column(Text)
    icona = Column(String(50))  # Emoji o nome icona

    # Gerarchia
    parent_id = Column(Integer, ForeignKey("kb_categorie.id"), nullable=True, index=True)

    ordine = Column(Integer, default=0)

    # Visibilità
    pubblica = Column(Integer, default=False)  # Visibile su portale cliente

    # Relationships
    parent = relationship("KBCategoria", remote_side="KBCategoria.id", backref="sottocategorie")
    articoli = relationship("KBArticolo", back_populates="categoria", lazy="dynamic")


class KBArticolo(BaseModel):
    """Articoli Knowledge Base"""

    __tablename__ = "kb_articoli"

    titolo = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    categoria_id = Column(Integer, ForeignKey("kb_categorie.id"), nullable=False, index=True)

    # Contenuto
    contenuto = Column(Text, nullable=False)  # Markdown o HTML
    formato = Column(String(20), default="MARKDOWN")  # MARKDOWN, HTML

    # Autore
    autore_id = Column(Integer, ForeignKey("tecnici.id"), nullable=False)

    # Visibilità
    pubblicato = Column(Integer, default=False)
    pubblico = Column(Integer, default=False)  # Visibile su portale cliente

    # SEO / Ricerca
    keywords = Column(String(500))  # Separati da virgola
    excerpt = Column(Text)  # Riassunto

    # Metriche
    visualizzazioni = Column(Integer, default=0)
    utile_count = Column(Integer, default=0)
    non_utile_count = Column(Integer, default=0)

    # Versioning
    versione = Column(Integer, default=1)
    parent_versione_id = Column(Integer, ForeignKey("kb_articoli.id"), nullable=True)

    # Relationships
    categoria = relationship("KBCategoria", back_populates="articoli", lazy="joined")
    autore = relationship("Tecnico", lazy="joined")
    parent_versione = relationship("KBArticolo", remote_side=[parent_versione_id], foreign_keys=[parent_versione_id], uselist=False)

    # Tag
    tags = relationship("KBArticoloTag", back_populates="articolo", lazy="dynamic")


class KBTag(BaseModel):
    """Tag per articoli KB"""

    __tablename__ = "kb_tags"

    nome = Column(String(50), unique=True, nullable=False, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)

    # Relationships
    articoli = relationship("KBArticoloTag", back_populates="tag", lazy="dynamic")


class KBArticoloTag(BaseModel):
    """Relazione molti-a-molti articoli-tag"""

    __tablename__ = "kb_articoli_tags"

    articolo_id = Column(Integer, ForeignKey("kb_articoli.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("kb_tags.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    articolo = relationship("KBArticolo", back_populates="tags")
    tag = relationship("KBTag", back_populates="articoli")


class KBArticoloFeedback(BaseModel):
    """Feedback articoli KB"""

    __tablename__ = "kb_articoli_feedback"

    articolo_id = Column(Integer, ForeignKey("kb_articoli.id", ondelete="CASCADE"), nullable=False, index=True)
    tecnico_id = Column(Integer, ForeignKey("tecnici.id"), nullable=True)

    utile = Column(Integer, nullable=False)  # 1 = utile, 0 = non utile
    commento = Column(Text)

    # Relationships
    articolo = relationship("KBArticolo")
    tecnico = relationship("Tecnico")

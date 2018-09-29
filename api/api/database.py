import getpass
import os
from sqlalchemy import (
    create_engine,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"
    user_id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False, unique=True)


class Beatmap(Base):
    __tablename__ = "beatmaps"

    beatmap_id = Column(Integer, primary_key=True)
    beatmapset_id = Column(Integer, nullable=False)

    # These must be constantly updated.
    file_md5 = Column(String(32), nullable=False)
    approved = Column(Integer, nullable=False)
    approved_date = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)

    artist = Column(Text, nullable=False)
    bpm = Column(Float, nullable=False)
    creator = Column(Text, nullable=False)
    difficultyrating = Column(Float, nullable=False)
    diff_size = Column(Float, nullable=False)
    diff_overall = Column(Float, nullable=False)
    diff_approach = Column(Float, nullable=False)
    diff_drain = Column(Float, nullable=False)
    hit_length = Column(Integer, nullable=False)
    source = Column(Text, nullable=False)
    genre_id = Column(Integer, nullable=False)
    language_id = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    total_length = Column(Integer, nullable=False)
    version = Column(Text, nullable=False)
    mode = Column(Integer, nullable=False)
    tags = Column(Text, nullable=False)
    max_combo = Column(Integer, nullable=False)

    # Intentionally omitted:
    # - favourite_count
    # - playcount
    # - passcount


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)  # Serial.

    beatmap_id = Column(Integer, ForeignKey("beatmaps.beatmap_id"), nullable=False)
    username = Column(Text, ForeignKey("players.username"), nullable=False)
    user_id = Column(Integer, ForeignKey("players.user_id"), nullable=False)

    mode = Column(Integer, nullable=False)
    beatmap_md5 = Column(String(32), nullable=False)
    replay_md5 = Column(String(32), nullable=False)
    count300 = Column(Integer, nullable=False)
    count100 = Column(Integer, nullable=False)
    count50 = Column(Integer, nullable=False)
    countgeki = Column(Integer, nullable=False)
    countkatu = Column(Integer, nullable=False)
    countmiss = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    maxcombo = Column(Integer, nullable=False)
    perfect = Column(Boolean, nullable=False)
    enabled_mods = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    rank = Column(String(3), nullable=False)
    pp = Column(Float, nullable=True)


class IncompleteMapset(Base):
    __tablename__ = "incomplete_mapsets"
    beatmapset_id = Column(Integer, primary_key=True)


_u = os.getenv("PGUSER", "postgres")
_p = os.getenv("PGPASSWORD", "")
_h = os.getenv("PGHOST", "localhost")
_d = os.getenv("PGDATABASE", _u)
engine = create_engine(f"postgresql://{_u}:{_p}@{_h}/{_d}")
Base.metadata.bind = engine
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)

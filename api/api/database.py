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
DBSession = None

_u = os.getenv("PGUSER", "postgres")
_p = os.getenv("PGPASSWORD", "")
_h = os.getenv("PGHOST", "localhost")
_d = os.getenv("PGDATABASE", _u)


def connect():
    engine = create_engine(f"postgresql://{_u}:{_p}@{_h}/{_d}")
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    global DBSession
    DBSession = sessionmaker(bind=engine)


def session():
    return DBSession()


class Player(Base):
    __tablename__ = "players"
    user_id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False, unique=True, index=True)


class Beatmap(Base):
    __tablename__ = "beatmaps"

    beatmap_id = Column(Integer, primary_key=True)
    beatmapset_id = Column(Integer, nullable=False)

    # These must be constantly updated.
    file_md5 = Column(String(32), nullable=False, unique=True)
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

    beatmap_id = Column(
        Integer, ForeignKey("beatmaps.beatmap_id"), nullable=False, index=True
    )
    username = Column(Text, ForeignKey("players.username"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("players.user_id"), nullable=False, index=True)

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
    accuracy = Column(Float, nullable=False)
    rank = Column(String(3), nullable=False)
    pp = Column(Float, nullable=True)

    def dict(self):
        return {
            "beatmap_id": self.beatmap_id,
            "username": self.username,
            "user_id": self.user_id,
            "mode": self.mode,
            "beatmap_md5": self.beatmap_md5,
            "count300": self.count300,
            "count100": self.count100,
            "count50": self.count50,
            "countgeki": self.countgeki,
            "countkatu": self.countkatu,
            "countmiss": self.countmiss,
            "score": self.score,
            "maxcombo": self.maxcombo,
            "perfect": self.perfect,
            "enabled_mods": self.enabled_mods,
            "date": self.date,
            "rank": self.rank,
            "accuracy": self.accuracy,
            "pp": self.pp,
        }


class BeatmapHash(Base):
    __tablename__ = "beatmap_hashes"
    beatmap_id = Column(Integer, ForeignKey("beatmaps.beatmap_id"), primary_key=True)
    file_md5 = Column(String(32), ForeignKey("beatmaps.file_md5"), primary_key=True)


class IncompleteMapset(Base):
    __tablename__ = "incomplete_mapsets"
    beatmapset_id = Column(Integer, primary_key=True)

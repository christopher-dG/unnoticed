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
from sqlalchemy.sql import func

from api import utils


Base = declarative_base()
DBSession = None

# PostgreSQL connection parameters.
_u = os.getenv("PGUSER", "postgres")
_p = os.getenv("PGPASSWORD", "")
_h = os.getenv("PGHOST", "localhost")
_d = os.getenv("PGDATABASE", _u)


def connect():
    """Connects to the database. Calling session before this will fail!"""
    engine = create_engine(f"postgresql://{_u}:{_p}@{_h}/{_d}")
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    global DBSession
    DBSession = sessionmaker(bind=engine)


def session():
    """Returns a database session. You must call connect first!"""
    return DBSession()


class Player(Base):
    """An osu! user."""

    __tablename__ = "players"
    user_id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False, unique=True, index=True)


class Beatmap(Base):
    """An osu! beatmap."""

    __tablename__ = "beatmaps"
    beatmap_id = Column(Integer, unique=False, primary_key=True)
    file_md5 = Column(String(32), unique=True, primary_key=True)


class Score(Base):
    """An osu! score."""

    __tablename__ = "scores"

    # These columns are generated for us upon insert.
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())

    beatmap_md5 = Column(
        String(32), ForeignKey("beatmaps.file_md5"), nullable=False, index=True
    )
    username = Column(Text, ForeignKey("players.username"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("players.user_id"), nullable=False, index=True)

    beatmap_id = Column(Integer, nullable=False, index=True)
    mode = Column(Integer, nullable=False, index=True)
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
    enabled_mods = Column(Integer, nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    accuracy = Column(Float, nullable=False)
    rank = Column(String(3), nullable=False)
    pp = Column(Float, nullable=True)

    def from_dict(d):
        """
        Construct a Score from a dict.
        These fields are left empty (they require disk access or external commands):
        - beatmap_id
        - user_id
        - pp
        """
        return Score(
            username=d["username"],
            beatmap_md5=d["beatmap_md5"],
            replay_md5=d["replay_md5"],
            count300=d["count300"],
            count100=d["count100"],
            count50=d["count50"],
            countgeki=d["countgeki"],
            countkatu=d["countkatu"],
            countmiss=d["countmiss"],
            score=d["score"],
            maxcombo=d["maxcombo"],
            perfect=d["perfect"],
            enabled_mods=d["enabled_mods"],
            date=utils.from_winticks(d["date"]),
            accuracy=utils.utils.accuracy(d),
            rank=utils.rank(d),
        )

    def to_dict(self):
        """Converts the score to a dict."""
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

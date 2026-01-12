"""SQLAlchemy database models for the retro console."""

from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from retro_console import settings

Base = declarative_base()


class Game(Base):
    """A game registered in the system."""

    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    package_path = Column(String, unique=True, nullable=False)
    author = Column(String)
    description = Column(String)
    play_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    high_scores = relationship("HighScore", back_populates="game", order_by="HighScore.score.desc()")
    plays = relationship("Play", back_populates="game")

    def get_top_scores(self, limit=10):
        """Get the top N high scores for this game."""
        return sorted(self.high_scores, key=lambda s: s.score, reverse=True)[:limit]

    def is_high_score(self, score):
        """Check if a score qualifies as a top 10 high score."""
        top_scores = self.get_top_scores(10)
        if len(top_scores) < 10:
            return True
        return score > top_scores[-1].score


class HighScore(Base):
    """A high score entry."""

    __tablename__ = "high_scores"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    initials = Column(String(3), nullable=False)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="high_scores")


class Play(Base):
    """A record of a game being played."""

    __tablename__ = "plays"

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, nullable=True)

    game = relationship("Game", back_populates="plays")


_engine = None
_Session = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{settings.DATABASE_PATH}")
    return _engine


def get_session():
    """Get a new database session."""
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _Session()


def init_db():
    """Initialize the database, creating tables if needed."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def get_or_create_game(session, name, package_path, author=None, description=None):
    """Get an existing game or create a new one."""
    game = session.query(Game).filter_by(name=name).first()
    if game is None:
        game = Game(
            name=name,
            package_path=package_path,
            author=author,
            description=description,
        )
        session.add(game)
        session.commit()
    else:
        game.author = author
        game.description = description
        game.package_path = package_path
        session.commit()
    return game


def record_play(session, game, score=None):
    """Record a game play and optionally update the score."""
    play = Play(game_id=game.id, score=score)
    session.add(play)
    game.play_count += 1
    session.commit()
    return play


def add_high_score(session, game, initials, score):
    """Add a new high score entry."""
    high_score = HighScore(
        game_id=game.id,
        initials=initials.upper()[:3],
        score=score,
    )
    session.add(high_score)
    session.commit()
    return high_score

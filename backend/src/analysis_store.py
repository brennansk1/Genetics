"""
In-memory analysis session store.

Stores analysis results by UUID with TTL-based automatic cleanup.
In a production deployment this would be backed by Redis or a database,
but for single-process development an in-memory dict is sufficient.
"""

import logging
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default TTL: 1 hour
DEFAULT_TTL_SECONDS = 3600

# How often the cleanup thread wakes up (seconds)
_CLEANUP_INTERVAL = 300  # 5 minutes


class AnalysisSession:
    """Container for a single analysis session's results."""

    def __init__(self, data: Dict[str, Any], ttl_seconds: int = DEFAULT_TTL_SECONDS):
        self.analysis_id: str = str(uuid.uuid4())
        self.created_at: datetime = datetime.utcnow()
        self.expires_at: datetime = self.created_at + timedelta(seconds=ttl_seconds)
        self.data: Dict[str, Any] = data

    @property
    def is_expired(self) -> bool:
        """Return True if this session has exceeded its TTL."""
        return datetime.utcnow() > self.expires_at


class AnalysisStore:
    """
    Thread-safe in-memory store for analysis results keyed by UUID.

    Usage:
        store = AnalysisStore()
        aid = store.save({"clinvar": [...], "prs": [...]})
        result = store.get(aid)
    """

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS):
        self._store: Dict[str, AnalysisSession] = {}
        self._lock = threading.Lock()
        self._ttl_seconds = ttl_seconds
        self._cleanup_thread: Optional[threading.Thread] = None
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, data: Dict[str, Any]) -> str:
        """
        Persist analysis results and return the assigned analysis_id.

        Args:
            data: Dictionary containing all analysis result sections.

        Returns:
            A UUID string that can be used to retrieve the results later.
        """
        session = AnalysisSession(data, ttl_seconds=self._ttl_seconds)
        with self._lock:
            self._store[session.analysis_id] = session
        logger.info(
            "Saved analysis session %s (expires %s)",
            session.analysis_id,
            session.expires_at.isoformat(),
        )
        return session.analysis_id

    def get(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis results by analysis_id.

        Args:
            analysis_id: UUID returned from a previous ``save`` call.

        Returns:
            The stored data dict, or ``None`` if the id is unknown or expired.
        """
        with self._lock:
            session = self._store.get(analysis_id)
            if session is None:
                return None
            if session.is_expired:
                del self._store[analysis_id]
                logger.info("Analysis session %s has expired and was removed.", analysis_id)
                return None
            return session.data

    def get_session_info(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Return metadata about a session without returning the full data payload.

        Args:
            analysis_id: UUID of the session.

        Returns:
            Dict with created_at, expires_at, and available section keys.
        """
        with self._lock:
            session = self._store.get(analysis_id)
            if session is None or session.is_expired:
                return None
            return {
                "analysis_id": session.analysis_id,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "sections": list(session.data.keys()),
            }

    def delete(self, analysis_id: str) -> bool:
        """
        Explicitly remove an analysis session.

        Args:
            analysis_id: UUID of the session to remove.

        Returns:
            True if a session was removed, False if it did not exist.
        """
        with self._lock:
            if analysis_id in self._store:
                del self._store[analysis_id]
                logger.info("Analysis session %s deleted.", analysis_id)
                return True
        return False

    def active_session_count(self) -> int:
        """Return the number of non-expired sessions."""
        with self._lock:
            return sum(1 for s in self._store.values() if not s.is_expired)

    # ------------------------------------------------------------------
    # TTL cleanup
    # ------------------------------------------------------------------

    def start_cleanup_task(self) -> None:
        """
        Start a background daemon thread that periodically removes expired
        sessions.  Safe to call multiple times; only one thread will run.
        """
        if self._running:
            return
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True, name="analysis-store-cleanup"
        )
        self._cleanup_thread.start()
        logger.info("Analysis store cleanup thread started (interval=%ds).", _CLEANUP_INTERVAL)

    def stop_cleanup_task(self) -> None:
        """Signal the cleanup thread to stop."""
        self._running = False

    def _cleanup_loop(self) -> None:
        """Background loop that purges expired sessions."""
        while self._running:
            time.sleep(_CLEANUP_INTERVAL)
            self._purge_expired()

    def _purge_expired(self) -> None:
        """Remove all expired sessions."""
        with self._lock:
            expired_ids = [
                aid for aid, session in self._store.items() if session.is_expired
            ]
            for aid in expired_ids:
                del self._store[aid]
            if expired_ids:
                logger.info("Purged %d expired analysis session(s).", len(expired_ids))


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
analysis_store = AnalysisStore()

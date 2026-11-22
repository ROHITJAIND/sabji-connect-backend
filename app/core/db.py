"""MongoDB connections: async (FastAPI) and sync (background tasks).

Adapted from the seahydrosys-ai reference architecture.
"""

import asyncio
import threading
from collections.abc import AsyncGenerator
from typing import Any, Optional

import certifi
from beanie import Document, init_beanie
from pymongo import AsyncMongoClient, MongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.database import Database

from app.core.config import env
from app.core.logger import logger

_Doc = dict[str, Any]
AsyncClient = AsyncMongoClient[_Doc]
AsyncDb = AsyncDatabase[_Doc]
SyncClient = MongoClient[_Doc]
SyncDb = Database[_Doc]


def _client_options() -> dict[str, Any]:
    return {
        "tlsCAFile": certifi.where(),
        "maxPoolSize": 10,
        "minPoolSize": 1,
        "serverSelectionTimeoutMS": 5000,
        "socketTimeoutMS": 45000,
        "connectTimeoutMS": 10000,
        "uuidRepresentation": "standard",
    }


class DatabaseManager:
    """Owns the async and sync MongoDB clients.

    Clients are created lazily; async client is recreated when
    the event loop changes (e.g. in test runners).
    """

    def __init__(self) -> None:
        self._async_client: Optional[AsyncClient] = None
        self._async_db: Optional[AsyncDb] = None
        self._client_loop: Optional[asyncio.AbstractEventLoop] = None
        self._sync_client: Optional[SyncClient] = None
        self._sync_db: Optional[SyncDb] = None
        self._beanie_initialized = False
        self._sync_lock = threading.Lock()

    # ── Async ────────────────────────────────────────────────────

    def get_async_client(self) -> AsyncClient:
        try:
            current_loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        loop_changed = current_loop is not None and current_loop is not self._client_loop
        loop_closed = self._client_loop is not None and self._client_loop.is_closed()

        if self._async_client is not None and (loop_changed or loop_closed):
            self._async_client = None
            self._async_db = None
            self._beanie_initialized = False
            logger.debug("Async MongoDB client reset due to event loop change")

        if self._async_client is None:
            try:
                self._async_client = AsyncMongoClient(env.MONGODB_URI, **_client_options())
                self._client_loop = current_loop
                logger.info("Async MongoDB client created")
            except Exception:
                logger.exception("Async MongoDB client creation failed")
                raise

        return self._async_client

    # ── Sync ─────────────────────────────────────────────────────

    def get_sync_client(self) -> SyncClient:
        with self._sync_lock:
            if self._sync_client is None:
                try:
                    self._sync_client = MongoClient(env.MONGODB_URI, **_client_options())
                    logger.info("Sync MongoDB client created")
                except Exception:
                    logger.exception("Sync MongoDB client creation failed")
                    raise
            return self._sync_client

    # ── Database accessors ───────────────────────────────────────

    def get_async_db(self, db_name: Optional[str] = None) -> AsyncDb:
        client = self.get_async_client()
        if db_name is not None:
            return client[db_name]
        if self._async_db is None:
            self._async_db = client[env.MONGODB_DATABASE]
        return self._async_db

    def get_sync_db(self, db_name: Optional[str] = None) -> SyncDb:
        client = self.get_sync_client()
        if db_name is not None:
            return client[db_name]
        if self._sync_db is None:
            self._sync_db = client[env.MONGODB_DATABASE]
        return self._sync_db

    # ── Beanie ODM initialization ────────────────────────────────

    async def init_beanie_models(
        self,
        document_models: Optional[list[type[Document]]] = None,
    ) -> None:
        if self._beanie_initialized:
            return

        if not document_models:
            logger.warning("No Beanie document models provided")
            return

        try:
            db = self.get_async_db()
            await init_beanie(database=db, document_models=document_models)
            self._beanie_initialized = True
            logger.info("Beanie initialized with %d models", len(document_models))
        except Exception:
            logger.exception("Beanie initialization failed")
            raise

    # ── Lifecycle ────────────────────────────────────────────────

    async def connect(self) -> None:
        """Verify connectivity at startup (fail fast)."""
        try:
            await self.get_async_client().admin.command("ping")
        except Exception:
            logger.exception("MongoDB initialization failed")
            await self.close_async()
            raise
        logger.info("MongoDB connected")

    async def close_async(self) -> None:
        if self._async_client is not None:
            await self._async_client.close()
            self._async_client = None
            self._async_db = None
            self._client_loop = None
            self._beanie_initialized = False
            logger.info("Async MongoDB connection closed")

    def close_sync(self) -> None:
        with self._sync_lock:
            if self._sync_client is not None:
                self._sync_client.close()
                self._sync_client = None
                self._sync_db = None
                logger.info("Sync MongoDB connection closed")

    async def close(self) -> None:
        try:
            self.close_sync()
        finally:
            await self.close_async()


db_manager = DatabaseManager()


async def get_api_db_session() -> AsyncGenerator[AsyncDb, None]:
    """FastAPI dependency yielding the async database."""
    yield db_manager.get_async_db()

"""
Connexion à la base de données PostgreSQL pour les métriques
"""
import os
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Gestionnaire de connexion à PostgreSQL"""
    
    _instance: Optional['DatabaseManager'] = None
    _pool: Optional[Pool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def database_url(self) -> str:
        """Construit l'URL de connexion depuis les variables d'environnement"""
        host = os.getenv("POSTGRES_HOST", "postgres")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "etsia")
        password = os.getenv("POSTGRES_PASSWORD", "etsia_secure_password")
        database = os.getenv("POSTGRES_DB", "etsia_metrics")
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    async def connect(self) -> None:
        """Établit la connexion au pool de connexions"""
        if self._pool is not None:
            return
        
        try:
            self._pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("✓ Connexion PostgreSQL établie")
        except Exception as e:
            logger.error(f"✗ Erreur de connexion PostgreSQL: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Ferme le pool de connexions"""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            logger.info("✓ Connexion PostgreSQL fermée")
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Acquiert une connexion du pool"""
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args) -> str:
        """Exécute une requête sans retour"""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Exécute une requête et retourne les résultats"""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Exécute une requête et retourne une seule ligne"""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """Exécute une requête et retourne une seule valeur"""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def health_check(self) -> bool:
        """Vérifie la santé de la connexion"""
        try:
            result = await self.fetchval("SELECT 1")
            return result == 1
        except Exception as e:
            logger.error(f"Health check PostgreSQL échoué: {e}")
            return False


# Instance globale
db = DatabaseManager()

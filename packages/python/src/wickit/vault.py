"""vault - Generic SQLite Database Management.

Provides a clean, reusable SQLite wrapper with automatic path management.
Can be used across all wickit products for persistent storage.

Example:
    >>> from wickit import vault
    >>> db = vault.SQLiteDatabase("myapp")
    >>> db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    >>> db.insert("users", {"id": 1, "name": "John"})

Classes:
    SQLiteDatabase: Generic SQLite wrapper with helper methods.
    Transaction: Context manager for database transactions.

Functions:
    get_database: Get a database instance for a product.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from contextlib import contextmanager

from .hideaway import get_data_dir


class DatabaseError(Exception):
    """Database operation error."""
    pass


class SQLiteDatabase:
    """Generic SQLite database wrapper with helper methods."""
    
    def __init__(self, product_name: str, db_name: str = "database.db"):
        self.product_name = product_name
        self.db_name = db_name
        self.db_path = get_data_dir(product_name) / db_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable column access by name
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_command(self, command: str, params: Tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE command and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.execute(command, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_many(self, command: str, params_list: List[Tuple]) -> int:
        """Execute a command with multiple parameter sets."""
        with self.get_connection() as conn:
            cursor = conn.executemany(command, params_list)
            conn.commit()
            return cursor.rowcount
    
    def create_table(self, table_name: str, columns: Dict[str, str], 
                   constraints: Optional[List[str]] = None) -> bool:
        """Create a table with specified columns and constraints."""
        if constraints is None:
            constraints = []
        
        columns_def = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        constraints_str = ", ".join(constraints) if constraints else ""
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def}"
        if constraints_str:
            query += f", {constraints_str}"
        query += ")"
        
        self.execute_command(query)
        return True
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert data into a table."""
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        values = tuple(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        return self.execute_command(query, values)
    
    def select(self, table: str, columns: str = "*", 
              where: Optional[str] = None, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Select data from a table."""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        
        return self.execute_query(query, params)
    
    def update(self, table: str, data: Dict[str, Any], 
              where: str, params: Optional[Tuple] = ()) -> int:
        """Update data in a table."""
        columns = list(data.keys())
        set_clause = ", ".join([f"{col} = ?" for col in columns])
        values = tuple(data.values()) + params
        
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return self.execute_command(query, values)
    
    def delete(self, table: str, where: str, params: Optional[Tuple] = ()) -> int:
        """Delete data from a table."""
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute_command(query, params)
    
    def create_index(self, table: str, columns: List[str], unique: bool = False) -> bool:
        """Create an index on specified columns."""
        index_name = f"idx_{table}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        unique_str = "UNIQUE " if unique else ""
        
        query = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {table} ({columns_str})"
        self.execute_command(query)
        return True
    
    def get_table_info(self, table: str) -> List[Dict[str, str]]:
        """Get information about table columns."""
        query = f"PRAGMA table_info({table})"
        return self.execute_query(query)
    
    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        return [row['name'] for row in self.execute_query(query)]
    
    def begin_transaction(self):
        """Begin a database transaction."""
        self.execute_command("BEGIN TRANSACTION")
    
    def commit(self):
        """Commit the current transaction."""
        self.execute_command("COMMIT")
    
    def rollback(self):
        """Rollback the current transaction."""
        self.execute_command("ROLLBACK")
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            self.begin_transaction()
            yield self
            self.commit()
        except Exception:
            self.rollback()
            raise
    
    def vacuum(self) -> bool:
        """Optimize the database."""
        self.execute_command("VACUUM")
        return True
    
    def backup(self, backup_path: Union[str, Path]) -> bool:
        """Create a backup of the database."""
        with self.get_connection() as conn:
            conn.backup(str(backup_path))
        return True
    
    def restore(self, backup_path: Union[str, Path]) -> bool:
        """Restore database from backup."""
        if not backup_path.exists():
            raise DatabaseError(f"Backup file not found: {backup_path}")
        
        # Close current connection and restore
        self.execute_command("PRAGMA read_uncommitted = ON")
        self.backup(self.db_path)  # Backup current before restore
        
        # Copy backup to database location
        import shutil
        shutil.copy2(backup_path, self.db_path)
        return True


class Transaction:
    """Context manager for database transactions."""
    
    def __init__(self, db: SQLiteDatabase):
        self.db = db
    
    def __enter__(self):
        self.db.begin_transaction()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()


def get_database(product_name: str, db_name: str = "database.db") -> SQLiteDatabase:
    """Get a database instance for a product."""
    return SQLiteDatabase(product_name, db_name)


def init_database(product_name: str, db_name: str = "database.db") -> SQLiteDatabase:
    """Initialize database for a product."""
    return SQLiteDatabase(product_name, db_name)


# Export main classes and functions
__all__ = [
    "SQLiteDatabase",
    "Transaction",
    "DatabaseError",
    "get_database",
    "init_database"
]
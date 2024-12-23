import chainlit as cl
from swarm import Agent
import pyodbc
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import asyncio
import os


class SQLAgent:
    def __init__(self, connection_string: str):
        """Initialize SQL Agent with connection string and establish connection

        Args:
            connection_string: MS SQL Server connection string
        """
        self.connection_string = connection_string
        self.conn = self._establish_connection()

    def _establish_connection(self) -> pyodbc.Connection:
        """Internal method to establish database connection"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        cursor = self.conn.cursor()
        cursor.execute(os.environ.get("ADMIN_QUERY"))
        try:
            yield cursor
        finally:
            cursor.close()

    @cl.step(type="tool")
    async def execute_query(self, query: str) -> str:
        """Execute a SQL query and return results

        Args:
            query: SQL query to execute
        """
        display_name = (
            f"🔍 Execute Query: {query[:100]}{'...' if len(query) > 100 else ''}"
        )
        cl.Step(name=display_name, type="tool")

        query = query.encode("utf-8").decode("unicode_escape")
        try:
            with self.get_cursor() as cursor:
                results = cursor.execute(query).fetchall()
                return str(results)
        except Exception as e:
            return f"Error executing query: {str(e)}"

    @cl.step(type="tool")
    async def get_table_names(self, unused_param: str = None) -> List[str]:
        """Get list of all tables in the database"""
        display_name = "📚 List All Tables"
        cl.Step(name=display_name, type="tool")

        try:
            with self.get_cursor() as cursor:
                tables = cursor.execute("SELECT name FROM sys.tables").fetchall()
                result = [table[0] for table in tables]
                return result
        except Exception as e:
            return f"Error getting table names: {str(e)}"

    @cl.step(type="tool")
    async def get_column_info(self, table_name: str) -> List[Dict[str, str]]:
        """Get column information for a specific table

        Args:
            table_name: Name of the table to get column info for
        """
        display_name = f"🏷️ Get Columns: {table_name}"
        cl.Step(name=display_name, type="tool")

        try:
            with self.get_cursor() as cursor:
                columns = cursor.execute(
                    f"""
                    SELECT c.name, t.name as type_name
                    FROM sys.columns c
                    JOIN sys.types t ON c.system_type_id = t.system_type_id
                    WHERE object_id = OBJECT_ID('dbo.{table_name}')
                """
                ).fetchall()
                return [{"name": col[0], "type": col[1]} for col in columns]
        except Exception as e:
            return f"Error getting column info: {str(e)}"

    @cl.step(type="tool")
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get essential schema information for a specific table

        Args:
            table_name: Name of the table to inspect
        """
        display_name = f"📋 Get Schema: {table_name}"
        cl.Step(name=display_name, type="tool")

        try:
            with self.get_cursor() as cursor:
                # Get column information with types
                column_query = """
                    SELECT 
                        c.name,
                        t.name as data_type,
                        c.is_nullable,
                        c.is_identity
                    FROM sys.columns c
                    JOIN sys.types t ON c.user_type_id = t.user_type_id
                    WHERE object_id = OBJECT_ID('dbo.{table_name}')
                """.format(
                    table_name=table_name
                )

                columns = [
                    {
                        "name": row[0],
                        "type": row[1],
                        "nullable": bool(row[2]),
                        "is_identity": bool(row[3]),
                    }
                    for row in cursor.execute(column_query).fetchall()
                ]

                # Get primary key columns
                pk_query = """
                    SELECT c.name
                    FROM sys.indexes i
                    JOIN sys.index_columns ic ON i.object_id = ic.object_id
                    JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
                    WHERE i.is_primary_key = 1
                    AND i.object_id = OBJECT_ID('dbo.{table_name}')
                """.format(
                    table_name=table_name
                )

                primary_keys = [row[0] for row in cursor.execute(pk_query).fetchall()]

                # Get foreign key relationships
                fk_query = """
                    SELECT 
                        pc.name as column_name,
                        ro.name as referenced_table,
                        rc.name as referenced_column
                    FROM sys.foreign_keys fk
                    JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                    JOIN sys.columns pc ON fkc.parent_column_id = pc.column_id AND fkc.parent_object_id = pc.object_id
                    JOIN sys.columns rc ON fkc.referenced_column_id = rc.column_id AND fkc.referenced_object_id = rc.object_id
                    JOIN sys.objects ro ON fk.referenced_object_id = ro.object_id
                    WHERE fk.parent_object_id = OBJECT_ID('dbo.{table_name}')
                """.format(
                    table_name=table_name
                )

                foreign_keys = [
                    {
                        "column": row[0],
                        "references": {"table": row[1], "column": row[2]},
                    }
                    for row in cursor.execute(fk_query).fetchall()
                ]

                return {
                    "table_name": table_name,
                    "columns": columns,
                    "primary_keys": primary_keys,
                    "foreign_keys": foreign_keys,
                }
        except Exception as e:
            return f"Error getting table schema: {str(e)}"

    @cl.step(type="tool")
    async def insert_data(self, table_name: str, data: Dict[str, Any]) -> str:
        """Insert data into specified table

        Args:
            table_name: Name of the table to insert into
            data: Dictionary of column names and values to insert
        """
        display_name = f"➕ Insert Into {table_name}: {str(data)[:100]}{'...' if len(str(data)) > 100 else ''}"
        cl.Step(name=display_name, type="tool")

        try:
            with self.get_cursor() as cursor:
                columns = ", ".join(data.keys())
                values = ", ".join(["?" for _ in data])
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
                cursor.execute(query, list(data.values()))
                self.conn.commit()
                return f"Successfully inserted data into {table_name}"
        except Exception as e:
            return f"Error inserting data: {str(e)}"

    # Create wrapper functions for non-async calls
    def _execute_query(self, query: str) -> str:
        return asyncio.run(self.execute_query(query))

    def _get_table_names(self, unused_param: str = None) -> List[str]:
        return asyncio.run(self.get_table_names(unused_param))

    def _get_column_info(self, table_name: str) -> List[Dict[str, str]]:
        return asyncio.run(self.get_column_info(table_name))

    def _get_table_schema(self, table_name: str) -> Dict[str, Any]:
        return asyncio.run(self.get_table_schema(table_name))

    def _insert_data(self, table_name: str, data: Dict[str, Any]) -> str:
        return asyncio.run(self.insert_data(table_name, data))

    def create_agent(self) -> Agent:
        """Create and return a Swarm Agent with SQL capabilities"""
        return Agent(
            name="SQL Helper",
            model="gemini/gemini-2.0-flash-exp",
            instructions="""You are a helpful AI assistant with SQL database capabilities.
            You can execute queries, list tables and their columns, and insert data.
            You can inspect detailed schema information for specific tables.
            Always validate inputs before executing SQL operations.
            Provide clear feedback about database operations.
            Try to answer questions about the structure yourself by using the functions provided.
            Be careful with data modifications and confirm before making changes.""",
            functions=[
                self._execute_query,
                self._get_table_names,
                self._get_column_info,
                self._get_table_schema,
                self._insert_data,
            ],
        )

    def __enter__(self):
        """Support for context manager protocol"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when using context manager"""
        self.close()

    def close(self):
        """Explicitly close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        """Cleanup database connection"""
        self.close()

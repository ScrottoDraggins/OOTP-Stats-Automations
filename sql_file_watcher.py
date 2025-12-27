"""
SQL File Watcher
A lightweight background service that monitors a directory for new folders containing
SQL files and executes them against an Azure MySQL database.

This service uses event-based filesystem monitoring (not polling) to efficiently
detect new folders and process SQL files within them.
"""

import os
import sys
import time
import logging
import mysql.connector
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, DirCreatedEvent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SQLFileWatcher:
    """
    A class that maintains a MySQL database connection and monitors a directory
    for new folders containing SQL files to execute.
    """
    
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        watch_path: str,
        port: int = 3306,
        ssl_ca: Optional[str] = None,
        ssl_disabled: bool = False
    ):
        """
        Initialize the SQL File Watcher.
        
        Args:
            host: MySQL server hostname (Azure MySQL endpoint)
            user: Database username
            password: Database password
            database: Database name
            watch_path: Directory path to monitor for new folders
            port: MySQL port (default: 3306)
            ssl_ca: Path to SSL CA certificate (optional, for Azure MySQL)
            ssl_disabled: Whether to disable SSL (default: False)
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.watch_path = watch_path
        self.port = port
        self.ssl_ca = ssl_ca
        self.ssl_disabled = ssl_disabled
        
        self.connection: Optional[mysql.connector.MySQLConnection] = None
        self.observer: Optional[Observer] = None
        self._running = False
        
        # Validate watch path
        if not os.path.exists(watch_path):
            raise ValueError(f"Watch path does not exist: {watch_path}")
        
        logger.info(f"SQL File Watcher initialized for path: {watch_path}")
    
    def _connect_to_database(self) -> None:
        """
        Establish connection to the MySQL database.
        """
        try:
            config = {
                'host': self.host,
                'user': self.user,
                'password': self.password,
                'database': self.database,
                'port': self.port,
                'autocommit': False,
                'connection_timeout': 30
            }
            
            # Add SSL configuration for Azure MySQL if provided
            if not self.ssl_disabled:
                if self.ssl_ca:
                    config['ssl_ca'] = self.ssl_ca
                    config['ssl_verify_cert'] = True
                else:
                    # For Azure MySQL, SSL is required by default
                    config['ssl_verify_cert'] = False
            
            self.connection = mysql.connector.connect(**config)
            logger.info(f"Successfully connected to database: {self.database} at {self.host}")
            
        except mysql.connector.Error as err:
            logger.error(f"Failed to connect to database: {err}")
            raise
    
    def _ensure_connection(self) -> None:
        """
        Ensure database connection is alive, reconnect if necessary.
        """
        try:
            if self.connection is None or not self.connection.is_connected():
                logger.warning("Database connection lost, reconnecting...")
                self._connect_to_database()
        except Exception as e:
            logger.error(f"Failed to ensure database connection: {e}")
            raise
    
    def _split_sql_statements(self, sql_content: str) -> list:
        """
        Split SQL content into individual statements.
        Handles semicolons within string literals and comments.
        
        Args:
            sql_content: The SQL content to split
            
        Returns:
            List of SQL statements
        """
        statements = []
        current_statement = []
        in_single_quote = False
        in_double_quote = False
        in_backtick = False
        in_single_line_comment = False
        in_multi_line_comment = False
        
        lines = sql_content.split('\n')
        
        for line in lines:
            i = 0
            while i < len(line):
                char = line[i]
                
                # Handle single-line comments
                if not in_single_quote and not in_double_quote and not in_backtick and not in_multi_line_comment:
                    if i < len(line) - 1 and line[i:i+2] == '--':
                        in_single_line_comment = True
                        current_statement.append(line[i:])
                        break
                
                # Handle multi-line comment start
                if not in_single_quote and not in_double_quote and not in_backtick and not in_single_line_comment:
                    if i < len(line) - 1 and line[i:i+2] == '/*':
                        in_multi_line_comment = True
                        current_statement.append(char)
                        i += 1
                        current_statement.append(line[i])
                        i += 1
                        continue
                
                # Handle multi-line comment end
                if in_multi_line_comment:
                    current_statement.append(char)
                    if i < len(line) - 1 and line[i:i+2] == '*/':
                        in_multi_line_comment = False
                        i += 1
                        current_statement.append(line[i])
                    i += 1
                    continue
                
                # Skip if in single-line comment
                if in_single_line_comment:
                    current_statement.append(char)
                    i += 1
                    continue
                
                # Handle string delimiters
                if char == "'" and not in_double_quote and not in_backtick:
                    # Check for escaped quote
                    if i > 0 and line[i-1] == '\\':
                        current_statement.append(char)
                    else:
                        in_single_quote = not in_single_quote
                        current_statement.append(char)
                elif char == '"' and not in_single_quote and not in_backtick:
                    if i > 0 and line[i-1] == '\\':
                        current_statement.append(char)
                    else:
                        in_double_quote = not in_double_quote
                        current_statement.append(char)
                elif char == '`' and not in_single_quote and not in_double_quote:
                    in_backtick = not in_backtick
                    current_statement.append(char)
                # Handle semicolon (statement terminator)
                elif char == ';' and not in_single_quote and not in_double_quote and not in_backtick:
                    # End of statement
                    stmt = ''.join(current_statement).strip()
                    if stmt:
                        statements.append(stmt)
                    current_statement = []
                else:
                    current_statement.append(char)
                
                i += 1
            
            # Reset single-line comment flag at end of line
            if in_single_line_comment:
                in_single_line_comment = False
            
            # Add newline if not at end of content
            current_statement.append('\n')
        
        # Add any remaining statement
        stmt = ''.join(current_statement).strip()
        if stmt:
            statements.append(stmt)
        
        return statements
    
    def _execute_sql_file(self, sql_file_path: str) -> None:
        """
        Execute SQL commands from a file.
        
        Args:
            sql_file_path: Path to the SQL file to execute
        """
        try:
            self._ensure_connection()
            
            logger.info(f"Executing SQL file: {sql_file_path}")
            
            with open(sql_file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()
            
            # Parse SQL statements properly handling strings and comments
            statements = self._split_sql_statements(sql_content)
            
            cursor = self.connection.cursor()
            
            for i, statement in enumerate(statements, 1):
                try:
                    logger.debug(f"Executing statement {i}/{len(statements)}")
                    cursor.execute(statement)
                except mysql.connector.Error as err:
                    logger.error(f"Error executing statement {i} in {sql_file_path}: {err}")
                    logger.error(f"Statement: {statement[:100]}...")
                    self.connection.rollback()
                    raise
            
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Successfully executed {len(statements)} statements from {sql_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to execute SQL file {sql_file_path}: {e}")
            if self.connection:
                self.connection.rollback()
    
    def _process_folder(self, folder_path: str) -> None:
        """
        Process all SQL files in a folder.
        
        Args:
            folder_path: Path to the folder containing SQL files
        """
        logger.info(f"Processing folder: {folder_path}")
        
        try:
            # Wait for files to be written (OOTP creates folder before writing files)
            max_wait = 30  # Wait up to 30 seconds
            wait_interval = 2  # Check every 2 seconds
            elapsed = 0
            
            while elapsed < max_wait:
                # Find all .sql files in the folder (recursively)
                sql_files = sorted(Path(folder_path).glob('**/*.sql'))
                
                if sql_files:
                    break
                
                logger.info(f"Waiting for SQL files to appear in {folder_path}... ({elapsed}s)")
                time.sleep(wait_interval)
                elapsed += wait_interval
            
            if not sql_files:
                logger.warning(f"No SQL files found in folder after {max_wait}s: {folder_path}")
                return
            
            logger.info(f"Found {len(sql_files)} SQL file(s) in {folder_path}")
            
            for sql_file in sql_files:
                self._execute_sql_file(str(sql_file))
            
            logger.info(f"Completed processing folder: {folder_path}")
            
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {e}")
    
    def start(self) -> None:
        """
        Start the file system watcher and begin monitoring for new folders.
        """
        if self._running:
            logger.warning("Watcher is already running")
            return
        
        try:
            # Connect to database
            self._connect_to_database()
            
            # Create event handler
            event_handler = self._create_event_handler()
            
            # Create and start observer
            self.observer = Observer()
            self.observer.schedule(event_handler, self.watch_path, recursive=False)
            self.observer.start()
            
            self._running = True
            logger.info(f"Started watching directory: {self.watch_path}")
            logger.info("Press Ctrl+C to stop")
            
            # Keep the main thread alive
            try:
                while self._running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received stop signal")
                self.stop()
                
        except Exception as e:
            logger.error(f"Error starting watcher: {e}")
            self.stop()
            raise
    
    def stop(self) -> None:
        """
        Stop the file system watcher and close database connection.
        """
        logger.info("Stopping SQL File Watcher...")
        
        self._running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped filesystem observer")
        
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Closed database connection")
        
        logger.info("SQL File Watcher stopped")
    
    def _create_event_handler(self) -> FileSystemEventHandler:
        """
        Create a file system event handler for directory creation events.
        
        Returns:
            FileSystemEventHandler: Configured event handler
        """
        watcher = self
        
        class NewFolderHandler(FileSystemEventHandler):
            """Handle directory creation events."""
            
            def on_created(self, event):
                """Called when a file or directory is created."""
                if isinstance(event, DirCreatedEvent):
                    logger.info(f"New folder detected: {event.src_path}")
                    # Process the new folder
                    watcher._process_folder(event.src_path)
        
        return NewFolderHandler()


def main():
    """
    Main entry point for the SQL File Watcher service.
    Loads configuration from environment variables.
    """
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Get configuration from environment variables
    host = os.getenv('OOTP_DB_HOST')
    user = os.getenv('OOTP_DB_USER')
    password = os.getenv('OOTP_DB_PASSWORD')
    database = os.getenv('OOTP_DB_NAME')
    watch_path = os.getenv('OOTP_WATCH_PATH')
    port_str = os.getenv('OOTP_DB_PORT', '3306')
    ssl_ca = os.getenv('OOTP_DB_SSL_CA')
    ssl_disabled = os.getenv('OOTP_DB_SSL_DISABLED', 'false').lower() == 'true'
    
    # Validate required configuration
    required_vars = {
        'OOTP_DB_HOST': host,
        'OOTP_DB_USER': user,
        'OOTP_DB_PASSWORD': password,
        'OOTP_DB_NAME': database,
        'OOTP_WATCH_PATH': watch_path
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in a .env file or as environment variables")
        sys.exit(1)
    
    # Parse port with error handling
    try:
        port = int(port_str)
    except ValueError:
        logger.error(f"Invalid OOTP_DB_PORT value: '{port_str}'. Must be a valid integer.")
        sys.exit(1)
    
    # Create and start watcher
    try:
        watcher = SQLFileWatcher(
            host=host,
            user=user,
            password=password,
            database=database,
            watch_path=watch_path,
            port=port,
            ssl_ca=ssl_ca,
            ssl_disabled=ssl_disabled
        )
        watcher.start()
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

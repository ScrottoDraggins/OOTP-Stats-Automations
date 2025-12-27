# OOTP-Stats-Automations
Automates import/export of OOTP baseball game stats for PowerBI analytics

## SQL File Watcher

A lightweight background service that monitors a Windows filesystem directory for new folders containing SQL files and automatically executes them against an Azure MySQL database.

### Features

- **Event-Based Monitoring**: Uses the `watchdog` library for efficient, event-driven filesystem monitoring (no polling)
- **Single Class Design**: All functionality encapsulated in the `SQLFileWatcher` class
- **MySQL Connection Management**: Maintains persistent database connection with automatic reconnection
- **Azure MySQL Compatible**: Supports SSL/TLS connections required by Azure MySQL
- **Automatic SQL Execution**: Processes all `.sql` files in newly created folders
- **Robust Error Handling**: Comprehensive logging and error recovery
- **Transaction Support**: Uses transactions for SQL execution with automatic rollback on errors

### Requirements

- Python 3.7 or higher
- Access to an Azure MySQL database
- Windows operating system (for filesystem monitoring)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/ScrottoDraggins/OOTP-Stats-Automations.git
cd OOTP-Stats-Automations
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the template:
```bash
copy .env.example .env
```

4. Edit `.env` with your database credentials and watch path:
```
DB_HOST=your-server.mysql.database.azure.com
DB_USER=your_username@your-server
DB_PASSWORD=your_password
DB_NAME=your_database_name
DB_PORT=3306
WATCH_PATH=C:\path\to\watch\directory
```

### Usage

#### Running the Service

Run the watcher service:
```bash
python sql_file_watcher.py
```

The service will:
1. Connect to your Azure MySQL database
2. Start monitoring the specified directory
3. Wait for new folders to be created
4. When a new folder is detected, execute all `.sql` files within it (in alphabetical order)
5. Continue running until stopped with Ctrl+C

#### Using as a Module

You can also import and use the `SQLFileWatcher` class in your own Python code:

```python
from sql_file_watcher import SQLFileWatcher

# Create watcher instance
watcher = SQLFileWatcher(
    host='your-server.mysql.database.azure.com',
    user='your_username@your-server',
    password='your_password',
    database='your_database_name',
    watch_path=r'C:\path\to\watch\directory',
    port=3306
)

# Start watching (blocks until stopped)
watcher.start()

# Or in a separate thread
import threading
thread = threading.Thread(target=watcher.start)
thread.daemon = True
thread.start()

# Stop when needed
watcher.stop()
```

### SQL File Format

SQL files should contain valid MySQL statements separated by semicolons:

```sql
-- example.sql
CREATE TABLE IF NOT EXISTS players (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    team VARCHAR(50)
);

INSERT INTO players (id, name, team) VALUES
    (1, 'Player One', 'Team A'),
    (2, 'Player Two', 'Team B');
```

### How It Works

1. **Initialization**: The `SQLFileWatcher` class connects to the MySQL database and validates the watch path
2. **Monitoring**: Uses `watchdog.observers.Observer` to monitor the directory for `DirCreatedEvent` events
3. **Event Handling**: When a new folder is created, the event handler is triggered immediately (no polling delay)
4. **SQL Processing**: All `.sql` files in the new folder are discovered and executed in alphabetical order
5. **Transaction Management**: Each SQL file's statements are executed within a transaction, with rollback on error
6. **Connection Resilience**: Database connection is checked before each operation and reconnected if necessary

### Configuration Options

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `DB_HOST` | Yes | - | MySQL server hostname |
| `DB_USER` | Yes | - | Database username |
| `DB_PASSWORD` | Yes | - | Database password |
| `DB_NAME` | Yes | - | Database name |
| `DB_PORT` | No | 3306 | MySQL port |
| `WATCH_PATH` | Yes | - | Directory to monitor |
| `DB_SSL_CA` | No | - | Path to SSL CA certificate |
| `DB_SSL_DISABLED` | No | false | Disable SSL (not recommended for Azure) |

### Logging

The service uses Python's `logging` module with INFO level by default. Logs include:
- Connection status
- Folder detection events
- SQL file execution progress
- Errors and warnings

To change the logging level, modify the `logging.basicConfig()` call in `sql_file_watcher.py`.

### Running as a Windows Service

To run this as a background Windows service, you can use tools like:
- **NSSM (Non-Sucking Service Manager)**: https://nssm.cc/
- **Python win32serviceutil**: Requires `pywin32` package

Example with NSSM:
```cmd
nssm install SQLFileWatcher "C:\path\to\python.exe" "C:\path\to\sql_file_watcher.py"
nssm start SQLFileWatcher
```

### Troubleshooting

**Connection Issues:**
- Verify your database credentials and network connectivity
- For Azure MySQL, ensure firewall rules allow your IP address
- Check if SSL is required (usually yes for Azure MySQL)

**Files Not Processing:**
- Verify the `WATCH_PATH` exists and is accessible
- Check file permissions
- Review logs for error messages

**SQL Execution Errors:**
- Check SQL syntax in your files
- Verify database permissions for the user
- Review transaction rollback messages in logs

### Security Considerations

- Never commit the `.env` file with real credentials to version control
- Use strong passwords and secure connection strings
- Consider using Azure Key Vault for production credentials
- Keep the watch directory secure with appropriate Windows file permissions
- Validate SQL file sources to prevent SQL injection attacks

### License

See LICENSE file for details.

# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```

Edit `.env`:
```env
DB_HOST=your-server.mysql.database.azure.com
DB_USER=your_username@your-server
DB_PASSWORD=your_password
DB_NAME=your_database_name
WATCH_PATH=C:\path\to\watch\directory
```

### 3. Run the Service
```bash
python sql_file_watcher.py
```

## Testing

1. **Create a test folder** in your `WATCH_PATH`:
   ```
   C:\path\to\watch\directory\test_folder\
   ```

2. **Add SQL files** to the folder:
   ```
   C:\path\to\watch\directory\test_folder\01_create.sql
   C:\path\to\watch\directory\test_folder\02_insert.sql
   ```

3. **Watch the logs** - SQL files will be executed automatically!

## Usage Patterns

### As a Service
```bash
python sql_file_watcher.py
```
Runs continuously until stopped (Ctrl+C)

### As a Module
```python
from sql_file_watcher import SQLFileWatcher

watcher = SQLFileWatcher(
    host='your-server.mysql.database.azure.com',
    user='your_username',
    password='your_password',
    database='your_database',
    watch_path=r'C:\watch\path'
)
watcher.start()
```

### Examples
```bash
python example_usage.py
```
Choose from interactive examples

## Troubleshooting

### Connection Failed
- Check database credentials in `.env`
- Verify Azure firewall allows your IP
- Ensure SSL is properly configured

### Files Not Processing
- Verify `WATCH_PATH` exists
- Check file has `.sql` extension
- Review logs for errors

### SQL Errors
- Check SQL syntax
- Verify database user has proper permissions
- Review transaction rollback messages

## Need Help?

See the full [README.md](README.md) for detailed documentation.

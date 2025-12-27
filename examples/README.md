# SQL File Examples

This folder contains example SQL files demonstrating the expected format for files that will be processed by the SQL File Watcher.

## Files in this example set

1. **01_create_tables.sql** - Creates the database schema (tables)
2. **02_insert_data.sql** - Inserts sample data
3. **03_queries_updates.sql** - Updates data and creates views/indexes

## How to use these examples

### Testing the watcher

1. Set up your `.env` file with valid database credentials
2. Start the SQL File Watcher:
   ```bash
   python sql_file_watcher.py
   ```
3. Copy this entire `sql_files` folder to your `WATCH_PATH` directory
4. The watcher will detect the new folder and execute all SQL files in alphabetical order

### Important notes

- Files are executed in **alphabetical order** (hence the numbering: 01_, 02_, 03_)
- All statements in a file are executed within a single transaction
- If any statement fails, the entire file's transaction is rolled back
- Each SQL statement should end with a semicolon (`;`)
- Comments are supported using `--` for single-line comments
- Multi-line comments `/* */` are also supported

## SQL File Format

```sql
-- Single line comment
/* 
   Multi-line
   comment
*/

-- Statement 1
CREATE TABLE example (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

-- Statement 2
INSERT INTO example (id, name) VALUES (1, 'Test');

-- Statement 3
SELECT * FROM example;
```

## Best Practices

1. **Number your files**: Use prefixes like `01_`, `02_`, etc., to control execution order
2. **One purpose per file**: Separate schema creation, data loading, and updates
3. **Use transactions**: The watcher wraps each file in a transaction automatically
4. **Add comments**: Document what each file does
5. **Test locally first**: Verify your SQL files work before deploying to the watch directory
6. **Handle errors gracefully**: Consider using `IF NOT EXISTS` for CREATE statements
7. **Idempotent operations**: Design SQL to be safely re-runnable if needed

## Folder Structure Example

When you create a new folder in the watch directory, organize it like this:

```
WATCH_PATH/
└── import_2024_01_15/
    ├── 01_create_tables.sql
    ├── 02_insert_data.sql
    └── 03_queries_updates.sql
```

The watcher will:
1. Detect the new `import_2024_01_15` folder
2. Find all `.sql` files (sorted alphabetically)
3. Execute `01_create_tables.sql`
4. Execute `02_insert_data.sql`
5. Execute `03_queries_updates.sql`
6. Log results and any errors

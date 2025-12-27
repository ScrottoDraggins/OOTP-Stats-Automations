"""
Example usage of the SQL File Watcher
This demonstrates how to use the SQLFileWatcher class programmatically.
"""

from sql_file_watcher import SQLFileWatcher
import os
import time
import threading

def example_basic_usage():
    """
    Basic example showing how to start and stop the watcher.
    """
    print("=== Basic Usage Example ===")
    print("This example requires a valid .env file with database credentials")
    print()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')
    watch_path = os.getenv('WATCH_PATH')
    
    if not all([host, user, password, database, watch_path]):
        print("ERROR: Missing required environment variables")
        print("Please set up your .env file with database credentials")
        return
    
    try:
        # Create watcher
        watcher = SQLFileWatcher(
            host=host,
            user=user,
            password=password,
            database=database,
            watch_path=watch_path
        )
        
        print(f"Starting watcher on: {watch_path}")
        print("Press Ctrl+C to stop")
        print()
        
        # Start watching (blocks until stopped)
        watcher.start()
        
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()
        print("Watcher stopped successfully")
    except Exception as e:
        print(f"ERROR: {e}")


def example_threaded_usage():
    """
    Example showing how to run the watcher in a background thread.
    """
    print("=== Threaded Usage Example ===")
    print("This example requires a valid .env file with database credentials")
    print()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get configuration
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')
    watch_path = os.getenv('WATCH_PATH')
    
    if not all([host, user, password, database, watch_path]):
        print("ERROR: Missing required environment variables")
        return
    
    try:
        # Create watcher
        watcher = SQLFileWatcher(
            host=host,
            user=user,
            password=password,
            database=database,
            watch_path=watch_path
        )
        
        # Start in background thread
        watcher_thread = threading.Thread(target=watcher.start)
        watcher_thread.daemon = True
        watcher_thread.start()
        
        print(f"Watcher running in background thread...")
        print(f"Monitoring: {watch_path}")
        print("Create a new folder in the watch directory to test")
        print("Press Ctrl+C to stop")
        print()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()
        watcher_thread.join(timeout=5)
        print("Watcher stopped successfully")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == '__main__':
    import sys
    
    print("SQL File Watcher Examples")
    print("=" * 50)
    print()
    print("Choose an example:")
    print("1. Basic usage (blocking)")
    print("2. Threaded usage (non-blocking)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    print()
    
    if choice == '1':
        example_basic_usage()
    elif choice == '2':
        example_threaded_usage()
    else:
        print("Invalid choice")
        sys.exit(1)

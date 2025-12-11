from utils.search_manager import SearchManager

# This will delete and recreate the index
search_manager = SearchManager()

print("Deleting old index...")
try:
    search_manager.index_client.delete_index(search_manager.index_name)
    print("✓ Old index deleted")
except Exception as e:
    print(f"Index didn't exist or error: {e}")

print("\nCreating new index with correct configuration...")
search_manager._create_index_if_not_exists()
print("✓ New index created!")

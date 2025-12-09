from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from config import Config


class BlobManager:
    def __init__(self):
        connection_string = Config.AZURE_STORAGE_CONNECTION_STRING
        if not connection_string:
            raise ValueError(
                "Azure Storage connection string is not configured"
                )
        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )

    def create_user_container(self, username):
        """Create a container for a new user"""
        try:
            container_name = username.lower()
            self.blob_service_client.create_container(container_name)
            return True, f"Container created for {username}"
        except ResourceExistsError:
            return False, "Container already exists"
        except Exception as e:
            return False, f"Error creating container: {str(e)}"

    def upload_file(self, username, file, filename):
        """Upload a file to user's container"""
        try:
            container_name = username.lower()
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=filename
            )
            blob_client.upload_blob(file, overwrite=True)

            return True, "File uploaded successfully"
        except Exception as e:
            return False, f"Error uploading file: {str(e)}"

    def delete_file(self, username, filename):
        """Delete a file from user's container"""
        try:
            container_name = username.lower()
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=filename
            )
            blob_client.delete_blob()

            return True, "File deleted successfully"
        except ResourceNotFoundError:
            return False, "File not found"
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"

    def list_user_files(self, username):
        """List all files in a user's container"""
        try:
            container_name = username.lower()
            container_client = self.blob_service_client.\
                get_container_client(container_name)

            blobs = container_client.list_blobs()
            files = []

            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'created': blob.creation_time,
                    'container': container_name
                })

            return files
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []

    def list_all_files(self):
        """List all files from all containers"""
        try:
            all_files = []
            containers = self.blob_service_client.list_containers()

            for container in containers:
                container_client = self.blob_service_client.\
                    get_container_client(container.name)
                blobs = container_client.list_blobs()

                for blob in blobs:
                    all_files.append({
                        'name': blob.name,
                        'size': blob.size,
                        'created': blob.creation_time,
                        'container': container.name,
                        'owner': container.name
                    })

            return all_files
        except Exception as e:
            print(f"Error listing all files: {str(e)}")
            return []

    def get_download_url(self, container_name, filename):
        """Get download URL for a file"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=filename
            )
            return blob_client.url
        except Exception as e:
            print(f"Error getting download URL: {str(e)}")
            return None

    def download_file(self, container_name, filename):
        """Download file content"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=filename
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None


def create_folder(self, username, folder_name):
    """Create a virtual folder by uploading a placeholder blob"""
    try:
        container_name = self._get_container_name(username)
        # Create a placeholder file to represent the folder
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name,
            blob=f"{folder_name}/.placeholder"
        )
        blob_client.upload_blob(b"", overwrite=True)
        return True, f"Folder '{folder_name}' created"
    except Exception as e:
        return False, f"Error creating folder: {str(e)}"


def list_user_folders(self, username):
    """List all folders (unique prefixes) in a user's container"""
    try:
        container_name = self._get_container_name(username)
        container_client = self.blob_service_client.\
            get_container_client(container_name)

        blobs = container_client.list_blobs()
        folders = set()

        for blob in blobs:
            # Extract folder name (everything before first /)
            if '/' in blob.name:
                folder = blob.name.split('/')[0]
                folders.add(folder)

        return sorted(list(folders))
    except Exception as e:
        print(f"Error listing folders: {str(e)}")
        return []


def list_files_in_folder(self, username, folder_name):
    """List files in a specific folder"""
    try:
        container_name = self._get_container_name(username)
        container_client = self.blob_service_client.get_container_client(container_name)

        prefix = f"{folder_name}/"
        blobs = container_client.list_blobs(name_starts_with=prefix)
        files = []

        for blob in blobs:
            if blob.name.endswith('.placeholder'):
                continue  # Skip placeholder files

            files.append({
                'name': blob.name.replace(prefix, ''),  # Remove folder prefix
                'full_path': blob.name,
                'size': blob.size,
                'created': blob.creation_time,
                'container': container_name,
                'folder': folder_name
            })

        return files
    except Exception as e:
        print(f"Error listing files in folder: {str(e)}")
        return []


def upload_file_to_folder(self, username, file, filename, folder_name):
    """Upload a file to a specific folder"""
    try:
        container_name = self._get_container_name(username)
        blob_path = f"{folder_name}/{filename}"
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_path
        )
        blob_client.upload_blob(file, overwrite=True)

        return True, "File uploaded successfully"
    except Exception as e:
        return False, f"Error uploading file: {str(e)}"


def delete_file_from_folder(self, username, folder_name, filename):
    """Delete a file from a specific folder"""
    try:
        container_name = self._get_container_name(username)
        blob_path = f"{folder_name}/{filename}"
        blob_client = self.blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_path
        )
        blob_client.delete_blob()

        return True, "File deleted successfully"
    except ResourceNotFoundError:
        return False, "File not found"
    except Exception as e:
        return False, f"Error deleting file: {str(e)}"
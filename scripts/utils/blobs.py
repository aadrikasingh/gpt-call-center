import json
import logging
import os
import urllib
from datetime import datetime, timedelta

from azure.identity import AzureDeveloperCliCredential
from azure.storage.blob import (BlobSasPermissions, BlobServiceClient,
                                generate_blob_sas)

# Use the current user identity to connect to Azure services unless a key is explicitly set for any of them
credential = AzureDeveloperCliCredential()


def upload_audio_file_to_container(audio_file_path: str, storage_account_name: str, container_name: str) -> None:
    """
    Uploads a file to an Azure Blob Storage container.

    Args:
        audio_file_path (str): Path to audio file to be uploaded.
        storage_account_name (str): Name of Azure Blob Storage account.
        container_name (str): Name of Azure Blob Storage container.
    """
    
    # Create connection to Azure Blob Storage account and container 
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)
    blob_container_client = blob_service_client.get_container_client(container_name)

    if not blob_container_client.exists():
        blob_container_client.create_container()

    # Upload file to container 
    blob_name = os.path.basename(audio_file_path)
    
    with open(audio_file_path,"rb") as data:
        blob_container_client.upload_blob(blob_name, data, overwrite=True)


def upload_json_to_container(blob_name: str, json_data: dict, storage_account_name: str, container_name: str) -> None:
    """
    Uploads a JSON-formatted string as a file to an Azure Blob Storage container.

    Args:
        blob_name (str): Name of output file.
        json_data (dict): Dictionary containing data to be saved in output file.
        storage_account_name (str): Name of Azure Blob Storage account.
        container_name (str): Name of Azure Blob Storage container.
    """
    
    # Create connection to Azure Blob Storage account and container 
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)
    blob_container_client = blob_service_client.get_container_client(container_name)

    if not blob_container_client.exists():
        blob_container_client.create_container()
    
    blob_container_client.upload_blob(blob_name, json_data, overwrite=True)

def get_filename_from_blob_url(blob_url: str) -> str:
   try:
       return urllib.parse.unquote(os.path.basename(blob_url.split('?')[0]))
   except Exception as e:
       logging.error(f"Error getting filename from URL {blob_url}: {e}")
       return 'default_file'


def create_sas_token_for_audio(storage_account_name: str, container_name: str, audio_file_path: str) -> str:
   """
   Creates a SAS URL for an audio file stored in an Azure Blob Storage container.

   Args:
       storage_account (str): Name of Azure Blob Storage account.
       container (str): Name of Azure Blob Storage container where audio file is stored.
       audio_file_path (str): Path to audio file.

   Returns:
       str: SAS URL for the specified audio file. 
   """

   # Create connection to Azure Blob Storage account and get URL for specified audio file 
   service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)
   
   audio_filename = get_filename_from_blob_url(audio_file_path)
   
   blob_client = service_client.get_blob_client(container=container_name, blob=audio_filename)
   
   sas_expiry_time = datetime.utcnow() + timedelta(hours=730)  # set the expiry time for the SAS token
  
   permissions = BlobSasPermissions(read=True)

   # Get user delegation key and generate SAS token for the specified audio file 
   delegation_key = service_client.get_user_delegation_key(datetime.utcnow()
                                                           , datetime.utcnow() + timedelta(hours=1))
  
    
   # generate the SAS token   
   sas_token = generate_blob_sas(permission = permissions
      , expiry = sas_expiry_time
      , account_name = storage_account_name
      , container_name = container_name
      , blob_name = audio_filename
      , user_delegation_key = delegation_key
      , resource_types = "object"
      , protocol = "https"
      , version = "2020-02-10"
      , snapshot = None
      , cache_control = None
      , content_disposition = None
      , content_encoding = None
      , content_language = None
      , content_type = None
   )

   sas_url = f"{blob_client.url}?{sas_token}"

   return sas_url
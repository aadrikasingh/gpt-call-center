from json import dumps
import glob
import os

from utils import speech, blobs


def process_files(audio_files, storage_account_name, source_container_name, target_container_name):
    """
    Process audio files in the specified directory.
    Uploads each file to Azure Blob Storage and transcribes it using Azure Speech Services.
    Saves the transcription as a JSON file in another Azure Blob Storage container.

    Args:
        audio_files (str): Path to directory containing audio files to be processed.
        storage_account_name (str): Name of Azure Blob Storage account.
        source_container_name (str): Name of Azure Blob Storage container for input files.
        target_container_name (str): Name of Azure Blob Storage container for output files.
    """
    
    # Set up reusable variables for speech-related values
    speech_endpoint = os.environ.get("AZURE_SPEECH_ENDPOINT") #"eastus.api.cognitive.microsoft.com"
    speech_subscription_key = os.environ.get("AZURE_SPEECH_KEY") #"b72f533b22da4aa78a927d1dd4d81497"
    locale = "en-US"
    
    for audio_file_path in glob.glob(audio_files):
        print(f"Processing '{audio_file_path}'")
        
        # Upload audio file to Azure Blob Storage        
        blobs.upload_audio_file_to_container(audio_file_path = audio_file_path
                                            , storage_account_name = storage_account_name
                                            , container_name = source_container_name)

        # Get SAS URL for uploaded audio file
        input_audio_url = blobs.create_sas_token_for_audio(storage_account_name = storage_account_name
                                                            , container_name = source_container_name
                                                            , audio_file_path = audio_file_path)

        # Create transcription job using Azure Speech Services
        transcription_id = speech.create_transcription(speech_endpoint = speech_endpoint
                                                        , speech_subscription_key = speech_subscription_key
                                                        , input_audio_url = input_audio_url
                                                        , use_stereo_audio = None
                                                        , locale = locale)
        print(f"Transcription ID: {transcription_id}")

        # Wait for transcription job to complete
        speech.wait_for_transcription(transcription_id = transcription_id
                                      , speech_endpoint = speech_endpoint
                                      , speech_subscription_key = speech_subscription_key)

        # Get URLs for transcription results from Azure Speech Services
        transcription_files = speech.get_transcription_files(transcription_id = transcription_id
                                                            , speech_endpoint = speech_endpoint
                                                            , speech_subscription_key = speech_subscription_key)

        # Get URL for JSON-formatted transcription result from Azure Speech Services
        transcription_url = speech.get_transcription_url(transcription_files = transcription_files)
        
        print(f"Transcription URI: {transcription_url}")

        # Download and parse JSON-formatted transcription result from Azure Blob Storage
        transcription = speech.get_transcription(transcription_url = transcription_url)
        
        # Extract conversation items from parsed transcript 
        phrases = speech.get_transcription_phrases(transcription = transcription)
        
        conversation_items = speech.transcription_phrases_to_conversation_items(phrases)

        # Save conversation items as a JSON file in another Azure Blob Storage container
        blob_name = f"{os.path.basename(audio_file_path)}.json"
        json_data = dumps(conversation_items)

        conversation = ""

        for conversation_item in conversation_items:
            conversation += f"{conversation_item['role']}: {conversation_item['display']} \n"

        json_data_final = {
            "source": transcription["source"]
            , "transcription_id": transcription_id
            , "transcription_url": transcription_url
            , "conversationDuration": transcription["duration"]
            , "conversation": conversation
            , "phrases": json_data   
        }    

        blobs.upload_json_to_container(blob_name = blob_name
                                       , json_data = dumps(json_data_final)
                                       , storage_account_name = storage_account_name
                                       , container_name = target_container_name)

if __name__ == "__main__":
     storage_account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME") #"saccgpt0001"
     source_container_name = "landing"
     target_container_name = "transcription"
     audio_files = "../data/*"

     print(f"Processing files...")
    
     # Call function to process audio files 
     process_files(audio_files = audio_files
                   , storage_account_name = storage_account_name
                   , source_container_name = source_container_name
                   , target_container_name = target_container_name)
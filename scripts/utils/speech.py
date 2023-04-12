from datetime import datetime
from http import HTTPStatus
from json import dumps, loads
import time
import uuid
from utils import rest_helper
from typing import Dict, List, Tuple, Any
import requests


# This should not change unless you switch to a new version of the Speech REST API.
speech_transcription_path = "/speechtotext/v3.0/transcriptions"

# How long to wait while polling batch transcription and conversation analysis status.
WAIT_SECONDS = 10

class TranscriptionPhrase:
    """A class representing a phrase in a transcription."""
    def __init__(
        self, id_: int, display: str, speaker_number: int, offset: str, offset_in_ticks: float, duration: str
    ) -> None:
        """
        Initialize a TranscriptionPhrase instance.

        Args:
            id_ (int): The ID of the phrase.
            display (str): The transcribed text.
            speaker_number (int): The number of the speaker.
            offset (str): The time offset of the phrase.
            offset_in_ticks (float): The time offset of the phrase in ticks.
            duration (str): The phrase time.
        """
        self.id = id_
        self.display = display
        self.speaker_number = speaker_number
        self.offset = offset
        self.offset_in_ticks = offset_in_ticks
        self.duration = duration

def create_transcription(speech_endpoint: str, speech_subscription_key: str, input_audio_url: str,
                         use_stereo_audio: bool, locale: str) -> str:
    """
    Creates a transcription for the given audio file using the Azure Speech to Text API.

    Args:
        speech_endpoint (str): The endpoint of the Speech to Text API.
        speech_subscription_key (str): The subscription key for the Speech to Text API.
        input_audio_url (str): The URL of the audio file to transcribe.
        use_stereo_audio (bool): Indicates whether the audio file is stereo or not.
        locale (str): The locale of the audio file.

    Returns:
        str: The ID of the created transcription.

    Raises:
        Exception: If the response from the Speech to Text API is not valid.
    """
    
    # Construct the URI for the API call.
    uri = f"https://{speech_endpoint}{speech_transcription_path}"

    # Construct the request body.
    content = {
        "contentUrls": [input_audio_url],
        "properties": {
            "diarizationEnabled": not use_stereo_audio,
            "timeToLive": "PT30M"
        },
        "locale": locale,
        "displayName": f"call_center_{datetime.now()}"
    }

    # Call the API to create the transcription.
    response = rest_helper.send_post(
        uri=uri,
        content=content,
        key=speech_subscription_key,
        expected_status_codes=[HTTPStatus.CREATED]
    )

    # Parse the response to get the transcription ID.
    transcription_uri = response["json"]["self"]
    transcription_id = transcription_uri.split("/")[-1]

    # Verify that the transcription ID is a valid GUID.
    try:
        uuid.UUID(transcription_id)
        return transcription_id
    except ValueError:
        raise Exception(f"Unable to parse response from Create Transcription API:\n{response['text']}")

def get_transcription_status(transcription_id: str, speech_endpoint: str, speech_subscription_key: str) -> bool:
    """
    Get transcription status for a given transcription ID using the provided endpoint and subscription key.

    :param transcription_id: str: ID of the transcription to check status for
    :param speech_endpoint: str: endpoint to use for the Speech to Text API
    :param speech_subscription_key: str: subscription key for the Speech to Text API
    :return: bool: True if the transcription succeeded, False otherwise
    :raises: Exception if the transcription failed
    """
    uri = f"https://{speech_endpoint}{speech_transcription_path}/{transcription_id}"
    headers = {"Ocp-Apim-Subscription-Key": speech_subscription_key}
    response = requests.get(uri, headers=headers)

    if response.status_code == requests.codes.ok:
        status = response.json()["status"]
        if status.lower() == "succeeded":
            return True
        elif status.lower() == "failed":
            raise Exception(f"Unable to transcribe audio input. Response:\n{response.text}")
    else:
        response.raise_for_status()

def wait_for_transcription(transcription_id: str, speech_endpoint: str, speech_subscription_key: str, wait_seconds: int = 15) -> None:
    """
    Wait for a given transcription to complete using the provided endpoint and subscription key.

    :param transcription_id: str: ID of the transcription to wait for
    :param speech_endpoint: str: endpoint to use for the Speech to Text API
    :param speech_subscription_key: str: subscription key for the Speech to Text API
    :param wait_seconds: int: number of seconds to wait between checks, default is 15
    """
    done = False
    while not done:
        print(f"Waiting {wait_seconds} seconds for transcription to complete.")
        time.sleep(wait_seconds)
        done = get_transcription_status(transcription_id, speech_endpoint, speech_subscription_key)

def get_transcription_files(transcription_id: str, speech_endpoint: str, speech_subscription_key: str) -> Dict:
    """
    Get transcription files for a given transcription ID using the provided endpoint and subscription key.

    :param transcription_id: str: ID of the transcription to get files for
    :param speech_endpoint: str: endpoint to use for the Speech to Text API
    :param speech_subscription_key: str: subscription key for the Speech to Text API
    :return: Dict: the transcription files response JSON
    """
    uri = f"https://{speech_endpoint}{speech_transcription_path}/{transcription_id}/files"
    headers = {"Ocp-Apim-Subscription-Key": speech_subscription_key}
    response = requests.get(uri, headers=headers)

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()

def get_transcription_url(transcription_files: dict) -> str:
    """
    Get the transcription URL from the JSON response of the GetTranscriptionFiles API.
    Raises an exception if the API response is unable to be parsed.

    Args:
        transcription_files (dict): The JSON response from the GetTranscriptionFiles API.

    Returns:
        str: The transcription URL from the API response.
    """
    # Filter the transcription files by 'kind' and retrieve the first match
    value = next((value for value in transcription_files['values'] if value.get('kind', '').lower() == 'transcription'), None)

    # Raise an exception if no matching value is found
    if value is None:
        raise Exception(f"Unable to parse response from Get Transcription Files API:\n{transcription_files['text']}")

    # Return the transcription URI
    return value['links']['contentUrl']


def get_transcription(transcription_url: str) -> Dict:
    """
    Get transcription data from a given URL.

    :param transcription_url: str: URL to get the transcription data from
    :return: Dict: the transcription response JSON
    """
    response = requests.get(transcription_url)

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        response.raise_for_status()

def get_transcription_phrases(transcription: Dict[str, Any]) -> List[TranscriptionPhrase]:
    """
    Extracts transcription phrases from a given transcription.

    Args:
        transcription: A dictionary containing recognized phrases.
        user_config: A dictionary containing user configurations.

    Returns:
        A list of TranscriptionPhrase objects.
    """
    def helper(id_and_phrase: Tuple[int, Dict[str, Any]]) -> TranscriptionPhrase:
        """
        Helper function to extract a TranscriptionPhrase from a recognized phrase.

        Args:
            id_and_phrase: A tuple containing the id and the recognized phrase.

        Returns:
            A TranscriptionPhrase object.
        """
        id, phrase = id_and_phrase
        best = phrase["nBest"][0]
        speaker_number: int
        if "speaker" in phrase:
            speaker_number = phrase["speaker"] - 1
        elif "channel" in phrase:
            speaker_number = phrase["channel"]
        else:
            raise Exception(f"nBest item contains neither channel nor speaker attribute.\n{best}")
        return TranscriptionPhrase(id, best["display"], speaker_number, phrase["offset"], phrase["offsetInTicks"], phrase["duration"])

    phrases = transcription["recognizedPhrases"]
    phrases.sort(key=lambda x: x.get("channel", x.get("speaker", 0)))  # Sort phrases by speaker/channel number.
    return [helper((i, phrase)) for i, phrase in enumerate(phrases)]

def transcription_phrases_to_conversation_items(phrases: List[TranscriptionPhrase]) -> List[Dict[str, Any]]:
    """
    Converts TranscriptionPhrase objects to conversation items.

    Args:
        phrases: A list of TranscriptionPhrase objects.

    Returns:
        A list of conversation items.
    """
    return [{
        "id": phrase.id,
        "display": phrase.display,
        "role": "Agent" if phrase.speaker_number == 0 else "Customer",  # The first person to speak is probably the agent.
        "participantId": phrase.speaker_number,
        "duration": phrase.duration        
    } for phrase in phrases]
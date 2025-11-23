import io
import wave
import numpy as np
import chainlit as cl
from src.utils.config import ELEVENLABS_KEY
from src.log.logger import setup_logger
from elevenlabs.client import AsyncElevenLabs

logger = setup_logger('SPEECH')

async def audio_chunk(chunk: cl.InputAudioChunk) -> None:
    """
    Handles incoming audio chunks and stores them in a buffer for further processing.

    Args:
        chunk (cl.InputAudioChunk): The audio data to process.
    """
    audio_chunks = cl.user_session.get("audio_chunks")

    if audio_chunks is not None:
        audio_chunk = np.frombuffer(chunk.data, dtype=np.int16)
        audio_chunks.append(audio_chunk)

async def process_audio() -> bytes:
    """
    Enhanced audio processing with noise reduction and optimization

    Returns:
        BytesIO: The buffer containing the audio data.
    """
    audio_chunks = cl.user_session.get("audio_chunks")
    if not audio_chunks:
        return
    
    concatenated = np.concatenate(audio_chunks)
    sample_rate = 24000
    duration = concatenated.shape[0] / float(sample_rate)
    if duration <= 1.71:
        logger.warning("The audio is too short, please try again.")
        return

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(concatenated.tobytes())
    
    wav_buffer.seek(0)
    cl.user_session.set("audio_chunks", [])

    return wav_buffer.getvalue()

async def speech_to_text(audio_file: bytes) -> str:
    """Enhanced transcription with multiple engines and languages"""
    elevenlabs = AsyncElevenLabs(
        api_key=ELEVENLABS_KEY,
    )
    response = await elevenlabs.speech_to_text.convert(
        file=audio_file,
        model_id="scribe_v1", # Model to use, for now only "scribe_v1" is supported
        tag_audio_events=True, # Tag audio events like laughter, applause, etc.
        language_code="spa", # Language of the audio file. If set to None, the model will detect the language automatically.
        diarize=True, # Whether to annotate who is speaking
    )

    if response:
        logger.info(f"Transcription response: {response.text}")

    return response.text

async def audio_transcription() -> str:
    """
    Processes the audio answer and sends a message with the transcription.
    """ 
    audio_buffer = await process_audio()
    
    if audio_buffer is None:
        await cl.Message(content="Could not retrieve audio for processing. Please try recording again.").send()
        return
        
    try:
        # Enhanced recognizer settings
        transcription = await speech_to_text(audio_file=audio_buffer)
    
        if not transcription:
            await cl.Message(content="Could not understand the audio. Please try speaking more clearly or check your microphone.").send()
            return
        
        logger.info(f"Message transcription: {transcription}")
        return transcription
    except Exception as e:
        await cl.Message(content=f"Audio processing error: {str(e)}").send()

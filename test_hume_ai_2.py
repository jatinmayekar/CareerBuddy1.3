# link: https://dev.hume.ai/docs/expression-measurement/websocket

import asyncio
import pyaudio
import wave
import os
import time
from hume import HumeStreamClient
from hume.models.config import ProsodyConfig
import numpy as np

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MIN_RECORD_SECONDS = 1
CHUNK_DURATION = 5  # Duration of each chunk in seconds
WAVE_OUTPUT_FILENAME = "user_input.wav"

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"Recording started. Press Enter to stop (minimum duration: {MIN_RECORD_SECONDS} seconds).")
    
    frames = []
    start_time = time.time()
    
    while True:
        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':
                elapsed_time = time.time() - start_time
                if elapsed_time >= MIN_RECORD_SECONDS:
                    break
                else:
                    print(f"Please record for at least {MIN_RECORD_SECONDS} seconds. Current duration: {elapsed_time:.1f} seconds.")
        
        data = stream.read(CHUNK)
        frames.append(data)
        elapsed_time = time.time() - start_time
        print(f"\rRecording: {elapsed_time:.1f} seconds {'🎙️' if int(elapsed_time) % 2 == 0 else '   '}", end="", flush=True)

    print("\nRecording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Audio saved as {WAVE_OUTPUT_FILENAME}")
    return elapsed_time

def split_audio(filename, chunk_duration):
    with wave.open(filename, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        
        chunk_size = int(chunk_duration * framerate)
        n_chunks = (n_frames + chunk_size - 1) // chunk_size  # Round up division
        
        chunks = []
        for i in range(n_chunks):
            chunk_filename = f"chunk_{i}.wav"
            with wave.open(chunk_filename, 'wb') as chunk_wf:
                chunk_wf.setnchannels(n_channels)
                chunk_wf.setsampwidth(sampwidth)
                chunk_wf.setframerate(framerate)
                
                start = i * chunk_size
                end = min((i + 1) * chunk_size, n_frames)
                wf.setpos(start)
                chunk_wf.writeframes(wf.readframes(end - start))
            
            chunks.append(chunk_filename)
    
    return chunks

async def process_audio_chunk(client, config, filename):
    try:
        async with client.connect([config]) as socket:
            result = await socket.send_file(filename)
            
            if 'prosody' in result and 'predictions' in result['prosody']:
                return result["prosody"]["predictions"][0]["emotions"]
            else:
                print(f"Unexpected API response format for {filename}")
                print(f"API Response: {result}")
                return None
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return None

async def process_all_chunks(chunks):
    client = HumeStreamClient(os.getenv("HUME_AI_API_KEY"))
    config = ProsodyConfig()
    
    tasks = [process_audio_chunk(client, config, chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    
    return [r for r in results if r is not None]

def aggregate_results(results):
    if not results:
        print("No valid results to aggregate.")
        return

    all_emotions = {}
    for chunk_result in results:
        for emotion in chunk_result:
            name = emotion['name']
            score = emotion['score']
            if name in all_emotions:
                all_emotions[name].append(score)
            else:
                all_emotions[name] = [score]
    
    avg_emotions = {name: np.mean(scores) for name, scores in all_emotions.items()}
    sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 Average Emotional Characteristics:")
    for name, score in sorted_emotions[:5]:
        print(f"{name}: {score:.4f}")

async def main():
    total_duration = record_audio()
    print(f"Total recording duration: {total_duration:.1f} seconds")
    
    chunks = split_audio(WAVE_OUTPUT_FILENAME, CHUNK_DURATION)
    print(f"Audio split into {len(chunks)} chunks")
    
    results = await process_all_chunks(chunks)
    print(f"Processed {len(results)} chunks successfully")
    
    aggregate_results(results)
    
    # Clean up
    os.remove(WAVE_OUTPUT_FILENAME)
    for chunk in chunks:
        os.remove(chunk)

if __name__ == "__main__":
    import msvcrt  # For Windows key input
    asyncio.run(main())
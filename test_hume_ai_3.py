import asyncio
import pyaudio
import wave
import os
import time
import cv2
from hume import HumeStreamClient
from hume.models.config import ProsodyConfig, FaceConfig
import numpy as np
import msvcrt

# Audio recording parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MIN_RECORD_SECONDS = 1
CHUNK_DURATION = 5  # Duration of each chunk in seconds
WAVE_OUTPUT_FILENAME = "user_input.wav"
VIDEO_OUTPUT_FILENAME = "user_video.mp4"

def record_audio_and_video():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"Recording started. Press Enter to stop (minimum duration: {MIN_RECORD_SECONDS} seconds).")
    
    audio_frames = []
    video_frames = []
    start_time = time.time()
    
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(VIDEO_OUTPUT_FILENAME, fourcc, 20.0, (640, 480))
    
    while True:
        if msvcrt.kbhit():
            if msvcrt.getch() == b'\r':
                elapsed_time = time.time() - start_time
                if elapsed_time >= MIN_RECORD_SECONDS:
                    break
                else:
                    print(f"Please record for at least {MIN_RECORD_SECONDS} seconds. Current duration: {elapsed_time:.1f} seconds.")
        
        # Audio recording
        audio_data = stream.read(CHUNK)
        audio_frames.append(audio_data)
        
        # Video recording
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            video_frames.append(frame)
        
        elapsed_time = time.time() - start_time
        print(f"\rRecording: {elapsed_time:.1f} seconds {'🎙️' if int(elapsed_time) % 2 == 0 else '   '}", end="", flush=True)

    print("\nRecording stopped.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    cap.release()
    out.release()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(audio_frames))
    wf.close()
    print(f"Audio saved as {WAVE_OUTPUT_FILENAME}")
    print(f"Video saved as {VIDEO_OUTPUT_FILENAME}")
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

async def process_video(client, config, filename):
    try:
        async with client.connect([config]) as socket:
            result = await socket.send_file(filename)
            
            if 'face' in result and 'predictions' in result['face']:
                return result["face"]["predictions"]
            else:
                print(f"Unexpected API response format for video {filename}")
                print(f"API Response: {result}")
                return None
    except Exception as e:
        print(f"Error processing video {filename}: {str(e)}")
        return None

async def process_all_data(audio_chunks, video_filename):
    client = HumeStreamClient(os.getenv("HUME_AI_API_KEY"))
    audio_config = ProsodyConfig()
    face_config = FaceConfig()
    
    audio_tasks = [process_audio_chunk(client, audio_config, chunk) for chunk in audio_chunks]
    video_task = process_video(client, face_config, video_filename)
    
    results = await asyncio.gather(*audio_tasks, video_task)
    
    audio_results = [r for r in results[:-1] if r is not None]
    video_result = results[-1]
    
    return audio_results, video_result

def aggregate_audio_results(results):
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

def aggregate_video_results(results):
    if not results:
        print("No valid video results to aggregate.")
        return

    all_emotions = {}
    for frame in results:
        if 'emotions' in frame:
            for emotion in frame['emotions']:
                name = emotion['name']
                score = emotion['score']
                if name in all_emotions:
                    all_emotions[name].append(score)
                else:
                    all_emotions[name] = [score]
    
    avg_emotions = {name: np.mean(scores) for name, scores in all_emotions.items()}
    sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop 5 Average Facial Emotional Characteristics:")
    for name, score in sorted_emotions[:5]:
        print(f"{name}: {score:.4f}")

async def main():
    total_duration = record_audio_and_video()
    print(f"Total recording duration: {total_duration:.1f} seconds")
    
    audio_chunks = split_audio(WAVE_OUTPUT_FILENAME, CHUNK_DURATION)
    print(f"Audio split into {len(audio_chunks)} chunks")
    
    audio_results, video_results = await process_all_data(audio_chunks, VIDEO_OUTPUT_FILENAME)
    print(f"Processed {len(audio_results)} audio chunks successfully")
    
    aggregate_audio_results(audio_results)
    aggregate_video_results(video_results)
    
    # Clean up
    os.remove(WAVE_OUTPUT_FILENAME)
    os.remove(VIDEO_OUTPUT_FILENAME)
    for chunk in audio_chunks:
        os.remove(chunk)

if __name__ == "__main__":
    asyncio.run(main())
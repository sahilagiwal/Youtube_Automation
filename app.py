import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import spacy
import requests

from moviepy.editor import ImageSequenceClip, AudioFileClip, VideoFileClip

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise Exception("API key not found. Please set OPENAI_API_KEY in your environment variables.")
client = OpenAI(api_key=api_key)

# Load Spacy Model for Keyword Extraction
nlp = spacy.load("en_core_web_sm")

def generate_script(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_keywords(text, max_keywords=2):
    doc = nlp(text)
    # Extract nouns and proper nouns as potential keywords, limited to max_keywords
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    return keywords[:max_keywords]  # Return only the first 'max_keywords' items

def generate_audio_from_text(text, output_file_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text
    )
    with open(output_file_path, "wb") as file:
        file.write(response.content)

def download_image(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

def generate_images(prompts):
    # directory_path = 'path/to/your/directory'
    # create_directory_if_not_exists(directory_path)
    image_paths = []
    # os.mkdir('temp/images/')
    for i, prompt in enumerate(prompts):
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
       
        image_path = f"image_{i}.png"
        download_image(image_url, image_path)
        image_paths.append(image_path)
    return image_paths
def create_video(image_paths, audio_path, output_video_path):
    # Convert Path objects to strings for compatibility with moviepy
    audio_clip = AudioFileClip(str(audio_path))
    if len(image_paths) > 0:
        image_display_duration = audio_clip.duration / len(image_paths)
    else:
        image_display_duration = 2  # default to 2 seconds per image if no images are available

    clip = ImageSequenceClip([str(path) for path in image_paths], fps=1/image_display_duration)
    final_clip = clip.set_audio(audio_clip)
    final_clip.write_videofile(str(output_video_path), codec='libx264', audio_codec='aac')


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' was created.")
    else:
        print(f"Directory '{directory_path}' already exists.")


# def crop_video(input_file, output_file, width, height):
#     # Load the video clip
#     video = VideoFileClip(input_file)
    
#     # Calculate center coordinates (assuming you want to center the crop)
#     x_center = video.w / 2
#     y_center = video.h / 2

#     # Crop the video
#     cropped_video = video.crop(x_center=x_center, y_center=y_center, width=width, height=height)
    
#     # Write the cropped video to a file
#     cropped_video.write_videofile(output_file, codec='libx264')
def main():
    script = generate_script("Write a trading motivational message 130 words")
    print("Generated Script:", script)
    
    # Define the path for the output audio file
    speech_file_path = Path(__file__).parent / "speech.mp3"
    generate_audio_from_text(script, speech_file_path)
    print(f"Audio content successfully written to {speech_file_path}")
    
    keywords = extract_keywords(script)
    image_paths = generate_images(keywords)
    print("Generated Images saved at:", image_paths)
    
    # Create a video from images and audio
    video_path = Path(__file__).parent / "output_video.mp4"
    create_video(image_paths, speech_file_path, video_path)
    print(f"Video successfully created at {video_path}")

if __name__ == "__main__":
    main()

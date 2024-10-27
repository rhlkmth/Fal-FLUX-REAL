# app.py
import streamlit as st
import fal_client
import os
from PIL import Image
import requests
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Flux Realism Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Initialize session state for API key
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

# Title and description
st.title("🎨 Flux Realism Image Generator")
st.markdown("Generate realistic images using Flux Realism model")

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            status_placeholder.markdown(f"🔄 {log['message']}")

def generate_image(prompt, image_size, num_steps, guidance_scale, strength, api_key):
    # Temporarily set the API key for this request
    os.environ['FAL_KEY'] = api_key
    
    result = fal_client.subscribe(
        "fal-ai/flux-realism",
        arguments={
            "prompt": prompt,
            "image_size": image_size,
            "num_inference_steps": num_steps,
            "guidance_scale": guidance_scale,
            "num_images": 1,
            "enable_safety_checker": False,
            "strength": strength,
            "output_format": "jpeg"
        },
        with_logs=True,
        on_queue_update=on_queue_update,
    )
    return result

def display_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    st.image(img, use_column_width=True)

# API Key input in sidebar
with st.sidebar:
    st.header("API Configuration")
    api_key = st.text_input(
        "Enter your FAL API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your FAL API key. Get one at fal.ai"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        st.success("API Key set! ✅")
    
    st.markdown("---")
    
    st.header("Generation Settings")
    
    image_size = st.selectbox(
        "Image Size",
        ["landscape_4_3", "landscape_16_9", "portrait_4_3", "portrait_16_9", "square", "square_hd"],
        index=0
    )
    
    num_steps = st.slider(
        "Number of Steps",
        min_value=20,
        max_value=50,
        value=28,
        help="More steps = better quality but slower generation"
    )
    
    guidance_scale = st.slider(
        "Guidance Scale",
        min_value=1.0,
        max_value=20.0,
        value=3.5,
        step=0.5,
        help="How closely to follow the prompt"
    )
    
    strength = st.slider(
        "Strength",
        min_value=0.0,
        max_value=1.0,
        value=1.0,
        step=0.1,
        help="The strength of the model's effect"
    )
    
    st.markdown("---")
    st.markdown("### Tips for better results:")
    st.markdown("""
    - Be very detailed in describing the scene
    - Include specific details about facial features and expressions
    - Describe clothing and accessories clearly
    - Mention lighting and background elements
    - Specify any particular styles or moods
    """)
    
    # Add a "Clear API Key" button
    if st.button("Clear API Key"):
        st.session_state.api_key = ""
        st.rerun()

# Main content area
prompt = st.text_area(
    "Enter your prompt",
    height=150,
    placeholder="""Example: A charismatic speaker is captured mid-speech. He has long, slightly wavy blonde hair tied back in a ponytail. His expressive face, adorned with a salt-and-pepper beard and mustache..."""
)

# Create columns for control buttons
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    generate_button = st.button("🎨 Generate Image", disabled=not st.session_state.api_key)
with col2:
    if st.button("📋 Load Example Prompt"):
        st.session_state.example_prompt = """A charismatic speaker is captured mid-speech. He has long, slightly wavy blonde hair tied back in a ponytail. His expressive face, adorned with a salt-and-pepper beard and mustache, is animated as he gestures with his left hand, displaying a large ring on his pinky finger. He is holding a black microphone in his right hand, speaking passionately. The man is wearing a dark, textured shirt with unique, slightly shimmering patterns, and a green lanyard with multiple badges and logos hanging around his neck. The lanyard features the "Autodesk" and "V-Ray" logos prominently. Behind him, there is a blurred background with a white banner containing logos and text, indicating a professional or conference setting. The overall scene is vibrant and dynamic, capturing the energy of a live presentation."""
        st.rerun()

# Show API key requirement if not set
if not st.session_state.api_key:
    st.warning("⚠️ Please enter your FAL API key in the sidebar to generate images")

# Create a placeholder for status messages
status_placeholder = st.empty()

# Create a placeholder for the image
image_placeholder = st.empty()

if generate_button and prompt and st.session_state.api_key:
    try:
        status_placeholder.markdown("🚀 Starting generation...")
        result = generate_image(prompt, image_size, num_steps, guidance_scale, strength, st.session_state.api_key)
        
        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0]["url"]
            status_placeholder.markdown("✨ Generation complete!")
            display_image(image_url)
            
            # Create columns for download button and share button
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"[Download Image]({image_url})")
            
            # Show generation parameters
            with st.expander("Generation Details"):
                st.json({
                    "image_size": image_size,
                    "steps": num_steps,
                    "guidance_scale": guidance_scale,
                    "strength": strength,
                    "prompt": prompt
                })
        else:
            st.error("No image was generated. Please try again.")
            
    except Exception as e:
        st.error(f"Error generating image: {e}")
        if "unauthorized" in str(e).lower():
            st.error("Invalid API key. Please check your API key and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Get your API key at <a href='https://fal.ai' target='_blank'>fal.ai</a></p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Gabor Orientation Game",
    page_icon="👁️",
    layout="centered"
)

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_orientation' not in st.session_state:
    st.session_state.current_orientation = None
if 'current_cpd' not in st.session_state:
    st.session_state.current_cpd = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'feedback_color' not in st.session_state:
    st.session_state.feedback_color = "blue"
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = False

# Game parameters
CPD_OPTIONS = [3, 6, 12, 18]
ORIENTATION_OPTIONS = [0, 45, 90]
ORIENTATION_NAMES = {0: "Horizontal (→)", 45: "Diagonal (↗)", 90: "Vertical (↑)"}

# Contrast parameters
INITIAL_CONTRAST = .5
MIN_CONTRAST = 0.0
CONTRAST_DECAY_RATE = 0.15

def calculate_contrast(score):
    """Calculate current contrast based on score"""
    return max(MIN_CONTRAST, INITIAL_CONTRAST * ((1 - CONTRAST_DECAY_RATE) ** score))

def generate_gabor(cpd, orientation_deg, contrast=1.0):
    """Generate a Gabor patch with specified parameters"""
    size_pixels = 512
    size_degrees = 8
    sigma_degrees = 1.2
    
    # Create coordinate grids
    x = np.linspace(-size_degrees/2, size_degrees/2, size_pixels)
    y = np.linspace(-size_degrees/2, size_degrees/2, size_pixels)
    X, Y = np.meshgrid(x, y)
    
    # Convert orientation to radians
    theta = np.deg2rad(orientation_deg + 90)
    
    # Sinusoidal grating
    frequency = 2 * np.pi * cpd
    sine_grating = np.sin(frequency * (X * np.cos(theta) + Y * np.sin(theta)))
    
    # Gaussian envelope
    gaussian = np.exp(-(X**2 + Y**2) / (2 * sigma_degrees**2))
    
    # Combine to create Gabor patch with contrast modulation
    # Add 0.5 gray background so low contrast fades to gray
    gabor = 0.5 + (contrast * sine_grating * gaussian)
    
    return gabor

def generate_new_patch():
    """Generate new random Gabor patch"""
    st.session_state.current_cpd = np.random.choice(CPD_OPTIONS)
    st.session_state.current_orientation = np.random.choice(ORIENTATION_OPTIONS)
    st.session_state.feedback = ""
    st.session_state.show_feedback = False

def check_answer(guessed_orientation):
    """Check if the answer is correct and update score"""
    if st.session_state.show_feedback:
        # Already showing feedback, ignore additional clicks
        return
    
    if guessed_orientation == st.session_state.current_orientation:
        st.session_state.score += 1
        st.session_state.feedback = "✓ Correct!"
        st.session_state.feedback_color = "green"
    else:
        correct_name = ORIENTATION_NAMES[st.session_state.current_orientation]
        st.session_state.feedback = f"✗ Wrong! It was {correct_name}"
        st.session_state.feedback_color = "red"
    
    st.session_state.show_feedback = True

def reset_game():
    """Reset the game"""
    st.session_state.score = 0
    st.session_state.feedback = ""
    generate_new_patch()

# Initialize game if needed
if st.session_state.current_orientation is None:
    generate_new_patch()

# Title and score
st.title("👁️ Gabor Orientation Game")

# Instructions at the top
st.markdown("### 🎮 How to Play")
st.markdown("""
Identify the orientation of the Gabor patch and select your answer:
- **Horizontal (→)**: Stripes go left-right
- **Vertical (↑)**: Stripes go up-down  
- **Diagonal (↗)**: Stripes go at 45°

Contrast decreases with each correct answer - see how high you can score!
""")

st.markdown("---")

current_contrast = calculate_contrast(st.session_state.score)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Score", st.session_state.score)
with col2:
    st.metric("Contrast", f"{current_contrast:.1%}")
with col3:
    if st.button("Reset Game", use_container_width=True):
        reset_game()
        st.rerun()

# Show feedback if available
if st.session_state.show_feedback:
    if st.session_state.feedback_color == "green":
        st.success(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)
    
    # Auto-advance after showing feedback
    generate_new_patch()
    st.rerun()
elif st.session_state.feedback:
    # Clear old feedback
    st.session_state.feedback = ""

# Generate and display Gabor patch
gabor = generate_gabor(
    st.session_state.current_cpd,
    st.session_state.current_orientation,
    current_contrast
)

# Create matplotlib figure
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(gabor, cmap='gray', vmin=0, vmax=1)
ax.axis('off')  # Hide axis

# Display the figure
st.pyplot(fig, use_container_width=True)
plt.close()

# Answer buttons - directly under the patch
st.markdown("### Select Orientation:")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("← Horizontal (0°)", key="horizontal", use_container_width=True, type="primary"):
        check_answer(0)
        st.rerun()

with col2:
    if st.button("↑ Vertical (90°)", key="vertical", use_container_width=True, type="primary"):
        check_answer(90)
        st.rerun()

with col3:
    if st.button("↗ Diagonal (45°)", key="diagonal", use_container_width=True, type="primary"):
        check_answer(45)
        st.rerun()

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This game tests your **contrast sensitivity** - your ability to detect oriented patterns at low contrast levels.
    
    **Rules:**
    - Identify the orientation of each Gabor patch
    - Contrast decreases by 8% with each correct answer
    - See how high you can score!
    
    **Settings:**
    - Spatial frequencies: 3, 6, 12, 15 cpd
    - Orientations: 0°, 45°, 90°
    - Contrast decay: 8% per correct answer
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Progress")
    st.markdown(f"**Current Score:** {st.session_state.score}")
    st.markdown(f"**Current Contrast:** {current_contrast:.2%}")
    
    # Show difficulty level
    if current_contrast > 0.5:
        difficulty = "Easy 😊"
    elif current_contrast > 0.2:
        difficulty = "Medium 😐"
    elif current_contrast > 0.05:
        difficulty = "Hard 😰"
    elif current_contrast > 0.01:
        difficulty = "Very Hard 🤯"
    else:
        difficulty = "Extreme! 💀"
    
    st.markdown(f"**Difficulty:** {difficulty}")
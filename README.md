# VLM-Agentic-Interface-Dobot-Magician

This project provides an agentic interface to control the Dobot Magician robot arm using a webcam and a workspace setup. The system integrates with the Gemini API for functionality.

## Getting Started

### Prerequisites
- Python 3.10
- Pip package manager
- Dobot Magician with necessary drivers installed
- Webcam
- An 8" x 5" white piece of paper
- Foam blocks (optional)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/JaredD-SWENG/VLM-Agentic-Interface-Dobot-Magician.git
    cd VLM-Agentic-Interface-Dobot-Magician
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Obtain a Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to generate an API key.
   
4. Create a `.env` file in the project directory and add your API key:
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

### Hardware Setup

1. **Connect the Dobot Magician via USB**:
   - Ensure that all necessary drivers are installed for your operating system.

2. **Connect the Webcam via USB**.

3. **Set up the workspace**:
   - Place an 8" x 5" white piece of paper as the workspace.
   - Position the paper using the following Dobot coordinates:
     - (300, -100)
     - (300, 100)
     - (200, 100)
     - (200, -100)

### Running the Application

1. Start the Streamlit application:
    ```bash
    streamlit run agenticcontroller.py
    ```

2. Use the application interface to command the Dobot Magician.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [Google AI Studio](https://aistudio.google.com/) for the Gemini API.
- Dobot Magician for hardware support.

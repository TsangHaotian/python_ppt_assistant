# PPTAssistant: Dongpo Jushi AI Assistant

## Project Introduction

PPTAssistant is a desktop application developed based on PyQt5 and OpenAI API, simulating conversations with Su Dongpo. Users can input questions to receive answers in the style of Dongpo Jushi, while also supporting font size adjustment and custom role settings.

## Project Screenshots
![f4d17af12820315556e1dcfd8694871](https://github.com/user-attachments/assets/e35d01ed-90ab-4f4d-8f20-cbfe03f27cb1)
![7be381eba2c68d793804da57be1777d](https://github.com/user-attachments/assets/e6ad6105-a0ca-47c9-a2cd-a556bd2bde69)

## Features

- **Role Play**: Engage in conversation as Su Dongpo, adhering to the expression style of Song Dynasty literati.
- **Conversation History**: Real-time display of dialogue content, supporting scrolling through history.
- **Font Size Adjustment**: Users can easily switch font sizes to enhance reading experience.
- **Custom Role Settings**: Users can modify the AI's role settings via the settings dialog.
- **Hotkey Support**: Supports `Ctrl+Enter` hotkey for sending messages, improving input efficiency.
- **Borderless Window**: Supports borderless window display, allowing window dragging and moving.

## Usage Instructions

1. **Install Dependencies**
   - Ensure Python 3.8 or higher is installed.
   - Install PyQt5 and OpenAI SDK:
     ```bash
     pip install PyQt5 openai
     ```

2. **Run the Program**
   - Save the code as `main.py`, then run the following command to start the application:
     ```bash
     python main.py
     ```

3. **User Guide**
   - After entering a question, click "Send" or press the `Ctrl+Enter` hotkey.
   - Click the "⚙️ Settings" button to modify the AI's role settings.
   - Click the "Aa Font" button to adjust the font size.
   - Click the "⨉ Close" button to exit the application.

## Project Structure

- **PPTAssistant Class**
  - Main window class, responsible for UI layout and event handling.
- **AISettingsDialog Class**
  - Role settings dialog, used to modify the AI's role settings.
- **Core Function Modules**
  - Contains core functions such as font size adjustment and role setting updates.

## Important Notes

- **API Key**: Replace the `api_key` in the code with your own OpenAI API key.
- **Resource Path**: Ensure the `resource` folder contains the `character.png` image file.
- **Network Issues**: If unable to connect to the OpenAI API, check the network connection or the validity of the API key.

## Example

### Dialogue Example

User: Mr. Dongpo, what is your view on modern technology?

Dongpo Jushi: Although I was born in the Song Dynasty, observing today's technology, it is truly astonishing. However, I also know that all things in the world have their limitations. While technology can change life, one must not forget ancient wisdom.

### Font Size Adjustment

Users can cycle through font sizes (18px -> 22px -> 26px -> 18px) by clicking the "Aa Font" button to adapt to different reading needs.


---

*Thank you for your support!*

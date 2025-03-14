# 🎙️ LiveKit Voice Assistant with Audio Validation & Summarization  
 
## 🚀 Overview  
This project implements a **voice assistant** using **LiveKit's Voice Pipeline Agent**, integrating **audio length validation** and **text summarization**. It ensures audio does not exceed 60 seconds by sending length validation to a **Flask server**, which trims and summarizes long responses using **Hugging Face's BART model**.  
 
## 🛠️ Features  
- **LiveKit Voice Assistant** for real-time interaction  
- **Pre-TTS Validation** to check estimated audio length  
- **Flask Backend API** to handle validation & processing  
- **Text Summarization** for long responses (using Hugging Face)  
- **Ngrok Integration** for easy backend exposure  
 
## 📌 How It Works  
1. User interacts with the **LiveKit Voice Agent**.  
2. Before text is sent to **TTS**, its estimated audio length is calculated.  
3. The estimated length is sent to the **Flask API** for validation.  
4. If the duration exceeds **60 seconds**, the **middle portion** of the text is trimmed and summarized.  
5. The modified text is returned and processed by **TTS**.

📢 Note
This repository only includes task file modifications for integrating audio validation and summarization.
For a full implementation of LiveKit's Voice Pipeline Agent, please refer to the official GitHub repository:

🔗 LiveKit Agents GitHub: https://github.com/livekit/agents/tree/main/examples/voice-pipeline-agent
 
## 🏗️ Setup  
### 1️⃣ Clone Repository  
```sh
git clone https://github.com/...../livekit-voice-assistant.git
cd livekit-voice-assistant
```
### 2️⃣ Install Dependencies  
```sh
pip install -r requirements.txt
```
### 3️⃣ Run Flask Server  
```sh
python backendserverflask.py
```
### 4️⃣ Start LiveKit Agent  
```sh
python minimal_assistant.py dev
```
### 5️⃣ Expose Flask API using Ngrok  
```sh
ngrok http 5000
```
Replace the **Flask server URL** in `minimal_assistant.py` with the generated **Ngrok URL**.  
 
## 📹 Demo  
[Link to Presentation Video](#)  
 
## 📜 Documentation  
For a detailed guide, check the [Documentation](https://github.com/DeepikaChinnasamy/livekit_agent_assignment/blob/main/Developer%20Home%20Assignment.docx) 

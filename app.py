from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import openai
import os
import threading

app = Flask(__name__)

# Set your OpenAI API key
#openai.api_key = "YOUR_OPENAI_API_KEY"


engine = pyttsx3.init()


engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)


engine_lock = threading.Lock()

def speak(text):
    with engine_lock:
        try:
            engine.say(text)
            engine.runAndWait()
            print(f"Speech completed: {text}")
        except Exception as e:
            print(f"Error in speak function: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/greet', methods=['GET'])
def greet():
    greeting = "Hello! I'm your AI assistant. Click the button and speak to start our conversation."
    threading.Thread(target=speak, args=(greeting,)).start()
    return jsonify({'greeting': greeting})

@app.route('/listen', methods=['GET'])
def listen():
    recognizer = sr.Recognizer()
    
    try:
        print("Getting list of microphones...")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"Microphone with name \"{name}\" found for `device_index={index}`")
        
        with sr.Microphone() as source:
            print("Microphone object created successfully")
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        
        print("Audio captured, attempting to recognize...")
        user_input = recognizer.recognize_google(audio)
        print(f"User said: {user_input}")
        return jsonify({'message': user_input})
    except sr.WaitTimeoutError:
        print("Listening timed out")
        return jsonify({'error': 'Listening timed out. Please try again.'})
    except sr.UnknownValueError:
        print("Could not understand audio")
        return jsonify({'error': 'Could not understand audio. Please try again.'})
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return jsonify({'error': f'Could not request results; {e}'})
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = response.choices[0].message['content']
    except Exception as e:
        ai_response = f"Sorry, I encountered an error: {str(e)}"
    
    
    speak(ai_response)
    
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import requests
import openai
import wikipedia
import webbrowser
import pyautogui

application = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "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"
model_id = 'gpt-3.5-turbo'

@application.route('/')
def index():
    return render_template('index.html')


# Route to handle chat requests
@application.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['user_input']

    # Get bot response
    bot_response = chat_with_gpt(user_input)

    return jsonify({'bot_response': bot_response})



def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=[{"role": "system", "content": "You are a GPT AI assistant named mindfulpal."}, {"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message['content'].strip()


def get_weather(city):
    api_key = "5cfd35f5845c442506f5381cfa1915d7"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}"
    print(city)
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] == 200:
        weather_info = f"The weather in {city} is {data['weather'][0]['description']}."
    else:
        weather_info = "Sorry, couldn't fetch weather information for that city."
    return weather_info

@application.route('/get_weather', methods=['POST'])
def handle_weather_request():
    data = request.json
    try:
        city = data['city']
        transcription = data['transcription']
        if "weather" in transcription.lower():
            weather_info = get_weather(city)
            return jsonify({"weather_info": weather_info})
        else:
            return jsonify({"message": "No weather request found in transcription"})
    except KeyError as e:
        return jsonify({"error": f"KeyError: {e}"})
    
def search_wikipedia(query):
    try:
        result = wikipedia.summary(query, sentences=2)
        print(result)
        return result
        
    except wikipedia.exceptions.DisambiguationError as e:
        return "It seems there are multiple possible interpretations. Can you be more specific?"
    except wikipedia.exceptions.PageError as e:
        return "Sorry, I couldn't find any relevant information on Wikipedia."
    
@application.route('/search_wikipedia', methods=['POST'])
def search_wikipedia_route():
    data = request.json
    query = data['query']
    result = search_wikipedia(query)
    return jsonify({'result': result})

@application.route('/perform_google_search', methods=['POST'])
def perform_google_search():
    data = request.json
    if 'query' not in data:
        return jsonify({'error': 'Query parameter missing'}), 400
    query = data['query']
    
    # Construct the Google search URL
    search_url = "https://www.google.com/search?q=" + query
    
    # Open the search URL in the default web browser
    webbrowser.open(search_url)
    
    return jsonify({'message': 'Search opened in browser'})

@application.route('/close_recent_tab', methods=['POST'])
def close_recent_tab():
    # Simulate Ctrl+W key press to close the current tab
    pyautogui.hotkey('ctrl', 'w')
    return jsonify({'message': 'Closed the most recent tab'})

if __name__ == '__main__':
    application.run(debug=True)

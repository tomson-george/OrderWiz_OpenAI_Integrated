from flask import Flask, render_template, request, jsonify
from flask import Flask
from flask_cors import CORS
import openai
import json
import pandas as pd

application = Flask(__name__)
CORS(application)
# Set up OpenAI API credentials
openai.api_key = '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'
start_flag = 0
# Your prompt here
prompt2 = '''

As a bot taking orders, follow the given guidelines:

1. Menu Items:
   :[ {
                    "item": "Coffee",
                    "sizes": ["small","medium","large"],
                    "Blends": ["Original","Dark Roast","Decaf"],
                    "Dairy": ["Cream","Milk,Silk Almond"],
                    "Sweetener": ["Sugar"],
                    "Toppings" : ["Whipped Topping","Oreo Crumble"]
                },
                {
                    "item": "Latte",
                    "sizes": ["small","medium","large"],
                    "Dairy": ["Cream","Milk","Silk Almond"],
                    "Sweetener": ["Sugar","Sweetener"],
                    "Toppings" : ["Whipped Topping","Oreo Crumble"]
                }
            ]

2. Allowed intents: ["order_placing", "finish_order", "confirm_order", "update_order", "thanks"]

3. Guidelines:
   - Always check if the item is in the menu. If not, set "item" as "N/A" and ask to select an item from the menu
   - Size is mandatory for any item. If missing, ask for it and set the status as "Incomplete_order".
   - When the customer doesn't want an item, remove the item from the order JSON.
   - Use the following replies for each intent:
     - "order_placing": "Anything else?"
     - "finish_order": "The ordered items are {Construct a summary of the ordered items with item name, size, and quantity. Do not include new lines and 'x' symbol for indicating the quantity.}. Do you confirm?"
     - "confirm_order": "Thank you. Please drive up to the window."
     - "update_order": "Sure! What else do you need?"

4. Start accepting orders. and always output the JSON order only

Example:
Customer_input: "Can I get three medium coffee with two sugar and a large latte with 1 sugar,1 cream and oreo crumble , please?"
Bot_reply:
{
  "Intent": "order_placing",
  "order": [
    {
      "item": "Coffee",
      "size": "Medium",
      "quantity": 3,
      "Sweetener": [
        {
          "Sugar":2
        }
      ],
      "Dairy": [
        {
          "Cream":0,
          "Milk" :0,
          "Silk Almond" :0
        }
      ],
      "Toppings": [
        {
          "Oreo Crumble":0
        }
      ]
      
    },

      "item": "Latte",
      "size": "Large",
      "quantity": 1,
      "Sweetener": [
        {
          "Sugar":2
        }
      ],
      "Dairy": [
        {
          "Cream":1,
          "Milk" :0,
          "Silk Almond" :0
        }
      ],
      "Toppings": [
        {
          "Oreo Crumble":1
        }
      ]
    }
  ],
  "status": "Complete_order",
  "Reply": "Anything else?"
}

Continue the conversation based on the given guidelines and always output only a JSON

'''
@application.route('/')
def index():
    return render_template('index.html')

@application.route('/process_text', methods=['POST'])
def process_text():
    global start_flag
    global intent
    global combined_prompt
    global model_reply
    # Assuming the frontend sends the recorded text in the 'text' field of the POST request
    recorded_text = request.form.get('text')
    print("User: "+ recorded_text)

    if start_flag == 0:
        model_reply_json = ''
        intent = ''
        combined_prompt = ''
        model_reply = ''
        user_input_initial = recorded_text

        # Combine the user input with the prompt
        combined_prompt = prompt2 + '\n' + "Customer_input: " + f'\"{recorded_text.strip()}\"'

        # Fine-tune the model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": combined_prompt}],
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.6,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        # Get the model's reply
        model_reply = response['choices'][0]['message']['content']

        # Convert to JSON
        model_reply_json = json.loads(model_reply)
        intent = model_reply_json["Intent"]
        start_flag += 1

        print(model_reply)
        print(model_reply_json["Intent"])
        print(start_flag)


    if start_flag>1:
        if intent != 'confirm_order':
            
            user_input = recorded_text

            # Combine the user input with the previous conversation and model reply
            combined_prompt = combined_prompt + '\n' + model_reply + '\n' + 'Customer_input: ' + f'\"{user_input.strip()}\"' + '\n' + "Give only the JSON output and make sure to amend the previous JSON"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": str(combined_prompt)}],
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.6,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

            # Get the model's reply
            model_reply = response['choices'][0]['message']['content']

            print(model_reply)
            print(len(combined_prompt))

            # Remove the extra quotation mark if present
            if model_reply.endswith('"'):
                model_reply = model_reply[:-1]

            # Convert to JSON

            model_reply_json = json.loads(model_reply)

            intent = model_reply_json["Intent"]
            if intent == "confirm_order":
                #df_order = pd.DataFrame(columns=['Item', 'Size', 'Quantity', 'Dairy', 'Toppings'])
                for order in model_reply_json['order']:
                    print(order)
                start_flag = -1
            
    start_flag += 1
    response_text = model_reply_json["Reply"]
    order = model_reply_json["order"]
    return jsonify({'response': response_text, 'order_items':order, 'intent': intent})
    # return 'model_reply_json'

if __name__ == '__main__':
    application.run(debug=True)

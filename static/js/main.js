document.addEventListener('DOMContentLoaded', function () {
    const chatBox = document.getElementById('chat-box');
    const recordBtn = document.getElementById('record-btn');
    let recognition = null;
    

    function scrollToBottom() {
        //chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addBotMessage(message) {
        const botMessage = document.createElement('p');
        botMessage.classList.add('bot-message');
        botMessage.textContent = message;
        chatBox.appendChild(botMessage);
    }

    function handleAudioRecording() {
        if (!recognition) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition)();
            recognition.lang = 'en-US';

            // Disable the button and change its color to grey during recording
            recordBtn.disabled = true;
            recordBtn.style.backgroundColor = '#ccc';

            recognition.onresult = function (event) {
                const recordedText = event.results[0][0].transcript;
                //addBotMessage('You: ' + recordedText);

                // Send the recorded text to the Flask application
                sendRecordedTextToFlask(recordedText);

                // Reset recognition after recording is complete
                recognition = null;
            };

            recognition.onerror = function (event) {
                console.error('Speech recognition error:', event.error);
                recognition.stop();
                // Reset recognition after error occurs during recording
                recognition = null;
                // Enable the button and restore its color if an error occurs during recording
                enableButton();
            };
        }

        // Start recording logic
        recognition.start();
    }

    function enableButton() {
        // Enable the button and restore its color to blue
        recordBtn.disabled = false;
        recordBtn.style.backgroundColor = '#007BFF';
    }

    function readTextAloud(text) {
        // Simulated text-to-audio conversion (using browser SpeechSynthesis)
        return new Promise((resolve, reject) => {
            const synth = window.speechSynthesis;
            const utterance = new SpeechSynthesisUtterance(text);
    
            utterance.onend = function () {
                resolve();
            };
    
            synth.speak(utterance);
        });
    }

    function sendRecordedTextToFlask(text) {
        recordBtn.setAttribute('src', '../static/images/loading.gif');
        fetch('/process_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `text=${encodeURIComponent(text)}`
        })
        .then(response => response.json())
        .then(data => {
            recordBtn.setAttribute('src', '../static/images/v159_244.png');
            const responseText = data.response;
            readTextAloud(responseText);
            let divSummary = document.getElementById('divSummary');
            let divOrderContainer = document.getElementById('orderContainer');

            let orderContainerTop = 132;
            let orderItemTop = 143;
            let orderQuantityTop = 172;
            let orderPriceTop = 147;
            //Read order items

            console.log(data);
                let orderItems = data.order_items;
                orderItems.forEach(order => {
                    document.querySelectorAll("." + order.item + "_" + order.size).forEach(element => element.remove());

                    if (order.item != "N/A"){
                        //Order Background
                        let orderContainer = document.createElement("div" );
                        orderContainer.classList.add("order_background");
                        orderContainer.classList.add(order.item + "_" + order.size);
                        orderContainer.setAttribute('style', 'top:' + orderContainerTop + 'px');
                        orderContainerTop += 87;
                        divOrderContainer.appendChild(orderContainer);

                        //Order Item Name
                        let spanOrderItem = document.createElement("span");
                        spanOrderItem.classList.add("order_item");
                        spanOrderItem.classList.add(order.item + "_" + order.size);
                        spanOrderItem.setAttribute('style', 'top:' + orderItemTop + 'px');
                        spanOrderItem.innerText = order.item;
                        orderItemTop += 87;
                        divSummary.appendChild(spanOrderItem);

                        //Order Quantity
                        let spanOrderQuantity = document.createElement("span");
                        spanOrderQuantity.classList.add("order_quantity");
                        spanOrderQuantity.classList.add(order.item + "_" + order.size);
                        spanOrderQuantity.setAttribute('style', 'top:' + orderQuantityTop + 'px');
                        spanOrderQuantity.innerText = order.quantity + "        " + order.size;
                        orderQuantityTop += 87;
                        divSummary.appendChild(spanOrderQuantity);

                        //Order Price
                        let spanOrderPrice = document.createElement("span");
                        spanOrderPrice.classList.add("order_price");
                        spanOrderPrice.classList.add(order.item + "_" + order.size);
                        spanOrderPrice.setAttribute('style', 'top:' + orderPriceTop + 'px');
                        spanOrderPrice.innerText = "$ 5.00";
                        orderPriceTop += 87;
                        divSummary.appendChild(spanOrderPrice);
                    }
                });

            if (data.intent == "confirm_order"){
                setTimeout(function(){
                window.location.reload(1);
                }, 5000);
            }

            //addBotMessage('Chatbot: ' + responseText);
            // Read the response text aloud to the user
            // readTextAloud(responseText);
            // Enable the button and restore its color after receiving the response
            enableButton();

        })
        .catch(error => {
            console.error('Error:', error);
            // Enable the button and restore its color if an error occurs during the fetch
            enableButton();
        });
    }

    recordBtn.addEventListener('click', function () {
        handleAudioRecording();
    });
});

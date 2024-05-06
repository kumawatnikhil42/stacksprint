import { GoogleGenerativeAI } from "@google/generative-ai";

const API_KEY = "AIzaSyBCXpXmT2N_-JWlQbRFe_MDciPQ1KXAkjg"; // Replace with your API key

const genAI = new GoogleGenerativeAI(API_KEY);

async function generateResponse(prompt) {
    if (!prompt.trim()) return ""; // Return empty string if prompt is empty
    
    // Show typing animation
    const typingIndicator = document.querySelector('.messages__item--typing ');
    typingIndicator.style.display = 'block';

    // Generate response using Google Generative AI
    const model = genAI.getGenerativeModel({ model: "gemini-pro" });
    const result = await model.generateContent(prompt);
    const response = await result.response;
    
    // Hide typing animation
    typingIndicator.style.display = 'none';

    return response.text();
}

class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        };

        this.state = false;
        this.visitorMessages = [];
        this.operatorResponses = [];
    }

    display() {
        const { openButton, chatBox, sendButton } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox));
        sendButton.addEventListener('click', () => this.onSendButton(chatBox));

        const inputField = chatBox.querySelector('input');
        inputField.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatBox);
            }
        });
    }
    

    toggleState(chatbox) {
        this.state = !this.state;
        chatbox.classList.toggle('chatbox--active', this.state);
    }

    async onSendButton(chatbox) {
        const inputField = chatbox.querySelector('input');
        const text = inputField.value.trim();
        inputField.value = ''; // Clear input field

        if (text === "") return;

        const response = await generateResponse(text);
        this.visitorMessages.push(text);
        this.operatorResponses.push(response);
        this.updateChatText(chatbox);
    }

    updateChatText(chatbox) {
        const chatMessages = chatbox.querySelector('.chatbox__messages');
        
        // Clear previous messages
        chatMessages.innerHTML = '';
    
        // Display visitor messages and operator responses in reverse order
        for (let i = this.visitorMessages.length - 1; i >= 0; i--) {
            const visitorMessage = document.createElement('div');
            visitorMessage.classList.add('messages__item', 'messages__item--visitor');
            visitorMessage.textContent = this.visitorMessages[i];
            chatMessages.appendChild(visitorMessage);
    
            const operatorResponse = document.createElement('div');
            operatorResponse.classList.add('messages__item', 'messages__item--operator');
            operatorResponse.textContent = this.operatorResponses[i];
            chatMessages.appendChild(operatorResponse);
        }
    }
}

const chatbox = new Chatbox();
chatbox.display();

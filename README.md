
# API FOR WEB CHATTING APPLICATION

Discover a user-friendly web chat app, similar to WhatsApp, crafted using Python Django Rest Framework. If you've ever enjoyed using WhatsApp, you'll find our platform familiar and intuitive. The best part? I'm providing you with a ready-to-use API, allowing you to effortlessly create your own chat application.



## Features

- Users can register on the platform to create their accounts.
- Registered users can log in to access their accounts and features.
- Enhanced security with a 2-step OTP verification process during login.
- Easily find and connect with other users on the platform.
- Initiate chat conversations with friends and contacts.
- Users have the ability to send text messages, videos, and audio files within chats.
- Create groups to facilitate group conversations and interactions.
- Broadcast messages can be created and sent to multiple recipients.
- Manage profile information by updating details such as password, mobile number, and email.
- Users can share their status updates to let others know what they're up to.
- Presence indicators like online/offline status and message read status are displayed.


## Technologies Used

- Django Rest Framework
- Django email module (django.core.mail)
- Python modules: base64, binascii, and magic
- Django Channels for real-time chat
- PyJWT is a Python library for generating JSON WEB TOKEN
- django-cors-headers
- Swagger for making Documentation
- PostgreSQL is used as the database
- Nginx, Gunicorn, Daphne, Redis, and AWS
- 
## Documentation

You can use my Documentation for more details 

[Documentation link](https://documenter.getpostman.com/view/24033907/2s9Xy5LAUY)


## WebSocket (WS) Connection for Real-Time Chat

Prerequisites
Before establishing a WebSocket connection for real-time chat, ensure the following prerequisites are met:

Authentication JWT Token: Users must have an authentication JWT (JSON Web Token) token to access WebSocket functionalities. This token is obtained upon successful login and should be included in the request headers.

Conversation Start: To begin a chat, users need to initiate a conversation. For initiating a Conversation please refer to my [API documentation](https://documenter.getpostman.com/view/24033907/2s9Xy5LAUY) The conversation initiation request should include the necessary details (e.g., recipient, etc...), and upon success, the server responds with a room_name which is essential for a WebSocket connection.

Establishing a WebSocket Connection
Follow these steps to establish a WebSocket connection for real-time chat:

Obtain Authentication Token: Users should be authenticated and have a valid JWT token. Include this token in the headers of your WebSocket connection request.

Start a Conversation: Use your application's API to initiate a conversation. Upon a successful conversation start, the server will respond with a room_name. This room_name is specific to the conversation and will be used in the WebSocket URL.

WebSocket URL: The WebSocket URL for your chat feature might resemble the following pattern:


## Usage/Examples

#### javascript code

```javascript
const socket = new WebSocket(`wss://multimedianow.xyz/ws/chat/${roomName}/?Authorization=${jwtToken}`);

socket.onopen = (event) => {
  console.log("WebSocket connection opened:", event);
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("Received message:", message);
};

socket.onclose = (event) => {
  console.log("WebSocket connection closed:", event);
};

```
##### Replace {room_name} with the actual room_name obtained from the conversation initiation step, and <your_jwt_token> with the user's JWT token

##### Once the WebSocket connection is established, you can send and receive real-time messages using the WebSocket API. Messages should be formatted as JSON objects, containing relevant information such as the sender, recipient, message content, and timestamps.


const axios = require('axios');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// WhatsApp API configuration
const WHATSAPP_API_TOKEN = process.env.WHATSAPP_API_TOKEN || 'your_token_here';
const WHATSAPP_PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID || 'your_phone_number_id';
const TO_PHONE_NUMBER = process.env.TEST_PHONE_NUMBER || 'your_test_phone_number';

// Function to send a test WhatsApp message
async function sendTestMessage() {
  try {
    console.log('Sending test WhatsApp message...');
    
    const response = await axios.post(
      `https://graph.facebook.com/v17.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        to: TO_PHONE_NUMBER,
        type: 'text',
        text: {
          body: 'This is a test message from the WhatsApp API integration. Please reply with your name and IC number to book an appointment.'
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${WHATSAPP_API_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('Message sent successfully!');
    console.log(response.data);
  } catch (error) {
    console.error('Error sending message:');
    if (error.response) {
      console.error(error.response.data);
    } else {
      console.error(error.message);
    }
  }
}

// Function to test the ChatGPT integration
async function testChatGPT() {
  try {
    console.log('Testing ChatGPT integration...');
    
    const OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'your_openai_api_key';
    
    const response = await axios.post(
      'https://api.openai.com/v1/chat/completions',
      {
        model: 'gpt-3.5-turbo',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful assistant that extracts name and IC number from messages. ' +
                     'Return the information in JSON format with keys "name" and "icNumber". ' +
                     'If either piece of information is missing, set the value to null.'
          },
          {
            role: 'user',
            content: 'My name is John Doe and my IC number is 123456789012'
          }
        ],
        temperature: 0.3,
        max_tokens: 150
      },
      {
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('ChatGPT response:');
    console.log(response.data.choices[0].message.content);
  } catch (error) {
    console.error('Error testing ChatGPT:');
    if (error.response) {
      console.error(error.response.data);
    } else {
      console.error(error.message);
    }
  }
}

// Run the tests
async function runTests() {
  // Test ChatGPT integration
  await testChatGPT();
  
  // Test WhatsApp API integration
  await sendTestMessage();
}

runTests(); 
const axios = require('axios');
const crypto = require('crypto');

// WhatsApp API configuration
const WHATSAPP_API_TOKEN = process.env.WHATSAPP_API_TOKEN || 'your_token_here';
const WHATSAPP_PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID || 'your_phone_number_id';
const WHATSAPP_VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN || 'your_verify_token';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || 'your_openai_api_key';

// Django API endpoint
const DJANGO_API_ENDPOINT = process.env.DJANGO_API_ENDPOINT || 'http://localhost:8000/api/appointments/';

/**
 * Handle webhook verification from WhatsApp
 */
exports.verifyWebhook = (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  // Check if a token and mode were sent
  if (mode && token) {
    // Check the mode and token sent are correct
    if (mode === 'subscribe' && token === WHATSAPP_VERIFY_TOKEN) {
      // Respond with the challenge token from the request
      console.log('WEBHOOK_VERIFIED');
      return res.status(200).send(challenge);
    }
  }
  
  // Respond with '403 Forbidden' if verify tokens do not match
  return res.sendStatus(403);
};

/**
 * Process incoming WhatsApp messages
 */
exports.processWebhook = async (req, res) => {
  try {
    // Return a 200 response immediately to acknowledge receipt
    res.status(200).send('EVENT_RECEIVED');
    
    const body = req.body;
    
    // Check if this is a WhatsApp message
    if (body.object && 
        body.entry && 
        body.entry[0].changes && 
        body.entry[0].changes[0].value.messages && 
        body.entry[0].changes[0].value.messages[0]) {
      
      const phoneNumberId = body.entry[0].changes[0].value.metadata.phone_number_id;
      const from = body.entry[0].changes[0].value.messages[0].from; // User's WhatsApp number
      const messageBody = body.entry[0].changes[0].value.messages[0].text.body;
      
      console.log(`Received message from ${from}: ${messageBody}`);
      
      // Process the message with ChatGPT to extract name and IC number
      const extractedInfo = await extractInformation(messageBody);
      
      if (extractedInfo.name && extractedInfo.icNumber) {
        // Create appointment in Django system
        const appointmentResult = await createAppointment(extractedInfo.name, extractedInfo.icNumber, from);
        
        // Send confirmation message
        await sendWhatsAppMessage(from, appointmentResult.message);
      } else {
        // Send a message asking for the required information
        await sendWhatsAppMessage(from, 
          "Please provide your full name and IC number to book an appointment. " +
          "For example: 'My name is John Doe and my IC number is 123456789012'");
      }
    }
  } catch (error) {
    console.error(`Error processing webhook: ${error}`);
  }
};

/**
 * Extract name and IC number from message using ChatGPT
 */
async function extractInformation(message) {
  try {
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
            content: message
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
    
    const content = response.data.choices[0].message.content;
    return JSON.parse(content);
  } catch (error) {
    console.error(`Error extracting information: ${error}`);
    return { name: null, icNumber: null };
  }
}

/**
 * Create an appointment in the Django system
 */
async function createAppointment(name, icNumber, whatsappNumber) {
  try {
    const response = await axios.post(
      DJANGO_API_ENDPOINT,
      {
        name: name,
        ic_number: icNumber,
        whatsapp_number: whatsappNumber
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error(`Error creating appointment: ${error}`);
    return { 
      success: false, 
      message: "Sorry, we couldn't create your appointment. Please try again later or contact our clinic directly."
    };
  }
}

/**
 * Send a WhatsApp message using the WhatsApp Business API
 */
async function sendWhatsAppMessage(to, message) {
  try {
    const response = await axios.post(
      `https://graph.facebook.com/v17.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        to: to,
        type: 'text',
        text: {
          body: message
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${WHATSAPP_API_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error(`Error sending WhatsApp message: ${error}`);
    return null;
  }
} 
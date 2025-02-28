import requests
import json
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# WhatsApp API integration
def send_whatsapp_message(to_number, message):
    """
    Send a WhatsApp message using the WhatsApp Business API
    
    This is a placeholder implementation. You'll need to replace this with your
    actual WhatsApp API integration code.
    
    For WhatsApp Business API, you might use:
    - Meta's WhatsApp Business API
    - Twilio's WhatsApp API
    - MessageBird
    - etc.
    """
    try:
        # This is a placeholder. Replace with your actual WhatsApp API code
        # Example using Meta's WhatsApp Business API:
        
        # WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
        # WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "your_token_here")
        
        # headers = {
        #     "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        #     "Content-Type": "application/json"
        # }
        
        # data = {
        #     "messaging_product": "whatsapp",
        #     "to": to_number,
        #     "type": "text",
        #     "text": {
        #         "body": message
        #     }
        # }
        
        # response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
        # response.raise_for_status()
        # return response.json()
        
        # For now, just log the message
        logger.info(f"WhatsApp message would be sent to {to_number}: {message}")
        return {"status": "success", "message": "Message logged (not actually sent)"}
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {"status": "error", "message": str(e)}

# ChatGPT API integration
def generate_appointment_message(appointment, is_update=False):
    """
    Generate an appointment message using the ChatGPT API
    
    This is a placeholder implementation. You'll need to replace this with your
    actual ChatGPT API integration code.
    """
    try:
        # This is a placeholder. Replace with your actual ChatGPT API code
        # Example using OpenAI's API:
        
        # OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_api_key_here")
        # OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
        
        # headers = {
        #     "Authorization": f"Bearer {OPENAI_API_KEY}",
        #     "Content-Type": "application/json"
        # }
        
        # If it's an update, create a different prompt
        if is_update:
            # prompt = f"Generate a polite message informing {appointment.name} that their appointment has been rescheduled to {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Include a reminder to arrive 15 minutes early and bring their IC card."
            message = f"Dear {appointment.name}, your appointment has been rescheduled to {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Please arrive 15 minutes early and bring your IC card. If you need to reschedule, please contact us. Thank you!"
        else:
            # prompt = f"Generate a polite message confirming an appointment for {appointment.name} on {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Include a reminder to arrive 15 minutes early and bring their IC card."
            message = f"Dear {appointment.name}, your appointment has been confirmed for {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Please arrive 15 minutes early and bring your IC card. If you need to reschedule, please contact us. Thank you!"
        
        # data = {
        #     "model": "gpt-3.5-turbo",
        #     "messages": [
        #         {"role": "system", "content": "You are a helpful assistant that generates polite appointment messages."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     "max_tokens": 150
        # }
        
        # response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        # response.raise_for_status()
        # message = response.json()["choices"][0]["message"]["content"].strip()
        
        # For now, just return a template message
        logger.info(f"Generated appointment message for {appointment.name}")
        return message
        
    except Exception as e:
        logger.error(f"Error generating appointment message: {str(e)}")
        # Fallback message in case of API failure
        if is_update:
            return f"Your appointment has been rescheduled to {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}."
        else:
            return f"Your appointment is confirmed for {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}."

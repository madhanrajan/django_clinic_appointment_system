import requests
import json
import os
from django.conf import settings
import logging
import openai

logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY", "your_api_key_here")

# WhatsApp API integration
def send_whatsapp_message(to_number, message):
    """
    Send a WhatsApp message using the WhatsApp Business API
    """
    try:
        # Meta's WhatsApp Business API configuration
        WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{os.environ.get('WHATSAPP_PHONE_NUMBER_ID', 'your_phone_number_id')}/messages"
        WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN", "your_token_here")
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        # Check if we're in debug mode
        if settings.DEBUG:
            # Just log the message in debug mode
            logger.info(f"WhatsApp message would be sent to {to_number}: {message}")
            return {"status": "success", "message": "Message logged (not actually sent in DEBUG mode)"}
        else:
            # Actually send the message in production
            response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {"status": "error", "message": str(e)}

# ChatGPT API integration
def generate_appointment_message(appointment, is_update=False):
    """
    Generate an appointment message using the ChatGPT API
    """
    try:
        # If it's an update, create a different prompt
        if is_update:
            prompt = f"Generate a polite message informing {appointment.name} that their appointment has been rescheduled to {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Include a reminder to arrive 15 minutes early and bring their IC card."
        else:
            prompt = f"Generate a polite message confirming an appointment for {appointment.name} on {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Include a reminder to arrive 15 minutes early and bring their IC card."
        
        # Check if we're in debug mode
        if settings.DEBUG:
            # Use template messages in debug mode
            if is_update:
                return f"Dear {appointment.name}, your appointment has been rescheduled to {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Please arrive 15 minutes early and bring your IC card. If you need to reschedule, please contact us. Thank you!"
            else:
                return f"Dear {appointment.name}, your appointment has been confirmed for {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}. Please arrive 15 minutes early and bring your IC card. If you need to reschedule, please contact us. Thank you!"
        else:
            # Use OpenAI API in production
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates polite appointment messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            message = response.choices[0].message.content.strip()
            logger.info(f"Generated appointment message for {appointment.name}")
            return message
        
    except Exception as e:
        logger.error(f"Error generating appointment message: {str(e)}")
        # Fallback message in case of API failure
        if is_update:
            return f"Your appointment has been rescheduled to {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}."
        else:
            return f"Your appointment is confirmed for {appointment.appointment_time.strftime('%A, %B %d, %Y at %I:%M %p')}."

# Function to extract name and IC number from a message using ChatGPT
def extract_information_from_message(message):
    """
    Extract name and IC number from a message using ChatGPT
    """
    try:
        # Use OpenAI API to extract information
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts name and IC number from messages. " +
                               "Return the information in JSON format with keys 'name' and 'icNumber'. " +
                               "If either piece of information is missing, set the value to null."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error extracting information: {str(e)}")
        return {"name": None, "icNumber": None}

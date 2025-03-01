# Django Clinic Appointment System with WhatsApp Integration

This project is a clinic appointment system built with Django that allows patients to book appointments through WhatsApp by providing their name and IC number.

## Features

- Book appointments through a web interface
- Book appointments through WhatsApp by providing name and IC number
- Admin dashboard to manage appointments
- Automatic appointment scheduling based on availability
- WhatsApp notifications for appointment confirmations

## Project Structure

- `mysite/`: Django project for the appointment system
- `src/`: Node.js server for WhatsApp API integration

## Setup Instructions

### Django Setup

1. Create a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. Install Django dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   cd mysite
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run the Django server:
   ```
   python manage.py runserver
   ```

### WhatsApp API Integration Setup

1. Install Node.js dependencies:
   ```
   npm install
   ```

2. Create a `.env` file based on `.env.example` and fill in your API keys:
   ```
   cp .env.example .env
   ```

3. Register for a WhatsApp Business API account:
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create a Meta developer account
   - Set up a WhatsApp Business API account
   - Get your WhatsApp API token and phone number ID

4. Register for an OpenAI API key:
   - Go to [OpenAI API](https://platform.openai.com/)
   - Create an account and get an API key

5. Run the Node.js server:
   ```
   npm start
   ```

6. Expose your webhook to the internet using ngrok or a similar service:
   ```
   ngrok http 3000
   ```

7. Configure your webhook URL in the Meta Developer Portal:
   - Use the URL provided by ngrok: `https://your-ngrok-url/webhook`
   - Set the verify token to match your `WHATSAPP_VERIFY_TOKEN` in the `.env` file

## API Endpoints

### Django API

- `GET /appointments/`: List all appointments
- `POST /appointments/`: Create a new appointment
- `GET /appointments/<id>/`: Get appointment details
- `PUT /appointments/<id>/`: Update an appointment
- `DELETE /appointments/<id>/`: Delete an appointment

### WhatsApp API

- `GET /webhook`: Webhook verification endpoint
- `POST /webhook`: Webhook for receiving WhatsApp messages

## How to Use

### Booking an Appointment via WhatsApp

1. Send a message to your WhatsApp Business number with your name and IC number.
   Example: "My name is John Doe and my IC number is 123456789012"

2. The system will use ChatGPT to extract your name and IC number from the message.

3. An appointment will be created in the system with the next available slot.

4. You will receive a confirmation message with your appointment details.

## Development

- To run the Django development server: `python manage.py runserver`
- To run the Node.js development server: `npm run dev`

## License

This project is licensed under the MIT License.

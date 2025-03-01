const express = require('express');
const bodyParser = require('body-parser');
const dotenv = require('dotenv');
const whatsappWebhook = require('./controllers/whatsappWebhook');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());

// Routes
app.get('/webhook', whatsappWebhook.verifyWebhook);
app.post('/webhook', whatsappWebhook.processWebhook);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
}); 
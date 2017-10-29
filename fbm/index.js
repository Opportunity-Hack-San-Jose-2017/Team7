'use strict';

// load the .env file
require('dotenv').load();
// use for send message api
const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;

// Imports dependencies and set up http server
const 
  express = require('express'),
  bodyParser = require('body-parser'),
  app = express().use(bodyParser.json()); // creates express http server

const request = require('request');
// Sets server port and logs message on success
app.listen(process.env.PORT || 1337, () => console.log('webhook is listening'));

// Creates the endpoint for our webhook 
app.post('/webhook', (req, res) => {  
 
  let body = req.body;

  // Checks this is an event from a page subscription
  if (body.object === 'page') {

    // Iterates over each entry - there may be multiple if batched
    body.entry.forEach(function(entry) {

      // Gets the message. entry.messaging is an array, but 
      // will only ever contain one message, so we get index 0
      let webhook_event = entry.messaging[0];
      console.log(webhook_event);
      console.log(webhook_event.message.nlp);

      // Get the sender PSID
      let sender_psid = webhook_event.sender.id;
      console.log('Sender PSID: ' + sender_psid);

      // Check if the event is a message or postback and
      // pass the event to the appropriate handler function
      if (webhook_event.message) {
        handleMessage(sender_psid, webhook_event.message);        
      } else if (webhook_event.postback) {
        handlePostback(sender_psid, webhook_event.postback);
      }
    });

    // Returns a '200 OK' response to all requests
    res.status(200).send('EVENT_RECEIVED');
  } else {
    // Returns a '404 Not Found' if event is not from a page subscription
    res.sendStatus(404);
  }

});

// Adds support for GET requests to our webhook
app.get('/webhook', (req, res) => {

  // Your verify token. Should be a random string.
  let VERIFY_TOKEN = "moo";
    
  // Parse the query params
  let mode = req.query['hub.mode'];
  let token = req.query['hub.verify_token'];
  let challenge = req.query['hub.challenge'];
    
  // Checks if a token and mode is in the query string of the request
  console.log("got something", mode, token);
  if (mode && token) {
  
    // Checks the mode and token sent is correct
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
      
      // Responds with the challenge token from the request
      console.log('WEBHOOK_VERIFIED', challenge);
      res.status(200).send(challenge);
    
    } else {
      // Responds with '403 Forbidden' if verify tokens do not match
      res.sendStatus(403);      
    }
  }
});

var states = {};

// Handles messages events
function handleMessage(sender_psid, received_message) {
  let response;
  console.log("received_message = ");
  console.log(received_message);

  // Check if the message contains text
  //if (received_message.text) {
      if (states[sender_psid]) {
          console.log("detected repeat user");
          states[sender_psid]++;
      } else {
          console.log("detected new user");
          states[sender_psid] = 1;
      }
      if (received_message.attachments && received_message.attachments[0].type == "location") {
          console.log("detected location:" + received_message.attachments[0].payload);
      }
      
      if (states[sender_psid] == 1) {
        response =  {
          "text": "Are you in immediate danger?",
          "quick_replies": [
            {
              "content_type": "text",
              "title": "Yes",
              "payload": "reply1"
            },
            {
              "content_type": "text",
              "title": "No",
              "payload": "reply2"
            }
          ]
        };
          
      } else if (states[sender_psid] == 2) {
        response =  {
            "text": "What is your location?",
            "quick_replies": [
            {
                "content_type":"location",
                "title": "location",
                "payload": "reply3"
            }
        ]

        };
      } else if (states[sender_psid] == 3) {
          response =  {
              "text": "Select a category",
              "quick_replies": [
                {
                  "content_type": "text",
                  "title": "Violence",
                  "payload": "reply1"
                },
                {
                  "content_type": "text",
                  "title": "Harassment",
                  "payload": "reply2"
                },
                {
                  "content_type": "text",
                  "title": "Danger",
                  "payload": "reply3"
                },
                {
                  "content_type": "text",
                  "title": "Other",
                  "payload": "reply4"
                }
              ]
            };
          
      } else if (states[sender_psid] == 4) {
        response =  {
            "text": "all done!"
        }  
      }
  
  // Sends the response message
  callSendAPI(sender_psid, response); 
}

// Handles messaging_postbacks events
function handlePostback(sender_psid, received_postback) {
  
}

// Sends response messages via the Send API
function callSendAPI(sender_psid, response) {
  // Construct the message body
  let request_body = {
    "recipient": {
      "id": sender_psid
    },
      "message": response
  }
  
  // Send the HTTP request to the Messenger Platform
  request({
    "uri": "https://graph.facebook.com/v2.6/me/messages",
    "qs": { "access_token": PAGE_ACCESS_TOKEN },
    "method": "POST",
    "json": request_body
  }, (err, res, body) => {
    if (!err) {
      console.log('message sent!')
    } else {
      console.error("Unable to send message:" + err);
    }
  });
}



/*
sample received message for location:

received_message =
{ mid: 'mid.$cAAUyL2qdT7Blm079vlfagm1JINrc',
  seq: 122,
  attachments:
   [ { title: 'Kenny\'s Location',
       url: 'https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.bing.com%2Fmaps%2Fdefault.aspx%3Fv%3D2%26pc%3DFACEBK%26mid%3D8100%26where1%3D37.3768458%252C%2B-121.9216105%26FORM%3DFBKPL1%26mkt%3Den-US&h=ATMOehDAvTA2uQXlInEg4gtMiXfP45kHp93oxyI5U4g0-NTWrHw_lG8uA0enti5ZycdO_5nGWg81ihlZNE7et7xOc-8T3EDJpA4OKejNc3fJANcyqw&s=1&enc=AZPjQPABJ8VVg6Yq3qO1pnV3yWV7_1kjoJm-AMpUuKoMmusinoqbVbdNEQ6e0MjAZNd3ppN-RTawq54zHALQLRBC',
       type: 'location',
       payload: [Object] } ] }
*/
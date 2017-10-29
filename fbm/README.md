# Set up
Install ngrok http://ngrok.com/
Make a .env file with content like so:
```
PAGE_ACCESS_TOKEN=<Facebook_page_token>
```
run use ``npm start``
`ngrok http 1337`

notes:
running npm start will start nodemon, which will watch and restart changes to 
index.js so you don't need to refresh the server everytime. 
port number is 1337
TODO: set up nodemon to watch for all js file changes

## Facebook setup
- create a facebook page and give it a user name
- create a facebook app on facebook dev
- in facebook app settings, click on Add Product and add Messenger
- set up webhook
- use "moo" as verify token for now ;)
- and use the ngrok for callback host like https://stuff.ngrok.io/webhook
- go to https://www.messenger.com/t/<your-bot-name> and start talking

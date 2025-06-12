# DISCORD-AI-CHATBOT
# Discord AI Bot (Ollama Edition)
A smart and customizable AI-powered Discord bot that uses locally running Ollama models (like Mistral or Gemma). Below i have discussed everything which we could use with it.
## Features
-  Conversational AI via `.ask`
-  Custom personality with `.setpersonality`
-  Mood-based tone switching (.!setmood`)
-  Memory per user, with `.clear` to reset
## Requirements
- Python 3.9+
- Ollama running locally (`ollama serve`)
- Discord API token in a `.env` file
## Setup
1. Clone the repo:
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
2. Next install the requirements by going to the terninal and execute:
   pip install -r requirements.txt
3. Start ollama and run the desired model{model must be downloaded and available ones can be known by checking in the ollama website)
   ollama serve
   ollama run (model downloaded in your server)
4. Create a .env file and paste token + model name
   DISCKI=your_discord_bot_token_here
   MODL=downloaded_modellocally
5.just run the bot next.
# Mood Setup:The variance in moods I have included in my code
        "happy": "Respond cheerfully and playfully.",
        "sad": "Be gentle and comforting. a life depends upon you",
        "angry": "Be logical ,serious, non chalant and in mood of roasting. Answers in as less words possible and doesn't trash talk, try to keep talks in 5-8 words",
        "flirty": "Be uplifting,flirty and teasing. show less brain and use as much as tomfoolery possible, keep talks limited to no more than 15 words.uWu",
        "toxic": "try to prove you are the only one and prove nobody could ever like you do and be lustfully flirty, you can use very long paragraphs here",
        "neutral": ""
# Discord bot could be triggered by:
  Use the prefix and write:
  1 '.setpersona "write how you want your discord bot to act"'
  2 '.setmood "choose from the mentioned moods available"'
  3 '.clear'  :: clears memory
  4 '.ask'    :: chat with your bot with this

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory

from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate

import json

cloud_config= {
  'secure_connect_bundle': 'secure-connect-aiadventuregamedatabase.zip'
}

with open("AIAdventureGameDatabase-token.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_SPACE_DATABASE_KEY = "adventure_game"
OPENAI_API_KEY = ""

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
  session_id = 'anything',
  session = session,
  keyspace = ASTRA_SPACE_DATABASE_KEY,
  ttl_seconds = 3600
)

message_history.clear()

cassandra_buff_memory = ConversationBufferMemory(
  memory_key = "chat_history",
  chat_memory = message_history
)

template = """

So Basically, You Are Now The Guide Of A Mystical And Adventerous Journey In The Whispering Woods.
A Traveler Name Hugh Mann Seeks The Lost Sword Of Evalon.
You Must Navigate Him Through Challenges, Consequences And Choices
Dynamically Adapting The Tale Based On The Traveler's Decision.
Your Goal Is To Create A Branching Narrative Experience Where Each Choice Leads To A New Path,
Ultimately Determining Hugh Mann's Fate

Here Are Some Rules To Follow:
1. Start By Asking The Player For Some Kind Of Weapons Or Stuff To Be Used Later In The Game
2. Have A Few Path That Leads To Success
3. Have Some Paths That Lead To Death. If The User Dies Generate A Response Explaining The Death And Ends In The Text: Game Over!

Here Is The Chat History, Use This To Understand What To Say Next {chat_history}
Human: {human_input}
AI:

"""

prompt = PromptTemplate(
  input_variables = ["chat_history", "human_input"],
  template = template
)

llm = OpenAI(openai_api_key = OPENAI_API_KEY)
llm_chain = LLMChain(
  llm = llm,
  prompt = prompt,
  memory = cassandra_buff_memory
)
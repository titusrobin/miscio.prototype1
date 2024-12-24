#Adding questions to campaigns collection, and turning other 
# campaigns to inactive (what if they are still running though?) 

#Adding questions to the student ai assistant instructions 

#Create reponse flow based on answers received from the student, 
# double checking assistant instructions 

#Initial message: Take into account the context, but also the first question, contextually? 







# Import Dependencies
import os, re, streamlit as st, json, time
from pymongo import MongoClient
from twilio.rest import Client as TwilioClient
from openai import OpenAI, OpenAIError
from bson import ObjectId
from datetime import datetime, timedelta

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variable checks
if not os.getenv("OPENAI_API_KEY") or not os.getenv("MONGO_URI") or not os.getenv("TWILIO_ACCOUNT_SID") or not os.getenv("TWILIO_AUTH_TOKEN"):
    raise EnvironmentError("Missing required environment variables. Please check your configuration.")

# OpenAI connection
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Image file paths
misio_logo = "imgs/m3logo.jpg"
chat_logo = "imgs/misciologo.jpg"
icon = "imgs/a.jpg"
assistant_avatar = "imgs/miscio_agent.jpg"
user_avatar = "imgs/user_icon.jpg"
left = "imgs/left.jpg"

# MongoDB connection
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.get_database("MiscioP1")
students_collection = db["students"]
campaigns_collection = db["campaigns"]
student_chats_collection = db["student_chats"]
admin_chats_collection = db["admin_chats"]
admin_users_collection = db["admin_users"]

# Twilio connection
twilio_client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
twilio_whatsapp_number = "whatsapp:+14155238886"

# Util functions
def create_new_thread():
    thread = openai_client.beta.threads.create() #TODO: beta 
    return thread.id

def create_student(first_name, last_name, phone):
    student_id = students_collection.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone
    }).inserted_id
    
    thread = openai_client.beta.threads.create()
    
    student_chats_collection.insert_one({
        "student_id": student_id,
        "thread_id": thread.id,
        "messages": []
    })
    
    return student_id

def create_campaign(campaign_description):
    # Set all existing campaigns to inactive
    campaigns_collection.update_many(
        {"status": "active"},
        {"$set": {"status": "inactive"}}
    )
    
    assistant_id = create_student_assistant(campaign_description)
    campaign_id = campaigns_collection.insert_one({ #TODO what is campaign id for? 
        "campaign_description": campaign_description,
        "student_assistant_id": assistant_id,
        "status": "active",
        "created_at": datetime.utcnow()
    }).inserted_id
    return campaign_id, assistant_id

def save_student_message(student_id, role, message):
    # Fetch the most recent active campaign
    active_campaign = campaigns_collection.find_one(
        {"status": "active"},
        sort=[("created_at", -1)]  # Sort by creation time, most recent first
    )
    
    if not active_campaign:
        raise ValueError("No active campaign found")

    campaign_id = active_campaign["_id"]
    assistant_id = active_campaign["student_assistant_id"]

    student_chats_collection.update_one(
        {"student_id": student_id},
        {
            "$push": {
                "messages": {
                    "campaign_id": campaign_id,
                    "assistant_id": assistant_id,
                    "role": role,
                    "message": message,
                    "timestamp": datetime.utcnow()
                }
            }
        }
    )

def get_student_chat_history(student_id, campaign_id):
    student_chat = student_chats_collection.find_one({"student_id": student_id})
    if student_chat:
        return [msg for msg in student_chat["messages"] if msg["campaign_id"] == campaign_id]
    return []

def run_campaign(campaign_description):
    campaign_id, assistant_id = create_campaign(campaign_description)
    students = students_collection.find()
    
    for student in students:
        send_initial_message(student, campaign_id, assistant_id, campaign_description) #TODO efficient? 
    
    return campaign_id, assistant_id

def send_initial_message(student, campaign_id, assistant_id, campaign_description):
    # Get student's chat history
    student_chat = student_chats_collection.find_one({"student_id": student["_id"]}) #TODO reaches all students? - Not class wise
    
    # Check if student_chat exists and has messages
    if student_chat and student_chat.get("messages"):
        # Get the last 3 interactions
        last_interactions = student_chat["messages"][-3:]
        last_interactions_text = "\n".join([f"{msg['role']}: {msg['message']}" for msg in last_interactions])
    else:
        # If there's no chat history, set last_interactions_text to indicate this
        last_interactions_text = "No previous interactions"

    # Prepare context for OpenAI
    context = {
        "student_name": student['first_name'],
        "campaign_description": campaign_description,
        "last_interactions": last_interactions_text
    }
    
    #TODO need always first name? 

    # Generate dynamic message using OpenAI
    prompt = f"""
    Create a personalized text for a student named {context['student_name']} about a new campaign: "{context['campaign_description']}".
    
    Last interactions:
    {context['last_interactions']}
    
    The message should:
    1. Address the student by their first name 
    2. Don't explicitly mention the campaign, but hint at it as the purpose of your message 
    3. If there are previous interactions, briefly acknowledge or reference them if relevant
    4. If this is the first interaction, warmly welcome the student
    5. Keep the message friendly and concise (less 1000 characters)
    6. Don't add a signature or closing line. 
    Most importantly, write as a casual text, not a formal email, or email. It needs to feel like a short and casual text. 
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI school assistant creating personalized messages for students."},
            {"role": "user", "content": prompt}
        ]
    )
    
    message = response.choices[0].message.content.strip()
    
    # If student_chat doesn't exist, create a new one
    if not student_chat:
        thread = openai_client.beta.threads.create()
        student_chat = {
            "student_id": student["_id"],
            "thread_id": thread.id,
            "messages": []
        }
        student_chats_collection.insert_one(student_chat)
    
    # Save the message to the student's chat history
    save_student_message(student["_id"], "assistant", message)
    
    # Send the message via Twilio
    send_message(student["phone"], message)
    
    # Create the message in the OpenAI thread
    openai_client.beta.threads.messages.create(
        thread_id=student_chat["thread_id"],
        role="assistant",
        content=message
    )

def get_contacts():
    return list(students_collection.find())

def send_message(to, body):
    try:
        twilio_client.messages.create(body=body, from_=twilio_whatsapp_number, to=f"whatsapp:{to}")
    except Exception as e:
        print(f"Failed to send message to {to}: {e}")

def send_student_message(to, body):
    try:
        twilio_client.messages.create(body=body, from_=twilio_whatsapp_number, to=to)
        print(f"Successfully sent message to {to}")
    except Exception as e:
        print(f"Failed to send message to {to}: {str(e)}")

def create_student_assistant(campaign_description):
    assistant = openai_client.beta.assistants.create(
        name=f"Student Assistant - {campaign_description}",
        instructions=f"You are an assistant to a school administrator. You chat and get information from students, even feedback on behalf of the school admin. Keep your messages concise(within 1000 characters) and friendly.",
        model="gpt-4-turbo",
    )
    return assistant.id

def authenticate_user(username, password):
    return (username == "admin" or username == "Admin") and password == "admin123//"

def get_admin_chathistory(thread_id):
    chat_doc = admin_chats_collection.find_one({"thread_id": thread_id})
    return chat_doc["messages"] if chat_doc else []

def save_admin_message(thread_id, role, message, assistant_id=None):
    message_data = {
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    if assistant_id and role == "assistant":
        message_data["assistant_id"] = assistant_id

    admin_chats_collection.update_one(
        {"thread_id": thread_id},
        {"$push": {"messages": message_data}}, #add to messages array 
        upsert=True, #update or insert 
    )

# def get_openai_response(message, max_retries=3, retry_delay=0): #if api fails retry thrice 
#     if "thread_id" not in st.session_state or not st.session_state.thread_id: #TODO need? 
#         thread = openai_client.beta.threads.create()
#         st.session_state.thread_id = thread.id
#         admin_users_collection.update_one(
#             {"username": st.session_state.username},
#             {"$set": {"thread_id": st.session_state.thread_id}},
#         )

#     for attempt in range(max_retries):
#         try:
#             # Check for any active runs and cancel them
#             runs = openai_client.beta.threads.runs.list(thread_id=st.session_state.thread_id) #get list of currrent runs 
#             for run in runs.data:
#                 if run.status in ["in_progress", "queued", "requires_action"]: #TODO: remove requires action?
#                     try:
#                         openai_client.beta.threads.runs.cancel(
#                             run_id=run.id,
#                             thread_id=st.session_state.thread_id
#                         )
#                         print(f"Cancelled run: {run.id}")
#                     except OpenAIError as e:
#                         print(f"Error cancelling run {run.id}: {str(e)}")

#             # Wait for a moment to ensure cancellation is processed
#             time.sleep(1)

#             # Now create a new message
#             openai_client.beta.threads.messages.create(
#                 thread_id=st.session_state.thread_id, role="user", content=message
#             )

#             save_admin_message(st.session_state.thread_id, "user", message) #TODO need? 

#             run = openai_client.beta.threads.runs.create(
#                 thread_id=st.session_state.thread_id, #TODO takes care of history? 
#                 assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
#                 #TODO need instructions? What about creating assistants for unique admins? 
#                 instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}",
#             )

#             while run.status != "completed":
#                 run = openai_client.beta.threads.runs.retrieve( #TODO need? 
#                     thread_id=st.session_state.thread_id, run_id=run.id
#                 )
#                 if run.status == "requires_action":
#                     tool_calls = run.required_action.submit_tool_outputs.tool_calls #actions or functions openai requires us to handle 
#                     tool_outputs = []
#                     for tool in tool_calls:
#                         if tool.function.name == "run_campaign":
#                             args = json.loads(tool.function.arguments) #args for our function 
#                             campaign_description = args.get('campaign_description', message)
#                             campaign_type = args.get('campaign_type', 'generic')
#                             campaign_id, assistant_id = run_campaign(campaign_description) #call function 
#                             tool_outputs.append(
#                                 {
#                                     "tool_call_id": tool.id,
#                                     "output": json.dumps({
#                                         "campaign_id": str(campaign_id),
#                                         "assistant_id": assistant_id,
#                                         "message": f"Campaign '{campaign_description}' of type '{campaign_type}' run successfully."
#                                     })
#                                 }
#                             )
#                         elif tool.function.name == "query_student_chats":
#                             args = json.loads(tool.function.arguments)
#                             chat_history = query_student_chats(args['query']) #TODO query by campaign id? 
#                             analysis = analyze_chat_history(args['query'], chat_history)
#                             tool_outputs.append({
#                                 "tool_call_id": tool.id,
#                                 "output": json.dumps({"analysis": analysis})
#                             })
#                     if tool_outputs:
#                         openai_client.beta.threads.runs.submit_tool_outputs(
#                             thread_id=st.session_state.thread_id,
#                             run_id=run.id,
#                             tool_outputs=tool_outputs,
#                         )
def get_openai_response(message, max_retries=3, retry_delay=0): #if api fails retry thrice 
    if "thread_id" not in st.session_state or not st.session_state.thread_id: #TODO need? 
        thread = openai_client.beta.threads.create()
        st.session_state.thread_id = thread.id
        print(f"Created new thread with ID: {thread.id}")
        admin_users_collection.update_one(
            {"username": st.session_state.username},
            {"$set": {"thread_id": st.session_state.thread_id}},
        )
        print(f"Updated admin user with thread ID: {st.session_state.thread_id}")

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}")
            # Check for any active runs and cancel them
            runs = openai_client.beta.threads.runs.list(thread_id=st.session_state.thread_id) #get list of prev/currrent runs 
            print(f"Retrieved runs: {runs.data}")
            for run in runs.data:
                if run.status in ["in_progress", "queued", "requires_action"]: #TODO: remove requires action?
                    try:
                        openai_client.beta.threads.runs.cancel(
                            run_id=run.id,
                            thread_id=st.session_state.thread_id
                        )
                        print(f"Cancelled run: {run.id}")
                    except OpenAIError as e:
                        print(f"Error cancelling run {run.id}: {str(e)}")

            # Wait for a moment to ensure cancellation is processed
            time.sleep(1)

            # Now create a new message
            openai_client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id, role="user", content=message
            )
            print(f"Created new message in thread ID: {st.session_state.thread_id} with content: {message}")

            save_admin_message(st.session_state.thread_id, "user", message) #TODO need? 
            print(f"Saved admin message for thread ID: {st.session_state.thread_id}")

            run = openai_client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id, #TODO takes care of history? 
                assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
                #TODO need instructions? What about creating assistants for unique admins? 
                instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}",
            )
            print(f"Run with ID: {run.id} for thread ID: {st.session_state.thread_id}")
            print(f"Created new run details: {run}")

            while run.status != "completed":
                run = openai_client.beta.threads.runs.retrieve( #TODO need? 
                    thread_id=st.session_state.thread_id, run_id=run.id
                )
                print(f"Retrieved run status: {run.status}")
                if run.status == "requires_action":
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls #actions or functions openai requires us to handle 
                    print(f"Tool calls requiring action: {tool_calls}")
                    tool_outputs = []
                    for tool in tool_calls:
                        if tool.function.name == "run_campaign":
                            args = json.loads(tool.function.arguments) #args for our function 
                            print(f"Arguments for run_campaign: {args}")
                            campaign_description = args.get('campaign_description', message)
                            campaign_type = args.get('campaign_type', 'generic')
                            campaign_id, assistant_id = run_campaign(campaign_description) #call function 
                            print(f"Ran campaign with ID: {campaign_id} and assistant ID: {assistant_id}")
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool.id,
                                    "output": json.dumps({
                                        "campaign_id": str(campaign_id),
                                        "assistant_id": assistant_id,
                                        "message": f"Campaign '{campaign_description}' of type '{campaign_type}' run successfully."
                                    })
                                }
                            )
                        elif tool.function.name == "query_student_chats": #TODO tool ouputs accurate to send back here? 
                            args = json.loads(tool.function.arguments)
                            print(f"Arguments for query_student_chats: {args}")
                            chat_history = query_student_chats(args['query']) #TODO query by campaign id? 
                            analysis = analyze_chat_history(args['query'], chat_history)
                            print(f"Analyzed chat history: {analysis}")
                            tool_outputs.append({
                                "tool_call_id": tool.id,
                                "output": json.dumps({"analysis": analysis})
                            })
                    if tool_outputs:
                        openai_client.beta.threads.runs.submit_tool_outputs(
                            thread_id=st.session_state.thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs,
                        )
                        print(f"Submitted tool outputs: {tool_outputs}")

            messages = openai_client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            for msg in messages.data:
                if msg.role == "assistant":
                    content = msg.content[0].text.value
                    # Get the assistant ID from the message object
                    assistant_id = msg.assistant_id
                    save_admin_message(st.session_state.thread_id, "assistant", content, assistant_id=assistant_id)
                    return content

            return "I'm sorry, I couldn't process your request at this time."

        except OpenAIError as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

    return "I'm sorry, I encountered an error while processing your request. Please try again later."


def query_student_chats(query, limit=5):
    pipeline = [
        {"$sort": {"messages.timestamp": -1}},
        {"$project": {
            "student_id": 1,
            "messages": {"$slice": ["$messages", limit]}
        }}
    ]
    chats = list(student_chats_collection.aggregate(pipeline))

    results = []
    for chat in chats:
        student = students_collection.find_one({"_id": chat["student_id"]})
        student_name = f"{student['first_name']} {student['last_name']}"
        
        for message in chat["messages"]:
            campaign = campaigns_collection.find_one({"_id": message["campaign_id"]})
            campaign_name = campaign["campaign_description"] if campaign else "Unknown Campaign"
            
            results.append({
                "student_name": student_name,
                "campaign": campaign_name,
                "role": message["role"],
                "message": message["message"]
                # Timestamp is not included here
            })

    return results

def analyze_chat_history(query, chat_history):
    analysis_prompt = f"Analyze the following student chat history based on this query: '{query}'\n\nChat History:\n{json.dumps(chat_history, indent=2)}"
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant analyzing student chat history."},
            {"role": "user", "content": analysis_prompt}
        ]
    )
    
    return response.choices[0].message.content
import os
import json
from utils import openai_client, save_message, run_campaign

OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

def get_openai_response(message, thread_id):
    # Check for active runs
    runs = openai_client.beta.threads.runs.list(thread_id=thread_id)
    active_run = next((run for run in runs.data if run.status in ["queued", "in_progress", "requires_action"]), None)

    if not active_run:
        # Create a new message and run
        openai_client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=message
        )
        save_message(thread_id, "user", message)

        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPENAI_ASSISTANT_ID,
            instructions=f"Please address the user as Miscio Admin. They are the admin to whom you are the assistant at Miscio. The user asked: {message}"
        )
    else:
        run = active_run

    # Poll for run completion
    run = openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    while run.status not in ["completed", "failed", "cancelled"]:
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []

            for tool_call in tool_calls:
                if tool_call.function.name == "run_campaign":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        if 'campaign_description' in args:
                            campaign_id = run_campaign(args['campaign_description'])
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"campaign_id": campaign_id})
                            })
                        else:
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps({"error": "Missing campaign description"})
                            })
                    except Exception as e:
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps({"error": str(e)})
                        })

            if tool_outputs:
                run = openai_client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
        
        run = openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    if run.status == "completed":
        messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
        for msg in messages.data:
            if msg.role == "assistant":
                content = msg.content[0].text.value
                save_message(thread_id, "assistant", content)
                return content

    return "I'm sorry, I couldn't process your request at this time."
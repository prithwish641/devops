import os
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    MemoryStorage,
    ConversationState,
    UserState
)
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

# Azure credentials
tenant_id = "adb53b4f-b05f-4dcb-a2e1-9111380568c3"
client_id = "9dcc52ff-3dda-4158-8ae9-9879b28abdc6"
client_secret = "47bb43fc-92bb-437d-8197-12cfe5dd4825"
subscription_id = "200c7489-b327-42c4-b931-85c9259878ae"
resource_group_name = "fs-det-AIOpsSDA"
vm_name = "AIOPS_VM"

credentials = ClientSecretCredential(tenant_id, client_id, client_secret)
compute_client = ComputeManagementClient(credentials, subscription_id)

async def shutdown_vm():
    async_poller = compute_client.virtual_machines.begin_deallocate(resource_group_name, vm_name)
    async_poller.result()
    print(f"VM {vm_name} is shut down.")

app_id = os.environ.get("MicrosoftAppId", "")
app_password = os.environ.get("MicrosoftAppPassword", "")
settings = BotFrameworkAdapterSettings(app_id, app_password)
adapter = BotFrameworkAdapter(settings)

memory_storage = MemoryStorage()
user_state = UserState(memory_storage)
conversation_state = ConversationState(memory_storage)

async def handle_message(context: TurnContext):
    user_message = context.activity.text.lower()
    if "shutdown vm" in user_message:
        await shutdown_vm()
        await context.send_activity("Shutting down the VM.")
    else:
        await context.send_activity(f'You said "{context.activity.text}"')

async def messages(req):
    body = await req.json()
    activity = TurnContext.deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    await adapter.process_activity(activity, auth_header, handle_message)
    return web.Response()

app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    web.run_app(app, port=3978)

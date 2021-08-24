from datetime import datetime, timedelta

from slack_sdk import WebClient

from slack_bolt import App, Ack
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.workflows.step import WorkflowStep, Configure, Update, Complete, Fail

app = App(
    # TODO: move secrets to env vars
    token='xoxb-2381002964196-2398730251988-s2b23yJJUURWLVczQpkzJEbn',
    signing_secret='2350a96485c3b20632211c5b04dff76f',
    process_before_response=True
)


def edit(ack: Ack, configure: Configure):
    ack()

    initial_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    blocks = [
        {
            "type": "section",
            "block_id": "intro-section",
            "text": {
                "type": "plain_text",
                "text": "Select vacation dates",
            },
        },
        {
            "type": "input",
            "block_id": "vacation_start",
            "label": {
                "type": "plain_text",
                "text": "Pick a start date for your vacation."
            },
            "element": {
                "type": "datepicker",
                "action_id": "vacation_start",
                "initial_date": initial_date,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                }
            }
        },
        {
            "type": "input",
            "block_id": "vacation_end",
            "label": {
                "type": "plain_text",
                "text": "Pick an end date for your vacation."
            },
            "element": {
                "type": "datepicker",
                "action_id": "vacation_end",
                "initial_date": initial_date,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a date"
                }
            }
        }
    ]
    configure(blocks=blocks)


def save(ack: Ack, view: dict, update: Update):
    values = view["state"]["values"]
    print(f"values: {values}")

    inputs = {
        'start_date': {'value': values['vacation_start']['vacation_start']['selected_date']},
        'end_date': {'value': values['vacation_end']['vacation_end']['selected_date']}
    }
    outputs = [
        {
            "type": "text",
            "name": "start_date",
            "label": "Vacation start",
        },
        {
            "type": "text",
            "name": "end_date",
            "label": "Vacation end",
        }
    ]
    update(inputs=inputs, outputs=outputs)
    ack()


def execute(step: dict, client: WebClient, complete: Complete, fail: Fail):
    try:
        inputs = step["inputs"]
        outputs = {
            "start_date": inputs["start_date"]["value"],
            "end_date": inputs["end_date"]["value"],
            # "task_description": inputs["task_description"]["value"],
        }
        complete(outputs=outputs)
    except Exception as err:
        fail(error={"error": str(err)})


# Create a new WorkflowStep instance
# ws = WorkflowStep(
#     callback_id="vacation",
#     edit=edit,
#     save=save,
#     execute=execute,
# )
# Pass Step to set up listeners
app.step(callback_id="vacation",
         edit=edit,
         save=save,
         execute=execute)


def lambda_handler(event, context):
    print(f"Received event: {event}")
    slack_handler = SlackRequestHandler(app=app)

    return slack_handler.handle(event, context)

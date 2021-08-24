from datetime import datetime, timedelta

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse

from slack_bolt import App, Ack
from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.workflows.step import WorkflowStep, Configure, Update, Complete, Fail

# Initiate the Bolt app as you normally would
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
        print(f'==== step ====: {step}')
        inputs = step["inputs"]
        # if everything was successful
        outputs = {
            "start_date": inputs["start_date"]["value"],
            "end_date": inputs["end_date"]["value"],
            # "task_description": inputs["task_description"]["value"],
        }
        complete(outputs=outputs)

        home_tab_update: SlackResponse = client.dialog_open(
            dialog={
                "callback_id": "vaction",
                "title": "Request something",
                "submit_label": "Request",
                "state": "Max",
                "elements": [
                    {
                        "type": "text",
                        "label": "Origin",
                        "name": "loc_origin"
                    },
                    {
                        "type": "text",
                        "label": "Destination",
                        "name": "loc_destination"
                    }
                ]
            },
            trigger_id=step['workflow_step_execute_id']
        )
        # views_publish(
        #     user_id=user_id,
        #     view={
        #         "type": "home",
        #         "title": {"type": "plain_text", "text": "Your tasks!"},
        #         "blocks": blocks,
        #     },
        # )

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
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e
    print(f"Received event: {event}")
    slack_handler = SlackRequestHandler(app=app)
    return slack_handler.handle(event, context)

    # body = event['body']
    # # challenge = body['challenge']
    # # print(f'{body}, type: {type(body)} challenge: {challenge}')
    #
    # trigger_id = json.loads(parse.parse_qs(parse.unquote(body))['payload'][0])['trigger_id']
    # print(f"{trigger_id}")
    # # slack_body = event.get("body")
    # # slack_event = json.loads(slack_body) if slack_body else {}
    # # challenge_answer = 'slack_event.get("challenge")'
    #
    # blocks = [
    #     {
    #         "type": "section",
    #         "block_id": "start_date",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": "Pick a start date for your vacation."
    #         },
    #         "accessory": {
    #             "type": "datepicker",
    #             "action_id": "datepicker_start",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Select a date"
    #             }
    #         }
    #     },
    #     {
    #         "type": "section",
    #         "block_id": "section12345",
    #         "text": {
    #             "type": "mrkdwn",
    #             "text": "Pick an end date for your vacation"
    #         },
    #         "accessory": {
    #             "type": "datepicker",
    #             "action_id": "datepicker_end",
    #             "placeholder": {
    #                 "type": "plain_text",
    #                 "text": "Select a date"
    #             }
    #         }
    #     }
    # ]
    #
    # # send_text_response(event, "Hello World From Lambda", trigger_id=trigger_id)
    #
    # return {"ok": "true"}
    #     # {
    #     # 'statusCode': 200,
    #     # 'body': challenge
    # # }

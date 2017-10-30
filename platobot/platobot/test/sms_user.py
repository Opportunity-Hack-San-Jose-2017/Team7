from platobot.constants import Channels
from platobot.message import message_callback


def init_request():
    state = 0
    responses = ["hi", "yes", "Kenya", "1", "I need help. I'm trapped."]
    user_number = "254-123-456-7890"

    print("{} sent: {}".format(user_number, responses[state]))
    next_question = message_callback(Channels.SMS, user_number=user_number, msg=responses[state])

    while state < len(responses):
        print("{} received: {}".format(user_number, next_question))
        state += 1
        if state < len(responses):
            print("{} sent: {}".format(user_number, responses[state]))
            next_question = message_callback(Channels.SMS, user_number=user_number, msg=responses[state])
    return


if __name__ == "__main__":
    init_request()

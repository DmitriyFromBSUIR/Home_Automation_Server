

class Provider:

    def __init__(self):
        self.msg_queue = []
        self.subscribers = {}

    def notify(self, msg):
        self.msg_queue.append(msg)

    def subscribe(self, msg, subscriber):
        self.subscribers.setdefault(msg, []).append(subscriber)

    def unsubscribe(self, msg, subscriber):
        self.subscribers[msg].remove(subscriber)

    def update(self):
        for msg in self.msg_queue:
            for sub in self.subscribers.get(msg, []):
                sub.run(msg)
        self.msg_queue = []


class Publisher:

    def __init__(self, msg_center):
        self.provider = msg_center

    def publish(self, msg):
        self.provider.notify(msg)


class Subscriber:

    def __init__(self, name, msg_center):
        self.name = name
        self.provider = msg_center

    def setMsgProvider(self, msg_center):
        self.provider = msg_center

    def subscribe(self, msg):
        self.provider.subscribe(msg, self)

    def unsubscribe(self, msg):
        self.provider.unsubscribe(msg, self)

    def run(self, msg):
        print("{} got {}".format(self.name, msg))


def test():
    message_center = Provider()

    pub_events_emitter_center = Publisher(message_center)

    jim = Subscriber("jim", message_center)
    jim.subscribe("cartoon")
    jim.subscribe("movie")
    jack = Subscriber("jack", message_center)
    jack.subscribe("music")
    gee = Subscriber("gee", message_center)
    gee.subscribe("movie")
    vani = Subscriber("vani", message_center)
    vani.subscribe("movie")
    vani.unsubscribe("movie")

    pub_events_emitter_center.publish("cartoon")
    pub_events_emitter_center.publish("music")
    pub_events_emitter_center.publish("ads")
    pub_events_emitter_center.publish("movie")
    pub_events_emitter_center.publish("cartoon")
    pub_events_emitter_center.publish("cartoon")
    pub_events_emitter_center.publish("movie")
    pub_events_emitter_center.publish("blank")

    message_center.update()

def mytest2():
    # create environment for messaging
    message_center = Provider()
    # create object for event publications
    pub_events_emitter_center = Publisher(message_center)

    # create subscriber with name "Lamp"
    lamp = Subscriber("Lamp", message_center)
    # subscribe Lamp on event "on"
    lamp.subscribe("on")
    # create subscriber with name "Dimmer"
    dimmer = Subscriber("Dimmer", message_center)
    # subscribe Dimmer on event "off"
    dimmer.subscribe("off")
    # create subscriber with name "Selector"
    selector = Subscriber("Selector", message_center)
    # subscribe Selector on event "num_value = 5"
    selector.subscribe("num_value = 5")
    selector.subscribe("num_value = 20")
    selector.unsubscribe("num_value = 20")
    selector.subscribe("lamp = on")

    pub_events_emitter_center.publish("on")
    pub_events_emitter_center.publish("off")
    pub_events_emitter_center.publish("num_value = 5")
    pub_events_emitter_center.publish("lamp = on")

    message_center.update()

if __name__ == "__main__":
    mytest2()
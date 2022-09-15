from mongoengine import *

class Website(Document):
    domain = StringField(required=True, unique=True)
    tags = ListField(StringField())


class Page(Document):
    url = StringField(required=True, unique=True)
    domain = ReferenceField(Website, reverse_delete_rule=CASCADE, required=True)
    tags = ListField(StringField())
    linked_from = ListField(ReferenceField(Website))

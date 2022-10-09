from mongoengine import *

class Website(Document):
    domain = StringField(required=True, unique=True)
    ranking = IntField()
    tags = ListField(StringField())

    meta = {'indexes': [{
        'fields': ['$domain'],
        'default_language': 'english',
    }]}

class Page(Document):
    title = StringField()
    description = StringField(max_length=300)
    url = StringField(required=True, unique=True)

    domain = ReferenceField(Website, reverse_delete_rule=CASCADE, required=True)
    linked_from = ListField(ReferenceField(Website))
    tags = ListField(StringField())

    meta = {'indexes': [
        {'fields': ['$title', "$description"],
         'default_language': 'english',
         'weights': {'title': 10, 'content': 5}
        }
    ]}
    
    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self.save()

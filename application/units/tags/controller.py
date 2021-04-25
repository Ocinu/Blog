from application.models import Tags, ControlDB


class NewTag(ControlDB):
    def __init__(self, tag_name):
        super().__init__()
        self.tag_name = tag_name

    @property
    def tag_name(self):
        return self._tag_name

    @tag_name.setter
    def tag_name(self, value: str):
        self._tag_name = value

    def save_tag(self):
        new_tag = Tags()
        new_tag.tag_name = self.tag_name
        if self.save_to_db(new_tag):
            return True
        return False


class TagController:
    def __init__(self, tag_id):
        self.tag = Tags.query.get(tag_id)


class TagTotal:
    def __init__(self):
        self.tags = Tags.query.all()

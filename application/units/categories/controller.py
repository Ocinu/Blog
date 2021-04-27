from application.models import Categories, ControlDB


class NewCategory(ControlDB):
    def __init__(self, category_name):
        super().__init__()
        self.category_name = category_name

    @property
    def category_name(self):
        return self._category_name

    @category_name.setter
    def category_name(self, value: str):
        self._category_name = value

    def add_new_category(self):
        new_cat = Categories()
        new_cat.category_name = self.category_name
        self.save_to_db(new_cat)


class CategoryController(ControlDB):
    def __init__(self, category_id):
        super().__init__()
        self.category = Categories.query.get(category_id)

    def delete_category(self):
        self.delete_from_db(self.category)


class CategoriesTotal:
    def __init__(self):
        self.categories = Categories.query.all()

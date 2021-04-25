from application.models import Categories


class CategoryController:
    def __init__(self, category_id):
        self.category = Categories.query.get(category_id)


class CategoriesTotal:
    def __init__(self):
        self.categories = Categories.query.all()


from application.routes import MainRoutes
from application.units.users.routes import UserRoutes
from application.units.articles.routes import ArticleRoutes
from application.units.categories.routes import CategoryRoutes
from application.units.tags.routes import TagRoutes

from app import app, manager

main_routes = MainRoutes(app, manager)
user_routes = UserRoutes(app)
article_routes = ArticleRoutes(app)
category_routes = CategoryRoutes(app)
tag_routes = TagRoutes(app)

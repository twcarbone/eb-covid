from app.api import bp


@bp.route("/hello")
def index():
    return "Hello from the EB Covid Data API!"
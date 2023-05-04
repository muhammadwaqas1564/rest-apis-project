import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate



from db import db
from blocklist import BLOCKLIST
import models




from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint



def create_app(db_url = None):
    app = Flask(__name__)

    app.config["PROPEGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
    
    db.init_app(app)
    migrate = Migrate(app,db)
    api = Api(app)
    


    app.config["JWT_SECRET_KEY"] = "jose"
    jwt = JWTManager(app)


    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_calback(jwt_header,jwt_payload):
        return (
            jsonify(
            {"Discription":"the token has been revoked","Error":"Token revoked"}
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callabler(jwt_header,jwt_payload):
        return(
            jsonify(
            {
                "description":"the token is not fresh",
                "error": "fresh_token_required"
            }
            ),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin":True}
        return {"is_admin":False}


    @jwt.expired_token_loader
    def expired_token_callable(jwt_header,jwt_payload):
        return (
            jsonify(
            {
                "message":"the token has been expired.","error":"token expired"
            }
            ), 401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callable(error):
        return(
            jsonify(
            {
                "message":"Signature verification failed","error":"invalid_token"
            }
            ), 401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callable(error):
        jsonify(
            {
                "Discription":"request does not contain an access token",
                "error":"authorization_required"
            }
            ), 401


    # with app.app_context():
    #     db.create_all()
    # @app.before_first_request
    # def create_tables():
    #     db.create_all()

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
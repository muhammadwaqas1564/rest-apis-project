from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError,IntegrityError

from db import db
from models import TagModel,StoreModel,ItemModel
from schemas import TagSchema,TagAndItemSchema


blp = Blueprint("Tags", "tags" , description="operation on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self,store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()


    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(seld,tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500,str(e))
        
        return tag


@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItems(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(
                500,
                "An Error occured while inserting the tag"
            )
        return tag

    @blp.response(200,TagAndItemSchema )
    def delete(self, item_id,tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = ItemModel.query.get_or_404(tag_id)
        
        item.tags.remove(tag)

        try: 
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(
                500,
                "An Error occured while inserting the tag"
            )
        return {"messege":"Item removed from tag","item":item,"tag":tag}




@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    

    @blp.response(
        202,
        description="Deletes a tag if no item is tags with it",
        example={"messege":"tag deleted."}
    )
    @blp.alt_response(404,description="Tag not found")
    @blp.alt_response(
        400,
        description="Returned if the tag as assignd to one or more items, in this case, the tag is not deleted"
    )
    def delete(self,tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"messege":"Tag deleted"}
        abort(
            400,
        "Could not delete tag. Make sure tag is associated with any item, then try againv"
        )
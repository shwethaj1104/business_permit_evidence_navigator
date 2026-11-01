from uuid import uuid4

from pymongo import ReturnDocument

from app.core.errors import AppError
from app.core.logging import logged_operation
from app.models.domain import Record, utcnow

PAGE_SIZE = 40


class ConversationRepository:
    """Keep conversation metadata small and retain all messages in separate records."""

    def __init__(self, db):
        # Share a database while separating history navigation from message storage.
        self.collection, self.messages = db.conversations, db.conversation_messages

    def require(self, conversation_id):
        # Read one existing conversation without silently substituting another.
        row = self.collection.find_one({"id": conversation_id}, {"_id": 0})
        if not row:
            raise AppError("Conversation not found. Start a new conversation.", 404)
        return row

    @logged_operation("conversations.history")
    def get(self, conversation_id, before=None):
        # Return a cursor page while preserving legacy embedded messages already stored.
        row = self.require(conversation_id)
        legacy = [
            {**message, "id": f"{conversation_id}:legacy:{index}", "order": index}
            for index, message in enumerate(row.get("messages", []))
        ]
        query = {"conversation_id": conversation_id}
        if before is not None:
            query["order"] = {"$lt": before}
        recent = list(self.messages.find(query, {"_id": 0}).sort("order", -1).limit(PAGE_SIZE + 1))
        combined = [message for message in legacy if before is None or message["order"] < before] + recent
        combined.sort(key=lambda message: message["order"])
        page = combined[-PAGE_SIZE:]
        return Record.model_validate(
            {
                "id": conversation_id,
                "profile_id": row["profile_id"],
                "messages": page,
                "has_older": len(combined) > PAGE_SIZE,
                "oldest_order": page[0]["order"] if page else None,
            }
        )

    @logged_operation("conversations.list")
    def list(self, profile_id, before=None):
        # Paginate all saved chats using stable creation-time and ID ordering.
        query = {"profile_id": profile_id} if profile_id is not None else {}
        if before:
            cursor = self.require(before)
            if profile_id is not None and cursor["profile_id"] != profile_id:
                raise AppError("Conversation cursor belongs to another profile.", 422)
            query["$or"] = [
                {"created_at": {"$lt": cursor["created_at"]}},
                {"created_at": cursor["created_at"], "id": {"$lt": before}},
            ]
        rows = list(self.collection.find(query, {"_id": 0}).sort([("created_at", -1), ("id", -1)]).limit(21))
        summaries = []
        for row in rows[:20]:
            old = row.get("messages", [])
            summaries.append(
                {
                    "id": row["id"],
                    "profile_id": row["profile_id"],
                    "title": row.get("title") or (old[0]["text"][:80] if old else "Untitled chat"),
                    "created_at": row["created_at"],
                    "updated_at": row.get("updated_at", row["created_at"]),
                    "preview": row.get("preview", ""),
                }
            )
        return {"conversations": summaries, "next_cursor": rows[19]["id"] if len(rows) > 20 else None}

    @logged_operation("conversations.rename")
    def rename(self, conversation_id, title):
        # Update navigation metadata while preserving messages and creation order.
        self.require(conversation_id)
        self.collection.update_one({"id": conversation_id}, {"$set": {"title": title}})

    @logged_operation("conversations.delete")
    def delete(self, conversation_id):
        # Remove metadata first to prevent new turns from being appended during deletion.
        result = self.collection.delete_one({"id": conversation_id})
        if not result.deleted_count:
            raise AppError("Conversation not found.", 404)
        self.messages.delete_many({"conversation_id": conversation_id})

    @logged_operation("conversations.save")
    def append(self, profile_id, conversation_id, question, answer):
        # Allocate ordered message slots atomically without trimming prior conversations.
        now = utcnow()
        if conversation_id:
            previous = self.require(conversation_id)
            if previous["profile_id"] is not None and previous["profile_id"] != profile_id:
                raise AppError("Start a new conversation for a different profile.", 409)
            if previous["profile_id"] is None and profile_id is not None:
                result = self.collection.update_one(
                    {"id": conversation_id, "profile_id": None},
                    {"$set": {"profile_id": profile_id}},
                )
                if not result.modified_count:
                    raise AppError("Conversation profile changed. Please retry.", 409)
            self.collection.update_one(
                {"id": conversation_id, "message_count": {"$exists": False}},
                {"$set": {"message_count": len(previous.get("messages", []))}},
            )
        else:
            conversation_id = str(uuid4())
            self.collection.insert_one(
                {
                    "id": conversation_id,
                    "profile_id": profile_id,
                    "created_at": now,
                    "title": question[:80],
                    "message_count": 0,
                }
            )
        row = self.collection.find_one_and_update(
            {"id": conversation_id},
            {"$inc": {"message_count": 2}, "$set": {"updated_at": now, "preview": question[:100]}},
            return_document=ReturnDocument.AFTER,
        )
        first_order = row["message_count"] - 2
        self.messages.insert_many(
            [
                {
                    "id": str(uuid4()),
                    "conversation_id": conversation_id,
                    "order": first_order,
                    "role": "user",
                    "text": question,
                    "answer": None,
                    "created_at": now,
                },
                {
                    "id": str(uuid4()),
                    "conversation_id": conversation_id,
                    "order": first_order + 1,
                    "role": "assistant",
                    "text": answer.message,
                    "answer": answer.model_dump(),
                    "created_at": now,
                },
            ]
        )
        return self.get(conversation_id)

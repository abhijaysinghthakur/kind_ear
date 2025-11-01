"""Report model."""
from datetime import datetime
from bson import ObjectId
from ..extensions import db


class Report:
    """Report model for abuse reporting."""

    collection = db.reports

    @staticmethod
    def create(reporter_id, reported_user_id, reason, description, chat_session_id=None, message_id=None):
        """Create a new report."""
        if isinstance(reporter_id, str):
            reporter_id = ObjectId(reporter_id)
        if isinstance(reported_user_id, str):
            reported_user_id = ObjectId(reported_user_id)
        if chat_session_id and isinstance(chat_session_id, str):
            chat_session_id = ObjectId(chat_session_id)
        if message_id and isinstance(message_id, str):
            message_id = ObjectId(message_id)

        report_doc = {
            'reporter_id': reporter_id,
            'reported_user_id': reported_user_id,
            'chat_session_id': chat_session_id,
            'message_id': message_id,
            'reason': reason,
            'description': description,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'reviewed_at': None,
            'reviewed_by': None,
            'resolution': None
        }

        result = Report.collection.insert_one(report_doc)
        report_doc['_id'] = result.inserted_id
        return report_doc

    @staticmethod
    def find_by_id(report_id):
        """Find report by ID."""
        if isinstance(report_id, str):
            report_id = ObjectId(report_id)
        return Report.collection.find_one({'_id': report_id})

    @staticmethod
    def get_all(filters=None, page=1, limit=20):
        """Get all reports with pagination and optional filters."""
        query = {}

        if filters and 'status' in filters:
            query['status'] = filters['status']

        skip = (page - 1) * limit
        reports = list(Report.collection.find(query).sort('created_at', -1).skip(skip).limit(limit))
        total = Report.collection.count_documents(query)

        return reports, total

    @staticmethod
    def update_status(report_id, status, admin_id, resolution=None):
        """Update report status and resolution."""
        if isinstance(report_id, str):
            report_id = ObjectId(report_id)
        if isinstance(admin_id, str):
            admin_id = ObjectId(admin_id)

        update_data = {
            'status': status,
            'reviewed_at': datetime.utcnow(),
            'reviewed_by': admin_id
        }

        if resolution:
            update_data['resolution'] = resolution

        Report.collection.update_one(
            {'_id': report_id},
            {'$set': update_data}
        )

    @staticmethod
    def count_pending():
        """Count pending reports."""
        return Report.collection.count_documents({'status': 'pending'})

    @staticmethod
    def to_dict(report_doc, include_users=False):
        """Convert report document to dictionary."""
        if not report_doc:
            return None

        result = {
            'id': str(report_doc['_id']),
            'reporter_id': str(report_doc['reporter_id']),
            'reported_user_id': str(report_doc['reported_user_id']),
            'chat_session_id': str(report_doc['chat_session_id']) if report_doc.get('chat_session_id') else None,
            'message_id': str(report_doc['message_id']) if report_doc.get('message_id') else None,
            'reason': report_doc['reason'],
            'description': report_doc['description'],
            'status': report_doc['status'],
            'created_at': report_doc['created_at'].isoformat(),
            'reviewed_at': report_doc['reviewed_at'].isoformat() if report_doc.get('reviewed_at') else None,
            'resolution': report_doc.get('resolution')
        }

        return result

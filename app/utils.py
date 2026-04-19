from datetime import datetime,timezone
from app.models import TokenBlockList
from app.extensions import db
import logging

def cleanup_expired_tokens():
    current_time=datetime.now(timezone.utc)
    deleted=TokenBlockList.query.filter(TokenBlockList.expires_at < current_time).delete()
    db.session.commit()
    logging.info(f"[CLEANUP] Deleted {deleted} expired tokens")
import pytz
import tzlocal
from flask_security import (
    RoleMixin,
    UserMixin,
)
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Unicode,
)
from sqlalchemy.orm import (
    backref,
    relationship,
)

from mxcubeweb.core.components.user.database import Base


class RolesUsers(Base):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey("user.id"))
    role_id = Column("role_id", Integer(), ForeignKey("role.id"))


class Role(Base, RoleMixin):
    __tablename__ = "role"
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class MessagesUsers(Base):
    __tablename__ = "messages_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", Integer(), ForeignKey("user.id"))
    message_id = Column("message_id", Integer(), ForeignKey("message.id"))


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer(), primary_key=True)
    at = Column(DateTime())
    message = Column(Text())
    read = Column(Boolean(False))
    from_username = Column(String(255), unique=False)
    from_nickname = Column(String(255), unique=False)
    from_host = Column(String(255), unique=False)


class User(Base, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(Unicode, unique=True, nullable=True)
    nickname = Column(String(255), unique=False)
    fullname = Column(String(255), unique=False)
    password = Column(String(255), nullable=False)
    session_id = Column(String(255), unique=False)
    socketio_session_id = Column(String(255), unique=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    requests_control = Column(Boolean(False))
    requests_control_msg = Column(String(255))
    in_control = Column(Boolean(False))
    selected_proposal = Column(String(255), unique=False)
    proposal_list = Column(JSON, unique=False)
    current_limssession = Column(JSON, unique=False)
    limsdata = Column(JSON, unique=False)
    last_request_timestamp = Column(DateTime())
    refresh_token = Column(String(255), unique=True)
    token = Column(String(255), unique=True)
    roles = relationship(
        "Role",
        secondary="roles_users",
        backref=backref("users", lazy="dynamic"),
    )
    messages = relationship(
        "Message",
        secondary="messages_users",
        backref=backref("users", lazy="dynamic"),
    )

    def has_roles(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    @property
    def isstaff(self):
        return "staff" in self.roles

    def todict(self):
        # Database stores dates in UTC
        current_login_at_str = ""

        if self.current_login_at:
            clt_dt = self.current_login_at.replace(tzinfo=pytz.timezone("UTC"))
            current_login_at_str = clt_dt.astimezone(tzlocal.get_localzone()).strftime(
                "%Y/%m/%d, %H:%M:%S"
            )

        return {
            "username": self.username,
            "email": self.email,
            "isstaff": "staff" in self.roles,
            "nickname": self.nickname,
            "inControl": self.in_control,
            "ip": self.current_login_ip,
            "currentLoginAt": current_login_at_str,
            "requestsControl": self.requests_control,
            "requestsControlMsg": self.requests_control_msg,
            "fullname": self.fullname,
        }

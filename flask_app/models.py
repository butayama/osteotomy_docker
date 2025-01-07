"""
models.py
"""

from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from flask_app.exceptions import ValidationError
from . import db, login_manager


class Permission:
    """
    Represents different levels of permissions associated with user roles.

    This class defines constants representing various permission levels.
    These constants can be used to assign or compare permissions in user
    management systems.

    Attributes:
        FOLLOW (int): Permission level allowing a user to follow other users.
        COMMENT (int): Permission level allowing a user to make comments.
        WRITE (int): Permission level allowing a user to create or write content.
        MODERATE (int): Permission level allowing a user to moderate content
        such as approving or rejecting submissions.
        ADMIN (int): Permission level granting full administrative access.
    """
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    """
    Represents a role within the application, which defines a set of permissions
    and is associated with users. Roles also define a default role for new users.

    This class includes methods for managing permissions, resetting them, checking
    permission existence, and inserting predefined roles.
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    """
    Represents the 'follows' relationship between users in a social network.

    This class models a many-to-many relationship where a user can follow other
    users. It stores the IDs of the follower and the followed user, along with
    the time the follow action was performed. Utilized in database interactions
    to store and query follow relationships within the application.

    Attributes:
        __tablename__ (str): Specifies the table name in the database.
        follower_id: The ID of the user who is following another user.
        followed_id: The ID of the user being followed.
        timestamp: The time when the follow action was recorded.
    """
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    """
    Represents a user in the application with authentication, authorization, and
    profile management capabilities.

    The User class integrates with a database and a web application context to handle user
    information, authentication, and role-based access control. It supports functionalities
    such as verifying passwords, managing user roles, generating tokens for actions like
    confirmation and password resets, managing follow relationships, and creating user-specific
    representations. The class is designed to be used as part of a larger application that
    handles user data and interactions, leveraging SQLAlchemy for database interactions.

    Attributes:
        __tablename__ (str): The name of the table in the database.
        id (int): The unique identifier for a user.
        email (str): The email address of the user.
        username (str): The username chosen by the user.
        role_id (int): The foreign key linking the user to their role.
        password_hash (str): The hashed representation of the user's password.
        confirmed (bool): Indicates whether the user's account has been confirmed.
        name (str): The full name of the user.
        location (str): The geographical location of the user.
        about_me (str): A self-description of the user.
        member_since (datetime): The date and time when the user joined.
        last_seen (datetime): The date and time when the user was last active.
        avatar_hash (str): The hash value for the user's gravatar.
        posts (query): A dynamic list of posts authored by the user.
        followed (query): A list of users that the user is following.
        followers (query): A list of users that follow the user.
        comments (query): A dynamic list of comments made by the user.

    Methods:
        add_self_follows:
            Adds a self-follow for every user in the database if not already present.

        password:
            Property to restrict access and modification of raw password values.

        verify_password:
            Verifies that the entered password matches the stored hash.

        generate_confirmation_token:
            Generates a token for email confirmation with a given expiration.

        confirm:
            Confirms a user's account using a provided token.

        generate_reset_token:
            Generates a token for resetting the password with a given expiration.

        reset_password (staticmethod):
            Resets the password for a user identified by a token.

        generate_email_change_token:
            Generates a token for changing the email address of the user.

        change_email:
            Updates the user's email address using an email change token.

        can:
            Checks if a user has a specific permission.

        is_administrator:
            Checks if the user has administrator privileges.

        ping:
            Updates the user's last_seen timestamp to the current time.

        gravatar_hash:
            Computes a hash based on the user's email for generating a Gravatar.

        gravatar:
            Generates a Gravatar URL for the user based on their email hash.

        follow:
            Follows another user if not already following.

        unfollow:
            Unfollows a user if currently following.

        is_following:
            Checks if the current user is following another user.

        is_followed_by:
            Checks if the current user is followed by another user.

        followed_posts:
            Property to retrieve posts by users followed by the current user.

        to_json:
            Converts the user object into a JSON serializable dictionary.

        generate_auth_token:
            Produces an authentication token for the user with an expiration.

        verify_auth_token (staticmethod):
            Validates an authentication token and retrieves the user.

        __repr__:
            Provides a string representation of the user instance.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()
        self.follow(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts',
                                          id=self.id),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    """
    Represents an anonymous user with no permissions or administrative privileges.

    This class extends the AnonymousUserMixin to provide methods for checking user
    permissions and administrative status. It is generally used in cases where a user
    is not authenticated or does not have a specific role in the system.
    """
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """
    This function is a Flask-Login user loader. It retrieves a user object from the database
    using the provided user ID. The retrieved user object allows Flask-Login to manage the
    user session. The function expects the user ID to be passed as an argument and converts
    it to an integer before querying the database.

    Args:
        user_id (str): The ID of the user as a string.

    Returns:
        User: A User object corresponding to the provided user ID or None if no user
        is found.
    """
    return User.query.get(int(user_id))


class Post(db.Model):
    """
    Represents a blog post in the application.

    The `Post` class models a blog post and contains related metadata, such as
    its creation timestamp, author, and associated comments. It also includes
    methods for converting posts to and from JSON format for API communication.

    Attributes
    ----------
    id : int
        Unique identifier for the post.
    body : str
        Content of the post.
    body_html : str
        HTML-rendered content of the post.
    timestamp : datetime
        The time when the post was created.
    author_id : int
        Foreign key referencing the id of the author user.
    comments : dynamic relationship
        Relationship to the `Comment` model representing comments on the post.

    Methods
    -------
    on_changed_body(target: Any, value: Any, oldvalue: Any, initiator: Any)
        Automatically sanitizes and renders the post body as HTML when the body
        content is changed.

    to_json() -> dict
        Converts the post object into a JSON-serializable dictionary containing
        key details about the post.

    from_json(json_post: dict) -> 'Post'
        Creates a `Post` object from a JSON dictionary by extracting the post
        body and initializing the post. Raises a `ValidationError` if the JSON
        does not contain a valid post body.
    """
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Comment(db.Model):
    """
    Represents a comment within a blogging system.

    This class defines the structure of a comment and its associated properties,
    including the ability to process and transform the comment body, convert
    its attributes to a JSON-serializable format, and create a comment from
    JSON data. It is designed to work with SQLAlchemy and is part of a broader
    database schema for a blogging or similar content-management application.

    Attributes
    ----------
    id : int
        Unique identifier for the comment.
    body : str
        The plain-text body of the comment written by the user.
    body_html : str
        The HTML-rendered version of the comment body.
    timestamp : datetime
        Date and time the comment was created (default is the current UTC time).
    disabled : bool
        Indicates whether the comment is disabled.
    author_id : int
        Foreign key linking the comment to its author (user).
    post_id : int
        Foreign key linking the comment to its associated post.

    Methods
    -------
    on_changed_body(target, value, oldvalue, initiator)
        Transforms the body of the comment into sanitized HTML when the
        body value changes. Ensures that only allowed HTML tags are present.

    to_json()
        Converts the comment attributes into a JSON-serializable dictionary
        for API responses.

    from_json(json_comment)
        Creates a new Comment object from a JSON dictionary. Validates that
        the dictionary includes a non-empty "body" field.

    Raises
    ------
    ValidationError
        Raised by from_json when the "body" field in the input JSON data
        is missing or empty.
    """
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id),
            'post_url': url_for('api.get_post', id=self.post_id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)

class UserMixin:
    __hash__ = object.__hash__
    @property
    def is_active(self):
        return True
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        try:
            return str(self.id)
        except AttributeError as error:
            raise error ('No user id found')
    
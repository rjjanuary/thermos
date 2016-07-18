from flask_wtf import Form
from wtforms.fields import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf.html5 import URLField
from wtforms.validators import DataRequired, url, Length, Email, Regexp, EqualTo,\
    url, ValidationError

from models import User


class BookmarkForm(Form):
    url = URLField('The URL of your bookmark:', validators=[DataRequired(), url()])
    description = StringField('Add an optional description:')
    tags = StringField('Tags', validators=[Regexp(r'^[a-zA-Z0-9, ]*$',
                  message="Tags can only contain letters and numbers")])

    def validate(self):
        if not self.url.data.startswith("http://") or \
            self.url.data.startswith("https://"):
                self.url.data = "http://" + self.url.data

        if not Form.validate(self):
            return False

        if not self.description.data:
            self.description.data = self.url.data

        #filter out empty and duplicate tag names
        stripped = [t.strip() for t in self.tags.data.split(',')] #split string on comma, strip whitespace
        not_empty = [tag for tag in stripped if tag] #filter out blanks
        tagset = set(not_empty) #put remaining items in a set, which inherently deduplicates
        self.tags.data=','.join(tagset) #join back into a csv string

        return True


from flask.ext import wtf

class ProfileUpdateForm(wtf.Form):
  name = wtf.TextField('Name', [wtf.validators.required()])
  email = wtf.TextField('Email', [
      wtf.validators.optional(),
      wtf.validators.email("That doesn't look like an email"),
    ])
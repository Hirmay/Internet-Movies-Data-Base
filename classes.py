# Creating search classes in this python file
from wtforms import Form, StringField, SelectField
class Search_M_W(Form):
    choices = [('Movie', 'Movie'),
               ('Web-Series', 'Web-Series'), ('Celebrity', 'Celebrity'),
              ('Director', 'Director')]
    select = SelectField('Search:', choices=choices)
    search = StringField('')

class ADD_M_W(Form):
    choices = [('Movie', 'Movie'),
               ('Web-Series', 'Web-Series')]
    select = SelectField('Add a Movie or Web-Series:', choices=choices)
    search = StringField('')  
    
class DELETE_M_W(Form):
    choices = [('Movie', 'Movie'),
               ('Web-Series', 'Web-Series')]
    select = SelectField('Delete a Movie or Web-Series:', choices=choices)
    search = StringField('')  
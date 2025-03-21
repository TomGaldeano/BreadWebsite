import datetime
from datetime import date, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, NoneOf, ValidationError, Length

from config import Data

data = Data()
message_ = "No bread on wednesday, saturday or sunday"



class FutureDaysOnly(object):
    def __call__(self, form, field):
        if field.data <= datetime.date.today():
            raise ValidationError("Current day is not valid")

future_days_only = FutureDaysOnly


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[DataRequired(message="required field"), NoneOf(data.invalid_characters, message="invalid symbol used")])
    group = StringField(validators=[DataRequired(message="required field"),
                                    NoneOf(data.invalid_characters, message="invalid symbol used")])
    email = StringField(validators=[DataRequired(message="required field"),
                                    NoneOf(data.invalid_characters, message="invalid symbol used")])
    password = PasswordField(validators=[DataRequired(), NoneOf(data.invalid_characters, message="invalid symbol used"),
                                         Length(min = 8, max= 50, message= "password must be 8 to 50 characters long")])
    submit = SubmitField("Register")

def generate_basic_form(num_entries, message):
    """Dynamically creates a FlaskForm with num_entries BooleanFields."""
    class DynamicDeleteForm(FlaskForm):
        pass

    # Add fields dynamically to the class
    for i in range(1, num_entries + 1):
        setattr(DynamicDeleteForm, f"field_{i}", BooleanField())

    setattr(DynamicDeleteForm, "submit", SubmitField("message"))

    return DynamicDeleteForm

class DeleteUserForm(FlaskForm):
    users_to_delete = StringField(validators=[DataRequired(message="required field"),
                                       NoneOf(data.invalid_characters, message="invalid symbol used")])
    submit = SubmitField("Delete")

class DeleteAccountForm(FlaskForm):
    submit = SubmitField("Delete")

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(message="required field"),
                                       NoneOf(data.invalid_characters, message="invalid symbol used")])
    password = PasswordField(validators=[DataRequired(), NoneOf(data.invalid_characters, message="invalid symbol used")])
    submit = SubmitField("Log in")

class ModifyUser(FlaskForm):
    username = StringField(validators=[DataRequired(message="required field"),
                                       NoneOf(data.invalid_characters, message="invalid symbol used")])
    old_password = PasswordField(validators=[DataRequired(), NoneOf(data.invalid_characters, message="invalid symbol used")])
    new_password = PasswordField(validators=[NoneOf(data.invalid_characters, message="invalid symbol used")])
    group = StringField(validators=[DataRequired(message="required field"),
                                    NoneOf(data.invalid_characters, message="invalid symbol used")])
    email = StringField(validators=[DataRequired(message="required field"),
                                    NoneOf(data.invalid_characters, message="invalid symbol used")])

class ModifyUserSumbmit(FlaskForm):
    submit = SubmitField("Save changes")

class BreadOrderForm(FlaskForm):
    White_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Seeds_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_and_Sultanas_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Pistacho_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Spelt_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_White_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Seeds_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_and_Sultanas_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Pistacho_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    White_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Seeds_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_and_Sultanas_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Pistacho_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Spelt_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_White_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Seeds_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_and_Sultanas_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Pistacho_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    date = DateField(default=date.today() + timedelta(days=1), validators=[DataRequired(message="required field"),
                                                                           FutureDaysOnly()])
    recurring = IntegerField(validators=[NumberRange(min=0, max=12, message="Invalid Number")],
                             default=0, label="Number of Weeks")
    day_time = SelectField(choices=[('Evening', 'Evening')])
    #day_time = SelectField(choices=[('Evening', 'Evening'),('Morning', "Morning")])
    submit = SubmitField("Order")


#spanish Forms
class LoginFormEs(FlaskForm):
    usuario = StringField(validators=[DataRequired(message="required field"),
                                       NoneOf(data.invalid_characters, message="invalid symbol used")])
    contraseña = PasswordField(validators=[DataRequired(), NoneOf(data.invalid_characters, message="invalid symbol used")])
    submit = SubmitField("Acceder")

class PedidoPan(FlaskForm):
    White_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Seeds_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_and_Sultanas_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Pistacho_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Pistacho_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Spelt_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_White_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Seeds_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_and_Sultanas_loaf = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)

    White_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Seeds_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Walnut_and_Sultanas_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Pistacho_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Pistacho_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Spelt_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_White_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Seeds_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")], default=0)
    Wholemeal_Walnut_and_Sultanas_stick = IntegerField(validators=[NumberRange(min=0, max=6, message="Invalid Number")],
                                               default=0)
    date = DateField(default=date.today() + timedelta(days=1), validators=[DataRequired(message="required field"),
                                                                           FutureDaysOnly()])
    recurring = IntegerField(validators=[NumberRange(min=0, max=12, message="Invalid Number")],
                             default=0, label="Number of Weeks")
    day_time = SelectField(choices=[('Evening', "Tarde")])
    #day_time = SelectField(choices=[('Morning', "Mañana"), ('Evening', 'Tarde')])
    submit = SubmitField("Order")

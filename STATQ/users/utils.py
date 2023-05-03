from flask import url_for
from flask_mail import Message

from STATQ import mail


def send_reset_email(user):
    token = user.get_reset_token()

    msg = Message('Nulstilling af kodeord',
                  sender='SR Batymetri',
                  recipients=[user.email])
    msg.body = f'''Følg nedenstående link for at nulstille kodeord:
    {url_for('users.reset_token', token=token, _external=True)}
    

    Hvis du ikke fremsatte denne forespørgsel, ignorér blot denne mail.

    SR Batymetri
    '''
    mail.send(msg)

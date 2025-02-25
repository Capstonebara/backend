from fastapi import APIRouter
from pydantic import EmailStr, BaseModel
from utils.email_utils import send_personalized_emails, send_local

email_routes = APIRouter()

# class EmailSchema(BaseModel):
#     subject: str
#     recipients: list[EmailStr]
#     body: str

# @email_routes.post("/send-email")
# async def send_email_route(email: EmailSchema):
#     test = await send_email(email.subject, email.recipients, email.body)

#     if test is True:
#         return {"message": "Email sending task has been send"}
#     else:
#         return {"message": "Email sending task has been failed"}


# class Recipient(BaseModel):
#     email: EmailStr
#     name: str = "Valued Customer"

# class EmailList(BaseModel):
#     recipients: list[Recipient]

# @email_routes.post("/send-emails-template")
# async def send_personalized(subject: str, email_list: EmailList):

#     recipients = [{"email": r.email, "name": r.name} for r in email_list.recipients]
#     test = await send_personalized_emails(subject, recipients)

#     if test is True:
#         return {"message": "Email sending task has been send"}
#     else:
#         return {"message": "Email sending task has been failed"}
    

# @email_routes.post("/send-emails-local")
# async def send_personalized_local(subject: str, email_list: EmailList):

#     recipients = [{"email": r.email, "name": r.name} for r in email_list.recipients]
#     test = await send_local(subject, recipients)

#     if test is True:
#         return {"message": "Email sending task has been send"}
#     else:
#         return {"message": "Email sending task has been failed"}

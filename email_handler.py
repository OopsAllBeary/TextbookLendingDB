import urllib.parse
import webbrowser


def open_status_email(email, first_name, status):

    if status == "Approved":
        subject = "Textbook Lending Application Approved"
        body = f"""
Hi {first_name},

Your Textbook Lending application has been approved.

We will follow up with next steps soon.

Thank you.
"""

    elif status == "Denied":
        subject = "Textbook Lending Application Update"
        body = f"""
Hi {first_name},

We have reviewed your Textbook Lending application and have an update.

Please contact us if you have questions.

Thank you.
"""

    else:
        return

    mailto = (
        f"mailto:{email}"
        f"?subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )

    webbrowser.open(mailto)
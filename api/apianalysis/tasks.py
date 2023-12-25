from datetime import timedelta
from django.utils import timezone
from apicore.models import Vaccination, Animal
from apiauth.models import Farmer
from django.core.mail import send_mail
from api.celery import app
    

@app.task
def check_vaccine_expiry():
    today = timezone.now()
    week_from_now = today + timedelta(days=7)

    expiring_vaccines = Vaccination.objects.filter(expiration_date__gte=today, expiration_date__lte=week_from_now)

    for vaccine in expiring_vaccines:
        animal = Animal.objects.filter(id=id).first()
        owner = Farmer.objects.filter(id=animal.owner).first()
        ownerEmail = owner.email
        animalName = animal.name
        send_mail(
            subject='Wygasajace szczepienie dla %s' % animalName,
            message='Szczepienie konczy waznosc dnia: "%s"' % vaccine.expiration_date,
            from_email='farmcontrol.management@gmail.com',
            recipient_list=[ownerEmail],
            fail_silently=False
        )
    return "success"

@app.task
def test(x,y):
    try:
        result = x + y
        print(f'Task completed successfully: {result}')
        return result
    except Exception as e:
        print(f'Task failed: {e}')
        raise


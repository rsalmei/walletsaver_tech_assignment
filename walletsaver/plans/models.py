from django.db import models, transaction

from plans.const import CARRIER_FASTWEB
from plans.scraping import fetch_plans


class CarrierPlanQuerySet(models.QuerySet):
    def from_carrier(self, carrier_id):
        return self.filter(carrier=carrier_id)


class CarrierPlanManager(models.Manager):
    def resync_plans(self, carrier_id: int):
        with transaction.atomic():
            # this logic must be in a db transaction, so the
            # data is only changed if no errors are raised.
            self.from_carrier(carrier_id).delete()
            for plan in fetch_plans(carrier_id):
                CarrierPlan.objects.create(carrier=carrier_id, **plan._asdict())


class CarrierPlan(models.Model):
    PROVIDERS = (
        (CARRIER_FASTWEB, 'fastweb'),
    )

    carrier = models.IntegerField(choices=PROVIDERS)
    title = models.CharField(max_length=128, unique=True)
    description = models.CharField(max_length=1024)
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    old_price = models.DecimalField(max_digits=8, decimal_places=2)

    objects = CarrierPlanManager.from_queryset(CarrierPlanQuerySet)()

    def __str__(self):
        return '#{} {}:{}'.format(self.id, self.get_carrier_display(), self.title)

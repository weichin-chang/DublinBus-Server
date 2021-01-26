from django.db import models


# Create your models here.
class BusStop(models.Model):
    stop_id = models.CharField(primary_key=True, max_length=16)
    stop_name = models.CharField(max_length=45, blank=True, null=True)
    stop_lat = models.FloatField(blank=True, null=True)
    stop_lng = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bus_stop'


class RouteHistory(models.Model):
    day_of_service = models.IntegerField(primary_key=True)
    trip_id = models.IntegerField()
    route_id = models.CharField(max_length=20, blank=True, null=True)
    direction = models.CharField(max_length=2, blank=True, null=True)
    line_id = models.CharField(max_length=10, blank=True, null=True)
    planned_duration = models.IntegerField(blank=True, null=True)
    actual_duration = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route_history'
        unique_together = (('day_of_service', 'trip_id'),)


class RouteProgram(models.Model):
    route_id = models.CharField(max_length=20, blank=True, null=True)
    direction = models.CharField(max_length=2, blank=True, null=True)
    line_id = models.CharField(max_length=10, blank=True, null=True)
    stop = models.ForeignKey(BusStop, models.DO_NOTHING, blank=True, null=True)
    program_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route_program'


class RouteStopInterval(models.Model):
    line_id = models.CharField(max_length=10, blank=True, null=True)
    direction = models.CharField(max_length=2, blank=True, null=True)
    day_of_service = models.IntegerField(blank=True, null=True)
    origin_id = models.CharField(max_length=16, blank=True, null=True)
    destination_id = models.CharField(max_length=16, blank=True, null=True)
    planned_interval = models.IntegerField(blank=True, null=True)
    actual_interval = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'route_stop_interval'


class PlannedStopInterval(models.Model):
    line_id = models.CharField(primary_key=True, max_length=10)
    direction = models.CharField(max_length=2)
    origin_id = models.CharField(max_length=16)
    destination_id = models.CharField(max_length=16)
    planned_interval = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planned_stop_interval'
        unique_together = (('line_id', 'direction', 'origin_id', 'destination_id'),)


class UserSavedRoutes(models.Model):
    user_save_route_id = models.AutoField(primary_key=True)
    user_email = models.CharField(max_length=100)
    origin_stop_id = models.CharField(max_length=16)
    origin_stop_name = models.CharField(max_length=45, null=True)
    destination_stop_id = models.CharField(max_length=16)
    destination_stop_name = models.CharField(max_length=45, null=True)
    line_id = models.CharField(max_length=10)
    direction = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'user_save_routes'


class SaveLeapCardDetails(models.Model):
    leap_info_id = models.AutoField(primary_key=True)
    leap_user_email = models.CharField(max_length=100)
    leap_password = models.CharField(max_length=100)
    user_reg_email = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user_leap_information'
# Generated by Django 5.1.3 on 2024-12-16 12:24

from django.db import migrations

from ..initial_data import create_groups


class Migration(migrations.Migration):

    dependencies = [
        ("CleanSMRs_eCommerce", "0003_plan_product_order_subscription"),
    ]

    operations = [migrations.RunPython(create_groups)]

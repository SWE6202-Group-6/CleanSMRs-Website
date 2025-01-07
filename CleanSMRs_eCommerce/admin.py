from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser, Order, Plan, Product, Subscription

# Register your models here.


class UserAdmin(BaseUserAdmin):
    """Modifies the admin user display."""

    ordering = ("first_name", "last_name")
    list_display = ("email", "first_name", "last_name", "is_staff")
    list_display_links = ("email",)

    fieldsets = (
        ("Login information", {"fields": ("email", "password")}),
        (
            "Personal information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "address",
                    "city",
                    "country",
                    "postal_code",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )


class OrderAdmin(admin.ModelAdmin):
    """Customises the admin display for the Order model."""

    list_display = (
        "id",
        "order_number",
        "date_placed",
        "status",
        "order_total",
    )

    # The order number shouldn't be editable.
    readonly_fields = ("order_number",)


class PlanAdmin(admin.ModelAdmin):
    """Customises the admin display for the Plan model."""

    list_display = ("id", "name", "duration_months")


class ProductAdmin(admin.ModelAdmin):
    """Customises the admin display for the Product model."""

    list_display = ("id", "name", "type", "price", "plan_id")


class SubscriptionAdmin(admin.ModelAdmin):
    """Customises the admin display for the Subscription model."""

    list_display = (
        "id",
        "plan_id",
        "user_id",
        "order_id",
        "start_date",
        "end_date",
    )


admin.site.register(CustomUser, UserAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

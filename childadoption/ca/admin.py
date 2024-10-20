from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ca.models import CustomUser, SuperAdmin, UserCust,AdoptionRequest,ChildDetails,Organization,ChildAppointment,SponserShipApplicants,LifeTimeSponserShip,LifeTimeSponserShipNeeds
from django.db.models import Sum
#THIS IS FOR MAIL
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class UserCustAdmin(admin.ModelAdmin):
    list_display = ('username', 'fname', 'lname', 'emailaddress', 'gender', 'location', 'addresss', 'phone_number')
    search_fields = ('username', 'fname', 'lname', 'emailaddress', 'gender', 'location', 'addresss', 'phone_number')

    def has_add_permission(self, request):
        # Disable the ability to add UserCust instances
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change UserCust instances
        return False

    # def has_delete_permission(self, request, obj=None):
    #     # Disable the ability to delete UserCust instances
    #     return False

admin.site.register(UserCust)
admin.site.register(ChildAppointment)
admin.site.register(SponserShipApplicants)
admin.site.register(LifeTimeSponserShipNeeds)


class DonateAdmin(admin.ModelAdmin):
    list_display = ('personal_details', 'credict_cardno', 'exp', 'amount')
    search_fields = ('personal_details__username', 'credict_cardno')
    readonly_fields = ('credict_cardno', 'exp', 'ccv', 'amount')  # Make fields read-only

    def has_add_permission(self, request):
        # Disable the ability to add Donate instances
        return False

    def has_change_permission(self, request, obj=None):
        # Only superusers can view Donate instances
        return request.user.is_superuser

    # def has_delete_permission(self, request, obj=None):
    #     # Disable the ability to delete Donate instances
    #     return False

admin.site.register(Organization)
# Change verbose name for the model
admin.site.register(LifeTimeSponserShip)

# class UserCustAdmin(admin.ModelAdmin):
#     list_display = ('username', 'total_donation')

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         queryset = queryset.annotate(total_donation=Sum('donate__amount'))
#         return queryset

#     def total_donation(self, obj):
#         return obj.total_donation

#     total_donation.admin_order_field = 'total_donation'


class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ('personal_details', 'subject')  # Corrected list_display
    search_fields = ('personal_details__username', 'subject')
    readonly_fields = ('personal_details', 'subject')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    # def has_delete_permission(self, request, obj=None):
    #     return False

admin.site.register(AdoptionRequest, AdoptionRequestAdmin)


class AdoptionFormViewAdmin(admin.ModelAdmin):
    list_display = ('personal_details', 'full_name', 'email', 'phone', 'address', 'age', 'marital_status', 'occupation', 'income', 'criminal_history', 'additional_comments', 'id_proof', 'isaccepted','feedback')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('personal_details', 'full_name', 'email', 'phone', 'address', 'age', 'marital_status', 'occupation', 'income', 'criminal_history', 'additional_comments', 'id_proof')  # Fields you want to be read-only
    list_filter = ('feedback','isaccepted')
    def has_add_permission(self, request):
        # Disable the ability to add instances
        return False

    def has_change_permission(self, request, obj=None):
        # Only superusers can view instances
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete instances
        return False





admin.site.register(ChildDetails)




# admin.site.register(SponserTable)
class SponserTableAdmin(admin.ModelAdmin):
    list_display = ('user', 'child', 'sponsor_type', 'credit_cardno', 'exp', 'ccv', 'budget')
    search_fields = ('user', 'child', 'sponsor_type', 'credit_cardno', 'exp', 'ccv', 'budget')

    def has_add_permission(self, request):
        # Disable the ability to add UserCust instances
        return False

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change UserCust instances
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete UserCust instances
        return False



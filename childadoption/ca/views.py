from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.views.generic import View
from django.views.generic import UpdateView,ListView,DetailView,TemplateView,CreateView
from ca.models import UserCust,AdoptionRequest,ChildDetails,Organization,ChildAppointment,Donation,SponserShipApplicants,LifeTimeSponserShip,LifeTimeSponserShipNeeds
from ca.forms import UserRegisterForm,LoginForm,UserUpdateForm,ChildForm,AdoptionRequestForm,AdoptionRequestFormO,ChildAppointmentForm,DonationForm,LifeTimeSponserShipForm,LifeTimeSponserShipNeedsForm
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy,reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import get_user_model
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
 
from childadoption import settings
import logging
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import Sum


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))



# razorpay_client.set_app_details({"title" : "Child Adoption", "version" : "1.0.0"})


def signin_required(fn):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return fn(request,*args,**kwargs)
        else:
            return redirect("login")
    return wrapper


logger = logging.getLogger(__name__)

class HomeView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve the current user's organization
            user_id = request.user.id
            user_obj = UserCust.objects.get(id=user_id)
            
            # Exclude the current user's organization from the queryset
            organizations = Organization.objects.exclude(user=user_obj)
        except UserCust.DoesNotExist:
            # Handle the case where the current user does not have an associated organization
            organizations = Organization.objects.all()

        # Payment success/failure handling
        status = request.GET.get('status')
        payment_type = request.GET.get('type')
        payment_id = request.GET.get('payment_id')
        order_id = request.GET.get('order_id')
        signature = request.GET.get('signature')
        code = request.GET.get('code')
        description = request.GET.get('description')

        logger.debug(f"Status: {status}, Type: {payment_type}, Payment ID: {payment_id}, Order ID: {order_id}, Signature: {signature}, Code: {code}, Description: {description}")

        if status == 'success':
            if payment_type == 'donation':
                donation_id = request.GET.get('donation_id')
                logger.debug(f"Donation ID: {donation_id}")
                if donation_id:
                    try:
                        donation = Donation.objects.get(id=donation_id)
                        donation.is_paid = True
                        donation.status = 'paid'
                        donation.save()
                        messages.success(request, "Donation payment successful.")
                    except Donation.DoesNotExist:
                        messages.error(request, "Donation record not found.")
                else:
                    messages.error(request, "Invalid donation ID.")
            elif payment_type == 'sponsorship':
                sp_child_id = request.GET.get('sp_child_id')
                print('============/////////////',sp_child_id)

                logger.debug(f"Sponsorship Child ID: {sp_child_id}")
                if sp_child_id:
                    try:
                        sponsorship = SponserShipApplicants.objects.get(id=sp_child_id)
                        sponsorship.is_paid = True
                        sponsorship.save()
                        messages.success(request, "Sponsorship payment successful.")
                    except SponserShipApplicants.DoesNotExist:
                        messages.error(request, "Sponsorship record not found.")
                else:
                    messages.error(request, "Invalid sponsorship child ID.")
            elif payment_type == 'need':
                need_id = request.GET.get('need_id')
              
                if need_id:
                    try:
                        need = LifeTimeSponserShipNeeds.objects.get(id=need_id)
                        need.is_paid = True
                        need.save()
                        messages.success(request, "Need payment successful.")
                    except Donation.DoesNotExist:
                        messages.error(request, "need record not found.")
                else:
                    messages.error(request, "Invalid donation ID.")        
        elif status == 'failed':
            messages.error(request, f"{payment_type.capitalize()} payment failed: {description}")

        return render(request, "home.html", {"orgs": organizations})

class ServiceView(View):
    def get(self,request,*args,**kwargs):
        org_id =  kwargs.get('pk')
        return render(request,"service.html",{"org_id":org_id})
    

     
class RegisterView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.instance.user_type = 'User'
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'register.html', {"form": form})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            pwd = form.cleaned_data.get("password")
            user_obj = authenticate(request, username=username, password=pwd)
            if user_obj:
                login(request, user_obj)
                messages.success(request, "Login successful!")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, "login.html", {"form": form})


class LogoutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("home")


# class SponserView(View):
#     def get(self,request,*args, **kwargs):
#         return render(request,"sponser.html")

    


class DonationView(View):
    def get(self, request,org_id, *args, **kwargs):
        categories = Donation.category_choices
        return render(request, "donation.html", {'categories': categories})

    def post(self, request,org_id, *args, **kwargs):
        category = request.POST.get('category')
        amount = request.POST.get('amount')
        user_obj = get_object_or_404(UserCust, id=request.user.id)
        org_obj = get_object_or_404(Organization, id=org_id)


        if not amount:
            messages.error(request, "Amount is required.")
            return redirect(request.path)
        try:
            amount = int(amount) * 100  # Convert to paise
        except ValueError:
            messages.error(request, "Invalid amount.")
            return redirect(request.path)

   
        # Save the donation
        donation = Donation.objects.create(
            category=category,
            amount=amount // 100,  # Store amount in rupees
       
            personal_details = user_obj,
            organization = org_obj
            
        )

        return redirect('process_payment', donation_id=donation.id)
    
    
class ProcessPaymentView(View):
    def get(self, request, donation_id, *args, **kwargs):
        donation = get_object_or_404(Donation, id=donation_id)
        amount = donation.amount * 100  # Convert to paise

        # Create Razorpay order
        order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Save the order ID to the donation object
        donation.order_id = order['id']
        donation.save()

        return render(request, "payment.html", {
            'order_id': order['id'],
            'amount': amount,
            'api_key': 'rzp_test_91eopcxhCbCO8V',
            "donation":donation
        })

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')
    donation_id = request.GET.get('donation_id')
    
    # Retrieve the donation object and update its status
    donation = get_object_or_404(Donation, id=donation_id)
    donation.is_paid = True
    donation.status = 'paid'
    donation.save()
    
    return render(request, 'payment_success.html', {
        'payment_id': payment_id,
        'order_id': order_id,
        'signature': signature,
        'donation': donation
    })

def payment_failure(request):
    code = request.GET.get('code')
    description = request.GET.get('description')
    return render(request, 'payment_failure.html', {'code': code, 'description': description})



@method_decorator(signin_required,name="dispatch")
class PrivacyView(View):
    def get(self,request,*args, **kwargs):
        return render(request,"privacy.html")


    
class DonatePayment(View):
    def get(self, request, *args, **kwargs):
        form = DonateForm()
        return render(request, "donatepayment.html", {"form": form})
    

class UserProfileEdit(UpdateView):
    template_name="userprofileedit.html"
    form_class=UserUpdateForm
    model=UserCust
    success_url=reverse_lazy("home")


class UserProfile(DetailView):
    template_name="userprofile.html"
    form_class=UserUpdateForm
    model=UserCust
    context_object_name="user"
    
@method_decorator(signin_required, name="dispatch")
class AdoptionRequestView(View):
    
    def get(self, request, *args, **kwargs):
        try:
            org_id = kwargs.get("org_id")
            organization = get_object_or_404(Organization, id=org_id)
            form = AdoptionRequestForm()
            has_approved_request = AdoptionRequest.objects.filter(
                organization=organization, personal_details=request.user, status='A'
            ).exists()
            print('===========', has_approved_request)
            return render(request, "adoption.html", {'form': form, 'has_approved_request': has_approved_request, "org_id": org_id})
        
        except Organization.DoesNotExist:
            print('//////????')
            return HttpResponse("Organization not found.", status=404)
        
        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse("An error occurred.", status=500)
    
    def post(self, request, *args, **kwargs):
        try:
            org_id = kwargs.get("org_id")
            organization = get_object_or_404(Organization, id=org_id)
            form = AdoptionRequestForm(request.POST, request.FILES)
            
            if form.is_valid():
                user_obj = UserCust.objects.get(id=request.user.id)
                
                adoption_request = form.save(commit=False)
                adoption_request.personal_details = user_obj
                adoption_request.organization = organization
                adoption_request.save()
                
                return redirect('home')
            
            has_approved_request = AdoptionRequest.objects.filter(
                organization=organization, personal_details=request.user, status='A'
            ).exists()
            return render(request, "adoption.html", {'form': form, 'has_approved_request': has_approved_request, "org_id": org_id})
        
        except Organization.DoesNotExist:
            print('////////====')
            return HttpResponse("Organization not found.", status=404)
        
        except UserCust.DoesNotExist:
            return HttpResponse("User not found.", status=404)
        
        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse("An error occurred.", status=500)

    

class SponsorChildView(View):
    def get(self, request, org_id, *args, **kwargs):
        organization = get_object_or_404(Organization, id=org_id)
        
        # Get all sponsorship applicants for the organization
        sponsorship_applicants = SponserShipApplicants.objects.filter(child__organization=organization)
        
        # Use a set to ensure unique children
        unique_children = {}
        for applicant in sponsorship_applicants:
            if applicant.child_id not in unique_children:
                unique_children[applicant.child_id] = applicant.child
        
        child_list = list(unique_children.values())
        
        return render(request, "sponser.html", {'child_list': child_list, 'organization': organization})
        
class success_sponcer(TemplateView):
    template_name="sponsor_success.html"    


class OrganizationHome(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                organization = Organization.objects.get(user=request.user)
                childs = ChildDetails.objects.filter(organization=organization).count()
                print(childs)
            except Organization.DoesNotExist:
                childs = 0
            context = {
                "childs": childs
            }
        else:
            # Redirect unauthenticated users to login page or set context accordingly
            return redirect('login')  # Adjust 'login' to the correct URL name of your login view
        
        return render(request, "organization_panel.html", context=context)
    

class OrgHome(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                organization = Organization.objects.get(user=request.user)
                childs = ChildDetails.objects.filter(organization=organization).count()
                donation_amt = Donation.objects.filter(organization=organization,is_paid = True)
                total_amt = donation_amt.aggregate(total=Sum('amount'))['total']

            except Organization.DoesNotExist:
                childs = [] 
        context = {
                "childs": childs,
                "total_amt":total_amt
            }
        return render(request, "org_home.html",context)
    

class ChildView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                organization = Organization.objects.get(user=request.user)
                childs = ChildDetails.objects.filter(organization=organization).order_by('-id')
            except Organization.DoesNotExist:
                childs = []  # handle the case where the organization does not exist
        else:
            childs = []  # handle the unauthenticated case

        form = ChildForm()
        return render(request, "org_child.html", {'childs': childs, 'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                organization = Organization.objects.get(user=request.user)
            except Organization.DoesNotExist:
                return redirect('error_page')  # handle the case where the organization does not exist

            form = ChildForm(request.POST, request.FILES)
            if form.is_valid():
                child = form.save(commit=False)
                child.organization = organization
                child.save()
                return redirect('chi')  # redirect to the same view after successful creation
        else:
            return redirect('login')  # redirect to login page if unauthenticated

        # If form is not valid or other issues, re-render the page with form errors
        childs = ChildDetails.objects.filter(organization=organization).order_by('-id')
        return render(request, "org_child.html", {'childs': childs, 'form': form})
    
class ChildEditView(View):
    def get(self, request, pk, *args, **kwargs):
        child = ChildDetails.objects.get(id=pk)
        if request.user.is_authenticated :
            form = ChildForm(instance=child)
            return render(request, "child_edit.html", {'form': form, 'child': child})
        else:
            return redirect('login')  # redirect to login page if unauthenticated or not authorized

    def post(self, request, pk, *args, **kwargs):
        child = get_object_or_404(ChildDetails, pk=pk)
        if request.user.is_authenticated :
            form = ChildForm(request.POST, request.FILES, instance=child)
            if form.is_valid():
                form.save()
                return redirect('chi')  # redirect to the list view after successful edit
            return render(request, "child_edit.html", {'form': form, 'child': child})
        else:
            return redirect('login')     
        
        
class ChildDeleteView(View):
    def get(self, request, pk, *args, **kwargs):
        child =ChildDetails.objects.get(id=pk)
        
        if request.user.is_authenticated:
            child.delete()
            return redirect('chi')  # Redirect to child list view after successful deletion
        else:
            return redirect('login')  # Redirect to login page if user is not authenticated or not authorized
       
class AdoptionRequestViewO(View):
    def get(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, user=request.user)
        adoption_requests = AdoptionRequest.objects.filter(organization=organization).order_by('-id')
        context = {
            'adoption_requests': adoption_requests
        }
        return render(request, "adoption_request.html", context)
    
class VerifyAdoptionRequest(View):
    def get(self, request, pk, sk, *args, **kwargs):
        adoption_request = get_object_or_404(AdoptionRequest, pk=pk)
        
        # Update the status based on the status key (sk) provided in the URL
        if sk == 'A':
            adoption_request.status = 'A'
        elif sk == 'R':
            adoption_request.status = 'R'
        elif sk == 'P':
            adoption_request.status = 'P'
        
        adoption_request.save()
        
        return redirect('ad_rst')
    

class UserAdoptionRequest(View):
    def get(self, request, *args, **kwargs):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to the login page if the user is not authenticated
        
        user = get_object_or_404(UserCust, id=request.user.id)
        adoption_requests = AdoptionRequest.objects.filter(personal_details=user).order_by('-id')
        
        return render(request, "ad_re.html", {"ad_rq": adoption_requests})
    

class UserChildList(View):
    def get(self, request, pk, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')  # Redirect to the login page if the user is not authenticated
        
        try:
            # Retrieve the organization object; return 404 if it does not exist
            org_obj = get_object_or_404(Organization, id=pk)
            
            # Filter child details by the organization
            child_objs = ChildDetails.objects.filter(organization=org_obj)
        
        except Organization.DoesNotExist:
            # Handle case where the organization does not exist
            return HttpResponse("Organization not found.", status=404)
        
        except Exception as e:
            # Handle other unexpected exceptions
            return HttpResponse(f"An error occurred: {e}", status=500)
        form = ChildAppointmentForm()
        # Render the template with the child objects
        return render(request, "user_child_list.html", {"child_objs": child_objs,"form":form})

class ChildAppointmentView(View):
    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
    
        # Create an instance of the ChildAppointmentForm
        form = ChildAppointmentForm()
        
        # Render the template with the child objects and the form
        return render(request, "appoinment.html", { "form": form })
    
    def post(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            # Retrieve the child details object based on pk; return 404 if it does not exist
            ch_obj = get_object_or_404(ChildDetails, id=pk)
            print(pk,'============//')
            print(ch_obj.id,'=========')
            org_id = ch_obj.organization.id  # Get organization id
            user_obj = get_object_or_404(UserCust, id=request.user.id)
            print(user_obj)
            
            # Create an instance of the ChildAppointmentForm with POST data
            form = ChildAppointmentForm(request.POST)
            
            # Validate form data and handle clean logic
            if form.is_valid():
                date = form.cleaned_data.get('date')
                
                # Check if there is already an appointment for this user and child on the selected date
                existing_appointment = ChildAppointment.objects.filter(
                    user=user_obj,
                    child=ch_obj
                ).exists()
                
                if existing_appointment:
                    form.add_error(None, "You have already scheduled an appointment for this student on this date.")
                    print('44')
                    # Re-render the template with the form and child details
                    return render(request, "appoinment.html", {"form": form})
                
                # If no existing appointment, proceed to save
                appointment = form.save(commit=False)
                appointment.user = user_obj
                appointment.child = ch_obj
                appointment.save()
                
                # Redirect to a success page or the same page
                print('33')
                return redirect('usr_ch_li', pk=org_id)  # Redirect to the child list page for the organization
            
        except (ChildDetails.DoesNotExist, UserCust.DoesNotExist):
            print('11')
            return HttpResponse("Child or user details not found.", status=404)
        
        # If the form is not valid or if there's an error, render the template with the form and child details
        print('22')
        return render(request, "appoinment.html", {"form": form})
    

@method_decorator(signin_required,name="dispatch")   
class AppoinmentListView(View):
    
    def get(self, request, *args, **kwargs):
        user_obj = get_object_or_404(UserCust, id=request.user.id)
        appointments = ChildAppointment.objects.filter(user=user_obj)
        
        return render(request, "appoinment_list.html", {
            'appointments': appointments
        })
    

        
class ChildAppoinmentDeleteView(View):
    def get(self, request, pk, *args, **kwargs):
        child =ChildAppointment.objects.get(id=pk)
        
        if request.user.is_authenticated:
            child.delete()
            return redirect('usr_ap_li') 
        else:
            return redirect('login') 
        
class OrgSponserShipApplicants(View):
    def get(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(UserCust, id=request.user.id)
            org_obj = Organization.objects.get(user=user)

            child_list = SponserShipApplicants.objects.filter(child__organization=org_obj)
            og_childs = ChildDetails.objects.filter(organization=org_obj)
            return render(request, "org_sponser.html", {'child_list': child_list,"og_childs":og_childs, 'organization': org_obj})
        except Organization.DoesNotExist:
            return HttpResponseBadRequest("Organization not found")
        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")

    def post(self, request, *args, **kwargs):
        try:
            child= request.POST.get('child')
            amount = request.POST.get('amount')

            sponsor_category = request.POST.get('sponsor_category')
            child_obj = get_object_or_404(ChildDetails, id=child)
            SponserShipApplicants.objects.create(child=child_obj,sponsor_category=sponsor_category ,amount = amount)
            return redirect('org_sp')  # Replace 'success_url' with the actual URL to redirect after success
        except ChildDetails.DoesNotExist:
            return HttpResponseBadRequest("Child not found")
        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")
        

class DeleteSponserShipApplicants(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            sponsorship_applicant = get_object_or_404(SponserShipApplicants, id=pk)
            # Check if the user has permission to delete this object
            # This is a placeholder check, replace with actual permission logic if needed
        
            sponsorship_applicant.delete()
            return redirect('org_sp') 
        except SponserShipApplicants.DoesNotExist:
            return HttpResponseBadRequest("Sponsorship applicant not found.")
        except Exception as e:
            return HttpResponseBadRequest(f"An error occurred: {str(e)}")


class SponserList(View):
    def get(self, request, sp_child, *args, **kwargs):
        child = get_object_or_404(ChildDetails, id=sp_child)
        sponsorship_list = SponserShipApplicants.objects.filter(child = child,is_paid = False).order_by('-id')
       
        return render(request,'pay_sponser.html',{"sponsorship_list":sponsorship_list})


def sponser_payment(request,sp_child):
    sp_child_obj = SponserShipApplicants.objects.get(id = sp_child)
    amount = sp_child_obj.amount * 100
    order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })
    
    return render(request, "payment_screen.html", {
            'order_id': order['id'],
            'amount': amount,
            'api_key': 'rzp_test_91eopcxhCbCO8V',
            'sp_child':sp_child_obj
            
        })

def payment_success_sp(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')
    sp_child = request.GET.get('sp_child')
    
    # Retrieve the donation object and update its status
    sponsership = get_object_or_404(SponserShipApplicants, id=sp_child)
    sponsership.is_paid = True

    sponsership.save()
    
    return render(request, 'payment_success_sp.html', {
        'payment_id': payment_id,
        'order_id': order_id,
        'signature': signature,
        'sponsership': sponsership
    })

def payment_failure_sp(request):
    code = request.GET.get('code')
    description = request.GET.get('description')
    return render(request, 'payment_failure_sp.html', {'code': code, 'description': description})


@signin_required
def create_sponsorship(request, pk):
    user_obj = get_object_or_404(UserCust, id=request.user.id)
    child_obj = get_object_or_404(ChildDetails, id=pk)

    # Check if the user has already sponsored a child
    existing_sponsorship = LifeTimeSponserShip.objects.filter(sponser=user_obj,child=child_obj).exists()

    if existing_sponsorship:
        messages.error(request, 'You have already sponsored this child. You cannot sponsor this child. choose another child')
        return redirect('sponsor_child', org_id=child_obj.organization.id)  # Redirect to a suitable view or URL

    if request.method == 'POST':
        
        form = LifeTimeSponserShipForm(request.POST)

        if form.is_valid():
            sponsorship = form.save(commit=False)
            sponsorship.child = child_obj
            sponsorship.sponser = user_obj
            try:
                sponsorship.save()
                messages.success(request, 'Sponsorship created successfully!')
                return redirect('sponsor_child', org_id=child_obj.organization.id)
            except ValidationError as e:
                messages.error(request, e.message)
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = LifeTimeSponserShipForm()

    return render(request, 'life_time.html', {'form': form})



def user_sponser_view(request):
    user_obj = get_object_or_404(UserCust, id=request.user.id)
    current_date = timezone.now().date()
    life_time_sp = LifeTimeSponserShip.objects.filter(sponser=user_obj, date_to__gt=current_date)
    return render(request, 'user_sponsorships.html', {'life_time_sp': life_time_sp})



def life_sponser_need_list(request, pk):
    l_s = get_object_or_404(LifeTimeSponserShip, id=pk)
    life_sposer_needs = LifeTimeSponserShipNeeds.objects.filter(lifeTimesponserShip=l_s,is_paid=False)
    return render(request, 'needs.html', {'life_sposer_needs': life_sposer_needs})


def need_payment(request,need_id):
    need = LifeTimeSponserShipNeeds.objects.get(id = need_id)
    amount = need.amount * 100
    order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })
    
    return render(request, "need_payment.html", {
            'order_id': order['id'],
            'amount': amount,
            'api_key': 'rzp_test_91eopcxhCbCO8V',
            'need':need
            
        })

def org_donation(request):
    user_obj = get_object_or_404(UserCust, id=request.user.id)

    org  = Organization.objects.get(user=user_obj)
    don = Donation.objects.filter(organization=org).order_by('-id')
    return render(request,'org_donation.html',{"dons":don})

def org_child_appointments(request):
    user_obj = get_object_or_404(UserCust, id=request.user.id)

    org  = Organization.objects.get(user=user_obj)
    appoinments= ChildAppointment.objects.filter(child__organization = org).order_by('-id')
    return render(request,'org_ch_appo.html',{"appoinments":appoinments})


def org_child_sponser_list(request):
    
    user_obj = get_object_or_404(UserCust, id=request.user.id)
    org = get_object_or_404(Organization, user=user_obj)
    
    sponserships = LifeTimeSponserShip.objects.filter(child__organization=org)
    child_ids = set()
    unique_sponserships = []
    
    for sponsorship in sponserships:
        if sponsorship.child.id not in child_ids:
            unique_sponserships.append(sponsorship)
            child_ids.add(sponsorship.child.id)
    
    return render(request, 'org_child_sponser.html', {"childs": unique_sponserships})

def org_child_detail_sp(request, pk):
    lifetime_sponsership = get_object_or_404(LifeTimeSponserShip, id=pk)
    today = timezone.now().date()
    lifetime_sponserships = LifeTimeSponserShip.objects.filter(child=lifetime_sponsership.child, date_to__gte=today)
    
    if request.method == 'POST':
        form = LifeTimeSponserShipNeedsForm(request.POST)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            sponsorship_need = form.save(commit=False)
            # Associate the newly created sponsorship need with the current lifetime sponsorship
            sponsorship_need.lifeTimesponserShip = lifetime_sponsership
            # Save the sponsorship need to the database
            sponsorship_need.save()
            return redirect('org_csl')  # Replace 'success_url' with your actual success URL
    else:
        form = LifeTimeSponserShipNeedsForm()

    return render(request, 'org_life_t_childs.html', {
        'lifetime_sponserships': lifetime_sponserships,
        'form': form
    })
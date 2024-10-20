from django.urls import path
from ca import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('',views.HomeView.as_view(),name="home"),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login',views.LoginView.as_view(),name="login"),
    path('logout/<int:pk>/',views.LogoutView.as_view(),name="logout"),
    # path('sponser/',views.SponserView.as_view(),name="sponser"),
    path('donate/<int:org_id>/',views.DonationView.as_view(),name="donate"),
    path('privacy/',views.PrivacyView.as_view(),name="privacy"),
    path('adoption/<int:org_id>/',views.AdoptionRequestView.as_view(),name="adoptionform"),
    path('donatepay/',views.DonatePayment.as_view(),name="donatepay"),
    path('profileedit/<int:pk>/',views.UserProfileEdit.as_view(),name="profileedit"),
    path('profile/<int:pk>/',views.UserProfile.as_view(),name="profile"),
    path('sponsor/<int:org_id>/', views.SponsorChildView.as_view(), name='sponsor_child'),
    path('successsponcer/', views.success_sponcer.as_view(), name='sponsor_success'),
    path('services/<int:pk>/',views.ServiceView.as_view(),name='service'),
    path('organization/',views.OrgHome.as_view(),name='org'),
    path('child/',views.ChildView.as_view(),name='chi'),
    path('child/edit/<int:pk>/',views.ChildEditView.as_view(),name='child-edit'),
    path('child-delete/<int:pk>/', views.ChildDeleteView.as_view(), name='child_delete'),
    path('adoption_request/',views.AdoptionRequestViewO.as_view(),name='ad_rst'),
    path('verify_request/<int:pk>/<str:sk>/',views.VerifyAdoptionRequest.as_view(),name='vr'),
    path('user/adoption/request/',views.UserAdoptionRequest.as_view(),name='ad_rq'),
    path('user/child/list/<int:pk>/',views.UserChildList.as_view(),name='usr_ch_li'),
    path('appoinment/<int:pk>/',views.ChildAppointmentView.as_view(),name='ap_c'),
    path('user/appoinment/',views.AppoinmentListView.as_view(),name='usr_ap_li'),
    path('user/appoinment/delete/<int:pk>/',views.ChildAppoinmentDeleteView.as_view(),name='ap_us_del'),
    path('process_payment/<int:donation_id>/', views.ProcessPaymentView.as_view(), name='process_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),
    path('org/sponsership/',views.OrgSponserShipApplicants.as_view(),name='org_sp'),
    path('delete/org/sponsership/<int:pk>/',views.DeleteSponserShipApplicants.as_view(),name='del_sp'),
    path('sponser/category/<int:sp_child>/',views.SponserList.as_view(),name='sponser_category'),
    path('sponser/pay/<int:sp_child>/',views.sponser_payment,name='pay_sp'),
    path('life_time/sponser/<int:pk>/',views.create_sponsorship,name='life_sp'),
    path('user/sponsering/',views.user_sponser_view,name='usersp'),
    path('child/needs/<int:pk>/',views.life_sponser_need_list,name='ch_n'),
    path('child/need/payment/need/<int:need_id>/',views.need_payment,name='n_p'),
    path('org/donations/',views.org_donation,name='org_dn'),
    path('org/child/appoinments/',views.org_child_appointments,name='org_ch_ap'),
    path('org/sposer/child/life/',views.org_child_sponser_list,name='org_csl'),
    path('org/child/sponser/lifetime/<int:pk>/',views.org_child_detail_sp,name='c_l_s')
    # path('ssp/', views.payment_success_sp, name='ssp'),
    # path('fsp/', views.payment_failure_sp, name='fsp'),

    # path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    # path('children/edit/<int:pk>/', views.ChildEditView.as_view(), name='child_edit'),
    # path('child-create/', views.ChildCreateView.as_view(), name='child_create'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
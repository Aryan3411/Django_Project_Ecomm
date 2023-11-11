from django.contrib import admin
from django.urls import path
from ecomm_app import views
from django.conf.urls.static import static
from ecomm import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home',views.home),
    path('pdetails/<pid>',views.product_details),
    path('register',views.register),
    path('login',views.u_login),
    path('contact',views.contact),
    path('service',views.service),
    path('cart',views.vcart),
    path('about',views.about),
    path('logout',views.u_logout),
    path('catfilter/<cv>',views.catfilter),
    path('sort/<sv>',views.sort),
    path('range',views.range),
    path('atcart/<pid>',views.atcart),
    path('remove/<pid>',views.remove),
    path('updateqty/<qv>/<cid>',views.updateqty),
    path('placeorder',views.placeorder),
    path('makepayment',views.makepayment),
    path('sendmail/<email>',views.sendusermail)
]

if settings.DEBUG:
    urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
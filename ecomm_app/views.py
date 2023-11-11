from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from ecomm_app.models import product
from ecomm_app.models import cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
def home(request):
    context={}
    p=product.objects.filter(is_active=True)
    context['products']=p
    return render(request,'index.html',context) 

def product_details(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context) 

def register(request):
    if request.method=='POST':
        n=request.POST['uname']
        p=request.POST['upass']
        cp=request.POST['ucpass']
        context={}
        if n=="" or p=="" or cp=="":
            context['errmsg']="fields can not be empty"
            return render(request,'register.html',context)
        elif p != cp:
            context['errmsg']="Password Did not match"
            return render(request,'register.html',context)
        else:
            try:
                u=User.objects.create(username=n,email=n,password=p)
                u.set_password(p)
                u.save()
                context['suc']="User Created sucessfully please Login"
                return render(request,'register.html',context)
            except Exception:
                context['errmsg']="UserName exist already try another"
                return render(request,'register.html',context)
    else:
        return render(request,'register.html') 

def u_login(request):
    if request.method=='POST':
        n=request.POST['uname']
        p=request.POST['upass']
        context={}
        if n=="" or p=="":
            context['errmsg']="fields can not be empty"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=n,password=p)
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalid Username and password"
                return render(request,'login.html',context)
    else:
        return render(request,'login.html')

def contact(request):
    return render(request,'contact.html') 

def vcart(request):
    c=cart.objects.filter(uid=request.user.id)
    l=len(c)
    s=0
    for x in c:
        s=s+ x.pid.price * x.qty
    context={}
    context['len']=l
    context['total']=s
    context['data']=c
    return render(request,'cart.html',context)

def remove(request, pid):
    uid = request.user.id
    try:
        c = cart.objects.get(uid=uid, pid=pid)
        c.delete()
        return redirect('/cart')
    except ObjectDoesNotExist:
        o = Order.objects.get(uid=uid, pid=pid)
        o.delete()
    
        return redirect('/placeorder')

def atcart(request,pid):
    if request.user.is_authenticated:
        userid=request.user.id
        u=User.objects.filter(id=userid)
        p=product.objects.filter(id=pid)
        q1=Q(uid=u[0])
        q2=Q(pid=p[0])
        c=cart.objects.filter(q1 & q2)
        n=len(c)
        context={}
        if n==1:
            m=product.objects.filter(id=pid)
            context['err']="Product already Exist"
            context['products']=m
            return render(request,'product_details.html',context)
        else:
            c=cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            m=product.objects.filter(id=pid)
            context['suc']="Product Added Sucessfully"
            context['products']=m
            return render(request,'product_details.html',context)
    else:
        return redirect('/login')

def about(request):
    return render(request,'about.html')

def service(request):
    return render(request,'service.html')

def u_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2)
    context={}
    context['products']=p
    return render(request,'index.html',context) 

def sort(request,sv):
    q1=Q(is_active=True)
    if sv=='0':
        col='price'
    else:
        col='-price'
    p=product.objects.filter(q1).order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def updateqty(request,qv,cid):
    c=cart.objects.filter(id=cid)
    if qv =='1':
        t=c[0].qty + 1
        c.update(qty=t)
    else:
        if c[0].qty > 1:
            t=c[0].qty - 1
            c.update(qty=t)
    return redirect('/cart')

def placeorder(request):
    userid=request.user.id
    c=cart.objects.filter(uid=userid)
    oid=random.randrange(1000,9999)
    for x in c:
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete()
    orders=Order.objects.filter(uid=request.user.id)
    context={}
    l=len(orders)
    s=0
    for x in orders:
        s=s+ x.pid.price * x.qty
    context={}
    context['len']=l
    context['total']=s
    context['data']=orders
    return render(request,'placeorder.html',context)

def makepayment(request):
    ue=request.user.email
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s=s+ x.pid.price * x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_aDHGtDwm5EmXDF", "nlbnMAmzbm0PUyXNTdhX9Bvh"))
    data = { "amount": s*100, "currency": "INR", "receipt": oid }
    payment = client.order.create(data=data)
    context={}
    context['data']=payment
    context['email']=ue
    return render(request,'pay.html',context)

def sendusermail(request,email):
    send_mail(
        "Estore Order",
        "Order Payed Successfully",
        "aryanshetye9168513411@gmail.com",
        [email],
        fail_silently=False,
    )
    return HttpResponse("mail")
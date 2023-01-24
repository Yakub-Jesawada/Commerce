from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.db.models import Max, Count
from django import forms
from . import models
from django.contrib.auth.decorators import login_required
from django.forms import TextInput, NumberInput
from .models import Listing, User


class NewListingForm(forms.Form):
    listingname = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'listingname', 'style': 'width: 300px;', 'class': 'form-control'}))
    baseprice = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Baseprice', 'style': 'width: 300px;', 'class': 'form-control'}))
    imageurl= forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'imageurl', 'style': 'width: 300px;', 'class': 'form-control'}))
    category= forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'categroy', 'style': 'width: 300px;', 'class': 'form-control'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'description', 'style': 'width: 300px;', 'class': 'form-control'}))


def index(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    listings = models.Listing.objects.filter(status = 'OPEN')
    watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
    return render(request, "auctions/index.html",{
        "listings" : listings,
        "watchingcount":watchingcount,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='/login')
def newlisting(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            current_user = request.user
            user = models.User(id= current_user.id)
            listingname = form.cleaned_data["listingname"]
            baseprice = form.cleaned_data["baseprice"]
            imageurl = form.cleaned_data['imageurl']
            category = form.cleaned_data["category"]
            description = form.cleaned_data['description']
            ins = models.Listing.objects.create(listingname=listingname,userid = user,baseprice = baseprice ,imageurl = imageurl,category = category,description = description)
            ins.save()
            watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
            return render(request, 'auctions/success.html',{
                'watchingcount':watchingcount,
                })
        else: 
            watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
            return render(request, 'auctions/failure.html',{
                'watchingcount':watchingcount,
                })
    else:
        current_user = request.user
        user = models.User(id= current_user.id)
        watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
        return render(request, 'auctions/newlisting.html',{
            'form':NewListingForm(),
            'watchingcount':watchingcount,
        })


def categories(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
    if request.method == "POST":
        catglist = []
        catg = list(models.Listing.objects.filter(status = 'OPEN').values('category').distinct())
        for i in catg:
            catglist.append(i['category'])
        catgory = request.POST['category']
        listingsByCategory = models.Listing.objects.filter(category = catgory)
        return render(request,'auctions/categories.html',{
            'listings':listingsByCategory,"category": catglist,'watchingcount':watchingcount,
        })
    catglist = []
    catg = list(models.Listing.objects.filter(status = 'OPEN').values('category').distinct())
    for i in catg:
        catglist.append(i['category'])
    return render(request,'auctions/categories.html',{"category": catglist,'watchingcount':watchingcount,})

@login_required(login_url='/login')
def listingitem(request, id):
    listingobj = models.Listing.objects.get(listingid = id)
    totalbid = models.Bid.objects.filter(itemid = id).count()
    bidinfo = models.Bid.objects.filter(itemid = id).order_by('-latestbid').values('latestbid')
    current_user = request.user
    user = models.User(id= current_user.id)
    watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
    qury = models.Watchlist.objects.filter(ownerid=user,itemid = listingobj)
    comments = models.Comment.objects.filter(itemid = listingobj)
    if not qury:
        item_in_watchlist = False
    else:
        item_in_watchlist = True

    if user == listingobj.userid:
        is_owner = True
    else:
        is_owner =False 

    if totalbid == 0:
        highestbid = float(listingobj.baseprice)
    else:
        highestbid = float(bidinfo[0]['latestbid'])

    if request.method == "POST":
        lbidprice = request.POST["lBid"]
        if totalbid == 0 and float(lbidprice) > float(listingobj.baseprice):
            itemid = models.Listing(listingid = id)
            smessage = "Your bid has been Successfully Registered!!"
            ins = models.Bid.objects.create(itemid = itemid,latestbid = lbidprice, userid= user)
            ins.save()
            totalbid += 1
            highestbid = lbidprice
        elif totalbid == 0 and float(lbidprice) <= float(listingobj.baseprice):
            smessage = "Your bid has Failed try with bid price more than Base price!!"
        elif float(lbidprice) > float(bidinfo[0]['latestbid']):
            itemid = models.Listing(listingid = id)
            smessage = "Your bid has been Successfully Registered!!"
            ins = models.Bid.objects.create(itemid = itemid,latestbid = lbidprice,userid= user)
            ins.save()
            totalbid += 1
            highestbid = lbidprice
        else:
            smessage = "Your bid has Failed try with bid price more than Latest Bid price!!"
        return render(request,'auctions/item.html',{
            "itemdetails": listingobj,
            'totalbid':totalbid,
            'smessage':smessage, 
            'is_msg': True,
            'highestbid':highestbid,
            'is_owner':is_owner,
            'watchingcount':watchingcount,
            "item_in_watchlist":item_in_watchlist,
            "comments":comments,
        })
    return render(request,'auctions/item.html',{
        "itemdetails": listingobj,
        'totalbid':totalbid, 
        'is_msg':False,
        'highestbid':highestbid,
        'is_owner':is_owner,
        'watchingcount':watchingcount,
        "item_in_watchlist":item_in_watchlist,
        "comments":comments,

    })       
    
@login_required(login_url='/login')
def addToWatchlist(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    itemidval = int(request.POST['id'])
    itemid = models.Listing(listingid = itemidval)
    check_redundent = models.Watchlist.objects.filter(ownerid=user,itemid=itemid)
    if not check_redundent :
        ins = models.Watchlist.objects.create(ownerid=user,itemid=itemid)
        ins.save()
    else:
        return redirect('/')
    return redirect('/')

@login_required(login_url='/login')
def deleteFromWatchlist(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    itemidval = int(request.POST['id'])
    itemid = models.Listing(listingid = itemidval)
    models.Watchlist.objects.get(ownerid=user,itemid=itemid).delete()
    return redirect('/displayWatchlist')

@login_required(login_url='/login')
def displayWatchlist(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    watchlistitems = models.Watchlist.objects.filter(ownerid = user)
    itemidinwatchlist = []
    watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
    for item in watchlistitems:
        itemidinwatchlist.append(models.Listing.objects.filter(listingid = item.itemid.listingid)[0])
    return render(request,'auctions/watchlist.html',{
        "listings":itemidinwatchlist,
        'watchingcount':watchingcount,
    })

@login_required(login_url='/login')
def closeListing(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    itemidval = int(request.POST['id'])
    itemid = models.Listing.objects.filter(listingid = itemidval)
    totalbid = models.Bid.objects.filter(itemid = itemidval).count()
    bidinfo = models.Bid.objects.filter(itemid = itemidval).order_by('-latestbid').values('latestbid')
    useriddetails = models.Bid.objects.filter(itemid = itemidval).order_by('-latestbid').values('userid')
    models.Watchlist.objects.filter(itemid__in=itemid).delete()
    if totalbid == 0:
        return redirect('/')
    else:
        soldPrice = float(bidinfo[0]['latestbid'])
        soldTo = useriddetails[0]['userid']
        itemid = models.Listing(listingid = itemidval)
        winnerid = models.User(id = soldTo)
        ins = models.WonBid.objects.create(itemid=itemid,winnerid=winnerid,winnerbid=soldPrice)
        ins.save()
    models.Listing.objects.filter(listingid = itemidval).update(status = 'CLOSED',listingsaleprice=soldPrice,listingwinner = winnerid.username)
    return redirect('/')


@login_required(login_url='/login')
def wonBids(request):
    current_user = request.user
    user = models.User(id= current_user.id)
    limit = models.WonBid.objects.filter(winnerid = user).values('itemid').count()
    wonitems = []
    for i in range(0,limit):
        wonitems.append(models.WonBid.objects.filter(winnerid = user).values('itemid')[i]['itemid'])
    watchingcount = models.Watchlist.objects.filter(ownerid = user).count()
    listings = models.Listing.objects.filter(listingid__in = wonitems)
    if  not listings:
        is_wonbids = True
    else:
        is_wonbids = False    
    return render(request,'auctions/wonbids.html',{
    "listings": listings,
    "is_wonbids":is_wonbids,
    'watchingcount':watchingcount,
})


@login_required(login_url='/login')
def addCommment(request,id):
    itemid = models.Listing.objects.get(listingid = id)
    commentry = request.POST['comment'] 
    current_user = request.user
    user = models.User(id= current_user.id)
    ins = models.Comment.objects.create(itemid=itemid,commentry=commentry,commentator=user)
    ins.save()
    return redirect('/')

# Wonbids add

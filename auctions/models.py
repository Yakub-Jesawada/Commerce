from operator import mod, truediv
from optparse import Option
from re import T
from tkinter import CASCADE
from django.contrib.auth.models import AbstractUser
from django.db import models


Bidding_Status = [
    ('OPEN','Lisitng is Open'),
    ('CLOSED','Listing is Closed')
]

class User(AbstractUser):
    pass


class Listing(models.Model):
    listingid = models.AutoField(primary_key=True)
    listingname = models.CharField(max_length=100)
    baseprice = models.DecimalField(max_digits=100, decimal_places=5)
    listingdate = models.DateTimeField(auto_now_add=True)
    imageurl= models.URLField(max_length = 200)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    category= models.CharField(max_length=100)
    description =  models.CharField(max_length=500)
    status = models.CharField(choices=Bidding_Status, default='OPEN', max_length=7)
    listingwinner = models.CharField(max_length=100,default=None, blank=True, null=True)
    listingsaleprice = models.DecimalField(max_digits=100, decimal_places=5, default=None, blank=True, null=True)

    

class Comment(models.Model):
    cid = models.AutoField(primary_key=True)
    itemid = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='itemcomments')
    commentry = models.CharField(max_length=500)
    commentator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cid}:{self.commentator} said {self.commentry} on the product {self.itemid}"


class Watchlist(models.Model):
    watchid = models.AutoField(primary_key=True)
    ownerid = models.ForeignKey(User,on_delete=models.CASCADE)
    itemid = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.watchid}:{self.ownerid} added {self.itemid} into watchlist "


class Bid(models.Model):
    bidid = models.AutoField(primary_key=True)
    itemid = models.ForeignKey(Listing,on_delete=models.CASCADE)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    latestbid = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return f"{self.bidid}:{self.latestbid} bidded for {self.itemid} "

class WonBid(models.Model):
    uid = models.AutoField(primary_key=True)
    itemid = models.ForeignKey(Listing,on_delete=models.CASCADE)
    winnerid = models.ForeignKey(User, on_delete=models.CASCADE)
    winnerbid = models.DecimalField(max_digits=100, decimal_places=2)
    
    def __str__(self):
        return f"{self.uid}:{self.winnerid} won the bid of {self.itemid} at {self.winnerbid} "
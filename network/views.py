from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import *


def index(request):
    posts = Post.objects.annotate(likes_count=Count('likes')).order_by('-time')
    paginator = Paginator(posts, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        'posts': page_obj,
        "title": "All posts",
    })

def new_post(request):
    if request.method == "POST":
        text = request.POST["text"]
        user = request.user

        if not text:
            return HttpResponse("Please type something before trying to post.")
        else:
            new = Post(user=user, text=text)
            new.save()
            return HttpResponseRedirect(reverse("index"))

def profile(request, profile):
    user = User.objects.get(username=profile)
    if user:
        posts = Post.objects.filter(user=user).annotate(likes_count=Count('likes')).order_by('-time')
        follower = request.user
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if (request.user.is_authenticated):
            isFollowing = Follows.objects.filter(follower=follower, following=user).exists()
            f = Follows.objects.filter(following=user)
            f2 = Follows.objects.filter(follower=user)
            followers = f.count()
            following = f2.count()
            return render(request, "network/profile.html", {
                "user1": user,
                "posts": page_obj,
                "isfollowing": isFollowing,
                "following": following,
                "followers": followers,
            })
        else: 
            return render(request, "network/profile.html", {
                "user1": user,
                "posts": page_obj,
            })
    else:
        return HttpResponseRedirect(reverse("index"))
    
def follow(request, person):
    follower = request.user
    following = User.objects.get(username=person)
    already = Follows.objects.filter(follower=follower, following=following).exists()
    if (already ):
        p = Follows.objects.filter(follower=follower, following=following)
        p.delete()
        return HttpResponseRedirect(reverse("profile", args=(following.username,)))
    else:
        f = Follows(follower=follower, following=following)
        f.save()
        return HttpResponseRedirect(reverse("profile", args=(following.username,)))

def following(request):
    if (request.user.is_authenticated):
        user = request.user
        accounts = Follows.objects.filter(follower=user).values_list('following', flat=True)
        posts = Post.objects.filter(user__in=accounts).order_by('-time')

        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/index.html", {
        "title": "Following",
        "posts": page_obj
        })
    else:
        return HttpResponse("please login")


@csrf_exempt
def edit(request, id):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "")
        try:
            post = Post.objects.get(pk=id)
            post.text = text
            post.save()
            return JsonResponse({"message": "Succesfully updated."}, status=201)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
        
@csrf_exempt
def like(request, id):
    if request.method == "POST":
        try:
            post = Post.objects.get(pk=id)
            user = request.user
            exists = Likes.objects.filter(post=post, user=user)
            if exists:
                exists.delete()
                return JsonResponse({"message": "Like removed"})
            else:
                f = Likes(post=post, user=user)
                f.save()
                return JsonResponse({"message": "Like added"})
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Bruh'}, status=400)
        
def update_likes(request, id):
    if request.method == "GET":
        try:
            post = Post.objects.get(pk=id)
            likes = Likes.objects.filter(post=post)
            l = likes.count()
            return JsonResponse({'likes': l})
        except Post.DoesNotExist:
            return JsonResponse({"error": "bruh"})
        
def haslike(request, id):
    if request.method == "GET":
        if (request.user.is_authenticated):
            try:
                post = Post.objects.get(pk=id)
                has = Likes.objects.filter(post=post, user=request.user)
                if has:
                    return JsonResponse({'hasliked': True})
                else:
                    return JsonResponse({'hasliked': False})
            except Post.DoesNotExist:
                return JsonResponse({'error': 'boo'})
        else:
            return JsonResponse({'hasliked': False})

        
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

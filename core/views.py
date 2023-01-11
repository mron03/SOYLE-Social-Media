from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, auth

from django.contrib import messages
#for checking of authentication of user
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Room, Message, Comment
from django.template.defaulttags import register
from datetime import datetime
import random
# Create your views here.



@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    user_following_list = []
    user_feed = []

    for following in FollowersCount.objects.filter(follower=request.user.username):
        user_following_list.append(following.user)
    
    for following in user_following_list:
        for post in Post.objects.filter(user = following):
            user_feed.append(post)
    
    for post in Post.objects.filter(user = request.user.username):
            user_feed.append(post)

    user_feed.sort(key=lambda x : x.created_at, reverse=True)              

    #Suggestion list creation
    all_profiles = Profile.objects.all()
    suggestion_list = []

    for profile in all_profiles:
        if profile.user.username not in user_following_list and profile.user.username != request.user.username:
            suggestion_list.append(profile)
    
    random.shuffle(suggestion_list)

    #LIST OF WHO LIKED A CERTAIN POST

    

    #Get the latest message from recent users

    messages =  Message.objects.all().order_by('-date_time')
    
    recent_messages = []
    temp = []
    for message in messages:
        if message.room not in temp:
            temp.append(message.room)
            recent_messages.append(message)
            
    
    
    if len(recent_messages) >= 3:
        recent_messages = recent_messages[:3]

    recent_rooms = []
    for message in recent_messages:
        for room in Room.objects.all():
            if int(message.room) == int(room.id):
                recent_rooms.append(room)

    recent_followings_profiles = []
    for room in recent_rooms:
        if room.u1 == user_object.id:
            chat_friend_user = User.objects.get(id = room.u2)
            chat_friend_profile = Profile.objects.get(user = chat_friend_user)

            for message in recent_messages:
                if int(message.room) == int(room.id):
                    chat_friend_profile.recent_message = message.value
                    chat_friend_profile.recent_message_time = message.date_time
                    break

            recent_followings_profiles.append(chat_friend_profile)
        elif room.u2 == user_object.id:
            chat_friend_user = User.objects.get(id = room.u1)
            chat_friend_profile = Profile.objects.get(user = chat_friend_user)
            for message in recent_messages:
                if message.room == room.u1:
                    chat_friend_profile.recent_message = message.value
                    break

            recent_followings_profiles.append(chat_friend_profile)

    today = datetime.today()

    comments = Comment.objects.all()

    context = {
        'user_profile' : user_profile, 
        'posts' : user_feed, 
        'suggestion_list' : suggestion_list[:4], 
        'followings_profiles' : recent_followings_profiles,
        'recent_messages' : recent_messages,
        'today' : today,
        'comments' : comments,
    }

    return render(request, 'index.html', context)
    
@login_required(login_url='signin')
def settings(request):
    
    user_profile = Profile.objects.get(user = request.user)

    if request.method == 'POST':

        
        if request.FILES.get('image') != None:
            user_profile.profileimg = request.FILES.get('image')
        
        user_profile.firstname = request.POST['firstname']
        user_profile.lastname = request.POST['lastname']
        user_profile.email = request.POST['email']
        user_profile.working_at = request.POST['working_at']
        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        user_profile.relationship = request.POST['relationship']
        user_profile.save()

        return redirect('settings')

    return render(request, 'settings.html', {'user_profile' : user_profile})

@login_required(login_url='signin')
def settings_security(request):
    user_object = User.objects.get(username = request.user.username)
    
    if request.method == 'POST':
        new_username = request.POST['username']
        new_password = request.POST['password']
        new_password2 = request.POST['password2']
        
        if new_password == new_password2:
            
            if not User.objects.filter(username = new_username).exists():
                #Refresh info in posts of user
                post_objects = Post.objects.filter(user = user_object.username)
                for post in post_objects:
                    post.user = new_username
                    post.save()

                #Refresh info in LikePost
                like_post_objects = LikePost.objects.filter(username = user_object.username)
                for like_post in like_post_objects:
                    like_post.username = new_username
                    like_post.save()

                #Refresh info in Follower
                followers_count_objects = FollowersCount.objects.filter(user = user_object.username)
                for followers_count in followers_count_objects:
                    followers_count.user = new_username
                    followers_count.save()

                #Change user info
                user_object.username = new_username
                user_object.set_password(new_password)
                user_object.save()

                #Login with new credentials
                user = auth.authenticate(username = new_username, password = new_password)
                auth.login(request, user)
                
            else:
                messages.info(request, 'Username already used')
                return redirect('settings-security')
        else:
            messages.info(request, 'Password does not match')
            return redirect('settings-security')
        

    return render(request, 'settings-security.html', {'user_object' : user_object})

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)
    username_profiles = []
    
    if request.method == 'POST':
        username = request.POST['username']
        if len(username) == 0:
            return redirect('/')

        username_objects = User.objects.filter(username__icontains = username)

        username_ids = []

        for user in username_objects:
            username_ids.append(user.id)
        
        for id in username_ids:
            username_profiles.append(Profile.objects.get(id_user = id))


    return render(request, 'search.html', {'user_profile' : user_profile, 'username_profile_list' : username_profiles})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        
        image = request.FILES.get('image_upload')

        if image is None:
            return redirect('/')

        caption = request.POST['caption']

        new_post = Post.objects.create(user = user, image = image, caption = caption)
        new_post.save()    
    
    return redirect('/')

@login_required(login_url='signin')
def like_post(request): 
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id = post_id)

    like_post = LikePost.objects.filter(post_id = post_id, username = username).first()

    if like_post is None:
        new_like = LikePost.objects.create(post_id = post_id, username = username)
        new_like.save()
        post.no_of_likes += 1
    else:
        like_post.delete()
        post.no_of_likes -= 1
        
    post.save()
    return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = user_object)
    user_post_length = len(user_posts)

    follower = request.user.username
    
    if FollowersCount.objects.filter(follower = follower, user = pk).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'
    
    user_followers = len(FollowersCount.objects.filter(user = pk))
    user_following = len(FollowersCount.objects.filter(follower = pk))

    context = {
        'user_object' : user_object,
        'user_profile' : user_profile,
        'user_posts' : user_posts,
        'user_post_length' : user_post_length,
        'button_text' : button_text,
        'user_followers' : user_followers,
        'user_following' : user_following,
    }


    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower'] #me
        user = request.POST['user']
        follower_user = User.objects.get(username = follower)
        user_user = User.objects.get(username = user)

        if FollowersCount.objects.filter(follower = follower, user = user).first():
            delete_follower = FollowersCount.objects.filter(follower = follower, user = user).first()
            delete_follower.delete()
            
        else:
            new_follower = FollowersCount.objects.create(follower = follower, user = user)
            new_follower.save()

            if not Room.objects.filter(u1 = follower_user.id, u2 = user_user.id).exists() or not Room.objects.filter(u1 = user_user.id, u2 = follower_user.id).exists():

                room = Room.objects.create(u1 = follower_user.id, u2 = user_user.id)
                room.save()
                
        return redirect('/')


    return redirect('/')


def refresh(request):

    return redirect('/')


def signup(request):
    
    if request.method == 'POST':
        
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email already exists')
                return redirect('signup')

            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken')
                return redirect('signup')

            else:
                user = User.objects.create_user(username = username, email = email, password = password)
                user.save()
                #Login user and redirect to settings page
                user_login = auth.authenticate(username = username, password = password)
                auth.login(request, user_login)

                #Create new Profile for new User
                user_model = User.objects.get(username = username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, email = email)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Passwords does not match')
            return redirect('signup')
    else: 

        return render(request, 'signup.html')
    

def signin(request):


    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password = password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Wrong Credentials')
            return redirect('signin')
                
    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def delete_post(request):
    post_id = request.GET.get('post_id')
    delete_post = Post.objects.get(id = post_id)
    delete_post.delete()

    return redirect('/')

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required(login_url='signin')
def followings(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    followings = FollowersCount.objects.filter(follower = request.user.username)
    followings_user = []
    followings_profiles = []

    for following in followings:
        followings_user.append(User.objects.get(username = following.user))
    
    for user in followings_user:
        followings_profiles.append(Profile.objects.get(user = user))
    

    last_message = {}

    for following in followings_profiles:

        if Room.objects.filter(u1 = user_object.id, u2 = following.user.id).exists():
            room_details = Room.objects.get(u1 = user_object.id, u2 = following.user.id)

        elif Room.objects.filter(u1 = following.user.id, u2 = user_object.id).exists():
            room_details = Room.objects.get(u1 = following.user.id, u2 = user_object.id)
        
        message = Message.objects.filter(user = user_object.username, room = room_details.id).last()
        
        if message is not None:
            last_message[following.user.username] = message.value


    context = {
        'user_profile' : user_profile,
        'followings' : followings_profiles,
        'last_message' : last_message,
    }

    return render(request, 'followings.html', context)

@login_required(login_url='signin')
def chat_profile(request):
    user = request.POST['user']
    return redirect('/profile/' + user)

@login_required(login_url='signin')
def room(request, follower, user):

    u1 = User.objects.get(username = follower)
    u2 = User.objects.get(username = user)

    user_profile = Profile.objects.get(user = u1)

    if Room.objects.filter(u1 = u1.id, u2 = u2.id).exists():
        room = Room.objects.get(u1 = u1.id, u2 = u2.id)
        u2_profile = Profile.objects.get(user = u2)
        return render(request, 'room.html', {'user_profile' : user_profile, 'room_details' : room, 'username' : u1, 'room' : u2_profile})
    elif Room.objects.filter(u1 = u2.id, u2 = u1.id).exists():
        room = Room.objects.get(u1 = u2.id, u2 = u1.id)
        u2_profile = Profile.objects.get(user = u2)
        return render(request, 'room.html', {'user_profile' : user_profile, 'room_details' : room, 'username' : u1,'room' : u2_profile})

    return redirect('/followings')


@login_required(login_url='signin')
def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value = message, user = username, room = room_id)
    new_message.save()

    return HttpResponse('Message has been sent')

@login_required(login_url='signin')
def getMessages(request, username, room):
    u1 = User.objects.get(username = username)
    u2 = User.objects.get(username = room)

    if Room.objects.filter(u1 = u1.id, u2 = u2.id).exists():
        room_details = Room.objects.get(u1 = u1.id, u2 = u2.id)

    elif Room.objects.filter(u1 = u2.id, u2 = u1.id).exists():
        room_details = Room.objects.get(u1 = u2.id, u2 = u1.id)
        
    messages = Message.objects.filter(room = room_details.id)
    
    return JsonResponse({'messages' : list(messages.values())})

@login_required(login_url='signin')
def comment(request):
    if request.method == 'POST':

        username = request.POST['username']
        post_id = request.POST['post_id']
        value = request.POST['value']

        user = User.objects.get(username = username)
        user_profile = Profile.objects.get(user = user)
        post = Post.objects.get(id = post_id)
        new_comment = Comment.objects.create(post = post, comment_creator = user_profile, value = value, username = username)
        new_comment.save()

    return redirect('/')




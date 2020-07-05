from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
# from django.views.decorators.cache import cache_page

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

# @cache_page(60 * 20)


def index(request):
    user = request.user
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {
        "group": group, "page": page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None,)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form, 'is_edit': False})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).all()
    following = not request.user.is_anonymous and Follow.objects.filter(
        user=request.user, author=user).exists()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {"page": page, "author": user,
                                            'posts': posts,
                                            "paginator": paginator,
                                            'following': following,
                                            'profile': True})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    posts = Post.objects.filter(author=user).all()
    form = CommentForm()
    comment = Comment.objects.filter(post=post_id)
    return render(request, 'post.html', {'post': post,
                                         'posts': posts,
                                         'author': user,
                                         'comments': comment,
                                         'form': form, })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect(reverse("post", kwargs={'username': username,
                                                'post_id': post_id}))
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(reverse("post", kwargs={'username': username,
                                                'post_id': post_id}))
    return render(request, "new_post.html", {'form': form,
                                             'post': post, 'is_edit': True})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    comment = Comment.objects.filter(post=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.post = post
            form.save()
            return redirect('post', username=post.author, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    author = request.user
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user, author=author).exists()
    if not follow and request.user.id != author.id:
        new_follow = Follow(user=request.user, author=author)
        new_follow.save()
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    if User.is_authenticated == request.user:
        return redirect(reverse('signup'))
    author = get_object_or_404(User, username=username)
    followobj = Follow.objects.filter(user=request.user, author=author).first()
    if followobj:
        followobj.delete()
    return redirect('profile', username=username)



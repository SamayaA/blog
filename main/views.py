import json
import requests

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.authtoken.models import Token
from django_filters import rest_framework as filters
from main.permissions import UserPermission

from .serializers import CategorySerializer, PostSerializer
from .models import Post, Category


# API
class PostViewSet(ModelViewSet):
    '''
    API - Post 
    Supports search filter by name and description
    '''
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [UserPermission]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', "category_id"]
    search_fields = ['name', 'description', 'short_description']
    # authentication_classes = [TokenAuthentication]
    
    def perform_create(self, serializer):
        category = get_object_or_404(Category, id=self.request.data.get('category'))
        return serializer.save(category=category)

class CategoryViewSet(ModelViewSet):
    '''
    API - Category
    Supports search filter by name and description
    '''
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [UserPermission]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_fields = ['id', "posts__name"]
    search_fields = ['name']

def signin(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user != None:
            auth.login(request, user=user)
            return redirect("index")
        else:
            messages.info(request, "Try again.")
            return redirect("signin")
    else:
        return render(request, "signin.html")

@login_required(login_url="signin")
def logout(request):
    auth.logout(request)
    return redirect("signin")

@login_required(login_url="signin")
def upload(request):
    '''
    Post request to create post
    '''
    if request.method == "POST":
        name = request.POST["name"]
        print(request.POST["category"])
        category = request.POST["category"].strip().lower().capitalize()
        description = request.POST["description"]
        short_description = request.POST["short_description"]
        image = smart_str(request.FILES.get("image"))
        
        try:
            category = Category.objects.get(name=category)
        except Category.DoesNotExist:
            messages.info(request, "Category does not exist")
            return redirect("index")
        
        new_post = Post.objects.create(
            name=name, 
            category=category,
            description=description,
            short_description=short_description,
            image=image
            )
        new_post.save()
    return redirect("index")


def index(request):
    '''
    on Get method lists all posts 
    on Post method deletes post of passed post id
    on this page you can fill the form to post the post
    '''
    posts = Post.objects.all()
    category_name = None
    category_id = request.GET.get('category_id')
    
    # Performs delete of certain post
    if request.method == 'POST' and request.user.is_authenticated:
        post_id = request.POST.get('post_id')
        headers = {
            "Content-Type": "application/json",
            'Authorization': f'Token {Token.objects.get(user=request.user)}'
        }
        response = requests.delete("http://" + request.get_host()+f'/api/posts/{post_id}', headers=headers)
        if response.status_code not in [201, 200]:
            return redirect('index')
        else:
            messages.info(request, f' Error! HTTP responce code {response.status_code}')
        return redirect('index')

    if request.method == 'GET':
        if category_id != None:
            posts = requests.get("http://" + request.get_host()+f'/api/posts/?category_id={category_id}').json()
            category_name = requests.get("http://" + request.get_host()+f'/api/categories/?id={category_id}').json()[0].get("name")
    categories = requests.get("http://" + request.get_host()+"/api/categories/").json()
    context = {
        "user": request.user.is_authenticated,
        "posts": posts,
        "categories": categories,
        'category_name': category_name,
        'category_id': category_id,
    }
    return render(request, "index.html", context)

@login_required(login_url='signin')
def edit(request, pk):
    '''
    Edit Post page
    Performs Get request to get all post information
    Performs Patch request to change post
    '''
    if request.method == 'GET':
        categories = requests.get("http://" + request.get_host()+"/api/categories/").json()
        post = requests.get("http://" + request.get_host()+f'/api/posts/{pk}/').json()
        context = {
            'categories': categories,
            'post': post
        }
        return render(request, 'edit.html', context=context)

    if request.method == 'POST':
        url = "http://" + request.get_host()+f'/api/posts/{pk}/'
        headers = {
            "Content-Type": "application/json",
            'Authorization': f'Token {Token.objects.get(user=request.user)}'
        }
        description = request.POST.get("description")
        short_description = request.POST.get("short_description")
        post = requests.get("http://" + request.get_host()+ f'/api/posts/{pk}/', headers=headers).json()
        # 
        image = request.FILES.get("image") if request.FILES.get("image") else post['image']
        # try:
        #     category = Category.objects.get(name=category)
        # except Category.DoesNotExist:
        #     messages.info(request, "Category does not exist")
        #     return redirect("edit")
        data = {
            'id': post['id'],
            'description': description,
            'short_description': short_description,
            'image': image
        }
        data = json.dumps(data)

        response = requests.patch(url, headers=headers, data=data)
        if response.status_code not in [201, 200]:
            return redirect('index')
        else:
            messages.info(request, f' Error! HTTP responce code {response.status_code}')
            return redirect('index')

@login_required(login_url='signin')
def category(request):
    '''
    Add category or change change category
    '''
    headers = {
            "Content-Type": "application/json",
            "Authorization": f'Token {Token.objects.get(user=request.user)}'
    }

    if request.method == "GET":
        category_id = request.GET.get("category_id")
        if category_id != None:
            category = requests.get("http://" + request.get_host()+ f'/api/categories/{category_id}/').json()
            context = {
                    'category': category,
                    'category_id': category_id,
            }
            return render(request, 'category.html', context=context)
        else:
            return render(request, 'category.html')

    if request.method == "POST":
        name = request.POST['name']
        data = {
            "name": name,
        }
        data = json.dumps(data)
        response = requests.post("http://" + request.get_host()+ f'/api/categories/', headers=headers, data=data)
        print(response.headers, response.text)

        if response.status_code not in [201, 200, 204]:
            return redirect('index')
        else:
            messages.info(request, f' Error! HTTP responce code {response.status_code}')
            return redirect('category')

    if request.method == "PUT":
        name = request.POST['name']
        id = request.POST['id']
        data = {
            'name': name,
        }
        headers = json.dumps(headers)
        data = json.dumps(data)
        response = requests.patch("http://" + request.get_host()+ f'/api/categories/{id}/', headers=headers, data=data)
        if response.status_code not in [201, 200, 204]:
            return redirect('index')
        else:
            messages.info(request, f' Error! HTTP responce code {response.status_code}')
            return redirect('index')


            

            
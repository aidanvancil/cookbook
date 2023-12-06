# Django Libs
from django.contrib.auth import authenticate, login as log, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django import forms

# File Libs
from .utils import get_recipes, get_recipe_by_url

# External Libs
from decouple import config
import psycopg2
import base64
import json

DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')

DATABASE_CONNECTION_PARAMS = {
    'dbname': DB_NAME,
    'user': DB_USER, 
    'password': DB_PASSWORD,
    'host': DB_HOST,
    'port': DB_PORT,
}

def create_user(request, user_data_json):
    if request.method == 'POST':
        try:
            data = json.loads(user_data_json)
            username = data.get('user').get('username')
            email = data.get('user').get('email')
            first_name = data.get('user').get('first_name')
            last_name = data.get('user').get('last_name')

            with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO public."User" (username, email, first_name, last_name) VALUES (%s, %s, %s, %s)',
                        (username, email, first_name, last_name)
                    )

            return redirect('home')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required(login_url='login')
def card(request, recipe_url):
    recipe_url = base64.b64decode(recipe_url.encode()).decode('utf-8')
    recipe = get_recipe_by_url(recipe_url)
    context = {
        'recipe': recipe,
        'link': request.GET.get('source', None)
    }
    return render(request, 'card.html', context)

@login_required(login_url='login')
def home(request):
    username = request.user.username
    user_recipes = []

    try:
        with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT api_url FROM public."Recipe" WHERE username = %s', (username,))
                user_recipes = cursor.fetchall()
                user_recipes = [i[0] for i in user_recipes]
    except Exception as e:
        print(f"Error fetching user recipes: {str(e)}")

    if request.method == 'POST':
        query = request.POST.get('q')
        recipes = get_recipes(query)

        paginator = Paginator(recipes, 12)
        page = request.GET.get('page')
        recipes = paginator.get_page(page)
        request.session['search_query'] = query
        print(user_recipes)
        context = { 
            'recipes': recipes,
            'user_recipes': user_recipes
        }
    else:
        query = request.session.get('search_query', '')
        recipes = get_recipes(query)
        print(user_recipes)
        paginator = Paginator(recipes, 12)
        page = request.GET.get('page')
        recipes = paginator.get_page(page)

        context = {
            'recipes': recipes,
            'user_recipes': user_recipes,
        }

    return render(request, 'home.html', context)


def errors(request):
    context = {
        'error': 404
    }
    return render(request, 'errors.html', context)
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            log(request, user)

            user_data = {
                'username': username,
                'email': form.cleaned_data.get('email'),
                'first_name': form.cleaned_data.get('first_name'),
                'last_name': form.cleaned_data.get('last_name'),
            }

            user_data_json = json.dumps({'user': user_data})

            return create_user(request, user_data_json)
    else:
        form = SignUpForm()

    context = {
        'form': form,
    }
    return render(request, 'signup.html', context)


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']

def login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            log(request, user)
            return redirect('home')
    else:
        form = LoginForm()

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def bookmarks(request):
    username = request.user.username
    user_recipes = []

    try:
        with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT api_url, title FROM public."Recipe" WHERE username = %s', (username,))
                user_recipes = cursor.fetchall()
                
    except Exception as e:
        print(f"Error fetching user recipes: {str(e)}")

    
    recipes_with_details = []
    for recipe_url, title in user_recipes:
        recipe_details = get_recipe_by_url(recipe_url)
        if recipe_details:
            recipes_with_details.append({'title': title, 'details': recipe_details})

    user_recipes = [i[0] for i in user_recipes]
    context = {
        'user_recipes': recipes_with_details,
        'user_recipe_urls': user_recipes
    }

    return render(request, 'bookmarks.html', context)

@login_required(login_url='login')
def bookmark_recipe(request):
    if request.method == 'POST':
        try:
            url = request.POST.get('url')
            username = request.user.username
            data = get_recipe_by_url(url)

            recipe_data = data.get('recipe', {})
            recipe_title = recipe_data.get('label')
            recipe_url = recipe_data.get('url')
            recipe_image = recipe_data.get('image')

            with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'INSERT INTO public."Recipe" (recipe_url, title, image, username, api_url) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (recipe_url) DO NOTHING',
                        (recipe_url, recipe_title, recipe_image, username, url,)
                    )

            labels_data = recipe_data.get('healthLabels', [])
            for label_data in labels_data:
                label_title = label_data

                with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute('INSERT INTO public."Label" (label_id, title) VALUES (%s, %s) ON CONFLICT (label_id) DO NOTHING RETURNING label_id', (label_title, label_title,))
                        result = cursor.fetchone()
                        if result:
                            label_id = result[0]
                        else:
                            cursor.execute('SELECT label_id FROM public."Label" WHERE label_id = %s', (label_title,))
                            label_id = cursor.fetchone()[0]

                        cursor.execute(
                            'INSERT INTO public."RecipeLabel" (recipe_url, label_id) VALUES (%s, %s) ON CONFLICT (recipe_url, label_id) DO NOTHING',
                            (recipe_url, label_id)
                        )

            ingredients_data = recipe_data.get('ingredients', [])
            for ingredient_data in ingredients_data:
                ingredient_title = ingredient_data.get('food')
                ingredient_id = ingredient_data.get('foodId')
                quantity = ingredient_data.get('quantity')
                measure = ingredient_data.get('measure')

                with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute('INSERT INTO public."Ingredient" (ingredient_id, title) VALUES (%s, %s) ON CONFLICT (ingredient_id) DO NOTHING', (ingredient_id, ingredient_title,))
                        cursor.execute(
                            'INSERT INTO public."RecipeIngredient" (recipe_url, ingredient_id, quantity, measure) '
                            'VALUES (%s, %s, %s, %s) ON CONFLICT (recipe_url, ingredient_id, quantity, measure) DO NOTHING',
                            (recipe_url, ingredient_id, quantity, measure,)
                        )
            return redirect('home')
        except psycopg2.IntegrityError:
            return redirect('home')
    return redirect('home')

@login_required(login_url='login')
def unbookmark_recipe(request):
    if request.method == 'POST':
        try:
            source = request.GET.get('source', None)
            url = request.POST.get('url')
            recipe = get_recipe_by_url(url)
            recipe_url = recipe.get('url')
            print(recipe_url)
            username = request.user.username
            with psycopg2.connect(**DATABASE_CONNECTION_PARAMS) as connection:
                with connection.cursor() as cursor:
                    cursor.execute('DELETE FROM public."RecipeIngredient" WHERE recipe_url = %s', (recipe_url,))
                    cursor.execute('DELETE FROM public."RecipeLabel" WHERE recipe_url = %s', (recipe_url,))
                    cursor.execute('DELETE FROM public."Recipe" WHERE api_url = %s AND username = %s', (url, username))
            print(source)
            if source == 'bookmarks':
                return redirect('bookmarks')
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error unbookmarking recipe: {str(e)}")
    return redirect('home')
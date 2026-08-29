from django.shortcuts import render,redirect,get_object_or_404
from .models import Recipe, Profile, Like, Rating, Comment
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count

def home(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    quick = request.GET.get('quick')

    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        recipes = recipes.filter(category=category)

    if quick:
        recipes = recipes.filter(prep_time__lte=15, prep_time__isnull=False)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(
            Like.objects.filter(user=request.user, recipe__in=recipes).values_list('recipe_id', flat=True)
        )

    trending = []
    if not query and not category and not quick:
        trending = Recipe.objects.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')[:4]

    return render(request, 'home.html', {
        'recipes': recipes,
        'categories': Recipe.CATEGORY_CHOICES,
        'active_category': category,
        'active_quick': quick,
        'liked_ids': liked_ids,
        'trending': trending,
    })


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    is_liked = False
    user_rating = None
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, recipe=recipe).exists()
        existing = Rating.objects.filter(user=request.user, recipe=recipe).first()
        user_rating = existing.stars if existing else None

    return render(request, 'recipe_detail.html', {
        'recipe': recipe,
        'is_liked': is_liked,
        'user_rating': user_rating,
        'star_range': range(1, 6),
        'comments': recipe.comments.select_related('user'),
        'ingredient_list': [line.strip() for line in recipe.ingredients.splitlines() if line.strip()],
        'step_list': [line.strip() for line in recipe.steps.splitlines() if line.strip()],
        'is_owner': request.user.is_authenticated and recipe.created_by_id == request.user.id,
    })


@login_required(login_url='/login/')
def toggle_like(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        like.delete()

    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    return redirect(next_url)

def signup_view(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username already exits")
            return redirect('/signup/')
        user=User.objects.create_user(username=username,password=password)
        user.save()
        messages.success(request,'Account created succesfully')
        return redirect('/login/')
    return render(request,'signup.html')
def login_view(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.error(request,"Invalid credentials")
            return redirect('/login/')
    return render(request,'login.html')    
def logout_view(request):
    logout(request)
    return redirect('/login/')

@login_required(login_url='/login/')
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        bio = request.POST.get('bio')
        image = request.FILES.get('profile_pic')

        profile.bio = bio

        if image:
            profile.profile_pic = image

        profile.save()

    return render(request, 'profile.html', {
        'profile': profile,
        'my_recipes': Recipe.objects.filter(created_by=request.user).order_by('-created_at'),
    })


@login_required(login_url='/login/')
def add_recipe(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        ingredients = request.POST.get('ingredients')
        steps = request.POST.get('steps')
        category = request.POST.get('category') or 'dinner'
        prep_time = request.POST.get('prep_time') or None
        servings = request.POST.get('servings') or None
        cost_estimate = request.POST.get('cost_estimate') or ''
        image = request.FILES.get('image')

        if not title:
            messages.error(request, "Title is required")
            return redirect('add_recipe')

        Recipe.objects.create(
            title=title,
            description=description,
            ingredients=ingredients,
            steps=steps,
            category=category,
            prep_time=prep_time,
            servings=servings,
            cost_estimate=cost_estimate,
            image=image,
            created_by=request.user,
        )
        messages.success(request, "Recipe added successfully!")
        return redirect('home')

    return render(request, 'add_recipe.html')


@login_required(login_url='/login/')
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe.created_by_id != request.user.id:
        messages.error(request, "You can only edit your own recipes.")
        return redirect('recipe_detail', recipe_id=recipe.id)

    if request.method == "POST":
        recipe.title = request.POST.get('title')
        recipe.description = request.POST.get('description')
        recipe.ingredients = request.POST.get('ingredients')
        recipe.steps = request.POST.get('steps')
        recipe.category = request.POST.get('category') or 'dinner'
        recipe.prep_time = request.POST.get('prep_time') or None
        recipe.servings = request.POST.get('servings') or None
        recipe.cost_estimate = request.POST.get('cost_estimate') or ''

        image = request.FILES.get('image')
        if image:
            recipe.image = image

        if not recipe.title:
            messages.error(request, "Title is required")
            return redirect('edit_recipe', recipe_id=recipe.id)

        recipe.save()
        messages.success(request, "Recipe updated!")
        return redirect('recipe_detail', recipe_id=recipe.id)

    return render(request, 'edit_recipe.html', {'recipe': recipe})


@login_required(login_url='/login/')
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if recipe.created_by_id != request.user.id:
        messages.error(request, "You can only delete your own recipes.")
        return redirect('recipe_detail', recipe_id=recipe.id)

    if request.method == "POST":
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect('home')

    return redirect('recipe_detail', recipe_id=recipe.id)


@login_required(login_url='/login/')
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        stars = request.POST.get('stars')
        if stars and stars.isdigit() and 1 <= int(stars) <= 5:
            Rating.objects.update_or_create(
                user=request.user, recipe=recipe, defaults={'stars': int(stars)}
            )
            messages.success(request, "Thanks for rating!")

    return redirect('recipe_detail', recipe_id=recipe.id)


@login_required(login_url='/login/')
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(user=request.user, recipe=recipe, text=text)

    return redirect('recipe_detail', recipe_id=recipe.id)

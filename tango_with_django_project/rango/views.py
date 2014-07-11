from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category   
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect

def index(request):
    context = RequestContext(request)
    
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    category_list = EncodeCategoryUrl(category_list)
    
    context_dict = {'categories': category_list, 'pages': pages_list}
    
    context_dict = fill_context_with_cat_list(context_dict)
    
    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)
        
        if(datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1
    
    return render_to_response('rango/index.html', context_dict, context)
    
    
def about(request):
    context = RequestContext(request)
    visits = request.session.get('visits')
    count = visits if visits else 0
    
    context_dict = {'aboutmessage' : "Rango Says: Here is the about page.", 'visits':visits}
    context_dict = fill_context_with_cat_list(context_dict)
    return render_to_response('rango/about.html', context_dict, context)
    
    
    
def category(request, category_name_url):
    context = RequestContext(request)
    
    category_name = category_name_url.replace('_', ' ')
    
    context_dict = {'category_name': category_name,'category_url':category_name_url}
    
    try:
        category = Category.objects.get(name=category_name)
        
        pages = Page.objects.filter(category=category)
        
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass
    
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    context_dict['result_list'] = result_list
    
    context_dict = fill_context_with_cat_list(context_dict)
        
    return render_to_response('rango/category.html', context_dict, context)
    
@login_required
def add_category(request):
    context = RequestContext(request)
    context_dict = {}
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()
    
    context_dict = fill_context_with_cat_list(context_dict)
    
    return render_to_response('rango/add_category.html', {'form':form}, context)


@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)
    
    category_name = DecodeCategoryUrl(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            page = form.save(commit=False)
            
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render_to_response('rango/add_category.html', {}, context)
        
            page.views = 0
            page.save()
            return category(request, category_name_url)
        
        else:
            print form.errors
    
    else:
        form = PageForm()

    context_dict =  {'category_url': category_name_url,
                    'category_name': category_name,
                    'form':form}
    try:
        category_name = category_name_url.replace('_', ' ')
        cgr = Category.objects.get(name=category_name)
        context_dict['category'] = cgr
    except Category.DoesNotExist:
        pass
    
    context_dict = fill_context_with_cat_list(context_dict)
    
    return render_to_response(
     'rango/add_page.html',
    context_dict,
     context
    )
    
def register(request):
    context = RequestContext(request)
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
        
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}
    context_dict = fill_context_with_cat_list(context_dict)
    return render_to_response('rango/register.html', context_dict , context)


@login_required
def restricted(request):
    context = RequestContext(request)
    context_dict = {}
    context_dict = fill_context_with_cat_list(context_dict)
    return render_to_response('rango/restricted.html',context_dict, context)

def user_login(request):
    context = RequestContext(request)
    context_dict = {}
    context_dict = fill_context_with_cat_list(context_dict)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Wrong username or password, please check again")
    
    else:
        return render_to_response('rango/login.html', context_dict, context)


def search(request):
    context = RequestContext(request)
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
    context_dict = {'result_list': result_list}
    context_dict = fill_context_with_cat_list(context_dict)
    return render_to_response('rango/category.html', context_dict, context)

def get_category_list():
    cat_list = Category.objects.all()
    cat_list = EncodeCategoryUrl(cat_list)

    return cat_list

def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)
        else:
                cat_list = Category.objects.all()

        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        cat_list = EncodeCategoryUrl(cat_list)

        return cat_list
    
def suggest_category(request):
        context = RequestContext(request)
        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)

        return render_to_response('rango/category_list.html', {'cat_list': cat_list }, context)
            
@login_required
def profile(request):
    context = RequestContext(request)
    
    u = User.objects.get(username=request.user)
    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None
    
    context_dict = {'user': u, 'userprofile': up}
    context_dict = fill_context_with_cat_list(context_dict)
    return render_to_response('rango/profile.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')
    
def track_url(request):
    context = RequestContext(request)
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

def EncodeCategoryUrl(category_list):
    for category in category_list:
        category.url = category.name.replace(' ', '_')
    return category_list

def DecodeCategoryUrl(category_name_url):
    category_name_url = category_name_url.replace('_', ' ')
    return category_name_url   

def fill_context_with_cat_list(context_dict):
    cat_list = get_category_list()
    context_dict['cat_list'] = cat_list 
    return context_dict

@login_required
def like_category(request):
    context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    
    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if(category):
            likes = category.likes + 1
            category.likes = likes
            category.save()
    
    return HttpResponse(likes)
import os
from random import randrange

def populate():
    python_cat = add_cat('Python', 128, 64)
    
    add_page(cat=python_cat,
        title="Official Python Tutorial",
        url="http://docs.python.org/2/tutorial")
    
    add_page(cat=python_cat,
        title="How to Think Like a Computer Scientist",
        url="http://www.greenteapess.com/thinkpython")
        
    add_page(cat=python_cat,
        title="Learn Python in 10 Minutes",
        url="http://www.korokithakis.com/tutorials/python/")
        
    django_cat = add_cat("Django", 64, 32)
    
    add_page(cat=django_cat,
        title="Django Rocks",
        url="http://www.djangorocks.com")
        
    add_page(cat=django_cat,
        title="How to Tango with Django",
        url="http://www.tangowithdjango.com")
    
    frame_cat = add_cat("Other Frameworks", 32, 16)
    
    add_page(cat=frame_cat,
        title="Bottle",
        url="http://bottlepy.org/docs/dev/")
        
    add_page(cat=frame_cat,
        title="Flask",
        url="http://flask.pocoo.org")        
    
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print "- {0} - {1}".format(str(c), str(p))

def add_page(cat, title, url, views=randrange(1000)):
    views = (views * randrange(10)) + randrange(1000) 
    p = Page.objects.get_or_create(category=cat,
        title=title,
        url=url,
        views=views)[0]
    return p
    
def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    return c
    
if __name__ == '__main__':
    print "Starting Rango population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
    from rango.models import Category, Page
    populate()
        
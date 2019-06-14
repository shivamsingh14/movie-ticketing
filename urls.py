from django.conf.urls import url, include
from django.contrib import admin
from app.users import urls as user_urls
from app.movies import urls as movie_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include([
        url('^users/', include(user_urls.urlpatterns, namespace='user')),
        url('^movies/', include(movie_urls.urlpatterns, namespace='movie')),
    ])
    )
]

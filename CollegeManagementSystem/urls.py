# from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='APIs Documentation',
        default_version='v1'
    ),
    public=True
)

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/v1/', include('main_app.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('re-docs/', schema_view.with_ui('redoc', cache_timeout=0), name='api-re-doc'),
]

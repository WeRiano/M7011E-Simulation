from django.urls import path, register_converter

from . import views

class FloatConverter:
    regex = '[\d\.\d]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return '{}'.format(value)


register_converter(FloatConverter, 'float')

urlpatterns = [
    path('get_current_conditions/<slug:conditions>/', views.get_conditions),
    path('get_current_conditions/<slug:conditions>/<int:user_id>/', views.admin_get_conditions),
    path('set_update_frequency/<float:delta>/', views.set_delta),
    path('set_update_frequency/<float:delta>/<int:user_id>/', views.admin_set_delta),
    path('set_buffer_settings/<float:storing>/<float:using>/', views.set_ratios),
    path('set_buffer_settings/<float:storing>/<float:using>/<int:user_id>/', views.admin_set_ratios),
    path('admin/reset_simulation/<int:user_id>/', views.admin_reset_sim)
]
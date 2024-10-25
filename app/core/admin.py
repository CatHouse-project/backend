"""
Django admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['id', 'last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

class AnswerAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('user', 'get_answer_preview')

    def get_answer_preview(self, obj):
        # 답안을 미리보기 형태로 출력
        return str(obj.answer)[:50] + '...'

    get_answer_preview.short_description = 'User Answer Preview'

class MatchAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['requester', 'recipient', 'status', 'created_at']

class GroupAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'get_members', 'created_at']

    def get_members(self, obj):
        # 그룹 멤버를 쉼표로 구분하여 출력
        return ', '.join([member.email for member in obj.members.all()])

    get_members.short_description = 'Group Members'

class ResultAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ['id', 'user', 'get_matching_data']

    def get_matching_data(self, obj):
        # 매칭 결과를 미리보기 형태로 출력
        return str(obj.matching_data)[:50] + '...'

    get_matching_data.short_description = 'Matching Result Preview'

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Answer, AnswerAdmin)
admin.site.register(models.Match, MatchAdmin)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Result, ResultAdmin)
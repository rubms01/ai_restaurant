from django.contrib import admin

from .models import (
    Article,
    Restaurant,
    RestaurantCategory,
    RestaurantImage,
    RestaurantMenu,
    Review,
    ReviewImage,
    SocialChannel,
    Tag,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # 관리자 리스트에 보이게 하는거
    list_display = [
        "id",
        "title",
        "show_at_index",
        "is_published",
        "created_at",
        "modified_at",
    ]
    # 수정 할때 아래 필드를 보여줌
    fields = ["title", "preview_image", "content", "show_at_index", "is_published"]

    # 검색어 입력
    search_fields = ["title"]

    # 관리자 페이지 오른쪽에 필터 사이드바를 만듭니다
    # show_at_index와 is_published 필드로 데이터를 필터링할 수 있게 해줍니다
    list_filter = ["show_at_index", "is_published"]

    # 날짜 기반 네비게이션
    date_hierarchy = "created_at"

    # 일괄 작업 기능
    # 여러 객체를 선택해서 한 번에 "발행 상태로 변경" 같은 작업을 할 수 있게 해줍니다
    actions = ["make_published"]

    # 리스트에 있는거 선택후 action에 비공개 -> 공개 상태로 변경.
    @admin.action(description="선택한 컬럼을 공개상태로 변경합니다.")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fields = ["name"]
    search_fields = ["name"]


class RestaurantMenuInline(admin.TabularInline):
    model = RestaurantMenu
    # 수정이나 추가시에 아래 빈칸 1칸생기게 하는거
    extra = 1


class RestaurantImageInline(admin.TabularInline):
    model = RestaurantImage
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "branch_name",
        "is_closed",
        "phone",
        "rating",
        "rating_count",
    ]
    fields = [
        "name",
        "branch_name",
        "category",
        "is_closed",
        "phone",
        "latitude",
        "longitude",
        "tags",
    ]
    readonly_fields = ["rating", "rating_count"]
    search_fields = ["name", "branch_name"]
    list_filter = ["tags"]
    # 옵션 선택시(드랍다운) : "한"을 입력 → 한식, 한정식 등 자동 완성 목록 표시
    autocomplete_fields = ["tags"]
    # 수정할때 : 위에 만든 클래스 같이 사용 가능
    inlines = [RestaurantMenuInline, RestaurantImageInline]

    # 인스턴스를 생성할때 인라인 표시 안하도록
    # 아직 식당도 안 만들었는데 메뉴를 어떻게 추가해? 레스토랑 생성 후 -> 레스토랑 메뉴,이미지 생성 가능.
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []


@admin.register(RestaurantCategory)
class RestaurantCategoryIAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fields = ["cuisine_type", "name"]


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "restaurant_name", "author", "rating", "contetnt_partial"]
    inlines = [ReviewImageInline]

    # 인스턴스를 생성할때 인라인 표시 안하도록
    def get_inline_instances(self, request, obj=None):
        return obj and super().get_inline_instances(request, obj) or []


@admin.register(SocialChannel)
class SocialChannelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    fields = ["name"]

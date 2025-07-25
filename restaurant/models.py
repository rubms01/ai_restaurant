from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError

# 배포 전 커밋


class Article(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    preview_image = models.ImageField(null=True, blank=True)
    content = models.TextField()
    show_at_index = models.BooleanField(default=False)  # 기본값은 표시안함
    is_published = models.BooleanField(default=False)  # 칼럼을 사용자에게 노출할지 여부
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    modified_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        verbose_name = "칼럼"
        verbose_name_plural = "칼럼s"

    def __str__(self):
        return f"{self.id} - {self.title}"


class Restaurant(models.Model):
    name = models.CharField("이름", max_length=100, db_index=True)
    branch_name = models.CharField(
        "지점", max_length=100, db_index=True, null=True, blank=True
    )
    description = models.TextField("설명", null=True, blank=True)
    address = models.CharField("주소", max_length=255, db_index=True)
    feature = models.CharField("특징", max_length=255, null=True, blank=True)
    is_closed = models.BooleanField("폐업여부", default=False)
    latitude = models.DecimalField(
        "위도",
        max_digits=16,  # 소수점포함 숫자자릿점 38.01215654
        decimal_places=12,  # 소수점 이하 자릿수 정수부: 소수부
        db_index=True,
        default="0.0000",
    )
    longitude = models.DecimalField(
        "경도",
        max_digits=16,
        decimal_places=12,
        db_index=True,
        default="0.0000",
    )
    phone = models.CharField(
        "전화번호", max_length=16, help_text="E.164 포멧"  # 국가 번호 : +82
    )
    rating = models.DecimalField(
        "평점",
        max_digits=3,
        decimal_places=2,
        default=0.0,
    )
    rating_count = models.PositiveIntegerField("평가수", default=0)  # 좋아요 갯수
    start_time = models.TimeField(
        "영업 시작 시간", null=True, blank=True
    )  # 영업 시작 시간
    end_time = models.TimeField("영업 종료 시간", null=True, blank=True)
    last_order_time = models.TimeField("라스트 오더 시간", null=True, blank=True)
    category = models.ForeignKey(
        "restaurant.RestaurantCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField("Tag", blank=True)  # M:N 관계
    region = models.ForeignKey(
        "restaurant.Region",
        on_delete=models.SET_NULL,  # 참조된 지역 삭제시 Null로 설정됨.
        null=True,
        blank=True,
        db_index=True,
        verbose_name="지역",
        related_name="restaurants",  # 역참조 이름 설정
    )

    class Meta:
        verbose_name = "레스토랑"
        verbose_name_plural = "레스토랑s"

    def __str__(self):
        return f"{self.name} {self.branch_name}" if self.branch_name else self.name

    # 관리자 페이지에 지점명 있으면 이름 지점명을 반환해주고, 없으면 식당 이름만 반환. ex.) 본스테이크 강남점, 본스테이크


class CuisineType(models.Model):
    name = models.CharField("이름", max_length=20)

    class Meta:
        verbose_name = "음식종류"
        verbose_name_plural = "음식종류s"

    def __str__(self):
        return self.name


class RestaurantCategory(models.Model):
    name = models.CharField("이름", max_length=20)
    cuisineType = models.ForeignKey(
        "CuisineType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

    def __str__(self):
        return self.name


class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    is_representative = models.BooleanField("대표 이미지 여부", default=False)
    # 이미지를 업데이트 했는데 체크하면 대표이지미로 변경.

    order = models.PositiveBigIntegerField("순서", null=True, blank=True)
    name = models.CharField("이름", max_length=100, null=True, blank=True)
    image = models.ImageField("이미지", max_length=100, upload_to="restaurant")
    # 사용자가 이미지를 업로드하면 MEDIA_ROOT/restaurant/폴더 아래 이미지 파일이 저장됐다.
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "레스토랑 카테고리"
        verbose_name_plural = "레스토랑 카테고리s"

    def __str__(self):
        return f"{self.id}:{self.image}"

    # 대표이미지를 2개 이상 저장 하지 못하도록 막는 코드를 작성.
    def clean(self):
        images = self.restaurant.restaurantimage_set.filter(is_representive=True)
        # .restaurantimage_set : 해당 Restaurant 연결된 모든 이미지들
        # .filter() : 괄호안이 조건이고, 그에 맞는 필터링한 이미지를 가져온다.

        if self.is_representative and images.exclude(id=self.id).count() > 0:
            raise ValidationError("대표 이미지는 하나만 설정 할 수 있습니다.")
        # 현재 이미지가 대표이미지고, 현재 이미지를 제외한 다른 이미지들이 1개 이상 존재한다면


class RestaurantMenu(models.Model):
    # 레스토랑을 참조함. 레스토랑 삭제되면 메뉴도 삭제
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField("이름", max_length=100)
    price = models.PositiveBigIntegerField("가격", default=0)
    image = models.ImageField(
        "이미지", upload_to="restaurant-menu", null=True, blank=True
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "레스토랑 메뉴"
        verbose_name_plural = "레스토랑 메뉴s"

    def __str__(self):
        return f"{self.id}:{self.image}"


class Review(models.Model):
    title = models.CharField("제목", max_length=100)
    author = models.CharField("작성자", max_length=100)
    profile_image = models.ImageField(
        "프로필 이미지", upload_to="review-profile", null=True, blank=True
    )
    content = models.TextField("내용")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    restaurant = models.ForeignKey(Restaurant, max_length=100, on_delete=models.CASCADE)
    social_channel = models.ForeignKey(
        "SocialChannel", on_delete=models.SET_NULL, blank=True, null=True
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "레스토랑 메뉴"
        verbose_name_plural = "리뷰s"

    def __str__(self):
        return f"{self.author} : {self.title}"

    @property
    def restaurant_name(self):
        return self.restaurant.name

    @property
    def contetnt_partial(self):
        return self.content[:20]


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(max_length=100, upload_to="review")
    created_at = models.DateTimeField("생성일", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("수정일", auto_now=True, db_index=True)

    class Meta:
        verbose_name = "리뷰이미지"
        verbose_name_plural = "리뷰이미지"

    def __str__(self):
        return f"{self.id}:{self.image}"


class SocialChannel(models.Model):
    name = models.CharField("이름", max_length=100)

    class Meta:
        verbose_name = "소셜채널"
        verbose_name_plural = "소셜채널"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        "이름", max_length=100, unique=True
    )  # 이 필드는 중복을 허용하지 않음

    class Meta:
        verbose_name = "태그"
        verbose_name_plural = "태그"

    def __str__(self):
        return self.name


class Region(models.Model):
    sido = models.CharField("광역시도", max_length=20)
    sigungu = models.CharField("시군구", max_length=20)
    eupmyeondong = models.CharField("읍면동", max_length=20)

    class Meta:
        verbose_name = "지역"
        verbose_name_plural = "지역"
        unique_together = ("sido", "sigungu", "eupmyeondong")

    def __str__(self):
        return f"{self.sido} {self.sigungu} {self.eupmyeondong}"

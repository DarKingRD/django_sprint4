from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="index"),
    path(
        "posts/create/",
        views.PostCreateView.as_view(),
        name="create_post"
    ),
    path(
        "posts/<int:post_id>/",
        views.PostDetailView.as_view(),
        name="post_detail"
    ),
    path(
        "posts/<int:post_id>/edit/",
        views.PostEditView.as_view(), name="edit_post"
    ),
    path(
        "posts/<int:post_id>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    path(
        "posts/<int:post_id>/add_comment/",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/delete_comment/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/edit_comment/",
        views.CommentEditView.as_view(),
        name="edit_comment",
    ),
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostsView.as_view(),
        name="category_posts",
    ),
    path(
        "profile/<str:username>/",
        views.ProfileView.as_view(),
        name="profile"
    ),
    path(
        "edit_profile/",
        views.ProfileEditView.as_view(),
        name="edit_profile"
    ),
]

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session
)

from app import db
from sqlalchemy.orm import joinedload, selectinload
from app.posts import post_bp
from .models import Post, Tag
from app.posts.forms import (
    PostForm,
    DeletePostForm
)


# Перегляд усіх активних постів
@post_bp.route("/")
@post_bp.route("")
def list_posts():
    stmt = (
        db.select(Post)
        .options(
            joinedload(Post.user),
            selectinload(Post.tags)
        )
        .where(Post.is_active.is_(True))
        .order_by(
            Post.posted.desc(),
            Post.id.desc()
        )
    )

    posts = db.session.scalars(stmt).all()

    return render_template(
        "posts/all_posts.html",
        posts=posts
    )


# Створення поста
@post_bp.route(
    "/create",
    methods=["GET", "POST"]
)
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        # Створюємо об'єкт
        post = Post(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            category=form.category.data,
            posted=form.publish_date.data,
            is_active=form.enabled.data,
            user_id=form.author_id.data
        )

        # Отримуємо вибрані теги з БД
        post.tags = db.session.scalars(
            db.select(Tag).where(
                Tag.id.in_(form.tags.data)
            )
        ).all()

        # Зберігаємо в базу
        db.session.add(post)
        db.session.commit()

        flash(
            "Пост успішно додано!",
            "success"
        )

        return redirect(
            url_for("posts.list_posts")
        )

    if request.method == "POST":
        flash(
            "Перевірте правильність даних.",
            "error"
        )

    return render_template(
        "posts/add_post.html",
        form=form,
        title="Додати пост"
    )


# Перегляд одного поста
@post_bp.route("/<int:id>")
def detail_post(id):
    # Якщо поста нема, повертаємо 404
    post = db.get_or_404(Post, id)

    return render_template(
        "posts/detail_post.html",
        post=post
    )


# Оновлення поста
@post_bp.route(
    "/<int:id>/update",
    methods=["GET", "POST"]
)
def update_post(id):
    post = db.get_or_404(Post, id)
    form = PostForm(obj=post)

    if request.method == "GET":
        form.tags.data = [
            tag.id for tag in post.tags
        ]
        form.author_id.data = post.user_id
        form.enabled.data = post.is_active
        form.publish_date.data = post.posted

    if form.validate_on_submit():
        # Оновлення полів об'єкта
        post.title = form.title.data.strip()
        post.content = form.content.data.strip()
        post.category = form.category.data
        post.is_active = form.enabled.data
        post.posted = form.publish_date.data
        post.user_id = form.author_id.data

        # Оновлюємо вибрані теги
        post.tags = db.session.scalars(
            db.select(Tag).where(
                Tag.id.in_(form.tags.data)
            )
        ).all()

        db.session.commit()

        flash(
            "Пост успішно оновлено!",
            "success"
        )

        return redirect(
            url_for(
                "posts.detail_post",
                id=post.id
            )
        )

    if request.method == "POST":
        flash(
            "Перевірте правильність даних.",
            "error"
        )

    return render_template(
        "posts/add_post.html",
        form=form,
        title="Редагувати пост"
    )


# Видалення поста
@post_bp.route(
    "/<int:id>/delete",
    methods=["GET", "POST"]
)
def delete_post(id):
    post = db.get_or_404(Post, id)
    form = DeletePostForm()

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()

        flash(
            "Пост успішно видалено!",
            "success"
        )

        return redirect(
            url_for("posts.list_posts")
        )

    return render_template(
        "posts/delete_confirm.html",
        post=post,
        form=form
    )

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MemoryForm
from .models import Answer, Comment, Like, Memory, MemoryMedia, Question

MAX_UPLOAD_MB = 50


def _visible_memories(user):
    """خاطره‌های عمومی + خاطره‌های خود کاربر."""
    if user.is_authenticated:
        return Memory.objects.filter(Q(visibility="public") | Q(author=user))
    return Memory.objects.filter(visibility="public")


def _save_media(memory, files):
    """فایل‌های آپلودشده را به MemoryMedia تبدیل می‌کند."""
    start = memory.media.count()
    has_cover = memory.media.filter(is_cover=True).exists()

    for i, f in enumerate(files):
        kind = (f.content_type or "").split("/")[0]
        if kind not in ("image", "video"):
            continue
        if f.size > MAX_UPLOAD_MB * 1024 * 1024:
            continue

        MemoryMedia.objects.create(
            memory=memory,
            file=f,
            media_type=kind,
            order=start + i,
            is_cover=(not has_cover and i == 0),
        )


def memory_detail(request, pk):
    memory = get_object_or_404(
        _visible_memories(request.user)
        .select_related("author", "folder", "folder__parent")
        .prefetch_related("media", "category"),
        pk=pk,
    )

    context = {
        "memory": memory,
        "questions": memory.questions.select_related("author").prefetch_related("answers__author"),
        "comments": memory.comments.filter(parent__isnull=True)
                          .select_related("author").prefetch_related("replies__author"),
        "like_count": memory.likes.count(),
        "user_liked": request.user.is_authenticated
                      and memory.likes.filter(user=request.user).exists(),
        "related": Memory.objects.filter(visibility="public", category__in=memory.category.all())
                         .exclude(pk=memory.pk).distinct()[:3],
    }
    return render(request, "blog/memory.html", context)


@login_required(login_url="account:login")
def memory_create(request):
    if request.method == "POST":
        form = MemoryForm(request.POST, user=request.user)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.author = request.user
            memory.save()
            form.save_m2m()
            _save_media(memory, request.FILES.getlist("media_files"))
            return redirect("memory_detail", pk=memory.pk)
    else:
        form = MemoryForm(user=request.user)

    return render(request, "blog/add-memory.html", {"form": form})


@login_required(login_url="account:login")
def memory_edit(request, pk):
    memory = get_object_or_404(Memory, pk=pk, author=request.user)
    form = MemoryForm(request.POST or None, instance=memory, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        _save_media(memory, request.FILES.getlist("media_files"))
        return redirect("memory_detail", pk=memory.pk)

    return render(request, "blog/add-memory.html", {"form": form})


@login_required(login_url="account:login")
@require_POST
def memory_delete(request, pk):
    memory = get_object_or_404(Memory, pk=pk, author=request.user)

    for m in memory.media.all():
        m.file.delete(save=False)

    memory.delete()
    return redirect("index")


@login_required(login_url="account:login")
@require_POST
def memory_like(request, pk):
    memory = get_object_or_404(_visible_memories(request.user), pk=pk)

    like, created = Like.objects.get_or_create(user=request.user, memory=memory)
    if not created:
        like.delete()

    return redirect("memory_detail", pk=memory.pk)


@login_required(login_url="account:login")
@require_POST
def memory_comment(request, pk):
    memory = get_object_or_404(_visible_memories(request.user), pk=pk)

    text = request.POST.get("context", "").strip()
    kind = request.POST.get("kind")

    if text:
        model = Question if kind == "question" else Comment
        model.objects.create(memory=memory, author=request.user, context=text)

    return redirect("memory_detail", pk=memory.pk)


@login_required(login_url="account:login")
@require_POST
def answer_question(request, question_id):
    question = get_object_or_404(Question.objects.select_related("memory"), pk=question_id)

    if question.memory.author_id != request.user.id:
        return HttpResponseForbidden("Only the author can answer.")

    text = request.POST.get("context", "").strip()
    if text:
        Answer.objects.create(question=question, author=request.user, context=text)

    return redirect("memory_detail", pk=question.memory_id)
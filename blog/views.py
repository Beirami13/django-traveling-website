from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import MemoryForm

from blog.models import Question, Answer, Memory


@login_required(login_url="account:login")
def memory_create(request):
    if request.method == "POST":
        form = MemoryForm(request.POST, user=request.user)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.author = request.user
            memory.save()
            form.save_m2m()
            return redirect("memory_detail", pk=memory.pk)
    else:
        form = MemoryForm(user=request.user)

    return render(request, "blog/add-memory.html", {"form": form})
@login_required(login_url="account:login")
def memory_edit(request, pk):
    memory = get_object_or_404(Memory, pk=pk, author=request.user)
    form = MemoryForm(request.POST or None, instance=memory, user=request.user)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('memory_detail', pk=memory.pk)

    return render(request, '/', {'form': form})

@login_required(login_url="account:login")
@require_POST
def memory_delete(request, pk):
    memory = get_object_or_404(Memory, pk=pk, author=request.user)
    for m in memory.media.all():
        m.file.delete(save=False)
    memory.delete()
    memory.delete()
    return redirect("index")

@login_required(login_url="account:login")
@require_POST
def answer_question(request, question_id):
    question = get_object_or_404(Question.objects.select_related('memory'), pk=question_id)

    if question.memory.author_id != request.user.id:
        return HttpResponseForbidden("Only the author can answer.")

    text = request.POST.get('context', '').strip()
    if text:
        Answer.objects.create(question=question, author=request.user, context=text)

    return redirect('/')
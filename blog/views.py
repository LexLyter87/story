from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Story, Comment, Category,Like
from .forms import StoryForm, CommentForm
from django.views import View
from .forms import UserRegisterForm, UserEditForm, ProfileEditForm
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST



class StoryListView(ListView):
    model = Story
    template_name = 'blog/story_list.html'
    context_object_name = 'stories'
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Story.objects.filter(status=Story.Status.PUBLISHED).annotate(like_count=Count('likes')).select_related('author', 'category')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            )
        return queryset.order_by('-published_at', '-pk')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured_story = Story.objects.filter(status=Story.Status.PUBLISHED).order_by('-published_at').first()
        context['featured_story'] = featured_story
        return context
    
    
class StoryDetailView(DetailView):
    model = Story
    template_name = 'blog/story_detail.html'
    context_object_name = 'story'

    def get_queryset(self):
        return Story.objects.filter(status=Story.Status.PUBLISHED).select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        context['comments'] = story.comments.filter(is_active=True).select_related('author__profile')
        context['comment_form'] = CommentForm()
        context['like_count'] = story.likes.count()
        if self.request.user.is_authenticated:
            context['user_likes'] = story.likes.filter(user=self.request.user).exists()
        else:
            context['user_likes'] = False
        return context


class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    form_class = StoryForm
    template_name = 'blog/story_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Ваш рассказ успешно создан!")
        return super().form_valid(form)
    
    success_url = reverse_lazy('blog:dashboard')
    

class AuthorRequireMixin(UserPassesTestMixin):
    def test_func(self):
        story = self.get_object()
        return self.request.user == story.author
    

class StoryUpdateView(LoginRequiredMixin, AuthorRequireMixin, UpdateView):
    model = Story
    form_class = StoryForm
    template_name = 'blog/story_form.html'

    def form_valid(self, form):
        messages.success(self.request, "Рассказ успешно обновлен.")
        return super().form_valid(form)
    
    success_url = reverse_lazy('blog:dashboard')


class StoryDeleteView(LoginRequiredMixin, AuthorRequireMixin, DeleteView):
    model = Story
    template_name = 'blog/story_confirm_delete.html'
    success_url = reverse_lazy('blog:story_list')

    def form_valid(self, form):
        messages.success(self.request, "Рассказ успешно удален.")
        return super().form_valid(form)
    

@login_required
def add_comment(request, slug):
    story = get_object_or_404(Story, slug=slug, status=Story.Status.PUBLISHED)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.story = story
            comment.author = request.user
            comment.save()
            messages.success(request, "Ваш комментарий добавлен и ожидает модерации.")
            return redirect('blog:story_detail', slug=story.slug)
    return redirect('blog:story_detail', slug=story.slug)


class RegisterView(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'registration/register.html', {'form': form})
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Аккаунт для {username} успешно создан! Теперь вы можете войти.")
            return redirect('login')
        
        return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    user_stories = Story.objects.filter(author=request.user).annotate(
        comment_count=Count('comments'),
        like_count=Count('likes')
    )

    drafts = user_stories.filter(status=Story.Status.DRAFT).order_by('-updated_at')
    published = user_stories.filter(status=Story.Status.PUBLISHED).order_by('-published_at')

    context = {
        'drafts': drafts,
        'published': published,
        'profile': request.user.profile
    }
    return render(request, 'blog/dashboard.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserEditForm(request.POST, instance=request.user)
        p_form = ProfileEditForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('blog:dashboard')
    
    else:
        u_form = UserEditForm(instance=request.user)
        p_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'blog/profile_edit.html', context)


class UserStoryListView(ListView):
    model = Story
    template_name = 'blog/user_stories.html'
    context_object_name = 'stories'
    paginate_by = 5

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Story.objects.filter(author=self.author, status=Story.Status.PUBLISHED).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context
    

class CategoryStoryListView(ListView):
    model = Story
    template_name = 'blog/category_stories.html'
    context_object_name = 'stories'
    paginate_by = 5

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Story.objects.filter(category=self.category, status=Story.Status.PUBLISHED).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def toggle_like(request, slug):
    story = get_object_or_404(
        Story,
        slug=slug,
        status=Story.Status.PUBLISHED
    )
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(story=story, user=request.user)
        if not created:
            like.delete()
            messages.info(request, 'Лайк удалён.')
        else:
            messages.success(request, 'Вы поставили лайк!')
    return redirect('blog:story_detail', slug=slug)
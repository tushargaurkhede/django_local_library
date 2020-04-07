from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre, Language

def index(request):
    '''view function for home page of site.'''

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    #The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Generate count of books under 'fiction' category
    fiction_books = Genre.objects.filter(name__contains='fiction')

    # Number of visits to this view, as counted in the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'fiction_books': fiction_books,
        'num_visits': num_visits,
    }

    # Render the HTML tempate index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.views import generic

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5
    
class BookDetailView(generic.DetailView):
    model = Book
    
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

from django.contrib.auth.mixins import LoginRequiredMixin

#Enable logged in user to see the list of books that he borrowed along with due date
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    '''Generic class-based view listing books on loan to current user'''
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

#Allow only Librarian group to see the list of all borrowed books
from django.contrib.auth.mixins import PermissionRequiredMixin 
    
class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    '''Generic class-based view listing books on loan across users. Only visible to users with can_mark_returned permission.'''
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

#Rendering form for processing
import datetime

from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    '''View function for renewing a specific BookInstance by librarian.'''
    book_instance = get_object_or_404(BookInstance, pk=pk)

    #If this is a POST request then process the form data
    if request.method == 'POST':

        #create a form instance and populate it with data from the request (binding)
        form = RenewBookForm(request.POST)

        #check if the form is valid
        if form.is_valid():
            #process the data in form.cleaned_data as required:
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            #redirect to a new URL
            return HttpResponseRedirect(reverse('all-borrowed'))

    #if this a GET (or any other method), create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

#Create, delete and edit author records from our library
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_birth': '05/01/1965','date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_birth': '05/01/1965','date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'
    

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'
    
    
#Create, delete and edit author records from our library
from catalog.models import Book

class BookCreate(CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

    

    

from django.test import TestCase

# Create your tests here.

from catalog.models import Author
from django.urls import reverse

class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #Create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % author_num, last_name = 'Surname %s' % author_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 3)

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from catalog.models import BookInstance, Book

class LoanedBooksByUserListViewTest(TestCase):

    def setUp(self):
        #Create test users
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        #Create test books
        test_book1 = Book.objects.create(title='Test Book 1')
        test_book2 = Book.objects.create(title='Test Book 2')

        #Create test book instances
        BookInstance.objects.create(book=test_book1, imprint='Test Imprint 1', borrower=test_user1, status='o')
        BookInstance.objects.create(book=test_book2, imprint='Test Imprint 2', borrower=test_user1, status='o')
        BookInstance.objects.create(book=test_book2, imprint='Test Imprint 3', borrower=test_user2, status='o')

    def test_loan_books_by_user_list_view(self):
        #Login as test_user1
        self.client.login(username='testuser1', password='12345')

        #Issue GET request to the view
        response = self.client.get(reverse('my-borrowed'))

        #Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        #Check that the correct template is used
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

        #Check that only books borrowed by test_user1 are displayed
        self.assertContains(response, 'Test Book 1')
        self.assertContains(response, 'Test Book 2')
        self.assertNotContains(response, 'Test Imprint 3')

        def test_only_borrowed_books_in_list(self):
            login = self.client.login(username='testuser1', password='12345')
            resp = self.client.get(reverse('my-borrowed'))

            # Check our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # Check that we got a response "success"
            self.assertEqual(resp.status_code, 200)

            # Check that initially we don't have any books in list (none on loan)
            self.assertTrue('bookinstance_list' in resp.context)
            self.assertEqual(len(resp.context['bookinstance_list']), 0)

            # Now change all books to be on loan
            get_ten_books = BookInstance.objects.all()[:10]

            for copy in get_ten_books:
                copy.status = 'o'
                copy.save()

            # Check that now we have borrowed books in the list
            resp = self.client.get(reverse('my-borrowed'))
            # Check our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # Check that we got a response "success"
            self.assertEqual(resp.status_code, 200)

            self.assertTrue('bookinstance_list' in resp.context)

            # Confirm all books belong to testuser1 and are on loan
            for bookitem in resp.context['bookinstance_list']:
                self.assertEqual(resp.context['user'], bookitem.borrower)
                self.assertEqual('o', bookitem.status)

        def test_pages_ordered_by_due_date(self):

            # Change all books to be on loan
            for copy in BookInstance.objects.all():
                copy.status = 'o'
                copy.save()

            login = self.client.login(username='testuser1', password='12345')
            resp = self.client.get(reverse('my-borrowed'))

            # Check our user is logged in
            self.assertEqual(str(resp.context['user']), 'testuser1')
            # Check that we got a response "success"
            self.assertEqual(resp.status_code, 200)

            # Confirm that of the items, only 10 are displayed due to pagination.
            self.assertEqual(len(resp.context['bookinstance_list']), 10)

            last_date = 0
            for copy in resp.context['bookinstance_list']:
                if last_date == 0:
                    last_date = copy.due_back
                else:
                    self.assertTrue(last_date <= copy.due_back)
    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        #Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual( len(resp.context['bookinstance_list']),0)

        #Now change all books to be on loan
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status='o'
            copy.save()

        #Check that now we have borrowed books in the list
        resp = self.client.get(reverse('my-borrowed'))
        #Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        #Confirm all books belong to testuser1 and are on loan
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        #Change all books to be on loan
        for copy in BookInstance.objects.all():
            copy.status='o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        #Check our user is logged in
        self.assertEqual(str(resp.context['user']), 'testuser1')
        #Check that we got a response "success"
        self.assertEqual(resp.status_code, 200)

        #Confirm that of the items, only 10 are displayed due to pagination.
        self.assertEqual( len(resp.context['bookinstance_list']),10)

        last_date=0
        for copy in resp.context['bookinstance_list']:
            if last_date==0:
                last_date=copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)

















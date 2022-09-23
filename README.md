# Blog site

### User
User can only be created by python manage.py createsuperuser or through User model 

### Routes
1. host/signin/ - Sign In page
2. host/main/ - page with all existing posts. If iser is authenticated than post/category create, delete and update are available
3. host/category/ - create or edit (category_id param is required) category
4. host/edit/ - edit (category_id param is required) post

### API
For every method except GET Token authentication is required
1. host/api/posts/
2. host/api/categories/



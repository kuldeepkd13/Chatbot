from django.shortcuts import render,redirect
from django.contrib import messages ,auth
from django.contrib.auth import login as auth_login

from django.contrib.auth.models import User
import os
from dotenv import load_dotenv
from .forms import PdfUploadForm
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import pickle
from .models import User
# from django.contrib.auth.decorators import login_required


# Create your views here.


# Load environment variables from .env file
load_dotenv()


def home(request):
    # Check if the username is in session storage
    username = request.session.get('username', None)
    return render(request, 'home.html', {'username': username})


    
def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.', extra_tags='error')
                return redirect('register')
            else:
                user = User(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password,
                    confirm_password=confirm_password
                )
                user.save()
                messages.success(request, 'User registered successfully.', extra_tags='success')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.', extra_tags='error')
            return redirect('register')
    else:
        return render(request, 'signup.html')
    
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if user.password == password:
                # Authentication successful
                auth_login(request, user)
                # print(user.username,"username")
                request.session['username'] = user.username
                messages.success(request, 'Logged in successfully.', extra_tags='success')
                return redirect('home')
            else:
                messages.error(request, 'Invalid password for the provided username.', extra_tags='error')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.', extra_tags='error')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    username = request.session.get('username', None)
    auth.logout(request)
    request.session.pop('username', None)
    messages.success(request, f"Thanks, {username}, for visiting our website!", extra_tags='success')
    return redirect('home')



pdf_data = {}

# Load or create an empty chat history list in the session
def get_or_create_chat_history(request):
    chat_history = request.session.get('chat_history', [])
    return chat_history

def process_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text=text)
    store_name = pdf_file.name[:-4]  # Extract the name without the '.pdf' extension
    return chunks, store_name

def pdf_upload_view(request):
    pdf_name = None
    username = request.session.get('username', None)
    if request.method == 'POST':
        form = PdfUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.cleaned_data['pdf_file']
            chunks, pdf_name = process_pdf(pdf_file)
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            pdf_data[pdf_name] = VectorStore  # Store data in memory instead of a file
            return render(request, 'upload_template.html', {'pdf_name': pdf_name , 'username': username})
    else:
        form = PdfUploadForm()

    context = {'form': form , 'username': username}
    return render(request, 'upload_template.html', context)

def chat_view(request):
    pdf_name = request.GET.get('pdf_name')
    chat_history = get_or_create_chat_history(request)  # Get or create chat history
    username = request.session.get('username', None)
    if pdf_name:
        VectorStore = pdf_data.get(pdf_name)
        if VectorStore is not None:
            query = request.GET.get('query', '')
            if query:
                docs = VectorStore.similarity_search(query=query, k=3)
                llm = OpenAI()
                chain = load_qa_chain(llm, chain_type="stuff")
                response = chain({"input_documents": docs, "question": query}, return_only_outputs=True)
                response_text = response.get('output_text', "No answer found.")
                chat_history.append({'question': query, 'response': response_text})
                request.session['chat_history'] = chat_history
            else:
                response_text = ""
            context = {'pdf_name': pdf_name, 'query': query, 'response_text': response_text, 'chat_history': chat_history ,'username': username}
            return render(request, 'chat_template.html', context)
        else:
            return render(request, 'error_template.html', {'error_message': 'PDF data not found.'})
    else:
        return render(request, 'error_template.html', {'error_message': 'PDF name not provided.'})


def end_chat_view(request):
    if request.method == 'POST':
        pdf_name = request.POST.get('pdf_name')
        if pdf_name:
            try:
                # Remove the PDF data from the in-memory dictionary
                if pdf_name in pdf_data:
                    del pdf_data[pdf_name]

                # Clear the chat history from the session
                request.session['chat_history'] = []

                return redirect('upload')
            except KeyError:
                pass

    return render(request, 'error_template.html', {'error_message': 'PDF name not provided.'})

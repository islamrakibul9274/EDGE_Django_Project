# 🖩 Calculator Store - Django Project  

Welcome to **Calculator Store**, an online store where you can browse and purchase various types of calculators, including **scientific, graphing, financial, and basic calculators**. Built using **Django**, **Bootstrap**, and **SQLite**, this project provides a clean and structured platform to showcase calculator products.  

## 🚀 Features  

✔ **Home Page** - Displays featured calculators.  
✔ **Blog Page** - Lists all calculators available for purchase with images, descriptions, and prices.  
✔ **Buy Now Button** - Redirects users to external websites for purchasing calculators.  
✔ **Admin Panel** - Allows admins to add, update, or delete calculator listings.  
✔ **Database Integration** - Uses SQLite to store all calculator products.  
✔ **Bootstrap UI** - Provides a responsive and modern layout.  

---

## 🛠️ Installation Guide  

Follow these steps to set up and run the project on your local machine.  

### 1️⃣ **Clone the Repository**  
```bash
git clone https://github.com/yourusername/calculator-store.git
cd calculator-store

2️⃣ Create a Virtual Environment
bash
Copy
Edit
python -m venv env
Activate the environment:

Windows: env\Scripts\activate
Mac/Linux: source env/bin/activate
3️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4️⃣ Apply Migrations
bash
Copy
Edit
python manage.py makemigrations
python manage.py migrate
5️⃣ Create a Superuser (Admin Panel)
bash
Copy
Edit
python manage.py createsuperuser
Follow the prompts to set up a username and password.

6️⃣ Run the Server
bash
Copy
Edit
python manage.py runserver
Then open the browser and visit:

Home Page: http://127.0.0.1:8000/
Blog Page: http://127.0.0.1:8000/blog/
Admin Panel: http://127.0.0.1:8000/admin/
📂 Project Structure
bash
Copy
Edit
calculator-store/
│── calculatorstore/   # Django Project Configuration
│── blog/              # Blog App (Models, Views, URLs)
│── templates/         # HTML Templates
│── static/            # CSS, JS, and Images
│── db.sqlite3         # Database File
│── manage.py          # Django Management Script
│── env/               # Virtual Environment (Ignore this in Git)
🛠️ Technologies Used
Django (Python Web Framework)
Bootstrap (CSS Framework)
SQLite (Database)
HTML, CSS (Frontend)
🤝 Contributing
Feel free to fork this repository and contribute improvements!

Fork the repository
Create a new branch (git checkout -b feature-branch)
Commit your changes (git commit -m "Added a new feature")
Push to your branch (git push origin feature-branch)
Create a Pull Request
📄 License
This project is open-source and available under the MIT License.